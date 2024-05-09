
from flask import Flask, request
from openai import OpenAI
import config

app = Flask(__name__)

#g_model = "moonshot-v1-8k"
#g_model = "moonshot-v1-32k"
g_model = "moonshot-v1-128k"

g_temperature = 0.3

client = OpenAI(
    api_key = '',
    base_url = 'https://api.moonshot.cn/v1',
)

@app.route('/infer', methods=['POST'])
def logic_infer():

    data = request.get_json()
    query = data.get('query')
    system_prompt = data.get('system_prompt')

    print(f'query = {query}')
    print(f'system_prompt = {system_prompt}')

    completion = client.chat.completions.create(
        model = g_model,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": query,
            }
        ],
        temperature=g_temperature,
    )

    print(f'** infer result = {completion.choices[0].message.content}')

    return { 'status': 'ok', 'result' : completion.choices[0].message.content }
