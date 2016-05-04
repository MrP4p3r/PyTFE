#! /usr/bin/python3.4
#  encoding=utf8

import sys
import os
import subprocess
import traceback

from io import BytesIO

from PyQt5.QtWidgets import *
from PyQt5.QtGui     import *
from PyQt5.QtCore    import *

import tfe

OK = 0
NOT_TEXT = 1
NOT_SUPPORTED = 2
INTERNAL_ERROR = 3

class MPlainTextEdit(QPlainTextEdit):
    def wheelEvent(self,event): 
        deg = event.angleDelta() / 8
        steps = deg / 15
        modif = event.modifiers()
        if modif == Qt.ControlModifier:
            event.accept()
            if steps.y() > 0:  self.zoomIn()
            else:              self.zoomOut()
            return
        else:
            event.accept()
            super().wheelEvent(event)
            return

class Main(QMainWindow):
    APP_TITLE = 'Python TFE'
    WORK_DIR  = '.'
    PATH      = None
    FILE_FORMATS = """
        Формат TFE (*.tfe);;
        Формат GPG (*.gpg)
    """
    _FILE_FORMATS = ['.tfe','.gpg']
    
    # параметры открытого файла
    FILE_FORMAT = None
    FILE_PATH = None
    FILE_NAME = 'Untitled'
    FILE_PASSPHRASE = None
    FILE_OPENED = False
    FILE_SAVED = True
    
    def __init__(self,path,*args):
        self.app = QApplication(sys.argv)
        super().__init__(*args)
        
        self.PATH = path
        self.WORK_DIR = os.path.join(os.path.expanduser('~'),'Desktop')
        if not os.path.isdir(self.WORK_DIR):
            self.WORK_DIR = os.path.expanduser('~')
        
        self.initUI()
        
        if len(sys.argv)>1:
            if os.path.isfile(sys.argv[1]):
                self.openArgFile(sys.argv[1])
    
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
        self.initDragNDrop()
    
    def updateWindowTitle(self):
        new_title = ''
        if not self.FILE_SAVED: new_title += '* '
        new_title += self.FILE_NAME
        new_title += ' - ' + self.APP_TITLE
        self.setWindowTitle(new_title)
    
    def initText(self):
        self.text = MPlainTextEdit()
        
        self.text.textChanged.connect(self.textChangedHandler)
        
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
        file  = menubar.addMenu('Файл')
        edit  = menubar.addMenu('Правка')
        view  = menubar.addMenu('Вид')
        #about = menubar.addMenu('О программе')
        
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
        
        # edit
        
        undoA = QAction('Отменить',self)
        undoA.setShortcut('Ctrl+Z')
        undoA.triggered.connect(self.text.undo)
        
        redoA = QAction('Повторить',self)
        redoA.setShortcuts(['Ctrl+Y','Ctrl+Shift+Z'])
        redoA.triggered.connect(self.text.redo)
        
        selaA = QAction('Выделить все',self)
        selaA.setShortcut('Ctrl+A')
        selaA.triggered.connect(self.text.selectAll)
        
        cutA = QAction('Вырезать',self)
        cutA.setShortcut('Ctrl+X')
        cutA.triggered.connect(self.text.cut)
        
        copyA = QAction('Копировать',self)
        copyA.setShortcut('Ctrl+C')
        copyA.triggered.connect(self.text.copy)
        
        pasteA = QAction('Вставить',self)
        pasteA.setShortcut('Ctrl+V')
        pasteA.triggered.connect(self.text.paste)
        
        edit.addAction(undoA)
        edit.addAction(redoA)
        edit.addSeparator()
        edit.addAction(selaA)
        edit.addAction(cutA)
        edit.addAction(copyA)
        edit.addAction(pasteA)
        
        # view
        wowA = QAction('Перенос слов',self)
        wowA.setStatusTip('Включить/отключить перенос слов')
        wowA.setShortcut('Ctrl+W')
        wowA.setCheckable(True)
        wowA.toggled.connect(self.v_triggerwow)
        
        view.addAction(wowA)
        
        # about
        about = QAction('О программе...',self)
        about.setStatusTip('Краткие сведения о программе')
        about.triggered.connect(self.a_about)
        
        menubar.addAction(about)
    
    def initStatusbar(self):
        statusbar = self.statusBar()
        statusbar.setFixedHeight(22)
        statusbar.setStyleSheet("""
            QStatusBar { border-top: 1px solid #d7d7d7; }
            QLabel { padding: 0 0 }
        """)
    
    def initDragNDrop(self):
        self.setAcceptDrops(True)
        self.text.setAcceptDrops(True)
        self.text.dragEnterEvent = self.dragEnterEvent
        self.text.dropEvent = self.dropEvent
    
    # ---------- MENU FUNCTIONS ----------
    
    def f_new(self):
        # ATTENTION!
        subprocess.Popen('python '+sys.argv[0],shell=False)
    
    def f_open(self):
        suggested_name = os.path.join(self.WORK_DIR,'*.*')
        path,ext = QFileDialog.getOpenFileName(
            self,
            'Открыть файл',
            self.WORK_DIR,
            self.FILE_FORMATS
        )
        if not path: return
        
        self.openFile(path)
        
        self.updateWindowTitle()
        return
    
    def f_save(self):
        if self.FILE_OPENED:
            # СОХРАНИТЬ ФАЙЛ С ТЕКУЩИМИ ОПЦИЯМИ
            if self.FILE_FORMAT == '.tfe':
                res = self.save_to_tfe(self.FILE_PATH)
            elif self.FILE_FORMAT == '.gpg':
                res = self.save_to_gpg(self.FILE_PATH)
            if res == OK:
                self.saveOk()
            elif res == INTERNAL_ERROR:
                self.saveError(res)
            self.updateWindowTitle()
            return res
        else:
            # СОХРАНИТЬ КАК
            res = self.f_save_as()
            return res
        
    
    def f_save_as(self):
        # запрос файла у пользователя
        self.FILE_OPENED = False
        if self.FILE_PATH is None:
            suggested_name = os.path.join(self.WORK_DIR,self.FILE_NAME)
        else:
            suggested_name = self.FILE_PATH
        path,ext = QFileDialog.getSaveFileName(
            self,
            'Сохранить файл',
            suggested_name,
            self.FILE_FORMATS
        )
        if not path: return
        
        _ext = os.path.splitext(path)[1]
        if _ext in self._FILE_FORMATS: ext = _ext
        
        if ext == '.tfe':
            res = self.save_to_tfe(path)
        elif ext == '.gpg':
            res = self.save_to_gpg(path)
        
        if res == OK:
            self.saveOk()
        elif res == INTERNAL_ERROR:
            self.saveError(res)
        self.updateWindowTitle()
        return res
    
    def f_esc(self):
        self.close()
    
    def v_triggerwow(self,ena):
        if ena:
            self.text.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        else:
            self.text.setWordWrapMode(QTextOption.NoWrap)
    
    def a_about(self):
        s = \
        "<h1>PyTFE</h1>"\
        "<p>Copyright &copy; 2016 Gleb Getmanenko</p>"\
        "<p>Это приложение позволяет сохранять текст в зашифрованном виде. "\
        "Текст можно сохранять как в формате приложения, "\
        "так и с использованием симметричного шифрования с помощью GPG.<p>"\
        "<a href='https://github.com/MrP4p3r/PyTFE'>Репозиторий на GitHub</a>"
        
        QMessageBox.about(self,"О программе",s)
    
    # ---------- EVENT HANDLERS ----------
    
    def textChangedHandler(self):
        if self.FILE_SAVED:
            self.FILE_SAVED = False
            self.updateWindowTitle()
    
    def dragEnterEvent(self,event):
        mime = event.mimeData()
        if mime.hasUrls():
            urls = mime.urls()
            if len(urls) == 1 and urls[0].toLocalFile():
                event.acceptProposedAction()
    
    def dropEvent(self,event):
        mime = event.mimeData()
        if mime.hasUrls():
            urls = mime.urls()
            print(urls[0].toLocalFile())
            self.openFile(urls[0].toLocalFile())
    
    def closeEvent(self,event):
        if not self.text.toPlainText().strip() and self.FILE_PATH is None:
            event.accept()
        elif self.FILE_SAVED:
            event.accept()
        else:
            res = self.saveFileQuestion()
            if res == QMessageBox.Yes:
                if self.f_save() == OK:
                    event.accept()
                else:
                    event.ignore()
            elif res == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
    
    # ---------- OTHER FUNCTIONS ----------
    
    def openArgFile(self,path):
        res = self.openFile(path)
        if res or res is None:
            exit()
    
    def openFile(self,path):
        #TODO
        ext = None
        _ext = os.path.splitext(path)[1]
        if _ext in self._FILE_FORMATS: ext = _ext
        
        if ext is None:
            res = NOT_SUPPORTED
        elif ext == '.tfe':
            res = self.open_from_tfe(path)
        elif ext == '.gpg':
            res = self.open_from_gpg(path)
        
        if res == OK:
            self.openOk()
        elif res == INTERNAL_ERROR:
            self.openError(res)
        elif res == NOT_SUPPORTED:
            self.openError(res)
        
        return res
    
    def save_to_tfe(self,path):
        if not self.FILE_OPENED:
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
        else:
            pas = self.FILE_PASSPHRASE
        s = self.text.toPlainText()
        b = s.encode('utf-8')               # КОДИРОВОЧКА
        bi = BytesIO(b)
        tpath = path+'~'
        with open(tpath,'wb') as bo:
            res = 0
            try: tfe.EncryptBuffer(bi,bo,len(b),pas,alg="Blowfish",hasht="MD5")
            except: res = 1; traceback.print_exc()
        if res == 0:
            os.replace(tpath,path)
            self.fileOpened('.tfe',path,pas)
            return OK
        else:
            os.remove(tpath) # MAY CAUSE PROBLEMS
            return INTERNAL_ERROR
    
    def open_from_tfe(self,path):
        if not tfe.isTfeFile(path):
            return NOT_SUPPORTED
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
            bo  = BytesIO()
            res = 0
            with open(path,'rb') as bi:
                try: tfe.DecryptBuffer(bi,bo,pas)
                except ValueError:
                    res = 1
                except:
                    res = 2
                    print('неясная ошибочка')
                    traceback.print_exc()
            #bi.close()
            if res == 0:
                print('расшифровалось, ага')
                bo.seek(0,0)
                b = bo.read()
                try:
                    s = b.decode('utf-8','replace')           # КОДИРОВОЧКА
                except:
                    traceback.print_exc()
                    res = self.openError(NOT_TEXT)
                    if res == QMessageBox.Yes:
                        try: s = b.decode('ascii')
                        except:
                            traceback.print_exc();
                            return INTERNAL_ERROR
                    else:
                        return
                self.text.setPlainText(s)
                self.fileOpened('.tfe',path,pas)
                return OK
            elif res == 1:
                d.setLabelText('Неверный пароль. Введите пароль:')
                continue
            else:
                return INTERNAL_ERROR
    
    def save_to_gpg(self,path):
        # раскомментить после добавления ассиметричного шифрования
        sym == '-c'
        # sym = MDialogGPGSym.getSym(self)
        if sym == '-c':
            if not self.FILE_OPENED:
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
                    if pas1!=pas2:
                        d.setLabelText('Пароли не совпадают. Введите пароль:')
                    else:
                        break
                    d.setTextValue('')
                #pas = pas1.encode('utf-8')         # пароль в байтах
                pas = pas1
            else:
                pas = self.FILE_PASSPHRASE
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
            except: res = 1; traceback.print_exc()
            print(res)
            if res == 0:
                self.fileOpened('.gpg',path,pas)
                return OK
            else:
                return INTERNAL_ERROR
        elif sym == '-e':
            # TODO
            #if not self.FILE_OPENED:
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
            except: res = 1; traceback.print_exc()
            #bo.close()
            if res == 0:
                # TODO
                #self.fileOpened('.gpg',path,pas)
                return OK
            else:
                return INTERNAL_ERROR
    
    def open_from_gpg(self,path):
        # ['gpg','--no-use-agent','--batch','--yes','-d',path] # symmetric
        # ['gpg','--no-use-agent','--batch','--yes ????????????
        ...
    
    # ---------- NOTIFIERS ----------
    
    def saveOk(self):
        self.statusBar().showMessage('Сохранено',1500)
    
    def saveError(self,er):
        if er == INTERNAL_ERROR:
            QMessageBox.critical(
                self, "Ошибка при сохранении",
                "Сработало внутреннее исключение при сохранении файла"
            )
    
    def openOk(self):
        self.statusBar().showMessage('Открыто',1500) #?
        self.updateWindowTitle()
    
    def openError(self,er):
        if er == INTERNAL_ERROR:
            QMessageBox.critical(
                self, "Ошибка при открытии",
                "Сработало внутреннее исключение при открытии файла"
            )
        elif er == NOT_SUPPORTED:
            QMessageBox.critical(
                self, "Ошибка при открытии",
                "Данный формат не поддерживается или файл поврежден"
            )
        elif er == NOT_TEXT:
            # может не понадобится
            res = QMessageBox.question(
                self, "Ошибка при открытии",
                "Расшифрованные данные не являются текстом. "\
                "Целостность данных не гарантирована. Продолжить?"
            )
            return res
    
    def saveFileQuestion(self):
        res = QMessageBox.question(
            self, "Файл не сохранен",
            "Файл не сохранен. Сохранить?",
            buttons = QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )
        return res
    
    def fileOpened(self,format,path,pas):
        self.FILE_FORMAT     = format
        self.FILE_PATH       = path
        self.WORK_DIR,self.FILE_NAME = os.path.split(path)
        self.FILE_PASSPHRASE = pas
        self.FILE_OPENED     = True
        self.FILE_SAVED      = True

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

