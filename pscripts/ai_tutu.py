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
from sd_api import doOnePrompt,doPromptBatch
import time
import traceback
from utils import get_json_data,time_str_to_seconds,duration
from log import logger
# 读取配置文件
with open('conf/config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
work_dir = config['work_dir']
batchCnt = config['tutu_batch_cnt']

pStatus = ProcessStatus()


async def runAiTutu(sceneJsonObjs,sce,temp_dir,source_file_name):
    seconds_per_tutu = config['seconds_per_tutu']
    #总时长
    drt = duration("00:00:00.000",sce['end'])
    tutus = []
    if seconds_per_tutu == 0 or seconds_per_tutu >= drt:
        tutus.append({
            "id":0,
            "duration":drt,
            "src":""
        })
    else:
        #计算多少张图片和持续时间
        cnt = int(drt / seconds_per_tutu)
        mode = round(drt % seconds_per_tutu,3)
        if mode > 0:
            for i in range(0, cnt):
                tutus.append({
                    "id":i,
                    "duration":seconds_per_tutu,
                    "src":""
                })
            tutus.append({
                "id":cnt,
                "duration":mode,
                "src":""
            })
        else:
            for i in range(0, cnt):
                tutus.append({
                    "id":i,
                    "duration":seconds_per_tutu,
                    "src":""
                })

    prompt = sce['prompt']
    seqnum = sce['seqnum']
    if prompt:
        if config['add_prompt_bef']:
            prompt = f"{config['add_prompt_bef']},{prompt}"
        if config['add_prompt']:
            prompt = f"{prompt},{config['add_prompt']}"


        #开始生图
        img_dir = f"{work_dir}/cache/{temp_dir}/images"
        img_path = f"{img_dir}/{seqnum}_{int(time.time())}"
        imgpaths = doPromptBatch(img_dir,img_path, prompt, len(tutus))
        for i, tutuObj in enumerate(tutus, 1):
            tutuObj["src"] = imgpaths[i-1]

    if len(tutus) > 0:
        sce['tutu'].extend(tutus)
        #logger.info(f"{sce}")
        #logger.info(f"{tutus}")

        with open(f"{work_dir}/cache/{temp_dir}/{source_file_name}.sce", 'w', encoding='utf-8') as file:
            json.dump(sceneJsonObjs, file, ensure_ascii=False, indent=4)

        objs = sceneJsonObjs['objs']
        tutu_done_count = 0
        for i in range(0, len(objs)):
            s = objs[i]
            if len(s['tutu']) > 0:
                tutu_done_count = tutu_done_count + 1

        jsonData = pStatus.get_json_data()
        jsonData['tutu_done_count'] = tutu_done_count
        pStatus.update(jsonData)


async def regenTutu(temp_dir,seqnum,id):
    pStatus.set_temp_dir(temp_dir)
    statusData = pStatus.get_json_data()
    sceneJsonObjs = get_json_data(statusData['sce_file_path'])
    objs = sceneJsonObjs["objs"]
    sce = None
    for obj in objs:
        if obj["seqnum"] == seqnum:
            sce = obj

    if sce == None:
        return

    tutus = sce['tutu']
    if len(tutus) == 0:
        return

    toChangeTu = None
    for tu in tutus:
        if tu['id'] == id:
            toChangeTu = tu

    if toChangeTu == None:
        return

    #开始生图
    prompt = sce['prompt']
    if prompt:
        if config['add_prompt_bef']:
            prompt = f"{config['add_prompt_bef']},{prompt}"
        if config['add_prompt']:
            prompt = f"{prompt},{config['add_prompt']}"

    img_dir = f"{work_dir}/cache/{temp_dir}/images"
    img_path = f"{img_dir}/{seqnum}_{id}_{int(time.time())}"
    img_path = doOnePrompt(img_dir,img_path, prompt)
    toChangeTu["src"] = img_path

    with open(f"{work_dir}/cache/{temp_dir}/{statusData['source_file_name']}.sce", 'w', encoding='utf-8') as file:
            json.dump(sceneJsonObjs, file, ensure_ascii=False, indent=4)






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
            toTutuSces = []
            for sce in sceneJsonObjs['objs']:
                #去除掉已经完成的
                if(len(sce['tutu']) == 0):
                    toTutuSces.append(sce)

            pStatus.write_stage("aitutu_start",f"将分批进行生图,参数: 同时处理个数:{batchCnt}")
            timeout_seconds = 60
            has_time_error = False


            for i in range(0, len(toTutuSces), batchCnt):
                # 获取当前批次的文件列表
                current_batch = toTutuSces[i:i + batchCnt]
                # 创建并发执行的任务
                #tasks = [runAiTutu(sceneJsonObjs,sce,temp_dir,jsonData["source_file_name"]) for sce in current_batch]
                # 并发执行当前批次的任务
                #await asyncio.gather(*tasks)
                tasks = []
                for sce in current_batch:
                    # 使用 asyncio.wait_for 调用 runTts 并设置超时时间
                    task = asyncio.wait_for(runAiTutu(sceneJsonObjs,sce,temp_dir,jsonData["source_file_name"]), timeout=timeout_seconds)
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
                    logger.error(traceback.format_exc())
                    # 这里可以处理超时的情况，例如重新尝试或跳过超时的任务
                    has_time_error = True
                    continue

            if has_time_error:
                await main(argv)
            pStatus.write_stage("aitutu_done",f"生图完成")
        else:
            temp_dir = argv[2]
            argv3 = (argv[3])
            logger.info(f"regen tutu:{temp_dir},{argv3}")
            params = argv3.split(":")
            if len(params) == 2:
                seqnum = int(params[0])
                id = int(params[1])
                await regenTutu(temp_dir,seqnum,id)
    else:
        logger.info("请提供一个文件路径作为参数。")


if __name__ == "__main__":
    asyncio.run(main(sys.argv))
