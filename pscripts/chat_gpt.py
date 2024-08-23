# -*- coding: utf-8 -*-
# author:laure
import requests
import json
from log import logger

# 读取配置文件
with open('conf/config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
work_dir = config['work_dir']


# ChatGPT API Endpoint
api_endpoint = f"{config['gpt_api_url']}/v1/chat/completions"
# API 密钥（替换为你自己的 API 密钥）
api_key = config['gpt_api_key']

# 请求头，包括 API 密钥和内容类型
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}


def askChatgpt(text):
    data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "system", "content": config['chat_magic_text']},
        {"role": "user", "content": text}
       ]
    }
    response = requests.post(api_endpoint, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        assistant_response = result["choices"][0]["message"]["content"]
        return assistant_response
    else:
        logger.info("API 请求失败，HTTP 状态码:", response.status_code)
        logger.info("错误信息:", response.text)
        return ""

if __name__ == "__main__":
    msg = askChatgpt("你非常聪明")
    logger.info(f"{msg}")