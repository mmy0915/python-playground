#coding=utf-8
"""
在互联网上查找视频字幕
"""
import hashlib
import os
import sys
import os.path

import requests
from requests.packages.urllib3 import disable_warnings


def calculateChecksum(filename):
    """
    按照shooter.cn使用的文件计算校验和
    整个想法是从视频文件抽样四个部分（开始，三分之一，三分之二，结束，
    并分别计算它们的校验和.
    """
    offset = 4096
    fobj = open(filename, 'rb')

    seek_positions = []
    hash_result = []
    fobj.seek(0, 2)
    total_size = fobj.tell()
    seek_positions.append(4096)
    seek_positions.append(total_size // 3 * 2)
    seek_positions.append(total_size // 3)
    seek_positions.append(total_size - 8192)
    for pos in seek_positions:
        fobj.seek(pos, 0)
        data = fobj.read(4096)
        m = hashlib.md5(data)
        hash_result.append(m.hexdigest())

    fobj.close()
    return ';'.join(hash_result)

def getSubtitleinfo(filename):
    """Splayer API请求
       return： 找到字幕return response 否则-1
    """
    response = requests.post(
        "https://www.shooter.cn/api/subapi.php",
        verify=False,
        params= {
            'filehash': calculateChecksum(filename),
            'pathinfo': os.path.realpath(filename),
            'format': 'json',
            'lang': "Chn",
        },
    )
    if response.text == u'\xff':
        return -1
    
    return response

"""
查找并写入字幕
return: -1:失败 字母地址：成功
"""
def shooterClient(filePath, subPath):
    disable_warnings()
    basename = os.path.splitext(os.path.basename(filePath))[0]

    response = getSubtitleinfo(filePath)
    #若找不到字幕文件则返回-1
    if response == -1:
        return -1
        
    subtitles = set([])
    for count in range(len(response.json())):
        if count != 0:
            _basename = "{}-alt.{}".format(basename, count)
        else:
            _basename = "{}".format(basename)
        
        for fileinfo in response.json()[count]['Files']:
            url = fileinfo['Link']
            ext = fileinfo['Ext']
            _response = requests.get(url, verify=False)
            subName = "{}\\{}.{}".format(subPath,_basename , ext)
            if count == 0:
                target_subName = subName

            if _response.ok and _response.text not in subtitles:
                #subtitles.add(_response.text)
                fobj = open(subName, 'wb+')
                fobj.write(_response.text.encode("utf-8"))
                fobj.close()
    return target_subName

if __name__ == '__main__':
    filename = "D:\\影视\\[电影天堂www.dy2018.com]狙击手幽灵射手BD中英双字.rmvb"
    subPath = "C:\\Users\\Tim Zhou\\Desktop"
    print(shooterClient(filename, subPath))
