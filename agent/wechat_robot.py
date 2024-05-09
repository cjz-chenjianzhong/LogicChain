import json
import requests

def push_message(mesg_str):

    url = ''

    # 要发送的JSON数据
    json_data = {
        "msgtype": "text",
        "text": {
            "content": mesg_str,
    		"mentioned_list":["@all"],
    #		"mentioned_mobile_list":["@all"],
        }
    }

    json_str = json.dumps(json_data)

    response = requests.post(url, data=json_str, headers={'Content-Type': 'application/json'})

    if response.status_code == 200:

        return { 'status' : 'ok', 'result' : '消息已推送' }

    else:

        return { 'status' : 'error' , 'error_info' : f'post zero_vision_steward_robot fail, response code {response.status_code}' }
