import requests
import json

json_data = {
'text_info' : '现在时间是 2024-05-05 07:46',
#'text_info' : '这个人骑车有没有带安全帽',
}

json_str = json.dumps(json_data)

url = 'http://127.0.0.1:5004/ctrl'

response = requests.post(url, data=json_str, headers={'Content-Type': 'application/json'})

if response.status_code == 200:
    print('Success!')
    result = json.loads(response.text)
    print(result)
else:
    print('Failed!')
    print('Status Code:', response.status_code)





