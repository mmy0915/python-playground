import subprocess
from Multimedia import *

class Video(Multimedia):
    def __init__(self, filePath, language):
        super().__init__(filePath, language)
        self.targetPath = None
        
    """
    调用cmd指令将输入的视频文件通过ffmpeg提取信息

    targetType：目标音频类型
    sampleRate:采样率 8K/16K
    channel：声道数

    return: 0 成功 <0 失败
    """
    def video2audio(self, targetType = 'wav', sampleRate = 16000, channel = 1):
        self.sampleRate = sampleRate
        self.channel = channel
        
        #判断程序目录中是否有temp文件夹。若不存在，则创建
        target = os.getcwd() + "\\temp\\"
        if not os.path.exists(target):
            os.mkdir(target)

        target += os.path.splitext(os.path.basename(self.filePath))[0]
        self.targetPath = "{}.{}".format(target, targetType)

        #若temp文件夹中转换目标已存在，则删除该文件
        if os.path.exists(self.targetPath):
            os.remove(self.targetPath)

        #进行转换
        if targetType == 'wav':
            cmd = "ffmpeg -i \"{}\" -ar {} -ac {} \"{}\"".format(self.filePath, sampleRate, channel, self.targetPath)
        elif targetType == 'pcm':
            cmd = "ffmpeg -i \"{}\" -acodec pcm_s16le -f s16le -ar {} -ac {} \"{}\"".format(self.filePath, sampleRate, channel, \
                                                                             self.targetPath)

        try:                                                       
            flag = subprocess.call(cmd, shell = True)
        except Exception as e:
            raise e

        return flag

if __name__ == '__main__':
    filePath = 'C:\\Users\\Tim Zhou\\Desktop\\SmartSub后端 - 副本\\2.mp4'
    language = 'en'
    
    v = Video(filePath, language)
    v.video2audio()
        
