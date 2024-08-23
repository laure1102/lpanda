# -*- coding: utf-8 -*-
# author:laure
import requests
import json
import re
from log import logger

# 读取配置文件
with open('conf/config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
work_dir = config['work_dir']


def contains_chinese(s):
    if s == None:
        return False
    pattern = re.compile(r'[\u4e00-\u9fff]+')  
    return bool(pattern.search(s)) 
def create_chat_completion(model, messages, use_stream=False):
    base_url = config['glm_api_url']
    if base_url.endswith('/'): 
        base_url = base_url[:-1]  
    data = {
        "model": model, # 模型名称
        "messages": messages, # 会话历史
        "stream": use_stream, # 是否流式响应
        "max_tokens": 500, # 最多生成字数
        "temperature": 0.8, # 温度
        "top_p": 0.8, # 采样概率
    }

    response = requests.post(f"{base_url}/v1/chat/completions", json=data, stream=use_stream)
    if response.status_code == 200:
        if use_stream:
            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')[6:]
                    try:
                        response_json = json.loads(decoded_line)
                        content = response_json.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        logger.info(content)
                    except:
                        logger.info("Special Token:", decoded_line)
        else:
            # 处理非流式响应
            decoded_line = response.json()
            content = decoded_line.get("choices", [{}])[0].get("message", "").get("content", "")
            return content
    else:
        logger.info("Error:", response.status_code)
        return None

def askChatglm(text):
    chat_messages = [
        {
            "role": "system",
            "content": config['chat_magic_text'],
        }
    ]
    chat_messages.append({"role": "user", "content": text})
    response = create_chat_completion("chatglm3-6b", chat_messages, use_stream=False)
    response = response.strip(u"\u200b")
    max_retries = 3  # 设置最大重试次数  
    retries = 0  

    while (response== None or response == "" or "敏感" in response ) and retries < max_retries:
        retries += 1  
        logger.info(f"retry times:{retries},last time response:{response},request text:{text}")  
        try:  
            response = create_chat_completion("chatglm3-6b", chat_messages, use_stream=False)  
            response = response.strip(u"\u200b")
        except Exception as e:  
            print(f"An error occurred: {e}")  
            break  # 如果发生异常，退出循环  

    #判断如果有中文，再次请求  请翻译成英文。
    if response!="" and contains_chinese(response):
        translate_messages = [
            {
                "role": "system",
                "content": "假设你现在是一名优秀的翻译师，擅长将中文翻译成英文",
            }
        ]
        logger.info(f"this response contains chiense char, to translate, the response before translate:{response}")  
        translate_messages.append({"role": "user", "content": f"请将<<>>中的文字翻译成英文:<<{response}>>"});
        response = create_chat_completion("chatglm3-6b", translate_messages, use_stream=False)
        logger.info(f"the response after translate:{response}")  
    
    if response== None or response== "":
        translate_messages = [
            {
                "role": "system",
                "content": "假设你现在是一名优秀的翻译师，擅长将中文翻译成英文",
            }
        ]
        logger.info(f"this response is null, to translate text, the response before translate:{response}") 
        translate_messages.append({"role": "user", "content": f"请将<<>>中的文字翻译成英文:<<{text}>>"});
        response = create_chat_completion("chatglm3-6b", translate_messages, use_stream=False)
        logger.info(f"the response after translate:{response}")  

    return response

if __name__ == "__main__":
    while True:
        user_input = input("请输入您的问题: ")
        response = askChatglm(user_input)
        logger.info("回复:", response)
        # 可以选择是否在每次循环后清除聊天历史
        # chat_messages.pop()

