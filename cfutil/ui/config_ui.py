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
        dialogConfig.resize(459, 339)
        self.verticalLayout = QtWidgets.QVBoxLayout(dialogConfig)
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelNode = QtWidgets.QLabel(dialogConfig)
        self.labelNode.setObjectName("labelNode")
        self.verticalLayout.addWidget(self.labelNode)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.listWidget = QtWidgets.QListWidget(dialogConfig)
        self.listWidget.setObjectName("listWidget")
        self.horizontalLayout.addWidget(self.listWidget)
        self.scrollArea = QtWidgets.QScrollArea(dialogConfig)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 179, 257))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(dialogConfig)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(dialogConfig)
        self.buttonBox.accepted.connect(dialogConfig.accept)
        self.buttonBox.rejected.connect(dialogConfig.reject)
        QtCore.QMetaObject.connectSlotsByName(dialogConfig)

    def retranslateUi(self, dialogConfig):
        _translate = QtCore.QCoreApplication.translate
        dialogConfig.setWindowTitle(_translate("dialogConfig", "Configuration"))
        self.labelNode.setText(_translate("dialogConfig", "TextLabel"))

