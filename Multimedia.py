#coding=utf-8

import os

"""
Multimedia类：多媒体类，保存文件信息
属性：
filePath:文件路径
language:多媒体文件的语言
"""

class Multimedia():
    def __init__(self, filePath, language):
        print(filePath)
        print(os.path.exists(filePath))
        if not os.path.exists(filePath):
            print(not os.path.exists(filePath))
            raise "File not exist!"

        self.filePath = filePath
        self.language = language

    """
    获取路径文件的二进制信息
    return:文件二进制内容
    """
    def getContent(self):
        with open(filePath, 'rb') as fp:
            return fp.read()
    
