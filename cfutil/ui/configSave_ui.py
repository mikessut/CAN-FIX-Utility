# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'configSave.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ConfigSaveDialog(object):
    def setupUi(self, ConfigSaveDialog):
        ConfigSaveDialog.setObjectName("ConfigSaveDialog")
        ConfigSaveDialog.resize(380, 398)
        self.verticalLayout = QtWidgets.QVBoxLayout(ConfigSaveDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelNodeName = QtWidgets.QLabel(ConfigSaveDialog)
        self.labelNodeName.setObjectName("labelNodeName")
        self.verticalLayout.addWidget(self.labelNodeName)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.labelNode = QtWidgets.QLabel(ConfigSaveDialog)
        self.labelNode.setObjectName("labelNode")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.labelNode)
        self.spinBoxNode = QtWidgets.QSpinBox(ConfigSaveDialog)
        self.spinBoxNode.setMinimum(1)
        self.spinBoxNode.setMaximum(255)
        self.spinBoxNode.setObjectName("spinBoxNode")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.spinBoxNode)
        self.label_2 = QtWidgets.QLabel(ConfigSaveDialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.labelDevice = QtWidgets.QLabel(ConfigSaveDialog)
        self.labelDevice.setObjectName("labelDevice")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.labelDevice)
        self.label_5 = QtWidgets.QLabel(ConfigSaveDialog)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.labelModel = QtWidgets.QLabel(ConfigSaveDialog)
        self.labelModel.setObjectName("labelModel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.labelModel)
        self.label_7 = QtWidgets.QLabel(ConfigSaveDialog)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.labelVersion = QtWidgets.QLabel(ConfigSaveDialog)
        self.labelVersion.setObjectName("labelVersion")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.labelVersion)
        self.labelStart = QtWidgets.QLabel(ConfigSaveDialog)
        self.labelStart.setObjectName("labelStart")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.labelStart)
        self.spinBoxStart = QtWidgets.QSpinBox(ConfigSaveDialog)
        self.spinBoxStart.setMaximum(65535)
        self.spinBoxStart.setObjectName("spinBoxStart")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.spinBoxStart)
        self.labelLast = QtWidgets.QLabel(ConfigSaveDialog)
        self.labelLast.setObjectName("labelLast")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.labelLast)
        self.spinBoxLast = QtWidgets.QSpinBox(ConfigSaveDialog)
        self.spinBoxLast.setMaximum(65535)
        self.spinBoxLast.setObjectName("spinBoxLast")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.spinBoxLast)
        self.verticalLayout.addLayout(self.formLayout)
        self.label_11 = QtWidgets.QLabel(ConfigSaveDialog)
        self.label_11.setObjectName("label_11")
        self.verticalLayout.addWidget(self.label_11)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEditFileName = QtWidgets.QLineEdit(ConfigSaveDialog)
        self.lineEditFileName.setObjectName("lineEditFileName")
        self.horizontalLayout.addWidget(self.lineEditFileName)
        self.buttonFile = QtWidgets.QToolButton(ConfigSaveDialog)
        self.buttonFile.setObjectName("buttonFile")
        self.horizontalLayout.addWidget(self.buttonFile)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.labelStatus = QtWidgets.QLabel(ConfigSaveDialog)
        self.labelStatus.setObjectName("labelStatus")
        self.verticalLayout.addWidget(self.labelStatus)
        self.progressBar = QtWidgets.QProgressBar(ConfigSaveDialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(ConfigSaveDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Close|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ConfigSaveDialog)
        self.spinBoxNode.valueChanged['int'].connect(ConfigSaveDialog.nodeChange)
        self.buttonBox.clicked['QAbstractButton*'].connect(ConfigSaveDialog.btnClick)
        self.buttonFile.clicked.connect(ConfigSaveDialog.btnFileClick)
        QtCore.QMetaObject.connectSlotsByName(ConfigSaveDialog)

    def retranslateUi(self, ConfigSaveDialog):
        _translate = QtCore.QCoreApplication.translate
        ConfigSaveDialog.setWindowTitle(_translate("ConfigSaveDialog", "Dialog"))
        self.labelNodeName.setText(_translate("ConfigSaveDialog", "Device Name"))
        self.labelNode.setText(_translate("ConfigSaveDialog", "Node Number:"))
        self.label_2.setText(_translate("ConfigSaveDialog", "Device ID:"))
        self.labelDevice.setText(_translate("ConfigSaveDialog", "Unknown"))
        self.label_5.setText(_translate("ConfigSaveDialog", "Model Number:"))
        self.labelModel.setText(_translate("ConfigSaveDialog", "Unknown"))
        self.label_7.setText(_translate("ConfigSaveDialog", "Version:"))
        self.labelVersion.setText(_translate("ConfigSaveDialog", "Unknown"))
        self.labelStart.setText(_translate("ConfigSaveDialog", "Start Configuration Key:"))
        self.labelLast.setText(_translate("ConfigSaveDialog", "Last Configuration Key:"))
        self.label_11.setText(_translate("ConfigSaveDialog", "File Name"))
        self.buttonFile.setText(_translate("ConfigSaveDialog", "..."))
        self.labelStatus.setText(_translate("ConfigSaveDialog", "TextLabel"))
