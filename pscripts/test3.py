
import json
from utils import vtt_to_json
# 读取配置文件
with open('config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)

batchCnt = config['tts_batch_cnt']
scene_split_chars = config['scene_split_chars']

file_path_sp = "build/2024_01_18_10_32_12_M1VjouHA/1.source001"
file_path_vtt = f"{file_path_sp}.vtt"

#1解析字幕
zimuArr = vtt_to_json(file_path_vtt)

print(f"{zimuArr[0]['text']}")

print(len(zimuArr[0]['text']))

sceneJsonObjs = {
    "objs":[]
}

scene_seqnum = 0
scene_text = ""
scene_start_index = 0

for i in range(0, len(zimuArr)):
    zimu = zimuArr[i]
    scene_text += f"{zimu['text']} "
    if len(scene_text) >= scene_split_chars or i == (len(zimuArr) - 1):
        scene_seqnum += 1
        sceneJsonObj = {}
        subZimus = zimuArr[scene_start_index: i+1]
        sceneJsonObj['seqnum'] = scene_seqnum
        sceneJsonObj['start'] = subZimus[0]['start']
        sceneJsonObj['end'] = subZimus[-1]['end']
        sceneJsonObj['text'] = scene_text
        sceneJsonObj['prompt'] = ''
        sceneJsonObj['tutu'] = ''
        sceneJsonObjs['objs'].append(sceneJsonObj)
        scene_start_index = i + 1
        scene_text = ""

