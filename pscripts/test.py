# -*- coding: utf-8 -*-
# author:laure
import sys
import os
import multiprocessing
from process_status import ProcessStatus
import json
from chat_gpt import askChatgpt
from chat_glm import askChatglm
import subprocess
import init_env
from utils import vtt_to_json
import time
from log import logger


from gen_video import create_video

def main(argv):
    create_video("cache/2024_03_06_17_04_34_q7aF0zyJ/test.source001.sce")

if __name__ == "__main__":
    main(sys.argv)
