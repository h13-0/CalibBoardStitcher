# Form implementation generated from reading ui file 'CalibBoardStitcher.ui'
#
# Created by: PyQt6 UI code generator 6.8.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_CalibBoardStitcher(object):
    def setupUi(self, CalibBoardStitcher):
        CalibBoardStitcher.setObjectName("CalibBoardStitcher")
        CalibBoardStitcher.resize(1080, 780)
        CalibBoardStitcher.setMinimumSize(QtCore.QSize(1080, 720))
        self.centralWidget = QtWidgets.QWidget(parent=CalibBoardStitcher)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralWidget.sizePolicy().hasHeightForWidth())
        self.centralWidget.setSizePolicy(sizePolicy)
        self.centralWidget.setMinimumSize(QtCore.QSize(1080, 720))
        self.centralWidget.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.centralWidget.setObjectName("centralWidget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.centralWidget)
        self.horizontalLayout_3.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mainGraphicView = QtWidgets.QGraphicsView(parent=self.centralWidget)
        self.mainGraphicView.setObjectName("mainGraphicView")
        self.verticalLayout.addWidget(self.mainGraphicView)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(5, 0, 5, -1)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.funcTabView = QtWidgets.QTabWidget(parent=self.centralWidget)
        self.funcTabView.setMinimumSize(QtCore.QSize(320, 0))
        self.funcTabView.setMaximumSize(QtCore.QSize(16777215, 240))
        self.funcTabView.setObjectName("funcTabView")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.genCalibBoardImageButton = QtWidgets.QPushButton(parent=self.tab)
        self.genCalibBoardImageButton.setGeometry(QtCore.QRect(10, 170, 295, 30))
        self.genCalibBoardImageButton.setObjectName("genCalibBoardImageButton")
        self.label_3 = QtWidgets.QLabel(parent=self.tab)
        self.label_3.setGeometry(QtCore.QRect(10, 10, 150, 30))
        self.label_3.setObjectName("label_3")
        self.rowCountSpinBox = QtWidgets.QSpinBox(parent=self.tab)
        self.rowCountSpinBox.setGeometry(QtCore.QRect(220, 50, 85, 30))
        self.rowCountSpinBox.setMinimumSize(QtCore.QSize(85, 30))
        self.rowCountSpinBox.setMaximum(999)
        self.rowCountSpinBox.setProperty("value", 30)
        self.rowCountSpinBox.setObjectName("rowCountSpinBox")
        self.colCountSpinBox = QtWidgets.QSpinBox(parent=self.tab)
        self.colCountSpinBox.setGeometry(QtCore.QRect(220, 10, 85, 30))
        self.colCountSpinBox.setMinimumSize(QtCore.QSize(85, 30))
        self.colCountSpinBox.setMaximum(999)
        self.colCountSpinBox.setProperty("value", 40)
        self.colCountSpinBox.setObjectName("colCountSpinBox")
        self.label_2 = QtWidgets.QLabel(parent=self.tab)
        self.label_2.setGeometry(QtCore.QRect(10, 50, 150, 30))
        self.label_2.setObjectName("label_2")
        self.label_4 = QtWidgets.QLabel(parent=self.tab)
        self.label_4.setGeometry(QtCore.QRect(10, 130, 150, 30))
        self.label_4.setObjectName("label_4")
        self.qrPixelSizeSpinBox = QtWidgets.QSpinBox(parent=self.tab)
        self.qrPixelSizeSpinBox.setGeometry(QtCore.QRect(220, 90, 85, 30))
        self.qrPixelSizeSpinBox.setMinimumSize(QtCore.QSize(85, 30))
        self.qrPixelSizeSpinBox.setMaximum(20)
        self.qrPixelSizeSpinBox.setProperty("value", 7)
        self.qrPixelSizeSpinBox.setObjectName("qrPixelSizeSpinBox")
        self.qrBoarderSpinBox = QtWidgets.QSpinBox(parent=self.tab)
        self.qrBoarderSpinBox.setGeometry(QtCore.QRect(220, 130, 85, 30))
        self.qrBoarderSpinBox.setMinimumSize(QtCore.QSize(85, 30))
        self.qrBoarderSpinBox.setMinimum(1)
        self.qrBoarderSpinBox.setMaximum(20)
        self.qrBoarderSpinBox.setProperty("value", 3)
        self.qrBoarderSpinBox.setObjectName("qrBoarderSpinBox")
        self.label_5 = QtWidgets.QLabel(parent=self.tab)
        self.label_5.setGeometry(QtCore.QRect(10, 90, 150, 30))
        self.label_5.setObjectName("label_5")
        self.funcTabView.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.loadSubImageSequenceButton = QtWidgets.QPushButton(parent=self.tab_2)
        self.loadSubImageSequenceButton.setGeometry(QtCore.QRect(210, 10, 95, 30))
        self.loadSubImageSequenceButton.setObjectName("loadSubImageSequenceButton")
        self.lineEdit_2 = QtWidgets.QLineEdit(parent=self.tab_2)
        self.lineEdit_2.setEnabled(False)
        self.lineEdit_2.setGeometry(QtCore.QRect(10, 10, 190, 30))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.execAutoMatchButton = QtWidgets.QPushButton(parent=self.tab_2)
        self.execAutoMatchButton.setGeometry(QtCore.QRect(10, 90, 295, 30))
        self.execAutoMatchButton.setObjectName("execAutoMatchButton")
        self.stitchMethodComboBox = QtWidgets.QComboBox(parent=self.tab_2)
        self.stitchMethodComboBox.setGeometry(QtCore.QRect(10, 170, 190, 30))
        self.stitchMethodComboBox.setObjectName("stitchMethodComboBox")
        self.importCalibResultButton = QtWidgets.QPushButton(parent=self.tab_2)
        self.importCalibResultButton.setGeometry(QtCore.QRect(210, 50, 95, 30))
        self.importCalibResultButton.setObjectName("importCalibResultButton")
        self.lineEdit_3 = QtWidgets.QLineEdit(parent=self.tab_2)
        self.lineEdit_3.setEnabled(False)
        self.lineEdit_3.setGeometry(QtCore.QRect(10, 50, 190, 30))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.label_7 = QtWidgets.QLabel(parent=self.tab_2)
        self.label_7.setGeometry(QtCore.QRect(10, 130, 295, 30))
        self.label_7.setObjectName("label_7")
        self.importCalibResultButton_2 = QtWidgets.QPushButton(parent=self.tab_2)
        self.importCalibResultButton_2.setGeometry(QtCore.QRect(210, 170, 95, 30))
        self.importCalibResultButton_2.setObjectName("importCalibResultButton_2")
        self.funcTabView.addTab(self.tab_2, "")
        self.verticalLayout_2.addWidget(self.funcTabView)
        self.label = QtWidgets.QLabel(parent=self.centralWidget)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.tableWidget = QtWidgets.QTableWidget(parent=self.centralWidget)
        self.tableWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        self.tableWidget.verticalHeader().setDefaultSectionSize(64)
        self.verticalLayout_2.addWidget(self.tableWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(5, 0, 5, 0)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_6 = QtWidgets.QLabel(parent=self.centralWidget)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout.addWidget(self.label_6)
        self.progressBar = QtWidgets.QProgressBar(parent=self.centralWidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.horizontalLayout.addWidget(self.progressBar)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.saveCalibResultButton = QtWidgets.QPushButton(parent=self.centralWidget)
        self.saveCalibResultButton.setMinimumSize(QtCore.QSize(0, 30))
        self.saveCalibResultButton.setObjectName("saveCalibResultButton")
        self.verticalLayout_2.addWidget(self.saveCalibResultButton)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        self.horizontalLayout_3.setStretch(0, 3)
        CalibBoardStitcher.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(parent=CalibBoardStitcher)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1080, 21))
        self.menuBar.setObjectName("menuBar")
        CalibBoardStitcher.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(parent=CalibBoardStitcher)
        self.mainToolBar.setObjectName("mainToolBar")
        CalibBoardStitcher.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, self.mainToolBar)
        self.actionDEBUG = QtGui.QAction(parent=CalibBoardStitcher)
        self.actionDEBUG.setObjectName("actionDEBUG")
        self.actionINFO = QtGui.QAction(parent=CalibBoardStitcher)
        self.actionINFO.setObjectName("actionINFO")

        self.retranslateUi(CalibBoardStitcher)
        self.funcTabView.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(CalibBoardStitcher)

    def retranslateUi(self, CalibBoardStitcher):
        _translate = QtCore.QCoreApplication.translate
        CalibBoardStitcher.setWindowTitle(_translate("CalibBoardStitcher", "CalibBoardStitcher"))
        self.genCalibBoardImageButton.setText(_translate("CalibBoardStitcher", "生成标定板图像"))
        self.label_3.setText(_translate("CalibBoardStitcher", "棋盘格列数（宽度方向）："))
        self.label_2.setText(_translate("CalibBoardStitcher", "棋盘格行数（高度方向）："))
        self.label_4.setText(_translate("CalibBoardStitcher", "二维码边框大小："))
        self.label_5.setText(_translate("CalibBoardStitcher", "二维码像素点大小："))
        self.funcTabView.setTabText(self.funcTabView.indexOf(self.tab), _translate("CalibBoardStitcher", "标定板生成"))
        self.loadSubImageSequenceButton.setText(_translate("CalibBoardStitcher", "加载子图像序列"))
        self.execAutoMatchButton.setText(_translate("CalibBoardStitcher", "执行自动匹配"))
        self.importCalibResultButton.setText(_translate("CalibBoardStitcher", "导入标定结果"))
        self.label_7.setText(_translate("CalibBoardStitcher", "选择拼接方式（仅影响预览，不影响自动匹配）："))
        self.importCalibResultButton_2.setText(_translate("CalibBoardStitcher", "更新拼接方式"))
        self.funcTabView.setTabText(self.funcTabView.indexOf(self.tab_2), _translate("CalibBoardStitcher", "标定板标定"))
        self.label.setText(_translate("CalibBoardStitcher", "子图像序列"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("CalibBoardStitcher", "图像ID"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("CalibBoardStitcher", "使能"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("CalibBoardStitcher", "图像"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("CalibBoardStitcher", "顶点对"))
        self.label_6.setText(_translate("CalibBoardStitcher", "运行进度："))
        self.saveCalibResultButton.setText(_translate("CalibBoardStitcher", "保存标定结果"))
        self.actionDEBUG.setText(_translate("CalibBoardStitcher", "DEBUG"))
        self.actionINFO.setText(_translate("CalibBoardStitcher", "INFO"))
