# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'connect.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ConnectDialog(object):
    def setupUi(self, ConnectDialog):
        ConnectDialog.setObjectName("ConnectDialog")
        ConnectDialog.resize(263, 349)
        self.verticalLayout = QtWidgets.QVBoxLayout(ConnectDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.labelAdapter = QtWidgets.QLabel(ConnectDialog)
        self.labelAdapter.setObjectName("labelAdapter")
        self.verticalLayout_3.addWidget(self.labelAdapter)
        self.comboAdapter = QtWidgets.QComboBox(ConnectDialog)
        self.comboAdapter.setObjectName("comboAdapter")
        self.verticalLayout_3.addWidget(self.comboAdapter)
        self.labelChannel = QtWidgets.QLabel(ConnectDialog)
        self.labelChannel.setObjectName("labelChannel")
        self.verticalLayout_3.addWidget(self.labelChannel)
        self.comboChannel = QtWidgets.QComboBox(ConnectDialog)
        self.comboChannel.setEditable(True)
        self.comboChannel.setObjectName("comboChannel")
        self.verticalLayout_3.addWidget(self.comboChannel)
        self.groupBitrate = QtWidgets.QGroupBox(ConnectDialog)
        self.groupBitrate.setEnabled(False)
        self.groupBitrate.setObjectName("groupBitrate")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBitrate)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.radio125 = QtWidgets.QRadioButton(self.groupBitrate)
        self.radio125.setChecked(True)
        self.radio125.setObjectName("radio125")
        self.verticalLayout_2.addWidget(self.radio125)
        self.radio250 = QtWidgets.QRadioButton(self.groupBitrate)
        self.radio250.setObjectName("radio250")
        self.verticalLayout_2.addWidget(self.radio250)
        self.radio500 = QtWidgets.QRadioButton(self.groupBitrate)
        self.radio500.setObjectName("radio500")
        self.verticalLayout_2.addWidget(self.radio500)
        self.radio1000 = QtWidgets.QRadioButton(self.groupBitrate)
        self.radio1000.setObjectName("radio1000")
        self.verticalLayout_2.addWidget(self.radio1000)
        self.verticalLayout_3.addWidget(self.groupBitrate)
        self.verticalLayout.addLayout(self.verticalLayout_3)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(ConnectDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.labelAdapter.setBuddy(self.comboAdapter)
        self.labelChannel.setBuddy(self.comboChannel)

        self.retranslateUi(ConnectDialog)
        self.buttonBox.accepted.connect(ConnectDialog.accept)
        self.buttonBox.rejected.connect(ConnectDialog.reject)
        self.comboAdapter.currentIndexChanged['int'].connect(ConnectDialog.interfaceChange)
        QtCore.QMetaObject.connectSlotsByName(ConnectDialog)

    def retranslateUi(self, ConnectDialog):
        _translate = QtCore.QCoreApplication.translate
        ConnectDialog.setWindowTitle(_translate("ConnectDialog", "CANBus Connect"))
        self.labelAdapter.setText(_translate("ConnectDialog", "CAN I&nterface"))
        self.labelChannel.setText(_translate("ConnectDialog", "&Channel"))
        self.groupBitrate.setTitle(_translate("ConnectDialog", "&Bitrate"))
        self.radio125.setText(_translate("ConnectDialog", "&125 Kbps"))
        self.radio250.setText(_translate("ConnectDialog", "&250 Kbps"))
        self.radio500.setText(_translate("ConnectDialog", "&500 Kbps"))
        self.radio1000.setText(_translate("ConnectDialog", "1&000 Kbps"))

