# -*- coding: utf-8 -*-
# author:laure
import sys
import os
import edge_tts
import asyncio
from concurrent.futures import TimeoutError
from process_status import ProcessStatus
from utils import vtt_to_json
import json
from log import logger
import re 

# 读取配置文件
with open('conf/config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
work_dir = config['work_dir']

batchCnt = config['tts_batch_cnt']
scene_split_chars = config['scene_split_chars']

pStatus = ProcessStatus()


async def runTts(file_lock, sceneJsonObjs,sce,temp_dir,source_file_name, voice, rate, volume):
    # logger.info(f'{sce}')
    mp3_dir_path = f"{work_dir}/cache/{temp_dir}/mp3/{sce['seqnum']}"
    file_path_vtt = f"{mp3_dir_path}.vtt"
    file_path_mp3 = f"{mp3_dir_path}.mp3"
    TEXT = sce['text']
    
    communicate = edge_tts.Communicate(text=TEXT, voice=voice, rate=rate, volume=volume)
    #字幕
    submaker = edge_tts.SubMaker()
    
    with open(file_path_mp3, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])
    zimuText = submaker.generate_subs();
    with open(file_path_vtt, "w", encoding="utf-8") as file:
        file.write(zimuText)
    
    #1解析字幕
    zimuArr = vtt_to_json(file_path_vtt)
    # 检查字幕最后一句话是否是小说的最后一句话，不是就是中间断了，重写跑一次
    #logger.info(f"TEXT:\n{TEXT}")
    #logger.info(f"vtt最后一句话:{zimuArr[-1]['text']}")
    lastZimuWord = zimuArr[-1]['text']
    lastZimuWord = lastZimuWord.replace(" ","")
    # 定义一个包含全角和半角标点符号以及空格的正则表达式  
    punctuation_pattern = r'[^\u4e00-\u9fa5a-zA-Z0-9]'
    org_text = re.sub(punctuation_pattern, '', TEXT)  
    last_index = org_text.rfind(lastZimuWord)
    logger.info(f"last_index:{last_index},lastZimuWord's Len:{len(lastZimuWord)},TEXT's Len:{len(org_text)}")
    text_len = len(org_text)
    lastZimuWord_len  = len(lastZimuWord)
    dif = (text_len - (last_index + lastZimuWord_len)) / text_len
    logger.info(f"dif:{dif}\n")
    if dif > 0.015 and last_index > 0:
        await runTts(file_lock, sceneJsonObjs,sce,temp_dir,source_file_name,  voice, rate, volume)
        return
    
    #vtt -> srt
    srtfile = f"{mp3_dir_path}.srt"
    with open(srtfile, 'w', encoding='utf-8') as f:
        for zimu in zimuArr:
            f.write(f"{zimu['seqnum']}\n")
            f.write(f"{zimu['start']} --> {zimu['end']}\n")
            text = zimu['text']
            text = text.replace(" ", "")
            f.write(f"{text}\n")
            f.write("\n")

    sce['start'] = zimuArr[0]['start']
    sce['end'] = zimuArr[-1]['end']
    sce['vttfile'] = file_path_vtt
    sce['srtfile'] = srtfile
    sce['mp3file'] = file_path_mp3

    async with file_lock:
        with open(f"{work_dir}/cache/{temp_dir}/{source_file_name}.sce", 'w', encoding='utf-8') as file:
                    json.dump(sceneJsonObjs, file, ensure_ascii=False, indent=4)

    objs = sceneJsonObjs['objs']
    mp3_done_count = 0
    for i in range(0, len(objs)):
        s = objs[i]
        if s['mp3file']:
            mp3_done_count = mp3_done_count + 1

    jsonData = pStatus.get_json_data()
    jsonData['mp3_done_count'] = mp3_done_count
    pStatus.update(jsonData)
    

async def main(argv):
    if len(argv) > 1:
        temp_dir = argv[1]
        pStatus.set_temp_dir(temp_dir)
        jsonData = pStatus.get_json_data()
        
        os.makedirs(f'{work_dir}/cache/{temp_dir}/mp3', exist_ok=True)

        # 读取场景文件
        with open(f"{jsonData['sce_file_path']}", 'r', encoding='utf-8') as file:
            sceneJsonObjs = json.load(file)
        toTtsSces = []
        for sce in sceneJsonObjs['objs']:
            #去除掉已经完成的
            if(not sce['mp3file']):
                toTtsSces.append(sce)
        
        # 将任务分批执行
        # logger.info(f"总共{len(toTtsFiles)}个分割文件，将分批进行处理...")
        
        voice = jsonData['role_name']
        rate = jsonData['rate']
        volume = jsonData['volume']
        pStatus.write_stage("tts_start",f"将分批处理语音,参数: 同时处理个数:{batchCnt},角色:{voice},音量:{volume},语速:{rate}")

        timeout_seconds = 30
        has_time_error = False
        file_lock = asyncio.Lock()

        for i in range(0, len(toTtsSces), batchCnt):
            # 获取当前批次的文件列表
            current_batch = toTtsSces[i:i + batchCnt]
            # 创建并发执行的任务
            #tasks = [runTts(file_lock, sceneJsonObjs,sce,temp_dir,jsonData["source_file_name"],  voice, rate, volume) for sce in current_batch]
            # 并发执行当前批次的任务
            #await asyncio.gather(*tasks)
            tasks = []  
            for sce in current_batch:  
                # 使用 asyncio.wait_for 调用 runTts 并设置超时时间  
                task = asyncio.wait_for(runTts(file_lock, sceneJsonObjs, sce, temp_dir, jsonData["source_file_name"], voice, rate, volume), timeout=timeout_seconds)  
                tasks.append(task)  
            
            # 并发执行当前批次的任务  
            try:  
                await asyncio.gather(*tasks)  
            
                for sce in current_batch:
                    logger.info(f"finished {sce['seqnum']}")
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

        pStatus.write_stage("tts_done",f"处理语音完成")
        
    else:
        logger.info("请提供一个文件路径作为参数。")


if __name__ == "__main__":
    asyncio.run(main(sys.argv))
