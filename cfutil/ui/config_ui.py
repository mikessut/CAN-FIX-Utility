# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'config.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dialogConfig(object):
    def setupUi(self, dialogConfig):
        dialogConfig.setObjectName("dialogConfig")
        dialogConfig.resize(338, 170)
        self.verticalLayout = QtWidgets.QVBoxLayout(dialogConfig)
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelConfig = QtWidgets.QLabel(dialogConfig)
        self.labelConfig.setObjectName("labelConfig")
        self.verticalLayout.addWidget(self.labelConfig)
        self.scrollArea = QtWidgets.QScrollArea(dialogConfig)
        self.scrollArea.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 322, 90))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.formLayout = QtWidgets.QFormLayout(self.scrollAreaWidgetContents)
        self.formLayout.setObjectName("formLayout")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.buttonBox = QtWidgets.QDialogButtonBox(dialogConfig)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(dialogConfig)
        self.buttonBox.accepted.connect(dialogConfig.accept)
        self.buttonBox.rejected.connect(dialogConfig.reject)
        self.buttonBox.clicked['QAbstractButton*'].connect(dialogConfig.btnClick)
        QtCore.QMetaObject.connectSlotsByName(dialogConfig)

    def retranslateUi(self, dialogConfig):
        _translate = QtCore.QCoreApplication.translate
        dialogConfig.setWindowTitle(_translate("dialogConfig", "Configuration"))
        self.labelConfig.setText(_translate("dialogConfig", "TextLabel"))

