from flask import Flask, request
import config

app = Flask(__name__)

g_prompt_template = config.prompt_template[config.LLM_CHOICE][config.LANGUAGE_CHOICE]

@app.route('/rule', methods=['POST'])
def rule():
    data = request.get_json()
    operate_type = data.get('type')

    if 'add' == operate_type:
        # add rule

        rule = data.get('rule')

        if type(rule) is not type([]):
            rule = [rule]

        with open(config.RULE_FILE, 'a', encoding='utf-8') as file:
            for rule_str in rule:
                # Remove \n from the rules.
                rule_str = rule_str.replace("\n", "")

                rule_str = rule_str + '\n'

                file.write(rule_str)

        return {'status' : 'ok'}

    elif 'update' == operate_type:
        # update rule

        rule_id = data.get('rule_id')
        rule = data.get('rule')

        with open(config.RULE_FILE, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        lines[rule_id - 1] = rule

        with open(config.RULE_FILE, 'w', encoding='utf-8') as file:
            file.writelines(lines)

        return {'status' : 'ok'}

    elif 'delete' == operate_type:
        # delete rule

        rule_id = data.get('rule_id')

        with open(config.RULE_FILE, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        lines[rule_id - 1] = ''

        with open(config.RULE_FILE, 'w', encoding='utf-8') as file:
            file.writelines(lines)

        return {'status' : 'ok'}

    elif 'delete_all' == operate_type:
        # delete all rules

        with open(config.RULE_FILE, 'w', encoding='utf-8') as file:
            file.write('')

        return {'status': 'ok'}

    elif 'get_all_rules' == operate_type:

        with open(config.RULE_FILE, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        all_rules = ''

        for id, line in enumerate(lines):
            rule_prefix_str = g_prompt_template['rule_prefix_template'].replace('###{RULE_ID}###', str(id+1))
            new_line = rule_prefix_str + line
            all_rules = all_rules + new_line

        return {'status' : 'ok', 'all_rules' : all_rules}

    else:

        print(f'invalid rule param, type = {operate_type}')
        return {'status' : 'error'}

