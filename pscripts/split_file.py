# -*- coding: utf-8 -*-
# author:laure
import sys
import os
import chardet
from process_status import ProcessStatus
import json
from log import logger
import re

# 读取配置文件
with open('conf/config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
work_dir = config['work_dir']

def read_file(file_path):
    try:
        logger.info(f"begin to read the file:{file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            content =  file.read()
            logger.info(f"read end")
            return content, None
    except UnicodeDecodeError:
        return None, f"Unicode 解码错误：{e}"
    except FileNotFoundError:
        return None, "文件未找到。"
    except IOError as e:
        return None, f"读取文件时发生错误：{e}"


def read_file2(file_path):
    try:
        with open(file_path, 'rb') as file:
            logger.info(f"begin to read the file:{file_path}")
            raw_data = file.read()
            logger.info(f"read end")
            
            logger.info(f"check the content code start")
            encoding = chardet.detect(raw_data)['encoding']
            content = raw_data.decode(encoding)
            logger.info(f"check the content code end")
            return content, None
    except FileNotFoundError:
        return None, "文件未找到。"
    except UnicodeDecodeError as e:
        return None, f"Unicode 解码错误：{e}"
    except IOError as e:
        return None, f"读取文件时发生错误：{e}"

def split_content(content, max_length=1000):
    paragraphs = content.split('\n')
    split_contents = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) < max_length:
            current_chunk += paragraph + "\n"
        else:
            split_contents.append(current_chunk)
            current_chunk = paragraph + "\n"
        #logger.info("拆分了一次")

    if current_chunk:
        split_contents.append(current_chunk)
    
    return split_contents

def write_chunks(chunks, base_file_name,temp_dir,role_name,rate,volume, scene_split_chars):
    base_name, _ = os.path.splitext(os.path.basename(base_file_name))
    
    os.makedirs(f'{work_dir}/cache', exist_ok=True)
    os.makedirs(f'{work_dir}/cache/{temp_dir}', exist_ok=True)
    pStatus = ProcessStatus(temp_dir)

    file_path_scene = f"{work_dir}/cache/{temp_dir}/{base_name}.sce"
    sceneJsonObjs = {
        "objs":[]
    }
    for i, chunk in enumerate(chunks, 1):
        sceneJsonObj = {}
        sceneJsonObj['seqnum'] = i
        sceneJsonObj['start'] = ''
        sceneJsonObj['end'] = ''
        sceneJsonObj['text'] = chunk
        sceneJsonObj['prompt'] = ''
        sceneJsonObj['tutu'] = []
        sceneJsonObj['vttfile'] = ''
        sceneJsonObj['srtfile'] = ''
        sceneJsonObj['mp3file'] = ''
        sceneJsonObj['mp4file'] = ''
        sceneJsonObj['mp4aufile'] = ''
        sceneJsonObjs['objs'].append(sceneJsonObj)
    try:
        with open(file_path_scene, 'w', encoding='utf-8') as file:
            json.dump(sceneJsonObjs, file, ensure_ascii=False, indent=4)
    except IOError as e:
        return False, f"写入文件时发生错误：{e}"
    
    try:
        pStatus.write_split_files(temp_dir,role_name,rate,volume,base_file_name,base_name,scene_split_chars,file_path_scene,len(sceneJsonObjs['objs']))
    except IOError as e:
        return False, f"写入status文件时发生错误：{e}"

    return True, None


if __name__ == "__main__":
    if len(sys.argv) > 5:
        source_path = sys.argv[1]
        temp_dir = sys.argv[2]
        role_name = sys.argv[3]
        rate = sys.argv[4]
        volume = sys.argv[5]
        logger.info(f"begin the main func:")
        content, read_error = read_file(source_path)
        # 使用正则表达式匹配只包含空白字符的行，并将其替换为空字符串  
        content = re.sub(r'^\s*$\n', '', content, flags=re.MULTILINE) 
        logger.info("完成了读取原文件")
        scene_split_chars = config['scene_split_chars']
        if content is not None:
            chunks = split_content(content,scene_split_chars)
            success, write_error = write_chunks(chunks, source_path, temp_dir,role_name,rate,volume, scene_split_chars)
            if success:
                logger.info("文件内容已成功拆分和写入")
            else:
                logger.info(write_error)
        else:
            logger.info(read_error)
    else:
        logger.info("请提供一个文件路径作为参数。")
