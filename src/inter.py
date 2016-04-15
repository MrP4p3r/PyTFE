#! /usr/bin/python3.4
#  encoding=utf8

import sys
import os
import subprocess

from PyQt5.QtWidgets import *
from PyQt5.QtGui     import *
from PyQt5.QtCore    import *

class Main(QMainWindow):
    apptitle = 'Python TFE'
    def __init__(self,path,*args):
        self.app = QApplication(sys.argv)
        super().__init__(*args)
        
        self.path = path
        
        self.initUI()
        
        #if os.path.isfile(sys.argv[1])
    
    def locres(self,fname):
        return os.path.join(self.path,fname)
    
    def initUI(self):
        # window
        self.setGeometry(0,0,800,600)
        self.setGeometry(
            QStyle.alignedRect(
                Qt.LeftToRight,
                Qt.AlignCenter,
                self.size(),
                self.app.desktop().availableGeometry()
            )
        )
        self.updateWindowTitle()
        self.app_icon = QIcon()
        self.app_icon.addFile(self.locres('icon.png'), QSize(256,256))
        self.setWindowIcon(self.app_icon)
        
        # widgets
        self.text = QPlainTextEdit()
        self.text.setFrameStyle(QFrame.NoFrame)
        self.setCentralWidget(self.text)
        self.initMenubar()
        self.initStatusbar()
        
        self.text.setStyleSheet("""
            QTextEdit {
                font: 10pt Consolas;
                background-color: #fdf6e3;
                color: #586e75;
                selection-background-color: #586e75;
                selection-color: #fdf6e3;
            }
        """)
        #line number color: #93a1a1
        #line number background color: #eee8d5
    
    def updateWindowTitle(self):
        self.setWindowTitle(self.apptitle)
    
    def initMenubar(self):
        menubar = self.menuBar()
        file = menubar.addMenu('Файл')
        edit = menubar.addMenu('Правка')
        view = menubar.addMenu('Вид')
        abot = menubar.addMenu('О программе')
        
        # file
        newA = QAction('Создать',self)
        newA.setStatusTip('Создать новый файл')
        newA.setShortcut('Ctrl+N')
        newA.triggered.connect(self.f_new)
        
        opeA = QAction('Открыть',self)
        opeA.setStatusTip('Открыть существующий файл')
        opeA.setShortcut('Ctrl+O')
        opeA.triggered.connect(self.f_open)
        
        savA = QAction('Сохранить',self)
        savA.setStatusTip('Сохранить файл')
        savA.setShortcut('Ctrl+S')
        savA.triggered.connect(self.f_save)
        
        sasA = QAction('Сохранить как...',self)
        sasA.setStatusTip('Сохранить файл с другими настройками')
        sasA.setShortcut('Ctrl+Shift+S')
        sasA.triggered.connect(self.f_save_as)
        
        escA = QAction('Выход',self)
        escA.setStatusTip('Выход')
        escA.setShortcuts(['Alt+F4','Esc'])
        escA.triggered.connect(self.f_esc)
        
        file.addAction(newA)
        file.addAction(opeA)
        file.addAction(savA)
        file.addSeparator()
        file.addAction(escA)
        
        # view
        wowA = QAction('Перенос слов',self)
        wowA.setStatusTip('Включить/отключить перенос слов')
        wowA.setShortcut('Cltr+W')
        wowA.triggered.connect(self.v_triggerwow)
        
        view.addAction(wowA)
    
    def initStatusbar(self):
        statusbar = self.statusBar()
        statusbar.setFixedHeight(22)
        statusbar.setStyleSheet("""
            QStatusBar { border-top: 1px solid #d7d7d7; }
            QLabel { padding: 0 0 }
        """)
    
    def f_new(self):
        subprocess.Popen('python '+sys.argv[0],shell=False)
    
    def f_open(self):
        ...
    
    def f_save(self):
        ...
    
    def f_save_as(self):
        ...
    
    def f_esc(self):
        ...
    
    def v_triggerwow(self):
        ...













