#coding=utf-8

from Multimedia import *
from vadCollector import *
import contextlib
import wave
import webrtcvad
import os
        
class Audio(Multimedia):
    def __init__(self, filePath, language = 'en', sampleRate = 16000, channel = 1):
        super().__init__(filePath, language)

        self.sampleRate = sampleRate
        self.channel = channel

    """
    获取音频采样率和帧数据
    return:
    """
    def readWave(self):
        with contextlib.closing(wave.open(self.filePath, 'rb')) as wf:
            #判断音频声道数是否为1
            numChannels = wf.getnchannels()
            assert numChannels == 1

            #判断采样精度是否为2
            sampleWidth = wf.getsampwidth()
            assert sampleWidth == 2

            #判断残阳率是是否是8000，16000或32000
            sampleRate = wf.getframerate()
            assert sampleRate in (8000, 16000, 32000)
            
            self.pcmData = wf.readframes(wf.getnframes())
            self.sampleRate = sampleRate

    """
    端点识别
    frameDuration_ms：帧长
    """
    def VAD(self, frameDuration_ms=30):
        self.startSpeech = []
        self.endSpeech = []
        
        #获取音频采样率和帧数据
        self.readWave()
        
        vad = webrtcvad.Vad(1)
        frames = frameGenerator(frameDuration_ms, self.pcmData, self.sampleRate)
        frames = list(frames)
        self.segments = vadCollector(self.sampleRate, 30, 300, vad, frames, self.startSpeech, self.endSpeech)
        
    """
    def generateSubtitles(self, subPath, isTrans = 0, toLang = 'zh',\
                          APP_ID = '10419140', \
                          API_KEY = 'RbSfUfFghiaqMzmfTGYF1s78',\
                          SECRET_KEY = 'b9cQZ8aek4mqo7BLRmz60nUcvRXSLQgl'):

        def trans_time(time):
            second = int(time)
            ms = int((time - second) * 1000)
            hour = second//3600
            second -= hour * 3600
            minute = second // 60
            second -= minute * 60

            return "{:002d}:{:002d}:{:002d},{:003d}".format(hour, minute, second, ms)

        aipSpeech = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
        t = Text()
        flag = -1

        #需要翻译时
        if isTrans:
            #输出翻译字幕文件地址
            self.subPath_trans = subPath + "\\" + os.path.splitext(os.path.basename(self.filePath))[0] + "_{}.srt".format(toLang)
            #若存在翻译字幕文件则删除
            if os.path.exists(self.subPath_trans):
                os.remove(self.subPath_trans)
            
            #输出源语字幕文件地址
            self.subPath = subPath + "\\" + os.path.splitext(os.path.basename(self.filePath))[0] + ".srt"

            #若路径中有原语字幕文件则直接翻译
            if os.path.exists(self.subPath):
                with open(self.subPath, 'r', encoding='utf-8') as fp:
                    for each in fp:
                        with open(self.subPath_trans, 'ab') as fp_trans:
                            if each[0].isdigit() or each == '\n':
                                fp_trans.write(each.encode("utf-8"))
                            else:
                                t.setText(each, fromLang = self.language, toLang = toLang, isTrans = 1)
                                fp_trans.write((t.getToText() + '\n').encode("utf-8"))

                flag = 0
                
            else:
                #端点识别
                self.VAD()

                for i, (segment, start_time, end_time) in enumerate(self.segments):
                    #语音识别
                    d0 = aipSpeech.asr(segment, 'pcm', self.sampleRate, {'lan': self.language})

                    try:
                        t.setText(d0["result"][0], fromLang = self.language, toLang = toLang, isTrans = isTrans)
                        #print('\n', i, ':', t.getText())
                        #print('\n', i, ':', t.getToText())
                    except KeyError:
                        t.setText(" ", fromLang = self.language, toLang = toLang, isTrans = isTrans)
                    finally:
                        with open(self.subPath, 'ab') as fp:
                            fp.write("{} --> {}\n".format(trans_time(start_time), trans_time(end_time)).encode("utf-8"))
                            fp.write("{}\n\n".format(t.getText()).encode("utf-8"))
                        with open(self.subPath_trans, 'ab') as fp_trans:
                            fp_trans.write("{} --> {}\n".format(trans_time(start_time), trans_time(end_time)).encode("utf-8"))
                            fp_trans.write("{}\n\n".format(t.getToText()).encode("utf-8"))

                flag = 1
        else:
           #输出并打开源语字幕文件地址
            self.subPath = subPath + "\\" + os.path.splitext(os.path.basename(self.filePath))[0] + ".srt"
            if os.path.exists(self.subPath):
                raise "Subtitle file exists in video path, please delete it"
            
            #端点识别
            self.VAD()

            for i, (segment, start_time, end_time) in enumerate(self.segments):
                #语音识别
                d0 = aipSpeech.asr(segment, 'pcm', self.sampleRate, {'lan': self.language})

                try:
                    t.setText(d0["result"][0], fromLang = self.language, toLang = toLang, isTrans = isTrans)
                    #print('\n', i, ':', t.getText())

                    fp.write("{} --> {}\n".format(trans_time(start_time), trans_time(end_time)).encode("utf-8"))
                    fp.write("{}\n\n".format(t.getText()).encode("utf-8"))
                except Exception as e:
                    #print("\nerror")
                    print(e)
                    continue

            #关闭文件
            fp.close()
            flag = 2

        return flag
    """
        
                    

'''if __name__ == "__main__":
    filePath = "C:\\Users\\lmq47\\Desktop\\新建文件夹\\temp\\example.wav"
    subPath = "C:\\Users\\lmq47\\Desktop"

    a = Audio(filePath, sampleRate = 16000)
    a.generateSubtitles(subPath, 1)'''
    
        
        
