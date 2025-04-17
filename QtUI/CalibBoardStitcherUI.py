import logging
import threading
from enum import Enum
from types import MethodType
from typing import Optional

import cv2.typing
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QSize, QPointF
from PyQt6.QtGui import QImage, QPixmap, QIcon
from PyQt6.QtWidgets import QGraphicsPixmapItem, QSpinBox, QMainWindow, QWidget, QGraphicsScene, QTableWidgetItem

from CalibBoardResult.CalibResult import MatchedPoint
from QtUI.Ui_CalibBoardStitcher import Ui_CalibBoardStitcher
from QtUI.Widgets.SubImagePixmapItem import SubImagePixmapItem


class SubImageStatus(Enum):
    HIDE = 0                        # 隐藏图像
    SHOW_ORIGINAL_LOCKED = 1        # 显示不可移动的原始图像
    SHOW_ORIGINAL_MOVABLE = 2       # 显示可移动的原始图像
    SHOW_TRANSFORMED_LOCKED = 3     # 显示不可移动的仿射后图像
    SHOW_TRANSFORMED_MOVABLE = 4    # 显示可移动的仿射后图像

class SubImage:
    def __init__(self, img_id: str, img_path: str, pos: tuple=(0, 0)):
        """
        子图像对象，管理UI中的子图像

        :param img_id: 图像id
        :param img_path: 图像文件路径
        :param pos: 子图像坐标
        """
        self.img_id = img_id
        self.img_path = img_path
        q_image = QImage(img_path)
        thumbnail = q_image.scaled(
            100, 100,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.thumbnail_pixmap = QPixmap.fromImage(thumbnail)

        self._original_draggable_pixmap_item = SubImagePixmapItem(QPixmap(q_image))
        self._transformed_draggable_pixmap_item = SubImagePixmapItem(QPixmap())
        self._original_draggable_pixmap_item.set_double_clicked_callback(self._double_clicked)
        self._transformed_draggable_pixmap_item.set_double_clicked_callback(self._double_clicked)

        self.enabled = False
        self._pos = pos
        self.status = SubImageStatus.SHOW_ORIGINAL_LOCKED
        self._double_clicked_callback = None

    def get_original_pixmap_item(self) -> SubImagePixmapItem:
        """
        获取原始图像对应的PixmapItem
        """
        return self._original_draggable_pixmap_item

    def get_transformed_pixmap_item(self) -> SubImagePixmapItem:
        """
        获取变换后的PixmapItem
        """
        return self._transformed_draggable_pixmap_item

    def update_transformed_img(self, img: cv2.typing.MatLike):
        """
        将子图像更新为校准变换后的图像
        :param img: 变换后的子图像，需要为BGRA四通道
        """
        h, w = img.shape[0:2]
        self._transformed_draggable_pixmap_item.setPixmap(
            QPixmap.fromImage(QImage(img, w, h, w * 4, QImage.Format.Format_ARGB32))
        )


    def set_pos(self, pos: tuple[float, float]):
        """
        设置控件在mainGraphicsView中显示的位置

        :param pos:
        """
        self._pos = pos
        if self._original_draggable_pixmap_item is not None:
            self._original_draggable_pixmap_item.setPos(QPointF(pos[0], pos[1]))
        if self._transformed_draggable_pixmap_item is not None:
            self._transformed_draggable_pixmap_item.setPos(QPointF(pos[0], pos[1]))



    def set_clicked_callback(self, callback):
        """
        设置SubImage的任意控件的双击回调函数

        :param callback: 回调函数
        """
        self._double_clicked_callback = callback

    def switch_to(self, status: SubImageStatus):
        """
        切换子图像对象的状态
        :param status: 要切换到的状态
        """
        if status == SubImageStatus.HIDE:
            self._original_draggable_pixmap_item.setVisible(False)
            self._transformed_draggable_pixmap_item.setVisible(False)
        elif status == SubImageStatus.SHOW_ORIGINAL_LOCKED:
            self._original_draggable_pixmap_item.setVisible(True)
            self._transformed_draggable_pixmap_item.setVisible(False)
            self._original_draggable_pixmap_item.lock()
        elif status == SubImageStatus.SHOW_ORIGINAL_MOVABLE:
            self._original_draggable_pixmap_item.setVisible(True)
            self._transformed_draggable_pixmap_item.setVisible(False)
            self._original_draggable_pixmap_item.unlock()
        elif status == SubImageStatus.SHOW_TRANSFORMED_LOCKED:
            self._original_draggable_pixmap_item.setVisible(False)
            self._transformed_draggable_pixmap_item.setVisible(True)
            self._transformed_draggable_pixmap_item.lock()
        elif status == SubImageStatus.SHOW_TRANSFORMED_MOVABLE:
            self._original_draggable_pixmap_item.setVisible(False)
            self._transformed_draggable_pixmap_item.setVisible(True)
            self._transformed_draggable_pixmap_item.unlock()

    def _double_clicked(self):
        if self._double_clicked_callback is not None:
            self._double_clicked_callback()

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

    # mainGraphicsView中的子图像相关信号
    _update_sub_image_signal = pyqtSignal(str)

    # TODO: 将下方信号并入_update_sub_image_signal信号中
    _del_sub_image_signal = pyqtSignal(str)
    _add_sub_image_signal = pyqtSignal(SubImage)
    _set_sub_image_matched_points_signal = pyqtSignal(str, list)

    _select_folder_signal = pyqtSignal(str, str)
    def __init__(self):
        Ui_CalibBoardStitcher.__init__(self)
        QWidget.__init__(self)

        self._main_scene = None
        self._btn_clicked_cb_map = {}
        # 图像Item
        ## 标定板图像Item
        self._calib_board_item = QGraphicsPixmapItem(QPixmap())

        ## 子图像Items
        self._sub_image_lock = threading.Lock()
        self._sub_image_items = {}

        self._select_folder_lock = threading.Lock()
        self._selected_folder = None

    def setupUi(self, main_window: QMainWindow):
        super().setupUi(main_window)

        # 初始化mainGraphicsView
        self._main_scene = QGraphicsScene()
        self.mainGraphicsView.setScene(self._main_scene)
        self.mainGraphicsView.wheelEvent = MethodType(self._wheel_event, self.mainGraphicsView)
        self.mainGraphicsView.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
        self._main_scene.addItem(self._calib_board_item)

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
        self._update_sub_image_signal.connect(self._update_sub_image_slot)
        self._add_sub_image_signal.connect(self._add_sub_image_slot)
        self._del_sub_image_signal.connect(self._del_sub_image)
        self._set_sub_image_matched_points_signal.connect(self._set_sub_image_matched_points_slot)

        # 连接选择文件夹信号
        self._select_folder_signal.connect(self._select_folder, type=Qt.ConnectionType.BlockingQueuedConnection)


    def set_btn_clicked_callback(self, event: ButtonClickedEvent, callback):
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
            img_id=id,
            img_path=img_path
        )
        with self._sub_image_lock:
            self._sub_image_items[id] = sub_img

        sub_img.set_clicked_callback(
            lambda v=sub_img.img_id: self._sub_image_clicked(v)
        )

        self._add_sub_image_signal.emit(sub_img)

    def del_sub_image(self, id: str):
        """
        删除子图像对象

        :param id: 图像id，通常定义为图像名。
        """
        # TODO
        with self._sub_image_lock:
            del self._sub_image_items[id]

    def set_sub_image_status(self, img_id: str, status: SubImageStatus):
        """
        设置子图的显示状态(不影响略缩图的显示)

        :param id:
        :param status:
        :return:
        """
        img_item_changed = False
        with self._sub_image_lock:
            if img_id in self._sub_image_items and self._sub_image_items[img_id].status != status:
                img_item_changed = True
                self._sub_image_items[img_id].status = status
        if img_item_changed:
            self._update_sub_image_signal.emit(img_id)

    def set_sub_image_pos(self, img_id: str, pos: tuple[float, float]):
        """
        设置指定子图像在mainGraphicsView中的显示位置

        :param img_id: 图像id
        :param pos: 要显示的位置
        """
        with self._sub_image_lock:
            if img_id in self._sub_image_items:
                self._sub_image_items[img_id].set_pos(pos)

    def set_sub_image_matched_points(self, img_id: str, matched_points: list[MatchedPoint]):
        """
        为指定的子图像设置匹配点

        :param img_id: 子图像ID
        :param matched_points: 匹配点列表
        """
        self._set_sub_image_matched_points_signal.emit(img_id, matched_points)
        pass


    def update_transformed_sub_img(self, img_id: str, transformed_img: cv2.typing.MatLike):
        """
        更新变换后的子图

        :param img_id: 图像id
        :param transformed_img: 变换后的子图图像, 需要为BGRA四通道图像
        """
        with self._sub_image_lock:
            if img_id in self._sub_image_items:
                self._sub_image_items[img_id].update_transformed_img(transformed_img)
        self._update_sub_image_signal.emit(img_id)

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
        self._calib_board_item.setPixmap(pixmap)
        self._calib_board_item.setZValue(-1)
        self._main_scene.update()

    @pyqtSlot(QSpinBox)
    def _get_spin_value(self, spin: QSpinBox):
        return spin.value()

    def _wheel_event(self, widget, event):
        delta = event.angleDelta().y()
        scale = 1 + delta / 1000.0

        if widget == self.mainGraphicsView:
            widget.scale(scale, scale)

    @pyqtSlot(str)
    def _update_sub_image_slot(self, img_id:str):
        """
        更新子图像信号槽

        :param img_id: 子图像ID
        """
        sub_img_item = None
        with self._sub_image_lock:
            if img_id in self._sub_image_items:
                sub_img_item = self._sub_image_items[img_id]

        # 更新子图像控件
        if sub_img_item is not None:
            sub_img_item.switch_to(sub_img_item.status)
        self._main_scene.update()


    @pyqtSlot(SubImage)
    def _add_sub_image_slot(self, sub_img: SubImage):
        """
        添加子图像的槽函数

        :param sub_img:
        """
        row_id = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_id)

        # 设置"子图像序列"列表区域内容
        self.tableWidget.setItem(row_id, 0, QTableWidgetItem(sub_img.img_id))
        self.tableWidget.setItem(row_id, 1, QTableWidgetItem(str(sub_img.enabled)))
        item = QTableWidgetItem()
        item.setIcon(QIcon(sub_img.thumbnail_pixmap))
        self.tableWidget.setItem(row_id, 2, item)
        self.tableWidget.setItem(row_id, 3, QTableWidgetItem("[]"))

        # 向主画布中添加子图像
        self._main_scene.addItem(sub_img.get_original_pixmap_item())
        self._main_scene.addItem(sub_img.get_transformed_pixmap_item())
        self._main_scene.update()

    def _del_sub_image(self, img_id: str):
        """
        从mainGraphicsView中删除子图对应控件(sub_img.get_original_pixmap_item)

        :param img_id: 子图像ID
        """
        with self._sub_image_lock:
            if img_id in self._sub_image_items:
                self._main_scene.removeItem(self._sub_image_items[img_id].get_original_pixmap_item)
                self._main_scene.update()

    @pyqtSlot(str, list)
    def _set_sub_image_matched_points_slot(self, img_id: str, matched_points: list[MatchedPoint]):
        with self._sub_image_lock:
            if img_id in self._sub_image_items:
                self._sub_image_items[img_id].get_original_pixmap_item().set_matched_points(
                    calib_board=self._calib_board_item,
                    matched_points=matched_points,
                    scene=self._main_scene
                )


    @pyqtSlot(str, str)
    def _select_folder(self, caption: Optional[str] = '', directory: Optional[str] = '') -> str:
        """
        选择文件夹的槽函数
        :return: 文件夹路径
        """
        with self._select_folder_lock:
            self._selected_folder = QtWidgets.QFileDialog.getExistingDirectory(self, caption, directory)
            self.subImageFolderPath.setText(self._selected_folder)

    def _sub_image_clicked(self, img_id: str):
        """
        子图控件双击回调函数

        :param img_id: 子图ID
        """

        # 切换子图状态
        curr_status = None
        with self._sub_image_lock:
            curr_status = self._sub_image_items[img_id].status


        if curr_status == SubImageStatus.SHOW_TRANSFORMED_LOCKED:
            self.set_sub_image_status(img_id, SubImageStatus.SHOW_ORIGINAL_MOVABLE)
        else:
            self.set_sub_image_status(img_id, SubImageStatus.SHOW_TRANSFORMED_LOCKED)


