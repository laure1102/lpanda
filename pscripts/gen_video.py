# -*- coding: utf-8 -*-
# author:laure
import sys
import os
from process_status import ProcessStatus
import json
from chat_gpt import askChatgpt
from chat_glm import askChatglm
import subprocess
import init_env
from utils import vtt_to_json
import time
from log import logger
import random
from utils import get_json_data,time_str_to_seconds,duration


# 读取配置文件
with open('conf/config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
work_dir = config['work_dir']

pStatus = ProcessStatus()




def create_video(sceObject, mp4_dir, sceObj):
    tutus = sceObj["tutu"]
    height = config['height']
    width = config['width']
    fps = config['fps']

    mp4_filename = f"{mp4_dir}/{sceObj['seqnum']}.mp4"
    ffmpeg_command = ['ffmpeg', '-y', '-f', 'image2pipe', '-r', str(fps), '-s', f'{width}x{height}']
    # 生成filter_complex参数
    filter_complex = ""
    concat_cmds = ""
    idx = 0


    for tu in tutus:
        duration = tu['duration']
        xiaoguos = []
        xiaoguos.append(f"[{idx}:v]scale=1200:-2,setsar=1:1[v{idx}];[v{idx}]crop=1200:670[v{idx}];[v{idx}]scale=8000:-1,zoompan=z='zoom+0.001':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d={int(fps*duration)}:s={width}x{height}:fps={fps}[v{idx}];")
        xiaoguos.append(f"[{idx}:v]scale=1200:-2,setsar=1:1[v{idx}];[v{idx}]crop=1200:670[v{idx}];[v{idx}]scale=8000:-1,zoompan=z='1.1':x='if(lte(on,-1),(iw-iw/zoom)/2,x+2)':y='if(lte(on,1),(ih-ih/zoom)/2,y)':d={int(fps*duration)}:s={width}x{height}:fps={fps}[v{idx}];")
        xiaoguos.append(f"[{idx}:v]scale=1200:-2,setsar=1:1[v{idx}];[v{idx}]crop=1200:670[v{idx}];[v{idx}]scale=8000:-1,zoompan=z='1.1':x='if(lte(on,1),(iw-iw/zoom)/2,x-2)':y='if(lte(on,1),(ih-ih/zoom)/2,y)':d={int(fps*duration)}:s={width}x{height}:fps={fps}[v{idx}];")
        xiaoguos.append(f"[{idx}:v]scale=1200:-2,setsar=1:1[v{idx}];[v{idx}]crop=1200:670[v{idx}];[v{idx}]scale=8000:-1,zoompan=z='1.1':x='if(lte(on,1),(iw-iw/zoom)/2,x)':y='if(lte(on,1),(ih-ih/zoom)/2,y-2)':d={int(fps*duration)}:s={width}x{height}:fps={fps}[v{idx}];")
        xiaoguos.append(f"[{idx}:v]scale=1200:-2,setsar=1:1[v{idx}];[v{idx}]crop=1200:670[v{idx}];[v{idx}]scale=8000:-1,zoompan=z='1.1':x='if(lte(on,1),(iw-iw/zoom)/2,x)':y='if(lte(on,-1),(ih-ih/zoom)/2,y+2)':d={int(fps*duration)}:s={width}x{height}:fps={fps}[v{idx}];")

        rdIdx = random.randint(0, len(xiaoguos))

        filter_complex += xiaoguos[rdIdx - 1]
        concat_cmds += f"[v{idx}]"
        ffmpeg_command.extend(['-i', f"{tu['src']}"])
        idx +=1
    # 去掉最后一个分号
    concat_cmds +=f"concat=n={len(tutus)}:v=1[out]"
    filter_complex += concat_cmds
    ffmpeg_command.extend(['-loglevel', "quiet"]) #quiet
    # 添加filter_complex参数
    ffmpeg_command.extend(['-filter_complex', filter_complex])
    # 添加concat参数
    ffmpeg_command.extend(['-map', f'[out]'])
    ffmpeg_command.extend([ '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-shortest', mp4_filename])
    # 使用subprocess运行ffmpeg命令
    ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)
    ffmpeg_process.stdin.close()
    ffmpeg_process.wait()

    logger.info(f"{mp4_filename}:视频创建完成")
    logger.info(f"{ffmpeg_command}")

    #添加音频和字幕
    # 构建 FFmpeg 命令
    # 判断_with_au.mp4文件是否存在，存在就删除
    video_path = f"{mp4_dir}/{sceObj['seqnum']}_with_au.mp4"
    if os.path.exists(video_path):
        os.remove(video_path)

    watermark_image = config['watermark_image']  # 水印图片的路径
    watermark_position = config['watermark_position']  # 水印位置，可以是topleft, topright
    srtfilename = sceObj['srtfile']
    srtfilename = srtfilename.replace("\\","/")
    srtfilename = srtfilename.replace(":","\:")
    if watermark_image and  watermark_position:
        posX = 10
        posY = 10
        if watermark_position == "topright":
            posX = "main_w-200"
            posY = 10

        ffmpeg_cmd = [
            "ffmpeg",
            "-loglevel", "quiet",  # 隐藏进度信息 quiet
            "-i", mp4_filename,        # 输入视频
            "-i", f"{sceObj['mp3file']}",        # 输入音频
            "-i", watermark_image,  # 水印图片路径
            "-filter_complex", f"overlay=x={posX}:y={posY},subtitles='{srtfilename}'",  # 添加水印，并将字幕叠加在水印上
            "-c:a", "aac",           # 音频编码：转换为 AAC
            "-strict", "-2",         # 部分 FFmpeg 版本需要这个选项来启用某些编码器
            video_path              # 输出文件
        ]
    else:
        ffmpeg_cmd = [
            "ffmpeg",
            "-loglevel", "quiet",  # 隐藏进度信息 quiet
            "-i", mp4_filename,        # 输入视频
            "-i", f"{sceObj['mp3file']}",        # 输入音频
            "-filter_complex", f"subtitles='{srtfilename}'",  # 添加水印
            "-c:a", "aac",           # 音频编码：转换为 AAC
            "-strict", "-2",         # 部分 FFmpeg 版本需要这个选项来启用某些编码器
            video_path              # 输出文件
        ]
    # 执行 FFmpeg 命令
    logger.info(f"ffmpeg command:{ffmpeg_cmd}")
    logger.info(f"{sceObj['seqnum']}:FFmpeg开始:" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    subprocess.run(ffmpeg_cmd)
    logger.info(f"{sceObj['seqnum']}:FFmpeg结束:" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    sceObj['mp4file'] = mp4_filename
    sceObj['mp4aufile'] = video_path

    jsonData = pStatus.get_json_data()
    with open(jsonData['sce_file_path'], 'w', encoding='utf-8') as file:
        json.dump(sceObject, file, ensure_ascii=False, indent=4)

    objs = sceObject['objs']
    mp4_done_count = 0
    for i in range(0, len(objs)):
        s = objs[i]
        if s['mp4aufile']:
            mp4_done_count = mp4_done_count + 1

    jsonData['mp4_done_count'] = mp4_done_count
    pStatus.update(jsonData)


def main(argv):
    if len(argv) > 1:
        temp_dir = argv[1]
        pStatus.set_temp_dir(temp_dir)
        jsonData = pStatus.get_json_data()
        sce_file_path = jsonData["sce_file_path"]
        sceObject = get_json_data(sce_file_path)
        toVideoFiles = []
        for sf in sceObject['objs']:
            if(not sf['mp4aufile']):
                toVideoFiles.append(sf)
        pStatus.write_stage("video_start",f"将进行合成视频")

        mp4_dir = f'{work_dir}/cache/{temp_dir}/mp4'
        if not os.path.exists(mp4_dir):
            os.mkdir(mp4_dir)
        for sceObj in toVideoFiles:
            create_video(sceObject, mp4_dir, sceObj)

        pStatus.write_stage("video_done",f"合成视频完成")
    else:
        logger.info("请提供一个文件路径作为参数。")


if __name__ == "__main__":
    main(sys.argv)
