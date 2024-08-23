# -*- coding: utf-8 -*-
# author:laure
import sys
import os
import asyncio
from concurrent.futures import TimeoutError
from process_status import ProcessStatus
import json
from chat_gpt import askChatgpt
from chat_glm import askChatglm
from log import logger
import time
# 读取配置文件
with open('conf/config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
work_dir = config['work_dir']
batchCnt = config['prompt_batch_cnt']

pStatus = ProcessStatus()


def get_json_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

async def runAiPrompt(sceneJsonObjs,sce,temp_dir,source_file_name):
    if config['chat_type'] == "gpt":
        sce["prompt"] = askChatgpt(sce['text'])
    if config['chat_type'] == "glm":
        sce["prompt"] = askChatglm(sce['text'])
    #time.sleep(10)
    
    with open(f"{work_dir}/cache/{temp_dir}/{source_file_name}.sce", 'w', encoding='utf-8') as file:
        json.dump(sceneJsonObjs, file, ensure_ascii=False, indent=4)

    objs = sceneJsonObjs['objs']
    gpt_done_count = 0
    for i in range(0, len(objs)):
        s = objs[i]
        if s['prompt']:
            gpt_done_count = gpt_done_count + 1

    jsonData = pStatus.get_json_data()
    jsonData['gpt_done_count'] = gpt_done_count
    pStatus.update(jsonData)

async def regenPrompt(temp_dir,seqnum):
    pStatus.set_temp_dir(temp_dir)
    statusData = pStatus.get_json_data()
    sceneJsonObjs = get_json_data(statusData['sce_file_path'])
    objs = sceneJsonObjs["objs"]
    sce = None
    for obj in objs:
        if obj["seqnum"] == seqnum:
            sce = obj

    if sce != None:
        logger.info("do regenPrompt")
        logger.info(f"temp_dir:{temp_dir},seqnum:{seqnum},{sce}")
        await runAiPrompt(sceneJsonObjs,sce,temp_dir,statusData['source_file_name'])

async def main(argv):
    if len(argv) > 3:
        action = argv[1]
        if action == "all":
            temp_dir = argv[2]
            pStatus.set_temp_dir(temp_dir)
            jsonData = pStatus.get_json_data()
             # 读取场景文件
            with open(f"{jsonData['sce_file_path']}", 'r', encoding='utf-8') as file:
                sceneJsonObjs = json.load(file)
            toPromptSces = []
            for sce in sceneJsonObjs['objs']:
                #去除掉已经完成的
                if(not sce['prompt']):
                    toPromptSces.append(sce)
            
            pStatus.write_stage("aiprompt_start",f"将分批进行推理ai提示词,参数: 同时处理个数:{batchCnt}")
            timeout_seconds = 60
            has_time_error = False
            
            for i in range(0, len(toPromptSces), batchCnt):
                # 获取当前批次的文件列表
                current_batch = toPromptSces[i:i + batchCnt]
                # 创建并发执行的任务
                #tasks = [runAiPrompt(sceneJsonObjs,sce,temp_dir,jsonData["source_file_name"]) for sce in current_batch]
                # 并发执行当前批次的任务
                #await asyncio.gather(*tasks)
                tasks = []  
                for sce in current_batch:  
                    # 使用 asyncio.wait_for 调用 runTts 并设置超时时间  
                    task = asyncio.wait_for(runAiPrompt(sceneJsonObjs,sce,temp_dir,jsonData["source_file_name"]), timeout=timeout_seconds)  
                    tasks.append(task)  

                try:  
                    await asyncio.gather(*tasks)  
                    for sf in current_batch:
                        logger.info(f"finished {sf['seqnum']}")
                except TimeoutError as e:  
                    logger.error(f"Timeout occurred for one or more tasks: {e}")  
                    # 这里可以处理超时的情况，例如重新尝试或跳过超时的任务
                    has_time_error = True
                    continue  
                except Exception as e:  
                    logger.error(f"other error occured: {e}")  
                    # 这里可以处理超时的情况，例如重新尝试或跳过超时的任务
                    has_time_error = True
                    continue  
            
            if has_time_error:
                await main(argv)
            pStatus.write_stage("aiprompt_done",f"推理ai提示词完成")
        else:
            temp_dir = argv[2]
            seqnum = int(argv[3])
            #logger.info(f"regen prompt:{temp_dir},{seqnum}")
            await regenPrompt(temp_dir,seqnum)
    else:
        logger.info("请提供一个文件路径作为参数。")


if __name__ == "__main__":
    asyncio.run(main(sys.argv))
