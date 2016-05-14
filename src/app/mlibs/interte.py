#! /usr/bin/python3.4
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import traceback

from io import BytesIO

from PyQt5.QtWidgets import *
from PyQt5.QtGui     import *
from PyQt5.QtCore    import *

from . import tfe
from .defaultvalues   import *
from .commonfunctions import *
from .mwidgetste      import *

class Main(QMainWindow):
    APP_TITLE = 'PyTFE'
    WORK_DIR  = '.'
    PATH      = None
    FILE_FORMATS = { 'TFE (*.tfe)': '.tfe', 'TXT (*.txt)': '.txt' }
    _FILE_FORMATS = { '.tfe', '.txt' }
    EXPORT_FILE_FORMATS = { 'Symmetric GPG (*.gpg)': '.gpg'}
    _EXPORT_FILE_FORMATS = { '.gpg' }

    # параметры открытого файла
    FILE_FORMAT = None
    FILE_PATH = None
    FILE_NAME = 'Untitled'
    FILE_PASSPHRASE = None
    FILE_ALGO = None
    FILE_OPENED = False
    FILE_SAVED = True

    def __init__(self, path, *args):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(self.APP_TITLE)
        super().__init__(*args)

        self.PATH = path
        self.WORK_DIR = os.path.join(os.path.expanduser('~'), 'Desktop')
        if not os.path.isdir(self.WORK_DIR):
            self.WORK_DIR = os.path.expanduser('~')

        self.stt = QSettings(os.path.expanduser(PATH_CONFIG), QSettings.IniFormat)
        self.loadTranslator()
        self.initUI()
        self.loadSettings()

        self.show()

        if len(sys.argv) > 1:
            if os.path.isfile(sys.argv[1]):
                self.openArgFile(sys.argv[1])

    def locres(self, fname):
        return os.path.join(self.PATH, fname)

    def saveSettings(self):
        self.stt.setValue('window/geometry', self.geometry())

        '''
        p = self.text.palette()
        f = self.text.font()

        self.stt.beginGroup('text')
        self.stt.setValue('base', p.color(QPalette.Base).name())
        self.stt.setValue('text', p.color(QPalette.Text).name())
        self.stt.setValue('highlight', p.color(QPalette.Highlight).name())
        self.stt.setValue('highlighttext', p.color(QPalette.HighlightedText).name())
        self.stt.setValue('fontfamily', f.family())
        self.stt.setValue('fontsize', f.pointSize())
        self.stt.endGroup()

        self.stt.setValue('app/default_algo', self.DEFAULT_ALGO)
        self.stt.setValue('app/use_default_algo', self.USE_DEFAULT_ALGO)
        '''

    def loadSettings(self):
        self.DEFAULT_ALGO = self.stt.value('app/default_algo', 'Blowfish')
        self.USE_DEFAULT_ALGO = mbool(self.stt.value('app/use_default_algo', True))

        p = self.text.palette()
        f = self.text.font()

        col1 = self.stt.value('text/base', DEFAULT_TEXT_BASE_C)
        col2 = self.stt.value('text/text', DEFAULT_TEXT_TEXT_C)
        col3 = self.stt.value('text/highlight', DEFAULT_TEXT_HIGHLIGHT_C)
        col4 = self.stt.value('text/highlighttext', DEFAULT_TEXT_HIGHLIGHTTEXT_C)
        p.setColor(QPalette.Base, QColor(col1))
        p.setColor(QPalette.Text, QColor(col2))
        p.setColor(QPalette.Highlight, QColor(col3))
        p.setColor(QPalette.HighlightedText, QColor(col4))

        ff = self.stt.value('text/fontfamily', DEFAULT_TEXT_FONTFAMILY)
        fs = int(self.stt.value('text/fontsize', DEFAULT_TEXT_FONTSIZE))
        f.setFamily(ff)
        f.setPointSize(fs)

        self.text.setPalette(p)
        self.text.setFont(f)

    def loadTranslator(self):
        try: self.app.removeTranslator(self.translator_app)
        except: pass

        try: self.app.removeTranslator(self.translator_qt)
        except: pass

        try: self.app.removeTranslator(self.translator_com)
        except: pass

        self.translator_app = QTranslator()
        self.translator_qt  = QTranslator()
        self.translator_com = QTranslator()

        self.locale = QLocale(
            int(self.stt.value('locale/locale', QLocale.English))
        )

        q = self.translator_app.load(
            self.locale, 'tr', '_', self.locres('tr'), '.qm'
        )
        if q: self.app.installTranslator(self.translator_app)

        q = self.translator_qt.load(
            self.locale, 'qt', '_', self.locres('tr'), '.qm'
        )
        if q: self.app.installTranslator(self.translator_qt)

        q = self.translator_com.load(
            'com',self.locres('tr'),'','.qm'
        )
        if q: self.app.installTranslator(self.translator_com)

    def updateLanguage(self):
        self.A['file'].setTitle(self.tr('File'))
        self.A['edit'].setTitle(self.tr('Edit'))
        self.A['view'].setTitle(self.tr('View'))
        self.A['about'].setText(self.tr('About...'))
        self.A['newA'].setText(self.tr('New file'))
        self.A['opeA'].setText(self.tr('Open'))
        self.A['savA'].setText(self.tr('Save'))
        self.A['sasA'].setText(self.tr('Save As...'))
        self.A['expA'].setText(self.tr('Export'))
        self.A['sttA'].setText(self.tr('Preferences'))
        self.A['escA'].setText(self.tr('Exit'))
        self.A['undoA'].setText(self.tr('Undo'))
        self.A['redoA'].setText(self.tr('Redo'))
        self.A['selaA'].setText(self.tr('Select All'))
        self.A['cutA'].setText(self.tr('Cut'))
        self.A['copyA'].setText(self.tr('Copy'))
        self.A['pasteA'].setText(self.tr('Paste'))
        self.A['wowA'].setText(self.tr('Word Wrap'))

        self.A['newA'].setStatusTip(self.tr('New file'))
        self.A['opeA'].setStatusTip(self.tr('Open an existing file'))
        self.A['savA'].setStatusTip(self.tr('Save file'))
        self.A['sasA'].setStatusTip(self.tr('Save file as...'))
        self.A['expA'].setStatusTip(self.tr('Save file in external format'))
        self.A['sttA'].setStatusTip(self.tr('Application settings and preferences'))
        self.A['escA'].setStatusTip(self.tr('Close the application'))
        self.A['wowA'].setStatusTip(self.tr('Enable/disable word wrapping'))

    def initUI(self):
        # window
        default_geom = QStyle.alignedRect(
            Qt.LeftToRight,
            Qt.AlignCenter,
            QSize(640,480),
            self.app.desktop().availableGeometry()
        )

        # set icon and load geometry from config.ini
        geom = self.stt.value('window/geometry', default_geom)
        self.setGeometry(geom)
        self.updateWindowTitle()
        self.app_icon = QIcon()
        self.app_icon.addFile(self.locres('icon.png'), QSize(256,256))
        self.setWindowIcon(self.app_icon)

        # init widgets
        self.initText() # creates self.text
        self.setCentralWidget(self.text)
        self.initMenubar()
        self.initStatusbar()
        self.initDragNDrop()

    def updateWindowTitle(self):
        new_title = ''
        if not self.FILE_SAVED:
            new_title += '* '
        new_title += self.FILE_NAME
        new_title += ' - ' + self.APP_TITLE
        self.setWindowTitle(new_title)

    def initText(self):
        self.text = MPlainTextEdit()

        self.text.textChanged.connect(self.textChangedHandler)

        self.text.setFrameStyle(QFrame.NoFrame)
        p = self.text.palette()
        f = QFont()

        col1 = self.stt.value('text/base', DEFAULT_TEXT_BASE_C)
        col2 = self.stt.value('text/text', DEFAULT_TEXT_TEXT_C)
        col3 = self.stt.value('text/highlight', DEFAULT_TEXT_HIGHLIGHT_C)
        col4 = self.stt.value('text/highlightext', DEFAULT_TEXT_HIGHLIGHTTEXT_C)
        p.setColor(QPalette.Base, QColor(col1))
        p.setColor(QPalette.Text, QColor(col2))
        p.setColor(QPalette.Highlight, QColor(col3))
        p.setColor(QPalette.HighlightedText, QColor(col4))

        ff = self.stt.value('text/fontfamily', DEFAULT_TEXT_FONTFAMILY)
        fs = int(self.stt.value('text/fontsize', DEFAULT_TEXT_FONTSIZE))
        f.setFamily(ff)
        f.setPointSize(fs)

        self.text.setPalette(p)
        self.text.setFont(f)

    def initMenubar(self):
        self.A = dict()

        menubar = self.menuBar()
        self.A['file']  = menubar.addMenu(self.tr('File'))
        self.A['edit']  = menubar.addMenu(self.tr('Edit'))
        self.A['view']  = menubar.addMenu(self.tr('View'))
        #about = menubar.addMenu('О программе')

        # file
        self.A['newA'] = QAction(self.tr('New'),self)
        self.A['newA'].setStatusTip(self.tr('New file'))
        self.A['newA'].setShortcut('Ctrl+N')
        self.A['newA'].triggered.connect(self.f_new)

        self.A['opeA'] = QAction(self.tr('Open'),self)
        self.A['opeA'].setStatusTip(self.tr('Open an existing file'))
        self.A['opeA'].setShortcut('Ctrl+O')
        self.A['opeA'].triggered.connect(self.f_open)

        self.A['savA'] = QAction(self.tr('Save'),self)
        self.A['savA'].setStatusTip(self.tr('Save file'))
        self.A['savA'].setShortcut('Ctrl+S')
        self.A['savA'].triggered.connect(self.f_save)

        self.A['sasA'] = QAction(self.tr('Save As...'),self)
        self.A['sasA'].setStatusTip(self.tr('Save file as...'))
        self.A['sasA'].setShortcut('Ctrl+Shift+S')
        self.A['sasA'].triggered.connect(self.f_save_as)

        self.A['expA'] = QAction(self.tr('Export'),self)
        self.A['expA'].setStatusTip(self.tr('Save file in external format'))
        self.A['expA'].setShortcut('Ctrl+Shift+E')
        self.A['expA'].triggered.connect(self.f_export)

        self.A['sttA'] = QAction(self.tr('Preferences'),self)
        self.A['sttA'].setStatusTip(self.tr('Application settings and preferences'))
        self.A['sttA'].triggered.connect(self.f_settings)

        self.A['escA'] = QAction(self.tr('Exit'),self)
        self.A['escA'].setStatusTip(self.tr('Close the application'))
        self.A['escA'].setShortcuts(['Alt+F4','Esc'])
        self.A['escA'].triggered.connect(self.f_esc)

        self.A['file'].addAction(self.A['newA'])
        self.A['file'].addAction(self.A['opeA'])
        self.A['file'].addAction(self.A['savA'])
        self.A['file'].addAction(self.A['sasA'])
        self.A['file'].addAction(self.A['expA'])
        self.A['file'].addSeparator()
        self.A['file'].addAction(self.A['sttA'])
        self.A['file'].addSeparator()
        self.A['file'].addAction(self.A['escA'])

        # edit

        self.A['undoA'] = QAction(self.tr('Undo'),self)
        self.A['undoA'].setShortcut('Ctrl+Z')
        self.A['undoA'].triggered.connect(self.text.undo)

        self.A['redoA'] = QAction(self.tr('Redo'),self)
        self.A['redoA'].setShortcuts(['Ctrl+Y', 'Ctrl+Shift+Z'])
        self.A['redoA'].triggered.connect(self.text.redo)

        self.A['selaA'] = QAction(self.tr('Select All'),self)
        self.A['selaA'].setShortcut('Ctrl+A')
        self.A['selaA'].triggered.connect(self.text.selectAll)

        self.A['cutA'] = QAction(self.tr('Cut'),self)
        self.A['cutA'].setShortcut('Ctrl+X')
        self.A['cutA'].triggered.connect(self.text.cut)

        self.A['copyA'] = QAction(self.tr('Copy'),self)
        self.A['copyA'].setShortcut('Ctrl+C')
        self.A['copyA'].triggered.connect(self.text.copy)

        self.A['pasteA'] = QAction(self.tr('Paste'),self)
        self.A['pasteA'].setShortcut('Ctrl+V')
        self.A['pasteA'].triggered.connect(self.text.paste)

        self.A['edit'].addAction(self.A['undoA'])
        self.A['edit'].addAction(self.A['redoA'])
        self.A['edit'].addSeparator()
        self.A['edit'].addAction(self.A['selaA'])
        self.A['edit'].addAction(self.A['cutA'])
        self.A['edit'].addAction(self.A['copyA'])
        self.A['edit'].addAction(self.A['pasteA'])

        # view
        self.A['wowA'] = QAction(self.tr('Word Wrap'),self)
        self.A['wowA'].setStatusTip(self.tr('Enable/disable word wrapping'))
        self.A['wowA'].setShortcut('Ctrl+W')
        self.A['wowA'].setCheckable(True)
        self.A['wowA'].toggled.connect(self.v_triggerwow)

        self.A['view'].addAction(self.A['wowA'])

        # about
        self.A['about'] = QAction(self.tr('About...'),self)
        self.A['about'].triggered.connect(self.a_about)

        menubar.addAction(self.A['about'])

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
        if getattr(sys, 'frozen', False):
            subprocess.Popen(sys.executable, shell=False)
        else:
            subprocess.Popen('python '+sys.argv[0], shell=False)

    def f_open(self):
        suggested_name = os.path.join(self.WORK_DIR, '*.*')
        path,ext = QFileDialog.getOpenFileName(
            self,
            self.tr('Open File'),
            self.WORK_DIR,
            ";;".join(self.FILE_FORMATS)
        )
        if not path: return

        self.openFile(path)
        self.updateWindowTitle()

    def f_save(self):
        if self.FILE_OPENED:
            # СОХРАНИТЬ ФАЙЛ С ТЕКУЩИМИ ОПЦИЯМИ
            res = None
            if self.FILE_FORMAT == '.tfe':
                res = self.save_to_tfe(self.FILE_PATH)
            elif self.FILE_FORMAT == '.txt':
                res = self.save_plain_text(self.FILE_PATH)

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
            suggested_name = os.path.join(self.WORK_DIR, self.FILE_NAME)
        else:
            suggested_name = self.FILE_PATH
        path,ext = QFileDialog.getSaveFileName(
            self,
            self.tr('Save File'),
            suggested_name,
            ";;".join(self.FILE_FORMATS)
        )
        if not path: return

        ext = self.FILE_FORMATS[ext]
        _ext = os.path.splitext(path)[1]
        if _ext in self._FILE_FORMATS: ext = _ext

        res = None
        if ext == '.tfe':
            res = self.save_to_tfe(path)
        elif ext == '.txt':
            res = self.save_plain_text(path)

        if res == OK:
            self.saveOk()
        elif res == INTERNAL_ERROR:
            self.saveError(res)
        self.updateWindowTitle()
        return res

    def f_export(self):
        if self.FILE_PATH is None:
            suggested_name = os.path.join(self.WORK_DIR, self.FILE_NAME)
        else:
            suggested_name = os.path.splitext(self.FILE_PATH)[0]
        path,ext = QFileDialog.getSaveFileName(
            self,
            self.tr('Export'),
            suggested_name,
            ";;".join(self.EXPORT_FILE_FORMATS)
        )
        print(path,ext)
        if not path: return

        print(path,ext)
        ext = self.EXPORT_FILE_FORMATS[ext]
        _ext = os.path.splitext(path)[1]
        if _ext in self._EXPORT_FILE_FORMATS: ext = _ext

        res = None
        if ext == '.gpg':
            res = self.export_to_gpg(path)

        if res == OK:
            self.exportOk()
        elif res == NOT_AVAILABLE:
            self.exportError(res)
        elif res == INTERNAL_ERROR:
            self.exportError(res)
        self.updateWindowTitle()
        return res

    def f_settings(self):
        q = MSettingsWindow(self.stt, self).exec()
        self.loadSettings()
        self.loadTranslator()
        self.updateLanguage()

    def f_esc(self):
        self.close()

    def v_triggerwow(self,ena):
        if ena:
            self.text.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        else:
            self.text.setWordWrapMode(QTextOption.NoWrap)

    def a_about(self):
        s = self.tr(\
        "<h1>PyTFE</h1>"\
        "<p>Copyright &copy; 2016 Gleb Getmanenko</p>"\
        "<p>The application allows you to encrypt and save text. "\
        "Text can be saved as TFE file "\
        "or be exported into GPG format using symmetric encryption.<p>"\
        "<a href='https://github.com/MrP4p3r/PyTFE'>GitHub Repository</a>"
        )

        QMessageBox.about(self, self.APP_TITLE,s)

    # ---------- EVENT HANDLERS ----------

    def textChangedHandler(self):
        if self.FILE_SAVED:
            self.FILE_SAVED = False
            self.updateWindowTitle()

    def dragEnterEvent(self, event):
        mime = event.mimeData()
        if mime.hasUrls():
            urls = mime.urls()
            if len(urls) == 1 and urls[0].toLocalFile():
                event.acceptProposedAction()

    def dropEvent(self, event):
        mime = event.mimeData()
        if mime.hasUrls():
            urls = mime.urls()
            self.openFile(urls[0].toLocalFile())

    def closeEvent(self, event):
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
        if event.isAccepted():
            self.exitRoutines()

    def exitRoutines(self):
        self.saveSettings()

    # ---------- OTHER FUNCTIONS ----------

    def openArgFile(self,path):
        res = self.openFile(path)
        if res or res is None:
            sys.exit()

    def openFile(self, path):
        #TODO
        ext = None
        _ext = os.path.splitext(path)[1]
        if _ext in self._FILE_FORMATS: ext = _ext

        if ext is None:
            res = NOT_SUPPORTED
        elif ext == '.tfe':
            res = self.open_from_tfe(path)
        elif ext == '.txt':
            res = self.open_plain_text(path)

        if res == OK:
            self.openOk()
        elif res == INTERNAL_ERROR:
            self.openError(res)
        elif res == NOT_SUPPORTED:
            self.openError(res)

        return res

    def save_to_tfe(self, path):
        if not self.FILE_OPENED:
            d = self.passwordInput()
            d.setLabelText(self.tr('Enter password:'))
            while True:
                # ввод пароля
                if not d.exec(): return
                pas1 = d.textValue()
                if len(pas1) < 4:
                    d.setLabelText(
                        self.tr('Password is too short. Enter password:')
                    )
                    continue
                d.setTextValue('')
                d.setLabelText(self.tr('Repeat password:'))

                # повторный ввод пароля
                if not d.exec(): return
                pas2 = d.textValue()

                # проверка пароля
                if pas1!=pas2:
                    d.setLabelText(
                        self.tr('Passwords do not match. Enter password:')
                    )
                else:
                    break
                d.setTextValue('')
            pas = pas1.encode('utf-8')          # пароль в байтах
            alg = self.DEFAULT_ALGO
        else:
            pas = self.FILE_PASSPHRASE
            alg = self.FILE_ALGO if not self.USE_DEFAULT_ALGO \
                  else self.DEFAULT_ALGO

        s = self.text.toPlainText()
        b = s.encode('utf-8')               # КОДИРОВОЧКА
        bi = BytesIO(b)
        tpath = path + '~'

        with open(tpath, 'wb') as bo:
            res = 0
            try:
                tfe.EncryptBuffer(bi, bo, len(b), pas, alg=alg, hasht="MD5")
            except:
                res = 1
                traceback.print_exc()

        if res == 0:
            os.replace(tpath, path)
            self.fileOpened('.tfe', path, pas, alg)
            return OK
        else:
            os.remove(tpath) # MAY CAUSE PROBLEMS
            return INTERNAL_ERROR

    def open_from_tfe(self, path):
        if not tfe.isTfeFile(path):
            return NOT_SUPPORTED

        alg = tfe.whatAlgoIn(path)

        d = self.passwordInput()
        d.setLabelText(self.tr('Enter password:'))
        while True:
            if not d.exec(): return
            pas1 = d.textValue()
            d.setTextValue('')
            pas = pas1.encode('utf-8')          # байты, байты
            bo  = BytesIO()
            res = 0

            with open(path, 'rb') as bi:
                try: tfe.DecryptBuffer(bi, bo, pas)
                except ValueError:
                    res = 1
                except:
                    res = 2
                    traceback.print_exc()

            #bi.close()
            if res == 0:
                bo.seek(0,0)
                b = bo.read()
                try:
                    s = b.decode('utf-8','replace')           # КОДИРОВОЧКА
                except:
                    traceback.print_exc()
                    res = self.openError(NOT_TEXT)
                    if res == QMessageBox.Yes:
                        try:
                            s = b.decode('ascii')
                        except:
                            traceback.print_exc();
                            return INTERNAL_ERROR
                    else:
                        return
                self.text.setPlainText(s)
                self.fileOpened('.tfe', path, pas, alg)
                return OK
            elif res == 1:
                d.setLabelText(self.tr('Wrong password. Enter password:'))
                continue
            else:
                return INTERNAL_ERROR

    def save_plain_text(self, path):
        s = self.text.toPlainText()
        tpath = path + '~'

        with open(tpath, 'w') as bo:
            res = 0
            try:
                bo.write(s)
            except:
                res = 1
                traceback.print_exc()

        if res == 0:
            os.replace(tpath, path)
            self.fileOpened('.txt', path, None, None)
            return OK
        else:
            os.remove(tpath) # MAY CAUSE PROBLEMS
            return INTERNAL_ERROR

    def open_plain_text(self, path):
        res = 0
        with open(path, 'r') as bi:
            try:
                s = bi.read()
            except:
                res = 2
                traceback.print_exc()

        #bi.close()
        if res == 0:
            self.text.setPlainText(s)
            self.fileOpened('.txt', path, None, None)
            return OK
        else:
            return INTERNAL_ERROR

    def export_to_gpg(self, path):
        if os.system('gpg --version'): return NOT_AVAILABLE
        sym = '-c'
        # раскомментить после добавления ассиметричного шифрования
        # sym = MDialogGPGSym.getSym(self)
        if sym == '-c':
            d = self.passwordInput()
            d.setLabelText(self.tr('Enter password:'))
            while True:
                # ввод пароля
                if not d.exec_(): return
                pas1 = d.textValue()
                d.setTextValue('')
                d.setLabelText(self.tr('Repeat password:'))

                # повторный ввод пароля
                if not d.exec(): return
                pas2 = d.textValue()

                # проверка пароля
                if pas1!=pas2:
                    d.setLabelText(self.tr('Passwords do not match. Enter password:'))
                else:
                    break
                d.setTextValue('')
            #pas = pas1.encode('utf-8')         # пароль в байтах
            pas = pas1
            s = self.text.toPlainText()
            b = s.encode('utf-8')               # КОДИРОВОЧКА
            #bi = BytesIO(b)
            #bo = open(path,'wb')
            res = 0
            print([
                'gpg', '-c', '--no-use-agent', '--passphrase', pas,
                '--batch', '--yes', '-o', path
            ])
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
            except:
                res = 1
                traceback.print_exc()
            if res == 0:
                return OK
            else:
                return INTERNAL_ERROR
        elif sym == '-e':
            # TODO
            #if not self.FILE_OPENED:
            d = QInputDialog(self)
            d.resize(300, d.height())
            d.setTextEchoMode(QLineEdit.Normal)
            d.setWindowTitle(self.tr('Recipient'))
            d.setLabelText(self.tr('Enter recipient:'))
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
                    [ 'gpg', '-e', '--no-use-agent', '-r', name, '-o', path ],
                    stdin = subprocess.PIPE
                )
                p.communicate(b)
                p.terminate()
            except:
                res = 1
                traceback.print_exc()
            #bo.close()
            if res == 0:
                # TODO
                return OK
            else:
                return INTERNAL_ERROR

    def open_from_gpg(self, path):
        # ['gpg', '--no-use-agent', '--batch', '--yes', '-d', path] # symmetric
        # ['gpg', '--no-use-agent', '--batch', '--yes ????????????
        ...

    # ---------- NOTIFIERS ----------

    def saveOk(self):
        self.statusBar().showMessage(self.tr('Saved'), 1500)

    def saveError(self, er):
        if er == INTERNAL_ERROR:
            QMessageBox.critical(
                self,
                self.tr('Error'),
                self.tr('Internal exception occurred while saving the file')
            )

    def openOk(self):
        self.statusBar().showMessage(self.tr('File opened'), 1500) #?
        self.updateWindowTitle()

    def openError(self, er):
        if er == INTERNAL_ERROR:
            QMessageBox.critical(
                self,
                self.tr('Error'),
                self.tr('Internal exception occurred while opening the file')
            )
        elif er == NOT_SUPPORTED:
            QMessageBox.critical(
                self,
                self.tr('Error'),
                self.tr('This file format is not supported or file is corrupted')
            )
        elif er == NOT_TEXT:
            res = QMessageBox.question(
                self,
                self.tr('Error'),
                self.tr('Decrypted data is not text. Continue?')
            )
            return res

    def exportOk(self):
        self.statusBar().showMessage(self.tr('Saved'), 1500)

    def exportError(self, er):
        if er == INTERNAL_ERROR:
            QMessageBox.critical(
                self,
                self.tr('Error'),
                self.tr('Internal exception occured while exporting the file')
            )
        elif er == NOT_AVAILABLE:
            QMessageBox.critical(
                self,
                self.tr('Error'),
                self.tr('Export to this external format is not available')
            )


    def saveFileQuestion(self):
        res = QMessageBox.question(
            self,
            self.tr('File Not Saved'),
            self.tr('Save changes to %s?')%self.FILE_NAME,
            buttons = QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )
        return res

    def passwordInput(self):
        d = QInputDialog(self)
        d.resize(300, d.height())
        d.setTextEchoMode(QLineEdit.Password)
        d.setWindowTitle(self.tr('Password'))
        return d

    def fileOpened(self, format, path, pas, alg):
        self.FILE_FORMAT     = format
        self.FILE_PATH       = path
        self.WORK_DIR,self.FILE_NAME = os.path.split(path)
        self.FILE_PASSPHRASE = pas
        self.FILE_ALGO       = alg
        self.FILE_OPENED     = True
        self.FILE_SAVED      = True

# ---------- ВИДЖЕТЫ ДЛЯ СОХРАНЕНИЯ ФАЙЛОВ ----------

class MRadioButton(QRadioButton):
    clicked = pyqtSignal(object)

    def __init__(self, text, rvalue, *args):
        super().__init__(text, *args)
        super().clicked.connect(self._valueEmitter)
        self.rvalue = rvalue

    def _valueEmitter(self, b):
        self.clicked.emit(self.rvalue)

class MDialogGPGSym(QDialog):
    sym = None

    def __init__(self, *args):
        super().__init__(*args)
        self.setWindowFlags(self.windowFlags()&~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(self.tr('GPG'))
        lo = QGridLayout(self)

        self.lab = QLabel()
        self.lab.setText(self.tr('Encryption algorithm'))

        r_Group = QButtonGroup()
        r_symm = MRadioButton(self.tr('Symmetric'), '-c')
        r_asym = MRadioButton(self.tr('Asymmetric'), '-e')
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
        if dialog.exec():
            return dialog.sym
        else:
            return None
