import sys
import os

# AGENT CONFIG FILE PATH
AGENT_FILE = './agent.txt'

# RULE CONFIG FILE PATH
RULE_FILE = './rule.txt'

# Agent Script Dir
AGENT_DIR = 'agent'

# Maximum execution time for the agent execution thread, unit is seconds.
ACT_THREAD_RUN_MAX_TIME = 120

# CLOCK, default period is 25 minutes
# The setting depends on your requirement for time granularity and the computational power cost you can afford.
CTRL_CLOCK_PERIOD = 25 * 60

# CLOCK ENABLE / UNENABLE
CTRl_CLOCK_ENABLE = False

# LLM chain reasoning upper limit count, to prevent infinite loops in chain reasoning
CTRL_INFER_CHAIN_CNT_MAX = 10

# LLM inference service url
INFER_URL = 'http://127.0.0.1:5000/infer'

# rule setting service url
RULE_URL = 'http://127.0.0.1:5001/rule'

# control service url
CTRL_URL = 'http://127.0.0.1:5004/ctrl'

# agnet setting service url
AGENT_URL = 'http://127.0.0.1:5002/agent'

# agent execution service url
ACT_URL = 'http://127.0.0.1:5003/act'

# Obtain the absolute path of the agent script,  based on the relative path, and add it to the system path.
agent_absolute_dir = os.path.abspath(AGENT_DIR)
sys.path.append(agent_absolute_dir)

# ------------------------------------ Prompt Template ------------------------------------
LLM_CHOICE = 'moonshot_v1_128K'
LANGUAGE_CHOICE = 'chinese'

# The fields to be replaced in the prompt template are all marked with ###{...}###.
prompt_template = {
    'moonshot_v1_128K' : {

        'chinese' : {

            # colock drive template
            'now_time_prompt_template' : '现在时间是 ###{NOW_TIME}###',

            # first time Rule-based Reasoning General Prompt Template
            'init_rule_infer_general_prompt_template' : '规则:\n###{RULES}###\n\n收到的信息:\n###{RECEIVE_TEXT_INFO}###',

            # first time Rule-based Reasoning System Prompt Template
            'init_rule_infer_system_prompt_template' : "根据收到的信息，逐一判断每条规则的触发条件是否被满足；如果规则的触发条件被满足，则输出此规则的动作指令, 动作指令描述请遵循规则原文描述；注意如果要触发的多个规则之间有互斥, 请忽略规则之间的互斥, 输出所有触发的规则; 如果多个规则的触发条件是相同的或相似的, 这些规则的每个规则都作为独立的触发规则输出, 不要遗漏; 直接输出规则序号和触发的动作指令两个信息就行, 不用解释; 千万不要把已执行动作当做包含该动作指令的规则的触发条件, 包含已执行动作的规则的触发条件如果不满足就不要在输出了; 严格按照规则条件触发, 规则触发条件里有比如貌似、疑似、可能等等之类可能性推测要求，那可以做可能性推理，但如果规则触发条件里没有比如貌似、疑似、可能等等之类可能性推测要求，那就不要做可能性的推测; 如果所有规则的触发条件都没有被满足，则输出'没有触发任何规则'; 用中文回答；",

            # Rule-based Reasoning Stop Text
            'stop_rule_infer_text' : '没有触发任何规则',

            # General prompt template for rule chain reasoning following initial rule-based reasoning.
            'chain_rule_infer_general_prompt_template' : '规则:\n###{RULES}###\n\n触发规则的原始信息和已触发的规则信息:\n###{RULE_TRIG_HISTORY_INFO}###',

            # Original information triggering the rule
            'raw_text_info_trig_rule' : '触发规则的原始信息: ###{RECEIVE_TEXT_INFO}###\n',

            # Historical results of rule triggering.
            'chain_rule_trig_info' : '第###{ID}###次迭代触发的规则: ###{RULE_TRIG_INFO}###\n',

            # System prompt template for rule chain reasoning following initial rule-based reasoning.
            'chain_rule_infer_system_prompt_template' : "现在收到的信息是触发规则的原始信息和已触发的规则信息，请判断还有没有其他规则被已经被触发规则的动作触发；如果还有其他规则的触发条件被满足，则输出这些规则的动作指令, 动作指令描述请遵循规则原文描述, 注意不要重复输出已触发的规则; 注意如果要触发的多个规则之间有互斥, 请忽略规则之间的互斥, 输出所有触发的规则; 如果多个规则的触发条件是相同的或相似的, 这些规则的每个规则都作为独立的触发规则输出, 不要遗漏; 直接输出规则序号和触发的动作指令两个信息就行, 不用解释; 条件不满足的规则不用输出；如果其他规则的触发条件都没有被满足，则输出'没有触发任何规则'；千万不要把已执行动作当做包含该动作指令的规则的触发条件, 包含已执行动作的规则的触发条件如果不满足就不要在输出了; 严格按照规则条件触发, 规则触发条件里有比如貌似、疑似、可能等等之类可能性推测要求，那您可以做可能性推理，但如果规则触发条件里没有比如貌似、疑似、可能等等之类可能性推测要求，那您就不要做可能性的推测; 用中文回答。",

            # Action(Agent) Decision General Prompt Template.
            'agent_decide_general_prompt_template' : '\n以下信息都是判断确定要执行动作的依据信息:\n\n\n###{RULES_AND_RULE_TRIG_HISTORY_INFO}###\n\n动作:\n###{ALL_AGENTS}###',

            # Action(Agent) Decision System Prompt Template.
            'agent_decide_system_prompt_template' : "收到的信息是用于判断确定要执行动作的依据信息，包括规则信息、触发规则的原始信息、已触发规则信息和动作信息；收到的动作信息中的动作主要由自然文本动作描述和json格式的具体动作描述构成；根据收到的依据信息，判断输出要执行的动作，并生成要执行动作的json，要输出的执行动作json中的键值都是原来动作json中出现过的词汇, 不要用原来动作json中没有出现过的词汇作为要输出的新json的键值, 要输出的执行动作json中的键值对应输入内容尽量根据原来json中说明字段的要求生成；一个要输出的执行动作一个json，一个json的最外层格式是'```json{触发本动作的规则动作指令: 这个字段填写触发本动作的规则动作指令原文, 执行脚本: ..., 方法: ..., 输入参数: ...}```'；注意和已触发规则信息的动作指令无关的动作信息和对应json内容千万不要输出；所要输出的动作依赖关系由已触发规则的动作指令的依赖关系决定，任一动作只有在所依赖的动作都已被执行并都有结果返回的情况下才能被触发，不依赖任何其他动作的动作先触发;  如果没有任何与触发的规则相匹配的动作可执行，则输出'没有动作可触发'",

            # Action(Agent) reasoning stop text
            'stop_agent_decide_text' : '没有动作可触发',

            # The key that stores the rule instructions for triggering actions,
            # [NOTICE] When the LLM (Large Language Model) generates a JSON format
            # agent (action), there must be a field in the JSON that uses this text as a keyword.
            # The content within this field is the rule action instruction that triggers the JSON format agent action.
            # This is because the result of the agent's execution will be sent back to the LLM to attempt to
            # trigger other rules again, at this time the LLM needs to know what rule action instruction triggered
            # the received agent's execution result.
            'rule_command_trig_action_key' : '触发本动作的规则动作指令',

            # The key that stores the Python script for executing the agent.
            'execute_script_key' : '执行脚本',

            # The key that stores the Python method for executing the agent
            'method_key' : '方法',

            # The key that stores the input parameters for the Python method executing the agent.
            'input_parameter_key' : '输入参数',

            # The result returned after the normal execution of the agent will be combined with the rule action instruction
            # that triggered this agent, and together they will be input into the LLM (Large Language Model) to attempt to trigger new rules.
            'agent_ok_result_template' : "已执行动作'###{RULE_COMMAND_TRIG_ACTION}###'的结果是'###{AGENT_RESULT}###'\n",

            # When the agent runs abnormally and does not return a result, a null result is combined with the rule action instruction
            # that triggered the agent and sent to the LLM (Large Language Model), allowing the LLM to attempt to trigger
            # new rules (in this case, the inference result of the LLM generally does not trigger any rules).
            'agent_no_result_template' : "已执行动作'###{RULE_COMMAND_TRIG_ACTION}###'的结果为空\n",

            # rule prefix template
            'rule_prefix_template' : '规则###{RULE_ID}###: ',

            # agent prefix template
            'agent_prefix_template' : '动作###{ACTION_ID}###: ',
        }
    }
}



