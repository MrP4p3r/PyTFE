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
        self.setWindowTitle(self.APP_TITLE)
    
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
            self.open_from_tfe(path)
            ...
        elif ext == '.gpg':
            # ВЫЗВАТЬ ОТКРЫВАЛКУ GPG
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
            self.save_to_tfe(path)
            ...
        elif ext == '.gpg':
            # ВЫЗВАТЬ СОХРАНЯЛКУ В GPG
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
        pas = pas1.encode('utf-8')          # пароль в байтах
        s = self.text.toPlainText()
        b = s.encode('utf-8')               # КОДИРОВОЧКА
        bi = BytesIO(b)
        bo = open(path,'wb')
        res = tfe.EncryptBuffer(bi,bo,len(b),pas)
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
            if not d.exec_(): return
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

class MSaveDialog(QDialog):
    data = {
        'text': None,
        'driver': None
    }
    fldst = {
        'tfe':   lambda x: ( x.lab.setText('Пароль:'), \
                             x.field.setEchoMode(QLineEdit.Password) ),
        'gpg-s': lambda x: ( x.lab.setText('Пароль:'), \
                             x.field.setEchoMode(QLineEdit.Password) ),
        'gpg-a': lambda x: ( x.lab.setText('Получатель:'), \
                             x.field.setEchoMode(QLineEdit.Normal) ),
    }
    def __init__(self,iparams,*args):
        super().__init__(*args)
        self.setWindowFlags(self.windowFlags()&~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(iparams['title'])
        lo = QGridLayout()
        self.setLayout(lo)
        
        r_Group = QButtonGroup()
        r_tfe  = MRadioButton('TFE','tfe')
        r_gpgs = MRadioButton('GPG (Symmetric)','gpg-s')
        r_gpga = MRadioButton('GPG (Assymetric)','gpg-a')
        r_Group.addButton(r_tfe)
        r_Group.addButton(r_gpgs)
        r_Group.addButton(r_gpga)
        r_tfe.clicked.connect(self.udriver)
        r_gpgs.clicked.connect(self.udriver)
        r_gpga.clicked.connect(self.udriver)
        r_gpga.clicked.connect(self.upassphrase)
        
        self.lab = QLabel()
        self.lab.setText('Пароль:')
        
        self.field = QLineEdit()
        self.field.setEchoMode(QLineEdit.Password)
        self.field.textChanged.connect(self.upassphrase)
        
        r_tfe.click()
        
        self.adjustSize()
        self.setMinimumWidth(350)
        self.setFixedSize(self.size())
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        lo.addWidget(r_tfe,      1,1,1,2)
        lo.addWidget(r_gpgs,     2,1,1,2)
        lo.addWidget(r_gpga,     3,1,1,2)
        lo.addWidget(self.lab,   4,1)
        lo.addWidget(self.field, 4,2)
        lo.addWidget(buttons,    5,2)
        
        self.field.setFocus()
    
    def upassphrase(self,p):
        self.data['text'] = p
    
    def udriver(self,d):
        self.fldst[d](self)
        self.field.setText('')
        self.data['driver'] = d
    
    @staticmethod
    def getEncParams(*args):
        dialog = MSaveDialog(*args)
        result = dialog.exec()
        return dialog.data if result == QDialog.Accepted else None

class MLineDialog(QDialog):
    data = { 'text': None }
    def __init__(self,iparams,*args):
        super().__init__(*args)
        self.setWindowTitle(iparams['title'])
        self.lab = QLabel()
        self.lab.setText(iparams['label'])
        
        lo = QGridLayout()
        self.setLayout(lo)
        
        self.field = QLineEdit()
        self.field.setEchoMode(iparams['echomode'])
        self.field.textChanged.connect(self.upassphrase)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        lo.addWidget(self.lab,1,1)
        lo.addWidget(self.field,1,2)
        lo.addWidget(buttons,2,1,1,2)
    
    def upassphrase(self,p):
        self.data['text'] = p
    
    @staticmethod
    def getText(*args):
        dialog = MLineDialog(*args)
        result = dialog.exec()
        return dialog.data if result == QDialog.Accepted else None









