
import json
from datetime import datetime,timedelta

def get_json_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)


# 将时间字符串转换为秒
def time_str_to_seconds(time_str):
    hms_str, milliseconds = time_str.split('.')
    hours, minutes, seconds = hms_str.split(':')
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000

def duration(start_str,end_str):
    start_sec = time_str_to_seconds(start_str)
    end_sec = time_str_to_seconds(end_str)
    duration = end_sec - start_sec
    # 对Decimal类型进行四舍五入，保留3位小数  
    rounded_num = round(duration, 3)  
    return rounded_num



def add_time_with_milliseconds(time1, time2):
    # Function to convert time string to timedelta
    def time_str_to_timedelta(time_str):
        hours, minutes, seconds = time_str.split(':')
        seconds, microseconds = seconds.split('.')
        return timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds), microseconds=int(microseconds) * 1000)

    # Convert time strings to timedelta objects
    timedelta1 = time_str_to_timedelta(time1)
    timedelta2 = time_str_to_timedelta(time2)

    # Add the time deltas
    total_timedelta = timedelta1 + timedelta2

    # Extract hours, minutes, seconds and microseconds
    total_seconds = int(total_timedelta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    microseconds = total_timedelta.microseconds // 1000  # Convert microseconds to milliseconds

    # Format the result as a string
    return f"{hours:02}:{minutes:02}:{seconds:02}.{microseconds:03}"


def vtt_to_json(vtt_path,start_seqnum = 0,start_dttm = "00:00:00.000"):
    try:
        subtitles = []
        i=0
        with open(vtt_path, 'r', encoding='utf-8') as srt_file:
            lines = srt_file.read().split('\n\n\n')
            for block in lines:
                if not block.strip():
                    continue
                block = block.strip().split('\n')
                if len(block) >= 2:
                    time_range = block[0].split(" --> ")
                    if len(time_range)>1:
                        start_time, end_time = time_range
                        # 提取字幕文本
                        subtitle_text = ''.join(block[1:])
                        # 创建字幕字典
                        i+=1
                        subtitle_dict = {
                            "seqnum":start_seqnum + i,
                            "start": add_time_with_milliseconds(start_dttm,start_time),
                            "end": add_time_with_milliseconds(start_dttm,end_time),
                            "text": subtitle_text
                        }
                        subtitles.append(subtitle_dict)
        return subtitles
    except Exception as e:
        return f"发生错误: {str(e)}"



if __name__ == "__main__":
    duration = duration('00:00:00.095','00:00:43.511')
    print(f"{duration}")
    seconds_per_tutu = 6
    print(f"{int(duration/seconds_per_tutu)},{duration%seconds_per_tutu}")
    aa = "爱的色放垃圾啊大家是否"
    print(f"{not aa}")

