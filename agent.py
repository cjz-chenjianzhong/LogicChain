from flask import Flask, request
import config

app = Flask(__name__)

g_prompt_template = config.prompt_template[config.LLM_CHOICE][config.LANGUAGE_CHOICE]

#----------------------------------------------------------------------
# DESCRIBTION: Agent Setting Service Entry
# PARAMETER:    ...
# UPDATE LOG:
#               2024/05/08 chenjianzhong: Created
#----------------------------------------------------------------------
@app.route('/agent', methods=['POST'])
def agent():
    data = request.get_json()
    operate_type = data.get('type')

    if 'add' == operate_type:
        # add agent

        agent = data.get('agent')

        if type(agent) is not type([]):
            agent = [agent]

        with open(config.AGENT_FILE, 'a', encoding='utf-8') as file:
            for agent_str in agent:
                # 去除代理中的换行
                agent_str = agent_str.replace("\n", "")

                agent_str = agent_str + '\n'

                file.write(agent_str)

        return {'status' : 'ok'}

    elif 'update' == operate_type:
        # update agent

        agent_id = data.get('agent_id')
        agent = data.get('agent')

        with open(config.AGENT_FILE, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        lines[agent_id - 1] = agent

        with open(config.AGENT_FILE, 'w', encoding='utf-8') as file:
            file.writelines(lines)

        return {'status' : 'ok'}

    elif 'delete' == operate_type:
        # delete agent

        agent_id = data.get('agent_id')

        with open(config.AGENT_FILE, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        lines[agent_id - 1] = ''

        with open(config.AGENT_FILE, 'w', encoding='utf-8') as file:
            file.writelines(lines)

        return {'status' : 'ok'}

    elif 'delete_all' == operate_type:
        # delete all agent

        with open(config.AGENT_FILE, 'w', encoding='utf-8') as file:
            file.write('')

        return {'status': 'ok'}

    elif 'get_all_agents' == operate_type:
        # get all agents

        with open(config.AGENT_FILE, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        all_agents = ''

        for id, line in enumerate(lines):
            agent_prefix_str = g_prompt_template['agent_prefix_template'].replace('###{ACTION_ID}###', str(id+1))
            new_line = agent_prefix_str + line
            all_agents = all_agents + new_line

        return {'status' : 'ok', 'all_agents' : all_agents}

    else:

        print(f'invalid agent param, type = {operate_type}')
        return {'status' : 'error'}