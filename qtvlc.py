#! /usr/bin/python

#
# Qt example for VLC Python bindings
# Copyright (C) 2009-2010 the VideoLAN team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
#

import sys
import os.path
import vlc
import time
import threading
import choose_mode
import SmartSub
import share_memory
import mmap
from PyQt4 import QtGui, QtCore

#全局变量
mylist = []
t = None

class Player(QtGui.QMainWindow):
    """A simple Media Player using VLC and Qt
    """

    def __init__(self, master=None):
        QtGui.QMainWindow.__init__(self, master)
        self.setWindowTitle("Media Player")
        self.clicknum = 0
        # creating a basic vlc instance
        self.instance = vlc.Instance(("--freetype-font=Microsoft JhengHei", "--subsdec-encoding=GB18030"))
        self.player = vlc.MediaPlayer()
        # creating an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()
        self.path = [0,0]
        self.createUI()
        self.isPaused = False
#创建播放器UI，pyqt语句
    def createUI(self):
        """Set up the user interface, signals & slots
        """
        self.widget = QtGui.QWidget(self)
        self.setCentralWidget(self.widget)

        # In this widget, the video will be drawn
        if sys.platform == "darwin": # for MacOS
            self.videoframe = QtGui.QMacCocoaViewContainer(0)
        else:
            self.videoframe = QtGui.QFrame()
        self.palette = self.videoframe.palette()
        self.palette.setColor (QtGui.QPalette.Window,
                               QtGui.QColor(0,0,0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        self.positionslider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.connect(self.positionslider,
                     QtCore.SIGNAL("sliderMoved(int)"), self.setPosition)

        self.hbuttonbox = QtGui.QHBoxLayout()
        self.playbutton = QtGui.QPushButton("Play")
        self.hbuttonbox.addWidget(self.playbutton)
        self.connect(self.playbutton, QtCore.SIGNAL("clicked()"),
                     self.PlayPause)

        self.stopbutton = QtGui.QPushButton("Stop")
        self.hbuttonbox.addWidget(self.stopbutton)
        self.connect(self.stopbutton, QtCore.SIGNAL("clicked()"),
                     self.Stop)

        

        #self.subbutton = QtGui.QPushButton("FS")
        #self.hbuttonbox.addWidget(self.subbutton)
        #self.connect(self.subbutton, QtCore.SIGNAL("clicked()"),
                    # self.full_screen)

        self.hbuttonbox.addStretch(1)
        self.volumeslider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
        self.volumeslider.setToolTip("Volume")
        self.hbuttonbox.addWidget(self.volumeslider)
        self.connect(self.volumeslider,
                     QtCore.SIGNAL("valueChanged(int)"),
                     self.setVolume)

        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addWidget(self.positionslider)
        self.vboxlayout.addLayout(self.hbuttonbox)

        self.widget.setLayout(self.vboxlayout)
        #菜单栏
        open = QtGui.QAction("&Open", self)
        open_sub = QtGui.QAction("&Subtitle",self)
        close_sub = QtGui.QAction("&Closesub", self)
        self.connect(open, QtCore.SIGNAL("triggered()"), self.OpenFile)
        self.connect(open_sub, QtCore.SIGNAL("triggered()"), self.OpenSub)
        self.connect(close_sub, QtCore.SIGNAL("triggered()"), self.CloseSub)
        exit = QtGui.QAction("&Exit", self)
        self.connect(exit, QtCore.SIGNAL("triggered()"), sys.exit)
        menubar = self.menuBar()
        filemenu = menubar.addMenu("&File")
        filemenu.addAction(open)
        filemenu.addAction(open_sub)
        filemenu.addAction(close_sub)
        filemenu.addSeparator()
        filemenu.addAction(exit)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(200)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"),
                     self.updateUI)
    #播放暂停功能
    def PlayPause(self):
        """Toggle play/pause status
        """
        if not self.playbutton.isEnabled():
            self.playbutton.setDisabled(False)

        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.playbutton.setText("Play")
            self.isPaused = True
        else:
            if self.mediaplayer.play() == -1:
                self.OpenFile()
                return
            self.mediaplayer.play()
            self.playbutton.setText("Pause")
            self.timer.start()
            self.isPaused = False
    #停止播放功能
    def Stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        self.playbutton.setText("Play")
        self.tp.cancel()
    #全屏功能
    #def full_screen(self):
        """
        Full Screen
        :return:
        """
        #self.mediaplayer.set_fullscreen(1)


    #可增加的广告功能
    '''def adPlay(self):
        adname = 'C:\\Users\\Tim Zhou\\Desktop\\2.mp4'
        self.ad = self.instance.media_new(adname)
        # put the media in the media player
        self.mediaplayer.set_media(self.media)
        # parse the metadata of the file
        self.ad.parse()
        # set the title of the track as window title
        self.setWindowTitle(self.ad.get_meta(0))
        # the media player has to be 'connected' to the QFrame
        # (otherwise a video would be displayed in it's own window)
        # this is platform specific!
        # you have to give the id of the QFrame (or similar object) to
        # vlc, different platforms have different functions for this
        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32":  # for Windows
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin":  # for MacOS
            self.mediaplayer.set_nsobject(self.videoframe.winId())
        self.PlayPause()'''

    #打开视频文件
    def OpenFile(self, filename=None):
        """Open a media file in a MediaPlayer
        """
        self.clicknum += 1
        if filename is None:
            filename = QtGui.QFileDialog.getOpenFileName(self,"Open File", os.path.expanduser('~'))
        if not filename:
            return

        # create the media
        if sys.version < '3':
            filename = unicode(filename)

        self.path[0] = filename

        share_memory.get_mmap_info(self.path[0])

        global mylist
        global t
        self.ex = choose_mode.Example()
        if self.ex.exec_():
            self.ex.show()
        mylist = self.ex.list
        t = self.ex.t
        print('************',t,'*******')
        self.media = self.instance.media_new(filename)
        # put the media in the media player
        self.mediaplayer.set_media(self.media)
        #self.mediaplayer.video_set_subtitle_file('D:/2_en.srt')
        # parse the metadata of the file
        self.media.parse()
        # set the title of the track as window title
        self.setWindowTitle(self.media.get_meta(0))
        #self.mediaplayer.video_set_subtitle_file('D:/1_en.srt')
        # the media player has to be 'connected' to the QFrame
        # (otherwise a video would be displayed in it's own window)
        # this is platform specific!
        # you have to give the id of the QFrame (or similar object) to
        # vlc, different platforms have different functions for this
        if sys.platform.startswith('linux'): # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32": # for Windows
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin": # for MacOS
            self.mediaplayer.set_nsobject(self.videoframe.winId())
        self.playbutton.setDisabled(True)
        self.tp = threading.Timer(30,self.PlayPause)
        self.tp.start()
        
        self.Sub()
    #打开自己的字幕文件
    def OpenSub(self, subname=None):
        """Open a subtitle file in a MediaPlayer
        """
        #self.PlayPause()
        if subname is None:
            subname = QtGui.QFileDialog.getOpenFileName(self, "Open Sub", os.path.expanduser('~'))
        if not subname:
            return

        # add subtitle
        if sys.version < '3':
            subname = unicode(subname)
        self.sub = subname.replace('/','\\')
        self.path[1] = self.sub
        self.mediaplayer.video_set_subtitle_file(self.sub)





        # the media player has to be 'connected' to the QFrame
        # (otherwise a video would be displayed in it's own window)
        # this is platform specific!
        # you have to give the id of the QFrame (or similar object) to
        # vlc, different platforms have different functions for this
        '''if sys.platform.startswith('linux'): # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32": # for Windows
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin": # for MacOS
            self.mediaplayer.set_nsobject(self.videoframe.winId())'''
    #读取字幕函数
    def Sub(self):
        timer_start(self.mediaplayer)
    #关闭字幕
    def CloseSub(self):
        self.mediaplayer.video_set_spu(-1)
        print(self.mediaplayer.video_set_spu(-1))
    #调节音量
    def setVolume(self, Volume):
        """Set the volume
        """
        self.mediaplayer.audio_set_volume(Volume)
    #调节播放位置
    def setPosition(self, position):
        """Set the position
        """
        # setting the position to where the slider was dragged
        self.mediaplayer.set_position(position / 1000.0)
        # the vlc MediaPlayer needs a float value between 0 and 1, Qt
        # uses integer variables, so you need a factor; the higher the
        # factor, the more precise are the results
        # (1000 should be enough)
    #刷新UI
    def updateUI(self):
        """updates the user interface"""
        # setting the slider to the desired position
        self.positionslider.setValue(self.mediaplayer.get_position() * 1000)

        if not self.mediaplayer.is_playing():
            # no need to call this function if nothing is played
            self.timer.stop()
            if not self.isPaused:
                # after the video finished, the play button stills shows
                # "Pause", not the desired behavior of a media player
                # this will fix it
                self.Stop()

#开启线程读取字幕
def timer_start(mediaplayer):
    t = threading.Thread(target= Sub,args= (mediaplayer,))
    t.start()
#读取字幕
def Sub(player):
    global mylist
    f = share_memory.read_mmap_info()
    file = os.path.basename(f)
    pwd = os.path.dirname(f)
    temp = file.split('.')
    #mylist =
    tmp = pwd.replace('/','\\')
    if mylist[1] == 0:
        pwd = pwd = tmp + '\\' + temp[0] + '.srt'
    elif mylist[1] == 2:
        pwd = tmp + '\\' + temp[0] + '_'+ mylist[2] +'.srt'
    print("hahah: "+ pwd)
    while True:
        vlc.libvlc_video_set_subtitle_file(player, bytes(pwd, 'utf-8'))
        time.sleep(5)


def main():
    global t
    app = QtGui.QApplication(sys.argv)
    player = Player()
    player.show()
    player.resize(640, 480)
    if sys.argv[1:]:
        player.OpenFile(sys.argv[1])
        player.OpenSub(sys.argv[1])
    if app.exec_() == 0:
        player.Stop()
        sys.exit(0)
if __name__ == '__main__':
    main()
