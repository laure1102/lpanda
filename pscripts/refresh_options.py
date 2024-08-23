# -*- coding: utf-8 -*-
# author:laure
import sys
import os
import edge_tts
import asyncio
from process_status import ProcessStatus
from utils import vtt_to_json
import json
from sd_api import getModels,getSamplers,getVaes

from log import logger

async def main(argv):
    config = {}
    try:
        all_voices = await edge_tts.list_voices()
        rolenames = []
        for r in all_voices:
            locale = r['Locale']
            country = locale.split("-")[0]
            if country == "zh":
                rolenames.append(r['ShortName'])
        config['rolenames'] = rolenames
    except Exception as e:
         logger.info("get rolenames error:")
         logger.info(f"{e}")
         config['rolenames'] = []
    try:
        config['sd_models'] = getModels()
    except Exception as e:
         logger.info("get sd_models error:")
         logger.info(f"{e}")
         config['sd_models'] = []
    try:
        config['sd_vaes'] = getVaes()
    except Exception as e:
         logger.info("get sd_vaes error:")
         logger.info(f"{e}")
         config['sd_vaes'] = []
    try:
        config['sd_samplers'] = getSamplers()
    except Exception as e:
         logger.info("get sd_samplers error:")
         logger.info(f"{e}")
         config['sd_samplers'] = []
    with open('conf/options.json', 'w', encoding='utf-8') as file:
            json.dump(config, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    asyncio.run(main(sys.argv))