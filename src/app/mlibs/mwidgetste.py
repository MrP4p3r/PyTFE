# from PySide.QtWidgets import *
from PySide.QtGui     import *
from PySide.QtCore    import *

from . import tfe
from .defaultvalues   import *
from .commonfunctions import *

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

class MComboBox(QWidget):
    i1 = True

    def __init__(self, lbl, lst, dval, *args):
        super().__init__(*args)
        self.setLayout(QGridLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.a = QLabel()
        self.a.setText(lbl)
        self.a.setFixedWidth(150)
        self.b = QComboBox()

        if len(lst) > 0:
            if len(lst[0]) == 2:
                self.i1 = False
                for i,j in lst: self.b.addItem(i, j)
            else:
                self.i1 = True
                for i in lst: self.b.addItem(i)

        if self.i1:
            self.b.setCurrentIndex(self.b.findText(dval))
        else:
            self.b.setCurrentIndex(self.b.findData(dval))

        self.layout().addWidget(self.a, 1, 1)
        self.layout().addWidget(self.b, 1, 2)

    def getval(self):
        if self.i1:
            return self.b.currentText()
        else:
            print(self.b.itemData(self.b.currentIndex()))
            return self.b.itemData(self.b.currentIndex())

class MCheckBox(QCheckBox):

    def __init__(self, lbl, dval, *args):
        super().__init__(*args)
        self.setText(lbl)
        self.setChecked(dval)

    def getval(self):
        return self.isChecked()

class MColorBox(QWidget):

    def __init__(self, lbl, dval, *args):
        super().__init__(*args)
        self.setLayout(QGridLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.a = QLabel()
        self.a.setText(lbl)
        self.a.setFixedWidth(150)
        self.b = QLineEdit()
        self.b.setText(dval)
        self.b.setEnabled(False)
        self.c = QPushButton()
        self.setbuttoncolor()

        self.c.clicked.connect(self.newcolor)

        self.layout().addWidget(self.a, 1, 1)
        self.layout().addWidget(self.b, 1, 2)
        self.layout().addWidget(self.c, 1, 3)

    def setbuttoncolor(self):
        self.c.setStyleSheet('background: %s'%self.b.text())

    def newcolor(self):
        col = QColorDialog.getColor(
            QColor(self.b.text()),
            self,
            self.tr('Select color')
        )
        if col.isValid():
            self.b.setText(col.name())
            self.setbuttoncolor()

    def getval(self):
        return self.b.text()

class MFontBox(QWidget):

    def __init__(self, lbl, dval, *args):
        super().__init__(*args)
        self.setLayout(QGridLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.a = QLabel()
        self.a.setText(lbl)
        self.a.setFixedWidth(150)
        self.b = QLineEdit()
        self.val = dval
        self.updateb()
        self.b.setEnabled(False)
        self.c = QPushButton()

        self.c.clicked.connect(self.newfont)

        self.layout().addWidget(self.a, 1, 1)
        self.layout().addWidget(self.b, 1, 2)
        self.layout().addWidget(self.c, 1, 3)

    def newfont(self):
        font,ok = QFontDialog.getFont(QFont(*self.val), self)
        if ok:
            self.val = (font.family(), font.pointSize())
        else:
            pass
        self.updateb()

    def updateb(self):
        self.b.setText('%s, %i'%self.val)
        self.b.setFont(QFont(*self.val))

    def getval(self):
        return self.val

class MSettingsWindow(QDialog):

    def __init__(self,stt,*args):
        super().__init__(*args)
        self.stt = stt
        self.setWindowFlags(self.windowFlags()&~Qt.WindowContextHelpButtonHint)
        self.initUI()

    def initUI(self):
        self.setFixedWidth(420)
        self.setFixedHeight(315)
        self.setWindowTitle(self.tr('Settings and preferences'))
        self.setLayout(QGridLayout())
        tabs = QTabWidget()
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Apply  | \
            QDialogButtonBox.Cancel | \
            QDialogButtonBox.RestoreDefaults,
            Qt.Horizontal
        )
        self.layout().addWidget(tabs)
        self.layout().addWidget(self.buttons)

        # APPLICATION SETTINGS
        APP = QWidget()
        lo = QVBoxLayout()
        APP.setLayout(lo)
        a = MComboBox(
            self.tr('Default algorithm'),
            [ x for x in tfe.algtab ],
            self.stt.value('app/default_algo',DEFAULT_APP_DEFAULT_ALGO)
        )
        b = MCheckBox(
            self.tr('Always save file using default algorithm'),
            mbool(self.stt.value('app/use_default_algo',
                                 DEFAULT_APP_USE_DEFAULT_ALGO))
        )
        lo.addWidget(a)
        lo.addWidget(b)
        lo.addStretch()
        self.opts = dict()
        self.opts['app/default_algo'] = a
        self.opts['app/use_default_algo'] = b

        # EDITOR SETTINGS
        EDT = QWidget()
        lo = QVBoxLayout()
        EDT.setLayout(lo)
        l = MComboBox(
            self.tr('Language'),
            [
                (
                    self.tr(QLocale.languageToString(
                        QLocale.Language(QLocale.Russian)
                    )),
                    QLocale.Language(QLocale.Russian)
                ),
                (
                    self.tr(QLocale.languageToString(
                        QLocale.Language(QLocale.English)
                    )),
                    QLocale.Language(QLocale.English)
                )
            ],
            QLocale.Language(int(self.stt.value('locale/locale', QLocale.English)))
        )
        c = MColorBox(
            self.tr('Background color'),
            self.stt.value('text/base', DEFAULT_TEXT_BASE_C)
        )
        d = MColorBox(
            self.tr('Text color'),
            self.stt.value('text/text', DEFAULT_TEXT_TEXT_C)
        )
        e = MColorBox(
            self.tr('Selection color'),
            self.stt.value('text/highlight', DEFAULT_TEXT_HIGHLIGHT_C)
        )
        f = MColorBox(
            self.tr('Selected text color'),
            self.stt.value('text/highlighttext', DEFAULT_TEXT_HIGHLIGHTTEXT_C)
        )
        g = MFontBox(
            self.tr('Font'),
            (
                self.stt.value('text/fontfamily', DEFAULT_TEXT_FONTFAMILY),
                int(self.stt.value('text/fontsize', DEFAULT_TEXT_FONTSIZE))
            )
        )

        lo.addWidget(l)
        lo.addWidget(c)
        lo.addWidget(d)
        lo.addWidget(e)
        lo.addWidget(f)
        lo.addWidget(g)
        lo.addStretch()

        tabs.addTab(APP, self.tr('Application'))
        tabs.addTab(EDT, self.tr('Editor'))

        self.opts['locale/locale'] = l
        self.opts['text/base'] = c
        self.opts['text/text'] = d
        self.opts['text/highlight'] = e
        self.opts['text/highlighttext'] = f
        self.opts['text/font(family,size)'] = g
        self.buttons.clicked.connect(self.buttonsClicked)

    def buttonsClicked(self, btn):
        if btn == self.buttons.button(QDialogButtonBox.Apply):
            self.applySettings()
            self.accept()
        elif btn == self.buttons.button(QDialogButtonBox.Cancel):
            self.reject()
        elif btn == self.buttons.button(QDialogButtonBox.RestoreDefaults):
            self.resetSettings()
            self.accept()

    def applySettings(self):
        self.stt.setValue('app/default_algo',
                          self.opts['app/default_algo'].getval())
        self.stt.setValue('app/use_default_algo',
                          self.opts['app/use_default_algo'].getval())
        self.stt.setValue('text/base',self.opts['text/base'].getval())
        self.stt.setValue('text/text',self.opts['text/text'].getval())
        self.stt.setValue('text/highlight',self.opts['text/highlight'].getval())
        self.stt.setValue('text/highlighttext',
                          self.opts['text/highlighttext'].getval())
        a,b = self.opts['text/font(family,size)'].getval()
        self.stt.setValue('text/fontfamily',a)
        self.stt.setValue('text/fontsize',b)
        self.stt.setValue('locale/locale',self.opts['locale/locale'].getval())

    def resetSettings(self):
        res = QMessageBox.question(
            self,self.tr('Restore Defaults'),
            self.tr('You are going to reset settings to defaults. Continue?'),
            buttons = QMessageBox.Yes | QMessageBox.No
        )
        if res == QMessageBox.Yes:
            self.stt.setValue('app/default_algo',
                              DEFAULT_APP_DEFAULT_ALGO)
            self.stt.setValue('app/use_default_algo',
                              DEFAULT_APP_USE_DEFAULT_ALGO)
            self.stt.setValue('text/base',
                              DEFAULT_TEXT_BASE_C)
            self.stt.setValue('text/text',
                              DEFAULT_TEXT_TEXT_C)
            self.stt.setValue('text/highlight',
                              DEFAULT_TEXT_HIGHLIGHT_C)
            self.stt.setValue('text/highlighttext',
                              DEFAULT_TEXT_HIGHLIGHTTEXT_C)
            self.stt.setValue('text/fontfamily',
                              DEFAULT_TEXT_FONTFAMILY)
            self.stt.setValue('text/fontsize',
                              DEFAULT_TEXT_FONTSIZE)
            self.stt.setValue('locale/locale',
                              QLocale.English)
