# -*- coding: utf-8 -*-
# author:laure
import os
from process_status import ProcessStatus
import init_env
import sys
import time
import subprocess
import json
from utils import get_json_data

from log import logger
# 读取配置文件
with open('conf/config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
work_dir = config['work_dir']
 
pStatus = ProcessStatus()

def main(argv):
    if len(argv) > 1:
        temp_dir = argv[1]
        pStatus.set_temp_dir(temp_dir)
        jsonData = pStatus.get_json_data()
        filename = jsonData["source_file_name"]
        logger.info(f"begin the merge_mp4 func:")
        logger.info(f"temp_dir:{temp_dir},filename:{filename}")

        sceobj = get_json_data(jsonData["sce_file_path"])
        # 要合并的mp4文件列表
        mp4_files=[]
        for sceObj in sceobj['objs']:
            if sceObj['mp4aufile']:
                mp4_files.append(sceObj['mp4aufile'])
                
        pStatus.write_stage("merge_video_start",f"开始合并mp4中间文件,总共{len(mp4_files)}个")
        #要按照文件名序号排序
        concat_file = f"{work_dir}/cache/{temp_dir}/merge.txt"
        with open(concat_file, 'w', encoding='utf-8') as f:
            for mp4f in mp4_files:
                mp4f_filename = mp4f.replace("\\","/")
                # mp4f_filename = mp4f.replace(f"{work_dir}/cache/{temp_dir}/","")
                f.write("file '{}'\n".format(mp4f_filename))

        output = f"{work_dir}/cache/{temp_dir}/{filename}.mp4"
        # 使用 ffmpeg 合并视频
        command = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_file, '-c', 'copy', output]
        subprocess.run(command)
        pStatus.write_stage("merge_video_done",f"合并完成")

    else:
        logger.info("请提供一个文件路径作为参数。")

if __name__ == "__main__":
    main(sys.argv)
