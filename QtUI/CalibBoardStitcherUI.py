import logging
import threading
from enum import Enum
from types import MethodType
from typing import Optional

import cv2.typing
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QSize
from PyQt6.QtGui import QImage, QPixmap, QIcon, QPen
from PyQt6.QtWidgets import QGraphicsPixmapItem, QSpinBox, QMainWindow, QWidget, QGraphicsScene, QTableWidgetItem

from QtUI.Ui_CalibBoardStitcher import Ui_CalibBoardStitcher

class DraggablePixmapItem(QGraphicsPixmapItem):
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)

    def mousePressEvent(self, event):
        """
        鼠标按压事件
        """
        # 设置透明度为0.5
        self.setOpacity(0.5)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件
        """
        # 设置透明度为1.0
        self.setOpacity(1.0)
        super().mouseReleaseEvent(event)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if self.isSelected():
            pen = QPen(Qt.GlobalColor.red)
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setDashOffset(5)
            pen.setDashPattern([3, 40])
            pen.setWidth(1)
            painter.setPen(pen)
            painter.setBrush(Qt.GlobalColor.transparent)
            painter.drawRect(self.boundingRect())
        else:
            painter.setPen(Qt.GlobalColor.transparent)
            painter.setBrush(Qt.GlobalColor.transparent)
            painter.drawRect(self.boundingRect())


class SubImage:
    def __init__(self, id: str, img_path: str):
        """
        子图像对象，存储QImage、Pixmap、PixmapItem等
        :param id: 图像id
        :param img: cv2格式的BGR图像
        """
        self.id = id
        self.img_path = img_path
        thumbnail = self.q_image.scaled(
            100, 100,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.thumbnail_pixmap = QPixmap.fromImage(thumbnail)
        self._original_draggable_pixmap_item = None
        self._transformed_draggable_pixmap_item = None
        self.enabled = False

    @property
    def q_image(self):
        return QImage(self.img_path)

    @property
    def transformed_draggable_pixmap_item(self) -> DraggablePixmapItem:
        if self._transformed_draggable_pixmap_item is None:
            self._transformed_draggable_pixmap_item = DraggablePixmapItem(QPixmap.fromImage(self.q_image))
        return self._transformed_draggable_pixmap_item

    @property
    def original_draggable_pixmap_item(self) -> DraggablePixmapItem:
        if self._original_draggable_pixmap_item is None:
            self._original_draggable_pixmap_item = DraggablePixmapItem(QPixmap.fromImage(self.q_image))
        return self._original_draggable_pixmap_item

    def update_transformed_img(self, img: cv2.typing.MatLike):
        """
        将子图像更新为校准变换后的图像
        :param img: 子图像
        """
        h, w = img.shape[0:2]
        self._transformed_draggable_pixmap_item = DraggablePixmapItem(
            QPixmap.fromImage(QImage(img, w, h, w * 3, QImage.Format.Format_RGB888))
        )

class ButtonClickedEvent(Enum):
    GEN_CALIB_BOARD_IMG_BTN_CLICKED = 1
    LOAD_SUB_IMG_SEQ_BTN_CLICKED = 2
    IMPORT_CALIB_RESULT_BTN_CLICKED = 3
    EXEC_AUTO_MATCH_BTN_CLICKED = 4
    SAVE_CALIB_RESULT_BUTTON = 5


class CalibBoardStitcherUI(Ui_CalibBoardStitcher, QWidget):
    _set_calib_board_img_signal = pyqtSignal(QImage)
    _set_progress_bar_value_signal = pyqtSignal(int)
    _get_spin_value_signal = pyqtSignal(QSpinBox)
    _add_sub_image_signal = pyqtSignal(SubImage)
    _select_folder_signal = pyqtSignal(str, str)
    def __init__(self):
        Ui_CalibBoardStitcher.__init__(self)
        QWidget.__init__(self)

        self._main_scene = None
        self._btn_clicked_cb_map = {}
        # 图像Item
        ## 标定板图像Item
        self._calib_board_item = None
        ## 子图像Items
        self._sub_image_items = {}

    def setupUi(self, main_window: QMainWindow):
        super().setupUi(main_window)

        # 初始化mainGraphicView
        self._main_scene = QGraphicsScene()
        self.mainGraphicView.setScene(self._main_scene)
        self.mainGraphicView.wheelEvent = MethodType(self._wheel_event, self.mainGraphicView)
        self.mainGraphicView.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)

        # 初始化tableWidget
        self.tableWidget.setIconSize(QSize(100, 100))

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
        self.execAutoMatchButton.clicked.connect(
            lambda: self._btn_clicked(ButtonClickedEvent.EXEC_AUTO_MATCH_BTN_CLICKED)
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
        # 设置添加子图像信号
        self._add_sub_image_signal.connect(self._add_sub_image)
        # 连接选择文件夹信号
        self._select_folder_signal.connect(self._select_folder, type=Qt.ConnectionType.BlockingQueuedConnection)
        self._select_folder_lock = threading.Lock()
        self._selected_folder = None

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
        h, w = img.shape[0:2]
        frame = QImage(rgb_img, w, h, w * 3, QImage.Format.Format_RGB888)
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

    def add_sub_image(self, id: str, img_path: str):
        """
        向UI中添加子图像，该API会首先在右侧`子图像序列`中添加子图像对象，并在使能对象后添加到手动标定画面

        :param id: 图像id，通常定义为图像名。
        :param img_path: 图像文件路径
        """
        sub_img = SubImage(
            id=id,
            img_path=img_path
        )
        self._sub_image_items[id] = sub_img
        self._add_sub_image_signal.emit(sub_img)

    def del_sub_image(self, id: str):
        """
        删除子图像对象

        :param id: 图像id，通常定义为图像名。
        """
        # TODO
        del self._sub_image_items[id]

    def select_folder(self, caption: Optional[str] = '', directory: Optional[str] = '') -> str:
        """
        通过UI选择文件夹

        :return: 文件夹路径
        """
        if threading.current_thread() == threading.main_thread():
            return QtWidgets.QFileDialog.getExistingDirectory(self, caption, directory)
        else:
            self._select_folder_signal.emit(caption, directory)
            with self._select_folder_lock:
                return self._selected_folder

    def set_update_img_transform_callback(self):
        pass

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
        self._calib_board_item = QGraphicsPixmapItem(pixmap)
        self._main_scene.clear()
        self._main_scene.addItem(self._calib_board_item)
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

    @pyqtSlot(SubImage)
    def _add_sub_image(self, sub_img: SubImage):
        """
        添加子图像的槽函数

        :param sub_img:
        """
        row_id = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_id)

        # 设置"子图像序列"列表区域内容
        self.tableWidget.setItem(row_id, 0, QTableWidgetItem(sub_img.id))
        self.tableWidget.setItem(row_id, 1, QTableWidgetItem(str(sub_img.enabled)))
        item = QTableWidgetItem()
        item.setIcon(QIcon(sub_img.thumbnail_pixmap))
        self.tableWidget.setItem(row_id, 2, item)
        self.tableWidget.setItem(row_id, 3, QTableWidgetItem("[]"))

        # 向主画布中添加子图像
        #self._main_scene.addItem(sub_img.original_draggable_pixmap_item)
        #self._main_scene.update()


    @pyqtSlot(str, str)
    def _select_folder(self, caption: Optional[str] = '', directory: Optional[str] = '') -> str:
        """
        选择文件夹的槽函数
        :return: 文件夹路径
        """
        with self._select_folder_lock:
            self._selected_folder = QtWidgets.QFileDialog.getExistingDirectory(self, caption, directory)

