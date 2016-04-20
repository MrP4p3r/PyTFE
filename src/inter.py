#! /usr/bin/python3.4
#  encoding=utf8

import sys
import os
import subprocess

from io import BytesIO

from PyQt5.QtWidgets import *
from PyQt5.QtGui     import *
from PyQt5.QtCore    import *

import tfe

class Main(QMainWindow):
    APP_TITLE = 'Python TFE'
    WORK_DIR  = '.'
    PATH      = None
    FILE_PATH = None
    FILE_FORMATS = """
        Формат TFE (*.tfe);;
        Формат GPG (*.gpg)
    """
    _FILE_FORMATS = ['.tfe','.gpg']
    
    def __init__(self,path,*args):
        self.app = QApplication(sys.argv)
        super().__init__(*args)
        
        self.PATH = path
        self.WORK_DIR = os.path.join(os.path.expanduser('~'),'Desktop')
        if not os.path.isdir(self.WORK_DIR):
            self.WORK_DIR = os.path.expanduser('~')
        
        self.initUI()
        
        #if os.path.isfile(sys.argv[1])
    
    def locres(self,fname):
        return os.path.join(self.PATH,fname)
    
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
        self.initText() # creates self.text
        self.setCentralWidget(self.text)
        self.initMenubar()
        self.initStatusbar()
    
    def updateWindowTitle(self):
        self.setWindowTitle(self.APP_TITLE)
    
    def initText(self):
        self.text = QPlainTextEdit()
        self.text.setFrameStyle(QFrame.NoFrame)
        p = self.text.palette()
        f = QFont()
        
        p.setColor(QPalette.Base,QColor('#fdf6e3'))
        p.setColor(QPalette.Text,QColor('#586e75'))
        p.setColor(QPalette.Highlight,QColor('#586e75'))
        p.setColor(QPalette.HighlightedText,QColor('#fdf6e3'))
        
        # line number color : #93a1a1
        # line number background color : #eee8d5
        
        f.setFamily('Courier New')
        f.setPointSize(10)
        
        self.text.setPalette(p)
        self.text.setFont(f)
    
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
        file.addAction(sasA)
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
        path,ext = QFileDialog.getOpenFileName(
            self,
            'Открыть файл',
            self.WORK_DIR,
            self.FILE_FORMATS
        )
        if path is None: return
        
        _ext = os.path.splitext(path)[1]
        if _ext in self._FILE_FORMATS: ext = _ext
        
        if ext == '.tfe':
            # ОТКРЫВАЛКА TFE
            self.open_from_tfe(path)
            ...
        elif ext == '.gpg':
            # ОТКРЫВАЛКА GPG
            self.open_from_gpg(path)
            ...
        
        return
    
    def f_save(self):
        if self.FILE_PATH is None:
            self.f_save_as()
            return
        
        # СОХРАНИТЬ ФАЙЛ С ТЕКУЩИМИ ОПЦИЯМИ
    
    def f_save_as(self):
        # запрос файла у пользователя
        path,ext = QFileDialog.getSaveFileName(
            self,
            'Сохранить файл',
            self.WORK_DIR,
            self.FILE_FORMATS
        )
        if path is None: return
        
        _ext = os.path.splitext(path)[1]
        if _ext in self._FILE_FORMATS: ext = _ext
        
        print(path,ext)
        
        if ext == '.tfe':
            # СОХРАНЯЛКА В TFE
            self.save_to_tfe(path)
            ...
        elif ext == '.gpg':
            # СОХРАНЯЛКА В GPG
            self.save_to_gpg(path)
            ...
        
        return
    
    def f_esc(self):
        exit() #TODO
    
    def v_triggerwow(self):
        ...
    
    def save_to_tfe(self,path):
        d = QInputDialog(self)
        d.resize(300,d.height())
        d.setTextEchoMode(QLineEdit.Password)
        d.setWindowTitle('Пароль')
        d.setLabelText('Введите пароль:')
        while True:
            # ввод пароля
            if not d.exec(): return
            pas1 = d.textValue()
            if len(pas1)<4:
                d.setLabelText('Слишком короткий пароль. Введите пароль:')
                continue
            d.setTextValue('')
            d.setLabelText('Повторите пароль:')
            # повторный ввод пароля
            if not d.exec(): return
            pas2 = d.textValue()
            # проверка пароля
            if pas1!=pas2: d.setLabelText('Пароли не совпадают. Введите пароль:')
            else: break
            d.setTextValue('')
        pas = pas1.encode('utf-8')          # пароль в байтах
        s = self.text.toPlainText()
        b = s.encode('utf-8')               # КОДИРОВОЧКА
        bi = BytesIO(b)
        bo = open(path,'wb')
        res = 0
        try: tfe.EncryptBuffer(bi,bo,len(b),pas)
        except: res = 1
        bo.close()
        if res == 0:
            ... # эмит save_ok
            return
        else:
            ... # msgbox save_error ???
            return
    
    def open_from_tfe(self,path):
        if not tfe.isTfeFile(path):
            ... # msgbox ошибка
            return
        d = QInputDialog(self)
        d.resize(300,d.height())
        d.setTextEchoMode(QLineEdit.Password)
        d.setWindowTitle('Пароль')
        d.setLabelText('Введите пароль:')
        while True:
            if not d.exec(): return
            pas1 = d.textValue()
            d.setTextValue('')
            pas = pas1.encode('utf-8')          # байты, байты
            bi  = open(path,'rb')
            bo  = BytesIO()
            res = 0
            try: tfe.DecryptBuffer(bi,bo,pas)
            except ValueError:     res = 1
            except Exception as e: print('неясная ошибочка'); print(e)
            bi.close()
            if res == 0:
                print('расшифровалось, ага')
                bo.seek(0,0)
                b = bo.read()
                s = b.decode('utf-8')           # КОДИРОВОЧКА
                self.text.setPlainText(s)
                ... # эмит open_ok
                return
            elif res == 1:
                d.setLabelText('Неверный пароль. Введите пароль:')
                continue
            else:
                ... # msg ошибочка
                return
        
    def save_to_gpg(self,path):
        sym = MDialogGPGSym.getSym(self)
        if sym == '-c':
            d = QInputDialog(self)
            d.resize(300,d.height())
            d.setTextEchoMode(QLineEdit.Password)
            d.setWindowTitle('Пароль')
            d.setLabelText('Введите пароль:')
            while True:
                # ввод пароля
                if not d.exec_(): return
                pas1 = d.textValue()
                if len(pas1)<4:
                    d.setLabelText('Слишком короткий пароль. Введите пароль:')
                    continue
                d.setTextValue('')
                d.setLabelText('Повторите пароль:')
                # повторный ввод пароля
                if not d.exec(): return
                pas2 = d.textValue()
                # проверка пароля
                if pas1!=pas2: d.setLabelText('Пароли не совпадают. Введите пароль:')
                else: break
                d.setTextValue('')
            #pas = pas1.encode('utf-8')          # пароль в байтах
            pas = pas1
            s = self.text.toPlainText()
            b = s.encode('utf-8')               # КОДИРОВОЧКА
            #bi = BytesIO(b)
            #bo = open(path,'wb')
            res = 0
            try:
                p = subprocess.Popen(
                    [
                        'gpg','-c','--no-use-agent','--passphrase',pas,
                        '--batch','--yes','-o',path
                    ],
                    stdin = subprocess.PIPE
                )
                print(p.communicate(b))
                print(p.terminate())
            except: res = 1
            print(res)
            #bo.close()
            if res == 0:
                ... # эмит save_ok
                return
            else:
                ... # msgbox save_error ???
                return
        elif sym == '-e':
            d = QInputDialog(self)
            d.resize(300,d.height())
            d.setTextEchoMode(QLineEdit.Normal)
            d.setWindowTitle('Получатель')
            d.setLabelText('Введите ?????:')
            # ввод пароля
            if not d.exec(): return
            name = d.textValue()
            s = self.text.toPlainText()
            b = s.encode('utf-8')               # КОДИРОВОЧКА
            #bi = BytesIO(b)
            #bo = open(path,'wb')
            res = 0
            try:
                p = subprocess.Popen(
                    ['gpg','-e','--no-use-agent','-r',name,'-o',path],
                    stdin = subprocess.PIPE
                )
                p.communicate(b)
                p.terminate()
            except: res = 1
            #bo.close()
            if res == 0:
                ... # эмит save_ok
                return
            else:
                ... # msgbox save_error ???
                return
    
    def open_from_gpg(self,path):
        # ['gpg','--no-use-agent','--batch','--yes','-d',path] # symmetric
        # ['gpg','--no-use-agent','--batch','--yes ????????????
        ...



# ---------- ВИДЖЕТЫ ДЛЯ СОХРАНЕНИЯ ФАЙЛОВ ----------

"""
GPG:
    Ассимметричное шифрование:
        Необходимо указать пользователя с ключом
    Симметричное шифрование:
        Необходимо ввести пароль
TFE (только симметричное):
    Необходимо ввести кодовую фразу
"""

class MRadioButton(QRadioButton):
    clicked = pyqtSignal(object)
    def __init__(self,text,rvalue,*args):
        super().__init__(text,*args)
        super().clicked.connect(self._valueEmitter)
        self.rvalue = rvalue
    def _valueEmitter(self,b):
        self.clicked.emit(self.rvalue)

class MDialogGPGSym(QDialog):
    sym = None
    def __init__(self,*args):
        super().__init__(*args)
        self.setWindowFlags(self.windowFlags()&~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle('Тип шифрования GPG')
        lo = QGridLayout(self)
        
        self.lab = QLabel()
        self.lab.setText('Выберите тип шифрования:')
        
        r_Group = QButtonGroup()
        r_symm = MRadioButton('Симметричное','-c')
        r_asym = MRadioButton('Ассиметричное','-e')
        r_Group.addButton(r_symm)
        r_Group.addButton(r_asym)
        r_symm.clicked.connect(self.changesym)
        r_asym.clicked.connect(self.changesym)
        
        r_symm.click()
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        
        lo.addWidget(self.lab, 1,1)
        lo.addWidget(r_symm,   2,1)
        lo.addWidget(r_asym,   3,1)
        lo.addWidget(buttons,  4,1)
        
        self.adjustSize()
        self.setMinimumWidth(350)
        self.setFixedSize(self.size())
    
    def changesym(self,v):
        self.sym = v
    
    @staticmethod
    def getSym(*args):
        dialog = MDialogGPGSym(*args)
        if dialog.exec(): return dialog.sym
        else: return None

