from flask import Flask, request
from datetime import datetime
import json
import requests
import config
import threading

app = Flask(__name__)

g_is_first_clock = True

#----------------------------------------------------------------------
# DESCRIBTION: Timer generates periodic clock signals to the LLM,
#              attempting to trigger rules related to time.
# PARAMETER:    ...
# UPDATE LOG:
#               2024/05/08 chenjianzhong: Created
#----------------------------------------------------------------------
def period_clock():
    global g_is_first_clock

    # 获取当前时间
    current_time = datetime.now()
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M')
    now_time_str = config.prompt_template[config.LLM_CHOICE][config.LANGUAGE_CHOICE]['now_time_prompt_template'].replace('###{NOW_TIME}###', formatted_time)
    print(now_time_str)

    if False == g_is_first_clock:

        # Skipping the first message transmission via a flag variable, as the control service has not yet started
        # when the system is initialized. After a period of delay, the transmission of clock messages is initiated.
        # Essentially, this is a delay to wait for the service to be ready, which is not a very clean logic.

        json_data = {
            'text_info': now_time_str,
        }

        response = requests.post(config.CTRL_URL, data=json.dumps(json_data), headers={'Content-Type': 'application/json'})

        if response.status_code != 200:
            print(f'send clock message to control severice fail, response code = {response.status_code}')

    g_is_first_clock = False

    # restart the timer
    threading.Timer(config.CTRL_CLOCK_PERIOD, period_clock).start()

if True == config.CTRl_CLOCK_ENABLE:
    period_clock()

#----------------------------------------------------------------------
# DESCRIBTION: Obtain candidate rules that match the received information;
#              currently, it results in getting all the rules, and recall
#              mechanisms similar to RAG (Retrieval-Augmented Generation)
#              have not yet been implemented.
# PARAMETER:    ...
# UPDATE LOG:
#               2024/05/08 chenjianzhong: Created
#----------------------------------------------------------------------
def get_rules():

    json_data = {
        'type': 'get_all_rules',
    }

    json_str = json.dumps(json_data)

    response = requests.post(config.RULE_URL, data=json_str, headers={'Content-Type': 'application/json'})

    if response.status_code == 200:
        result = json.loads(response.text)
        return result
    else:
        print('get rules Failed!')
        print('Status Code:', response.status_code)
        return {'status' : 'error'}

#----------------------------------------------------------------------
# DESCRIBTION: Obtain the candidate agent actions.
# PARAMETER:    ...
# UPDATE LOG:
#               2024/05/08 chenjianzhong: Created
#----------------------------------------------------------------------
def get_agents():

    json_data = {
        'type': 'get_all_agents',
    }

    json_str = json.dumps(json_data)

    response = requests.post(config.AGENT_URL, data=json_str, headers={'Content-Type': 'application/json'})

    # 检查请求是否成功
    if response.status_code == 200:
        result = json.loads(response.text)
        return result
    else:
        print('get agents Failed!')
        print('Status Code:', response.status_code)
        return {'status' : 'error'}

#----------------------------------------------------------------------
# DESCRIBTION: Used for accessing the large model inference service.
# PARAMETER:   ...
# UPDATE LOG:
#               2024/05/08 chenjianzhong: Created
#----------------------------------------------------------------------
def LLM_infer(system_prompt, query):

    json_data = {
        'system_prompt' : system_prompt,
        'query'         : query,
    }

    response = requests.post(config.INFER_URL, data=json.dumps(json_data), headers={'Content-Type': 'application/json'})

    if response.status_code == 200:
        result = json.loads(response.text)
        return result
    else:
        print('llm infer Failed!')
        print('Status Code:', response.status_code)
        return {'status' : 'error'}

#----------------------------------------------------------------------
# DESCRIBTION: Used for accessing the action execution service.
# PARAMETER:    act_str : The LLM generates a result text based on rules,
#                         triggered rule information, and action information,
#                         which generally includes the JSON text of the agent
#                         to be executed.
# UPDATE LOG:
#               2024/05/08 chenjianzhong: Created
#----------------------------------------------------------------------
def ACT_Execute(act_str):

    json_data = {
        'act_text' : act_str,
    }

    response = requests.post(config.ACT_URL, data=json.dumps(json_data), headers={'Content-Type': 'application/json'})

    if response.status_code == 200:
        result = json.loads(response.text)
        return result
    else:
        print('act execute Failed!')
        print('Status Code:', response.status_code)
        return {'status' : 'error'}

#----------------------------------------------------------------------
# DESCRIBTION:  control service entry, Used to receive various types
#               of information, invoke the LLM to make decisions based
#               on rules, and determine the action to be executed.
# PARAMETER:   ...
# UPDATE LOG:
#               2024/05/08 chenjianzhong: Created
#----------------------------------------------------------------------
@app.route('/ctrl', methods=['POST'])
def ctrl():
    rule_trig_history = ''

    # Obtain all rules, currently no recall is made based on the received information.
    ret = get_rules()
    if ret['status'] == 'error':
        return {'status' : 'error'}
    else:
        all_rules = ret['all_rules']

    data = request.get_json()

    # Received text information.
    receive_text_info = data.get('text_info')

    prompt_template_dic = config.prompt_template[config.LLM_CHOICE][config.LANGUAGE_CHOICE]

    # Construct an initial rule inference query.
    init_rule_infer_general_prompt_str = prompt_template_dic['init_rule_infer_general_prompt_template']

    init_rule_infer_general_prompt_str = init_rule_infer_general_prompt_str.replace('###{RULES}###', all_rules).replace('###{RECEIVE_TEXT_INFO}###', receive_text_info)

    init_rule_infer_system_prompt_str = prompt_template_dic['init_rule_infer_system_prompt_template']

    # The received raw information is recorded into the historical rule trigger information.
    raw_text_info_trig_rule_str = prompt_template_dic['raw_text_info_trig_rule']

    rule_trig_history += raw_text_info_trig_rule_str.replace('###{RECEIVE_TEXT_INFO}###', receive_text_info)

    # The information is passed to the LLM for the initial rule inference.
    infer_ret = LLM_infer(init_rule_infer_system_prompt_str, init_rule_infer_general_prompt_str)
    if infer_ret['status'] == 'ok':
        result = infer_ret['result']

        if prompt_template_dic['stop_rule_infer_text'] in result:

            # Rule inference stop
            return { 'status' : 'ok', 'result' : prompt_template_dic['stop_rule_infer_text'] }

        else:

            # Rule triggered, the action command of the triggered rule is stored in the chained inference result history.
            chain_rule_trig_info = prompt_template_dic['chain_rule_trig_info']

            chain_rule_trig_info = chain_rule_trig_info.replace('###{ID}###', '0').replace('###{RULE_TRIG_INFO}###', result)

            rule_trig_history += chain_rule_trig_info

    else:
        return {'status' : 'error'}

    # Construct a chained rule inference query.
    chain_rule_infer_general_prompt_str = prompt_template_dic['chain_rule_infer_general_prompt_template']

    chain_rule_infer_general_prompt_str = chain_rule_infer_general_prompt_str.replace('###{RULES}###', all_rules).replace('###{RULE_TRIG_HISTORY_INFO}###', rule_trig_history)

    chain_rule_infer_system_prompt_str = prompt_template_dic['chain_rule_infer_system_prompt_template']

    # Input all the results of the triggered rules into the LLM for chained inference, continuing until 'no rules are triggered'
    # or the number of chained inference attempts exceeds the upper limit.
    infer_chain_cnt = 1

    while True:

        infer_ret = LLM_infer(chain_rule_infer_system_prompt_str, chain_rule_infer_general_prompt_str)

        if infer_ret['status'] == 'ok':
            result = infer_ret['result']

            if prompt_template_dic['stop_rule_infer_text'] in result:
                # chained inference stop
                break
            else:
                # Chained rule inference triggers the rule, the action command of the triggered rule is stored in the chained inference result history.
                chain_rule_trig_info = prompt_template_dic['chain_rule_trig_info']

                chain_rule_trig_info = chain_rule_trig_info.replace('###{ID}###', str(infer_chain_cnt)).replace('###{RULE_TRIG_INFO}###', result)

                rule_trig_history += chain_rule_trig_info

                chain_rule_infer_general_prompt_str = chain_rule_infer_general_prompt_str.replace('###{RULES}###', all_rules).replace('###{RULE_TRIG_HISTORY_INFO}###', rule_trig_history)

        else:

            return {'status' : 'error'}

        infer_chain_cnt += 1

        if infer_chain_cnt > config.CTRL_INFER_CHAIN_CNT_MAX:
            print(f'infer chain count > infer chain count max ({config.CTRL_INFER_CHAIN_CNT_MAX})')
            break

    # -------- Based on the results of the rule inference, determine the action to be executed. --------

    # Obtain all Agents(Actions)
    ret = get_agents()
    if ret['status'] == 'error':
        return {'status' : 'error'}
    else:
        all_agents = ret['all_agents']

    agent_decide_general_prompt_str = prompt_template_dic['agent_decide_general_prompt_template'].replace('###{RULES_AND_RULE_TRIG_HISTORY_INFO}###', chain_rule_infer_general_prompt_str)
    agent_decide_general_prompt_str = agent_decide_general_prompt_str.replace('###{ALL_AGENTS}###', all_agents)

    agent_decide_system_prompt_str = prompt_template_dic['agent_decide_system_prompt_template']

    # 大模型首次推理要执行的代理APP
    infer_ret = LLM_infer(agent_decide_system_prompt_str, agent_decide_general_prompt_str)
    if infer_ret['status'] == 'ok':

        infer_result = infer_ret['result']

        if prompt_template_dic['stop_agent_decide_text'] in infer_result:
            # The LLM infers and selects the Agent(Action) to be executed.
            return { 'status': 'ok', 'rule_trig_result': rule_trig_history, 'action_result': prompt_template_dic['stop_agent_decide_text'] }
        else:
            pass
    else:

        return { 'status' : 'error' }

    # Agent(Action) Execute
    act_ret = ACT_Execute(infer_result)

    if act_ret['status'] != 'ok':
        return {'status' : 'error', 'rule_trig_result': rule_trig_history, 'action_result' : 'try to execute action fail' }

    # [Note] there is no chained calling of actions.
    # chained execution of actions can be constructed by setting up chained rules.
    return { 'status' : 'ok', 'rule_trig_result': rule_trig_history, 'action_result' : 'try to exectue action ok' }






