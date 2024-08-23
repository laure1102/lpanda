# -*- coding: utf-8 -*-
# author:laure
import json
import os
from datetime import datetime
# 读取配置文件
with open('conf/config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
work_dir = config['work_dir']

defaultJson = {
    "temp_dir":"",
    "role_name":"zh-CN-YunxiNeural",
    "rate":"+10%",
    "volume":"+0%",
    "source_file_name":"",
    "source_file_path":"",
    "sce_file_path":"",
    "create_dttm":"",
    "end_dttm":"",
    "scene_split_chars":0,#单个场景的字符数
	"current_stage":"",#当前进程的状态
	"current_stage_descr":"",#当前进程的状态
    "sce_count":0,
    "mp3_done_count":0,
    "gpt_done_count":0,
    "tutu_done_count":0,
    "mp4_done_count":0,
    "seconds_per_tutu":0 #每张图持续的时间，0 为持续一段字幕结束,单位 秒
}



class ProcessStatus:
    def __init__(self, temp_dir=""):
        self.temp_dir = temp_dir
        self.statusFilename = f"{work_dir}/cache/{self.temp_dir}/status.json"

    def set_temp_dir(self, temp_dir):
        self.temp_dir = temp_dir
        self.statusFilename = f"{work_dir}/cache/{self.temp_dir}/status.json"

    def open_file2write(self):
        if os.path.exists(self.statusFilename):
            # 读取现有数据
            with open(self.statusFilename, 'r', encoding='utf-8') as file:
                return json.load(file)
        else:
            # 创建新文件并写入数据
            with open(self.statusFilename, 'w', encoding='utf-8') as file:
                json.dump(defaultJson, file, ensure_ascii=False, indent=4)
                return defaultJson

    def get_json_data(self):
        with open(self.statusFilename, 'r', encoding='utf-8') as file:
            return json.load(file)

    def write_split_files(self,temp_dir,role_name,rate,volume,source_file_path,source_file_name,scene_split_chars,sce_file_path,sce_count, stage="split_done",stage_descr="场景拆分完成"):
        jsonData = self.open_file2write()
        jsonData["temp_dir"] = temp_dir
        jsonData["role_name"] = role_name
        jsonData["rate"] = rate
        jsonData["volume"] = volume
        jsonData["source_file_path"] = source_file_path
        jsonData["source_file_name"] = source_file_name
        jsonData["scene_split_chars"] = scene_split_chars
        jsonData["sce_file_path"] = sce_file_path
        jsonData["sce_count"] = sce_count
        jsonData["current_stage"] = stage
        jsonData["current_stage_descr"] = stage_descr
        now = datetime.now()
        # 格式化时间
        formatted_time = now.strftime("%y-%m-%d %H:%M:%S")
        jsonData["create_dttm"] = formatted_time

        with open(self.statusFilename, 'w', encoding='utf-8') as file:
            json.dump(jsonData, file, ensure_ascii=False, indent=4)
        
    def write_stage(self, stage="",stage_descr=""):
        jsonData = self.open_file2write()
        jsonData["current_stage"] = stage
        jsonData["current_stage_descr"] = stage_descr
        with open(self.statusFilename, 'w', encoding='utf-8') as file:
            json.dump(jsonData, file, ensure_ascii=False, indent=4)

    def update(self,jsonData):
        with open(self.statusFilename, 'w', encoding='utf-8') as file:
            json.dump(jsonData, file, ensure_ascii=False, indent=4)
