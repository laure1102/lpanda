# -*- coding: utf-8 -*-
# author:laure
import os

# 获取脚本所在的目录
script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
ffmpeg_path = script_dir +"/libs/ffmpeg/bin"
os.environ["PATH"] += os.pathsep + ffmpeg_path
