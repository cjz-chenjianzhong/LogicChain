from flask import Flask, request
import multiprocessing
import importlib
import re
import json
import threading
import config
import requests

app = Flask(__name__)

g_prompt_template = config.prompt_template[config.LLM_CHOICE][config.LANGUAGE_CHOICE]

execute_script_key_str = g_prompt_template['execute_script_key']

method_key_str = g_prompt_template['method_key']

input_parameter_key_str = g_prompt_template['input_parameter_key']

# Get Rule's Action Command that Triggers the Agent
rule_command_trig_action_key_str  = g_prompt_template['rule_command_trig_action_key']

# Agent Normal Result Handling Template: This template combines the rule-based command to trigger the agent and the agent's result
agent_ok_result_template = g_prompt_template['agent_ok_result_template']

# Agent Exceptional Result Handling Template: This template combines the rule-based command to trigger the agent with a null result.
agent_no_result_template = g_prompt_template['agent_no_result_template']

#----------------------------------------------------------------------
# DESCRIBTION:  This function is used to call a method from any Python
#               script. In our system, it is commonly used to excute
#               the entry method(function) in the python script of agent.
# PARAMETER:    ...
# UPDATE LOG:
#               2024/05/08 chenjianzhong: Created
#----------------------------------------------------------------------
def call_function(module_name, function_name, *args, **kwargs):
    module = importlib.import_module(module_name)
    function = getattr(module, function_name)
    return function(*args, **kwargs)

#----------------------------------------------------------------------
# DESCRIBTION:  agent execute function, entry for agent execution thread;
#               call agent function in the script.
#               combines the rule-based command to trigger the agent and
#               the agent's result, then send them to LLM to trig new rule.
# PARAMETER:    json_str_list : list of agent json string
# UPDATE LOG:
#               2024/05/08 chenjianzhong: Created
#----------------------------------------------------------------------
def act_execute_func(json_str_list):
    ret = ''

    for json_str in json_str_list:

        try:
            # json string to json
            agent = json.loads(json_str)

            print(f'agent = {agent}')

            agent_ret = call_function( agent[execute_script_key_str], agent[method_key_str], *(agent[input_parameter_key_str].values()) )

            if agent_ret['status'] == 'ok':

                agent_ok_result_str = agent_ok_result_template.replace('###{RULE_COMMAND_TRIG_ACTION}###', agent[rule_command_trig_action_key_str]).replace('###{AGENT_RESULT}###', agent_ret['result'])

                ret += agent_ok_result_str

            else:
                agent_no_result_str = agent_no_result_template.replace('###{RULE_COMMAND_TRIG_ACTION}###', agent[rule_command_trig_action_key_str])

                ret += agent_no_result_str

        except Exception as e:

            print(f'call_function error = {str(e)}')
            return { 'status' : 'error', 'error_info' : str(e) }

    # The result of the action execution is sent back to the master control service, and efforts continue to trigger rules
    json_data = {
        'text_info': ret,
    }

    response = requests.post(config.CTRL_URL, data=json.dumps(json_data), headers={'Content-Type': 'application/json'})

    return response.status_code

#----------------------------------------------------------------------
# DESCRIBTION:  Process entry function: for each agent task, a process
#               is initiated to execute it, within which a thread is
#               started to perform the agent task. The use of a process
#               facilitates the implementation of a timeout exit feature
#               for the agent execution. Whether the agent task executes
#               successfully to completion or times out, the process
#               will exit and be terminated.
# PARAMETER:    json_str_list : list of agent json string
# UPDATE LOG:
#               2024/05/08 chenjianzhong: Created
#----------------------------------------------------------------------
def act_process_func(json_str_list):

    thread = threading.Thread(target = act_execute_func, args=(json_str_list, ))

    thread.start()
    thread.join(config.ACT_THREAD_RUN_MAX_TIME)
    print('process exit')
    exit()

#----------------------------------------------------------------------
# DESCRIBTION: Agent execution service entry: Receives the execution
#              agent text sent by the master control service. The text
#              contains one or more agent JSON strings in a specified
#              format. Match and parse the agent JSON from the text
#              and execute it.
# PARAMETER:    ...
# UPDATE LOG:
#               2024/05/08 chenjianzhong: Created
#----------------------------------------------------------------------
@app.route('/act', methods=['POST'])
def act():
    data = request.get_json()
    act_text = data.get('act_text')

    # Preprocessing of text containing JSON strings.
    act_text = act_text.replace('\n', '')
    act_text = act_text.replace(' ', '')

    # The JSON generated by LLM often contains the character ” and “, which is different from the " symbol, so it needs to be addressed.
    act_text = act_text.replace("”", '"').replace("“", '"')

    json_pattern = r"```json\{.*?\}```"
    json_matches = re.finditer(json_pattern, act_text)

    json_str_list = []

    for json_match in json_matches:

        json_string = json_match.group()

        # Remove the prefixes and suffixes used to mark the JSON string
        json_string = json_string.replace("```json", "")
        json_string = json_string.replace("```", "")

        json_str_list.append(json_string)


    if [] == json_str_list:

        return {'status': 'error', 'error_info' : 'no agent json to execute'}

    # One or more received agents are uniformly executed by a single process.
    process = multiprocessing.Process(target=act_process_func, args=(json_str_list,))
    process.start()

    return { 'status' : 'ok' }







