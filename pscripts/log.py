import logging
import os
import json

# 读取配置文件
with open('conf/config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
work_dir = config['work_dir']

def setup_logger():
    # 创建一个日志记录器
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # 创建一个文件处理器
    os.makedirs(f'{work_dir}/logs', exist_ok=True)
    file_handler = logging.FileHandler(f'{work_dir}/logs/app.log')
    file_handler.setLevel(logging.DEBUG)
    # 设置日志的编码为UTF-8  
    logging.basicConfig(  
        encoding='utf-8'  
    )  
    # 创建一个格式化器并将其添加到处理器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # 将处理器添加到日志记录器
    logger.addHandler(file_handler)

    return logger

# 在模块加载时即配置日志
logger = setup_logger()
