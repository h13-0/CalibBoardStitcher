import logging
from enum import Enum
from types import MethodType

import cv2.typing
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QGraphicsPixmapItem, QSpinBox, QMainWindow, QWidget, QGraphicsScene

from QtUI.Ui_CalibBoardStitcher import Ui_CalibBoardStitcher

class ButtonClickedEvent(Enum):
    GEN_CALIB_BOARD_IMG_BTN_CLICKED = 1
    LOAD_SUB_IMG_SEQ_BTN_CLICKED = 2
    IMPORT_CALIB_RESULT_BTN_CLICKED = 3
    SAVE_CALIB_RESULT_BUTTON = 4

class CalibBoardStitcherUI(Ui_CalibBoardStitcher, QWidget):
    _set_calib_board_img_signal = pyqtSignal(QImage)
    _set_progress_bar_value_signal = pyqtSignal(int)
    _get_spin_value_signal = pyqtSignal(QSpinBox)
    def __init__(self):
        Ui_CalibBoardStitcher.__init__(self)
        QWidget.__init__(self)

        self._main_scene = None
        self._btn_clicked_cb_map = {}

    def setupUi(self, main_window: QMainWindow):
        super().setupUi(main_window)

        # 初始化mainGraphicView
        self._main_scene = QGraphicsScene()
        self.mainGraphicView.setScene(self._main_scene)
        self.mainGraphicView.wheelEvent = MethodType(self._wheel_event, self.mainGraphicView)
        self.mainGraphicView.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)

        # 添加按钮槽函数
        self.genCalibBoardImageButton.clicked.connect(
            lambda: self._btn_clicked(ButtonClickedEvent.GEN_CALIB_BOARD_IMG_BTN_CLICKED)
        )
        self.loadSubImageSequenceButton.clicked.connect(
            lambda: self._btn_clicked(ButtonClickedEvent.LOAD_SUB_IMG_SEQ_BTN_CLICKED)
        )
        self.importCalibResultButton.clicked.connect(
            lambda: self._btn_clicked(ButtonClickedEvent.IMPORT_CALIB_RESULT_BTN_CLICKED)
        )
        self.saveCalibResultButton.clicked.connect(
            lambda: self._btn_clicked(ButtonClickedEvent.SAVE_CALIB_RESULT_BUTTON)
        )

        # 进度条修改信号
        self._set_progress_bar_value_signal.connect(self._set_progress_bar_value)
        # 修改标定板图像信号
        self._set_calib_board_img_signal.connect(
            self._set_calib_board_img, type=Qt.ConnectionType.BlockingQueuedConnection
        )
        # 读取spin值信号
        self._get_spin_value_signal.connect(self._get_spin_value)



    def set_cb_changed_callback(self, event: ButtonClickedEvent, callback):
        """
        设置按钮单机事件的回调函数

        :param event: 按钮单机事件
        :param callback: 回调函数，无参数无返回值
        """
        self._btn_clicked_cb_map[event.name] = callback

    def set_progress_bar_value(self, value: int):
        """
        设置进度条进度
        :param value: 进度条值
        """
        self._set_progress_bar_value_signal.emit(value)

    def set_calib_board_img(self, img: cv2.typing.MatLike):
        # 获取mainGraphicView的size
        target_w = self.mainGraphicView.width()
        target_h = self.mainGraphicView.height()
        logging.debug("Widget: {}, size: {}".format("mainGraphicView", (target_w, target_h)))
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        y = img.shape[0]
        x = img.shape[1]
        frame = QImage(rgb_img, x, y, x * 3, QImage.Format.Format_RGB888)
        self._set_calib_board_img_signal.emit(frame)

    def get_row_count(self) -> int:
        """
        获取标定板行数
        :return: 标定板行数
        """
        return self._get_spin_value(self.rowCountSpinBox)

    def get_col_count(self) -> int:
        """
        获取标定板列数
        :return: 标定板列数
        """
        return self._get_spin_value(self.colCountSpinBox)

    def get_qr_pixel_size(self) -> int:
        """
        获取二维码像素大小
        :return: 二维码像素大小
        """
        return self._get_spin_value(self.qrPixelSizeSpinBox)

    def get_qr_border(self) -> int:
        """
        获取二维码边框大小
        :return: 二维码边框大小
        """
        return self._get_spin_value(self.qrBoarderSpinBox)

    @pyqtSlot(ButtonClickedEvent)
    def _btn_clicked(self, event: ButtonClickedEvent):
        """
        按钮点击事件槽函数

        :param event: 事件源
        """
        if not event.name in self._btn_clicked_cb_map:
            logging.warning("Callback: " + event.name + " not set.")
        else:
            self._btn_clicked_cb_map[event.name]()

    @pyqtSlot(int)
    def _set_progress_bar_value(self, value: int):
        self.progressBar.setValue(value)

    @pyqtSlot(QImage)
    def _set_calib_board_img(self, img: QImage):
        """
        设置标定板图像的槽函数
        :param img: QImage格式的图像
        """
        pixmap = QPixmap.fromImage(img)
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self._main_scene.clear()
        self._main_scene.addItem(pixmap_item)
        self._main_scene.update()

    @pyqtSlot(QSpinBox)
    def _get_spin_value(self, spin: QSpinBox):
        return spin.value()

    def _wheel_event(self, widget, event):
        delta = event.angleDelta().y()
        scale = 1 + delta / 1000.0

        if(
            widget == self.mainGraphicView
        ):
            widget.scale(scale, scale)
