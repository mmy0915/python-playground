import sys
from PyQt4 import QtGui, QtCore
import qtvlc
import share_memory
import os
import threading
import time
import SmartSub
import images_qr

class Example(QtGui.QDialog):
    myclicked = QtCore.pyqtSignal(list)
    
    def __init__(self):
        super(Example,self).__init__()

        self.initUI()
        #self.sourcemenu()
        #self.translatemenu()
        #self.check_trans()
        self.findonline = 1
        self.sf = {'中文': 'zh', 'English': 'en', '粤语': 'ct', 'Others': 4 }
        self.tf = {'中文': 'zh', 'English': 'en', '粤语': 'ct', '日本語': 'jp', 'Français': 'fr', 'Deutsch': 'de' }
        self.list = [0,0,0,0,0,0]
        self.t = None
    #初始化UI
    def initUI(self):
        #setting window
        self.setFixedSize(400,300)
        self.center()
        self.setWindowTitle('Choose mode')
        self.setWindowIcon(QtGui.QIcon(':/pictures/logo.png'))
        self.widget = QtGui.QWidget(self)
        #设置样式表
        self.setStyleSheet("QDialog{background-image:url(:/pictures/6.png);background-repeat:no-repeat}"
                           'QPushButton{background-image:url(:/pictures/btnn.png) center;height:30px;width:100px;border:1px solid #9C9C9C;border-radius:8px;background-repeat:repeat;}'
                           'QPushButton{font-size:15px;font-weight:bold;font-family:"Roman Times";color:black;}'
                           'QPushButton:hover{background-image:url(:/pictures/btnn_change.jpg);}'
                           'QLabel{background:rgb(255,255,255);font-size:15px;font-weight:bold;font-family:"Helvetica";color:black;}'
                           'QCheckBox{background:rgb(255,255,255);font-size:15px;font-weight:bold;font-family:"Helvetica";color:black;}'
                           "QComboBox{height:30px;width:90px;border:1px solid #000;border-radius:5px;padding-right:0px;padding-left:5px;background-color:rgb(156,156,156)}"
                           "QComboBox::drop-down{width:32px;subcontrol-origin:padding; subcontrol-position:top right; border-left-width:1px;border-left-color:darkgray; border-left-style:solid; border-top-right-radius:3px; border-bottom-right-radius:3px;}"
                           "QComboBox::down-arrow{image:url(:/pictures/Sort.png);}"
                           )
        #set font
        font = QtGui.QFont()
        font.setFamily('SansSerif')
        font.setFixedPitch(True)
        font.setPointSize(10)

        


        #set button
        self.okbtn = QtGui.QPushButton('Start',self)
        self.cancelbtn = QtGui.QPushButton('Cancel',self)
        self.okbtn.setToolTip('Start Play Video')
        self.okbtn.resize(self.okbtn.sizeHint())
        self.cancelbtn.setToolTip('Quit')
        self.cancelbtn.resize(self.cancelbtn.sizeHint())
        self.okbtn.setFont(font)
        self.cancelbtn.setFont(font)
        self.okbtn.move(60,250)
        self.cancelbtn.move(250,250)
        self.player = qtvlc.Player()
        #self.player.resize(640, 480)
        #self.okbtn.clicked().connect(self.send)
        self.connect(self.okbtn, QtCore.SIGNAL('clicked()'), self.send)
        #self.connect(self.okbtn, QtCore.SIGNAL('clicked()'), self.player.OpenFile)
        #print(type(self.okbtn))
        #self.connect(self.okbtn, QtCore.SIGNAL('clicked()'), self.player.show)
        #self.cancelbtn.clicked().connect(self.close)
        self.connect(self.cancelbtn,QtCore.SIGNAL('clicked()'),self.close)
        # set source file language
        # def sourcemenu(self):
        self.combo1 = QtGui.QComboBox(self)
        self.combo1.addItem('')
        self.combo1.addItem("中文")
        self.combo1.addItem("English")
        self.combo1.addItem("粤语")
        self.combo1.addItem("Others")
        self.combo1.move(35, 150)
        # 当一个选项被选择，我们调用 onActivated() 方法。
        self.connect(self.combo1, QtCore.SIGNAL('activated(QString)'), self.sourcefile)

        # set srt language
        # def translatemenu(self):
        self.combo2 = QtGui.QComboBox(self)
        self.combo2.addItem('')
        self.combo2.addItem("中文")
        self.combo2.addItem("English")
        self.combo2.addItem("粤语")
        self.combo2.addItem("日本語")
        self.combo2.addItem("Français")
        self.combo2.addItem("Deutsch")

        self.combo2.move(230, 150)
        # 当一个选项被选择，我们调用 onActivated() 方法。
        self.connect(self.combo2, QtCore.SIGNAL('activated(QString)'), self.translatefile)
        # def check_trans(self):
        # 插入单选框
        self.checkbox = QtGui.QCheckBox(self)
        self.checkbox.setFocusPolicy(QtCore.Qt.NoFocus)  # 默认情况下单选框接受聚焦，被聚焦的表现形式为单选框的标签被一个薄薄的矩形所覆盖
        self.checkbox.move(230, 105)
        self.checkbox.toggle()  # 默认选中


        # 将用户定义的changeTitle()函数与单选框的stateChanged()信号连接起来。
        self.connect(self.checkbox, QtCore.SIGNAL('stateChanged(int)'), self.isTrans)

        self.checkbox2 = QtGui.QCheckBox(self)
        self.checkbox2.setFocusPolicy(QtCore.Qt.NoFocus)
        self.checkbox2.setToolTip('<b>翻译</b>功能仅支持<b>srt</b>格式字幕')
        self.checkbox2.move(15,195)
        self.checkbox2.toggle()


    

    #set window in the center
    def center(self):

        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())



    #get users' choice for translation
    def isTrans(self, value):
        if self.checkbox.isChecked():
            self.checkbox.setChecked(1)
        else:
            self.checkbox.setChecked(0)
    #get checkbox state
    def getCheckState(self):
        self.list[1] = self.checkbox.checkState()
        self.list[3] = self.checkbox2.checkState()
    #get users' choice for find subtitle online
    def isFindOnline(self):
        if self.checkbox2.isChecked():
            self.findonline = 1
        else:
            self.findonline = 0
        self.list[3] = self.findonline


    # 获取视频语言和翻译语言并传给参数列表
    def sourcefile(self, text1):
        #print(type(self.sf[text1]))
        self.list[0] = self.sf[text1]

    def translatefile(self, text2):
        #print(text2,self.tf[text2])
        self.list[2] = self.tf[text2]

    # 生成字幕
    def generateSub(self,list):
        ss = SmartSub.SmartSub(list[4], list[5], list[0], 16000, list[1], list[2], list[3])
        ss.run()
        
    # 获取参数列表
    def getlist(self):
        return self.list
    
    # 将参数列表传给播放器
    def send(self):
        file = share_memory.read_mmap_info()
        pwd = os.path.dirname(file)
        self.list[4] = file
        self.list[5] = pwd
        self.getCheckState()
        self.close()
        self.t = threading.Thread(target = self.generateSub,args = (self.list,))
        self.t.setDaemon(True)
        self.t.start()
        print(self.t)


'''def main():
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()'''
