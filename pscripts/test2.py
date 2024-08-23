# -*- coding: utf-8 -*-
# author:laure
import subprocess
import re
import os
import json
from utils import vtt_to_json

def get_json_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

# 将时间字符串转换为秒
def time_str_to_seconds(time_str):
    hms_str, milliseconds = time_str.split('.')
    hours, minutes, seconds = hms_str.split(':')
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000

# 主逻辑
def create_video(split_sfile_name):
    ssfn_arr = split_sfile_name.split("/")
    filename = ssfn_arr[2]
    temp_dir = ssfn_arr[1]
    jsonData = get_json_data(f"{split_sfile_name}.sce")
    objs = jsonData["objs"]
    objs[0]['start'] = "00:00:00.000"
    
    with open(f"{split_sfile_name}.timeline", "w") as f:
        for obj in objs:
            start_sec = time_str_to_seconds(obj['start'])
            end_sec = time_str_to_seconds(obj['end'])
            duration = end_sec - start_sec

            f.write(f"file '../../{obj['tutu']}'\n")
            f.write(f"duration {duration}\n")
        # 重复最后一张图片以确保最后一项的持续时间
        f.write(f"file '../../{objs[-1]['tutu']}'\n")
    # 构建 FFmpeg 命令
    ffmpeg_cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", f"{split_sfile_name}.timeline",
        "-vsync", "vfr",
        "-pix_fmt", "yuv420p",
        f"{split_sfile_name}.mp4"
    ]

    # 执行 FFmpeg 命令
    subprocess.run(ffmpeg_cmd)


if __name__ == '__main__':
    # 生成视频
    create_video('build/2024_01_18_10_32_12_M1VjouHA/1.source001')