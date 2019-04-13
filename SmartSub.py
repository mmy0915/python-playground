#coding=utf-8

from Video import *
from Audio import *
from shooterClient import *
from Text import *
from aip import AipSpeech

"""
SmartSub功能类
videoPath：视频地址
subPath:字幕目标地址
videoLang:视频语言
sampleRate:音频采样率
isTrans:是否翻译
toLang:翻译目标语言
isFindOnline:是否在互联网直接查找字幕
"""
class SmartSub(object):
    def __init__(self, videoPath, subPath, videoLang, sampleRate=16000, isTrans = 0, toLang = None, isFindOnline = 0):
        self.videoPath = videoPath
        self.subPath = subPath
        self.videoLang = videoLang
        self.isTrans = isTrans
        self.toLang = toLang
        self.sampleRate = sampleRate
        self.isFindOnline = isFindOnline

        self.APP_ID = '10419140'
        self.API_KEY = 'RbSfUfFghiaqMzmfTGYF1s78'
        self.SECRET_KEY = 'b9cQZ8aek4mqo7BLRmz60nUcvRXSLQgl'

    def findOnline(self):
        return shooterClient(self.videoPath, self.subPath)

    """
    生成字幕
    思路：若字幕目录中存在原字幕且要翻译，则根据原字幕文件翻译；
        若字幕目录中不存在原字幕且要翻译，则生成并翻译；
        若字幕目录中存在原字幕且不要翻译，报错；
        若字幕目录中不存在原字幕且不要翻译，则生成字幕
        
    subPath:输出字幕路径
    isTrans:是否翻译
    APP_ID, API_KEY, SECRET_KEY:百度语音识别相关开发者参数
    return: 0 根据原字幕翻译成功
            1 生成、翻译成功
            2 生成成功
    """
    
    def generateSubtitles(self):
        """
        转换时间为字幕要求的格式
        """
        def trans_time(time):
            second = int(time)
            ms = int((time - second) * 1000)
            hour = second//3600
            second -= hour * 3600
            minute = second // 60
            second -= minute * 60

            return "{:002d}:{:002d}:{:002d},{:003d}".format(hour, minute, second, ms)

        aipSpeech = AipSpeech(self.APP_ID, self.API_KEY, self.SECRET_KEY)
        tmp = self.subPath
        t = Text()
        flag = -1

        #需要翻译时
        if self.isTrans:
            #输出翻译字幕文件地址
            self.subPath_trans = tmp + "\\" + os.path.splitext(os.path.basename(self.videoPath))[0] + "_{}.srt".format(self.toLang)
            #若存在翻译字幕文件则删除
            if os.path.exists(self.subPath_trans):
                os.remove(self.subPath_trans)
            
            #输出源语字幕文件地址
            self.subPath = tmp + "\\" + os.path.splitext(os.path.basename(self.videoPath))[0] + ".srt"

            #若路径中有原语字幕文件则直接翻译
            if os.path.exists(self.subPath):
                with open(self.subPath, 'r', encoding='utf-8') as fp:
                    for each in fp:
                        with open(self.subPath_trans, 'ab') as fp_trans:
                            if each[0].isdigit() or each == '\n':
                                fp_trans.write(each.encode("utf-8"))
                            else:
                                t.setText(each, fromLang = self.videoLang, toLang = self.toLang, isTrans = self.isTrans)
                                fp_trans.write((t.getToText() + '\n').encode("utf-8"))

                flag = 0
                
            else:
                #端点识别
                self.a.VAD()

                for i, (segment, start_time, end_time) in enumerate(self.a.segments):
                    #语音识别
                    d0 = aipSpeech.asr(segment, 'pcm', self.sampleRate, {'lan': self.videoLang})

                    try:
                        t.setText(d0["result"][0], fromLang = self.videoLang, toLang = self.toLang, isTrans = self.isTrans)
                        #print('\n', i, ':', t.getText())
                        #print('\n', i, ':', t.getToText())
                    except KeyError:
                        t.setText(" ", fromLang = self.videoLang, toLang = self.toLang, isTrans = self.isTrans)
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
            self.subPath = tmp + "\\" + os.path.splitext(os.path.basename(self.videoPath))[0] + ".srt"
            if os.path.exists(self.subPath):
                raise "Subtitle file exists in video path, please delete it"
            
            #端点识别
            self.a.VAD()

            for i, (segment, start_time, end_time) in enumerate(self.a.segments):
                #语音识别
                d0 = aipSpeech.asr(segment, 'pcm', self.sampleRate, {'lan': self.videoLang})

                try:
                    t.setText(d0["result"][0], fromLang = self.videoLang, toLang = self.toLang, isTrans = self.isTrans)
                    #print('\n', i, ':', t.getText())
                    with open(self.subPath, 'ab') as fp:
                        fp.write("{} --> {}\n".format(trans_time(start_time), trans_time(end_time)).encode("utf-8"))
                        fp.write("{}\n\n".format(t.getText()).encode("utf-8"))
                except Exception as e:
                    #print("\nerror")
                    print(e)
                    continue

            flag = 2

        return flag
    
    """
    生成字幕
    思路：现在互联网上查找，若不存在则生成

    sampleRate:采样率
    
    return: 0 根据原字幕翻译成功
            1 生成、翻译成功
            2 生成成功
    """
    def run(self):
        self.v = Video(self.videoPath, self.videoLang)

        if self.isFindOnline:
            #若找到字幕
            isFind = self.findOnline()
            print("isfind: ",isFind)
            if isFind == -1:
                pass
            elif self.isTrans:
                #仅支持翻译.srt格式字幕
                if os.path.splitext(os.path.basename(isFind))[1] == '.srt':
                    tmp = self.subPath
                    t = Text()
                    self.subPath = tmp + "\\" + os.path.splitext(os.path.basename(self.videoPath))[0] + ".srt"
                    self.subPath_trans = tmp + "\\" + os.path.splitext(os.path.basename(self.videoPath))[0] + "_{}.srt".format(self.toLang)
                    #若存在翻译字幕文件则删除
                    if os.path.exists(self.subPath_trans):
                        os.remove(self.subPath_trans)
                    
                    with open(self.subPath, 'r', encoding='utf-8') as fp:
                            for each in fp:
                                with open(self.subPath_trans, 'ab') as fp_trans:
                                    if each[0].isdigit() or each == '\n':
                                        fp_trans.write(each.encode("utf-8"))
                                    else:
                                        t.setText(each, fromLang = self.videoLang, toLang = self.toLang, isTrans = self.isTrans)
                                        fp_trans.write((t.getToText() + '\n').encode("utf-8"))
                    return 1
                else:
                    raise "This subtitle format is not supported, please convert it to .srt format"
            else:
                return 0
            
            
            
        #视频中提取音频
        assert self.v.video2audio('wav', self.sampleRate, 1) >= 0
        #从音频中得到字幕
        self.a = Audio(self.v.targetPath, self.videoLang, self.sampleRate, 1)
        #return a.generateSubtitles(self.subPath, self.isTrans, self.toLang)
        return self.generateSubtitles()

if __name__ == "__main__":
    videoPath = "D:\\影视\\[电影天堂www.dy2018.com]狙击手幽灵射手BD中英双字.rmvb"
    subPath = "C:\\Users\\Tim Zhou\\Desktop"

    SS = SmartSub(videoPath, subPath, 'en', 16000, 2, 'zh', 2)
    print(SS.run())
        
