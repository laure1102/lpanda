# -*- coding: utf-8 -*-
# author:laure
import base64
import datetime
import json
import os
from log import logger

import requests

#sd api https://base_url/docs

# 读取配置文件
with open('conf/config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
work_dir = config['work_dir']


def submit_post(url: str, data: dict):
    return requests.post(url, data=json.dumps(data))

def submit_get(url: str):
    return requests.get(url)


def save_encoded_image(b64_image: str, output_path: str):
    # 判断当前目录下是否存在 output 文件夹，如果不存在则创建
    # 将文件放入当前目录下的 output 文件夹中
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(b64_image))
    return output_path



def doOnePrompt(dir,filename, prompt,moreParams={}):
    if not os.path.exists(dir):
        os.mkdir(dir)
    #检查文件是否存在，存在直接返回
    filepath = f"{filename}.png"
    if os.path.exists(filepath):
        return filepath

    base_url = config['sd_url']
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    txt2img_url = base_url + "/sdapi/v1/txt2img" # 服务器地址
    data = {
     'prompt': prompt,
     'negative_prompt': config["negative_prompt"],
     "height":config["height"],
     "width":config["width"],
     "override_settings": {
        "sd_model_checkpoint": config["sd_model_checkpoint"],
        "sd_vae": config["sd_vae"]
        },
     "sampler_index": config["sampler_index"]
   }
    data.update(moreParams)
    # 将 data.prompt 中的文本，删除文件名非法字符，已下划线分隔，作为文件名
    response = submit_post(txt2img_url, data)
    # logger.info(f"response:{response.json()}")
    imgpath  = save_encoded_image(response.json()['images'][0], filepath)
    logger.info(f"doOnePrompt saved image:{imgpath}")
    return imgpath


def doPromptBatch(dir,filename, prompt,batchSize=1,moreParams={}):
    if not os.path.exists(dir):
        os.mkdir(dir)

    base_url = config['sd_url']
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    txt2img_url = base_url + "/sdapi/v1/txt2img" # 服务器地址
    data = {'prompt': prompt,
     'negative_prompt': config["negative_prompt"],
     "height":config["height"],
     "width":config["width"],
     "override_settings": {
        "sd_model_checkpoint": config["sd_model_checkpoint"],
        "sd_vae": config["sd_vae"]
        },
     "sampler_index": config["sampler_index"],
     "batch_size":batchSize
    }
    data.update(moreParams)
    # 将 data.prompt 中的文本，删除文件名非法字符，已下划线分隔，作为文件名
    response = submit_post(txt2img_url, data)
    #logger.info(f"{response.json()['images']}")
    imgpaths = []
    for i, img in enumerate(response.json()['images'], 1):
        #检查文件是否存在，存在直接返回
        filepath = f"{filename}_{i}.png"
        if os.path.exists(filepath):
            imgpaths.append(filepath)
            continue
        ipt  = save_encoded_image(img, filepath)
        logger.info(f"doPromptBatch saved image:{ipt}")
        imgpaths.append(ipt)
    return imgpaths


def getModels():
    base_url = config['sd_url']
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    api = base_url + "/sdapi/v1/sd-models" # 服务器地址
    response = submit_get(api)
    return response.json()


def getVaes():
    base_url = config['sd_url']
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    api = base_url + "/sdapi/v1/sd-vae" # 服务器地址
    response = submit_get(api)
    return response.json()


def getSamplers():
    base_url = config['sd_url']
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    api = base_url + "/sdapi/v1/samplers" # 服务器地址
    response = submit_get(api)
    return response.json()
