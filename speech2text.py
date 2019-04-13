from aip import AipSpeech
import time

"""
基于百度REST API的语音识别模块

fileContent: 音频二进制文件
fileType: 音频类型
sampleRate: 采样率
lan: 音频语言(中文 = "zh", 英语 = "en", 粤语 = "ct" 不区分大小写)
APP_ID, API_KEY, SECRET_KEY:百度API申请信息
"""

def speech2text(fileContent, fileType = "pcm", sampleRate = 8000, lan = "en",\
                APP_ID = "10419140",\
                API_KEY = "RbSfUfFghiaqMzmfTGYF1s78",\
                SECRET_KEY = "b9cQZ8aek4mqo7BLRmz60nUcvRXSLQgl"):    

    aipSpeech = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
    d0 = aipSpeech.asr(fileContent, fileType, sampleRate, {'lan': lan})

    if not d0["err_no"]:
        return d0["result"][0]
    else:
        return " "

if __name__ == "__main__":
    with open("example.pcm", "rb") as fp:
        start = time.clock()
        print(speech2text(fp.read(), sampleRate = 16000))
        end = time.clock()
        print(end - start)

