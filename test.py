import subprocess, os

images = os.listdir('./pictures')
f = open('images.qrc', 'w+')
f.write(u'<!DOCTYPE RCC>\n<RCC version="1.0">\n<qresource>\n')

for item in images:
    f.write(u'<file alias="icons/'+ item +'">icons/'+ item +'</file>\n')


f.write(u'</qresource>\n</RCC>')
f.close()

pipe = subprocess.Popen(r'pyrcc4 -o images.py images.qrc', stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr = subprocess.PIPE, creationflags=0x08)
