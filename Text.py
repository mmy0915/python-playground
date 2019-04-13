#coding=utf-8

import http.client
import hashlib
from urllib import parse
import random

"""
Text类：储存文本
属性：
text:文本内容
fromLang:text原语言
toLan: 翻译目标语言
isTrans:判断是否自动翻译到目标语言
"""
class Text(object):
    def __init__(self, text = "", fromLang = 'en', toLang = 'zh', isTrans = 2):
        self.setText(text, fromLang, toLang, isTrans)

    """
    获得text内容
    return:Text文本
    """
    def getText(self):
        return self.text

    """
    获得toText内容
    return:toText文本
    """
    def getToText(self):
        return self.toText

    """
    设置text内容
    return:
    """
    def setText(self, text, fromLang = 'en', toLang = 'zh', isTrans = 2):
        self.text = text.strip().strip(",").strip("，")
        self.toText = ""
        
        self.fromLang = fromLang
        self.toLang = toLang

        if isTrans == 2:
            self.translate()
            
    """
    翻译text到目标语言
    appid, secretKey:百度翻译api
    myUrl:百度翻译地址
    return:
    """
    def translate(self, appid="20171123000099052", secretKey="lyrTGCIkOA0vm_6iJtF1", myUrl = '/api/trans/vip/translate'):
        httpClient = None

        salt = random.randint(32768, 65536)
        sign = appid + self.text + str(salt) + secretKey
        m1 = hashlib.md5()
        m1.update(sign.encode(encoding = 'utf-8'))
        sign = m1.hexdigest()
        myUrl = myUrl + '?appid=' + appid + '&q=' + parse.quote(self.text) + '&from=' \
                + self.fromLang + '&to=' + self.toLang + '&salt=' + str(salt) + '&sign=' + sign
    
        try:
            httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
            httpClient.request('GET', myUrl)
            response = httpClient.getresponse()
            outStr = response.read().decode('utf-8')
            outStr = eval(outStr)
        except Exception as e:
            raise e
        finally:
            if httpClient:
                httpClient.close()
        try:
            self.toText = outStr['trans_result'][0]['dst'].strip(",").strip("，")
        except:
            self.toText = " "

if __name__ == '__main__':
    '''
    words = "classified advertising is that advertising reaches schools in certain sections of the paper and thus distinguished from display advertising,\
                such groupings as help wanted well as seed lots and found a mate,"

    t = Text(words)
    '''
    filePath = "C:\\Users\\lmq47\\Desktop\\1.srt"
    t = Text()

    with open(filePath, 'r', encoding='utf-8') as f:
        with open("C:\\Users\\lmq47\\Desktop\\1_en.srt", 'w') as f2:
            for each in f:
                if each[0].isdigit() or each == '\n':
                    f2.write(each)
                else:
                    t.setText(each, fromLang = 'zh', toLang = 'en', isTrans = 1)
                    f2.write(t.getToText() + '\n')
                
        
        
