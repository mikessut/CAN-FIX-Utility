# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'firmware.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dialogFirmware(object):
    def setupUi(self, dialogFirmware):
        dialogFirmware.setObjectName("dialogFirmware")
        dialogFirmware.resize(345, 282)
        self.verticalLayout = QtWidgets.QVBoxLayout(dialogFirmware)
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelFile = QtWidgets.QLabel(dialogFirmware)
        self.labelFile.setObjectName("labelFile")
        self.verticalLayout.addWidget(self.labelFile)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.editFile = QtWidgets.QLineEdit(dialogFirmware)
        self.editFile.setObjectName("editFile")
        self.horizontalLayout.addWidget(self.editFile)
        self.btnFile = QtWidgets.QPushButton(dialogFirmware)
        self.btnFile.setObjectName("btnFile")
        self.horizontalLayout.addWidget(self.btnFile)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 1, 1, 1)
        self.labelDevice = QtWidgets.QLabel(dialogFirmware)
        self.labelDevice.setObjectName("labelDevice")
        self.gridLayout.addWidget(self.labelDevice, 0, 0, 1, 1)
        self.comboNode = QtWidgets.QComboBox(dialogFirmware)
        self.comboNode.setObjectName("comboNode")
        self.gridLayout.addWidget(self.comboNode, 1, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.labelStatus = QtWidgets.QLabel(dialogFirmware)
        self.labelStatus.setObjectName("labelStatus")
        self.verticalLayout.addWidget(self.labelStatus)
        self.progressBar = QtWidgets.QProgressBar(dialogFirmware)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.buttonBox = QtWidgets.QDialogButtonBox(dialogFirmware)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.labelFile.setBuddy(self.editFile)
        self.labelDevice.setBuddy(self.comboNode)

        self.retranslateUi(dialogFirmware)
        self.buttonBox.rejected.connect(dialogFirmware.reject)
        self.btnFile.clicked.connect(dialogFirmware.btnFileClick)
        self.buttonBox.clicked['QAbstractButton*'].connect(dialogFirmware.btnClick)
        QtCore.QMetaObject.connectSlotsByName(dialogFirmware)
        dialogFirmware.setTabOrder(self.buttonBox, self.editFile)
        dialogFirmware.setTabOrder(self.editFile, self.btnFile)
        dialogFirmware.setTabOrder(self.btnFile, self.comboNode)

    def retranslateUi(self, dialogFirmware):
        _translate = QtCore.QCoreApplication.translate
        dialogFirmware.setWindowTitle(_translate("dialogFirmware", "Upload Firmware"))
        self.labelFile.setText(_translate("dialogFirmware", "&File"))
        self.btnFile.setText(_translate("dialogFirmware", "..."))
        self.labelDevice.setText(_translate("dialogFirmware", "Node"))
        self.labelStatus.setText(_translate("dialogFirmware", "<<Status>>"))

