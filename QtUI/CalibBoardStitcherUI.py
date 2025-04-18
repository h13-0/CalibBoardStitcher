import logging
import threading
from enum import Enum
from types import MethodType
from typing import Optional, Callable

import cv2.typing
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QSize
from PyQt6.QtGui import QImage, QPixmap, QIcon
from PyQt6.QtWidgets import QGraphicsPixmapItem, QSpinBox, QMainWindow, QWidget, QGraphicsScene, QTableWidgetItem

from CalibBoardResult.CalibResult import MatchedPoint
from QtUI.SubImage import SubImage, SubImageStatus
from QtUI.Ui_CalibBoardStitcher import Ui_CalibBoardStitcher


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
    _select_save_file_signal = pyqtSignal(str, str, str)
    def __init__(self):
        Ui_CalibBoardStitcher.__init__(self)
        QWidget.__init__(self)

        self._main_scene = None

        # 回调函数
        self._btn_clicked_cb_map = {}
        self._matched_points_changed_callback = None

        # 图像Item
        ## 标定板图像Item
        self._calib_board_item = QGraphicsPixmapItem(QPixmap())

        ## 子图像Items
        self._sub_image_lock = threading.Lock()
        self._sub_image_items = {}

        # 文件选择功能
        self._select_folder_lock = threading.Lock()
        self._selected_folder = None
        self._select_save_file_lock = threading.Lock()
        self._selected_save_file = None

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

        # 连接选择文件信号
        self._select_folder_signal.connect(self._select_folder_slot, type=Qt.ConnectionType.BlockingQueuedConnection)
        self._select_save_file_signal.connect(self._select_save_file_slot, type=Qt.ConnectionType.BlockingQueuedConnection)


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
        sub_img.set_matched_point_changed_callback(self._matched_points_changed)

        with self._sub_image_lock:
            self._sub_image_items[id] = sub_img

        sub_img.set_selected_callback(
            lambda v=sub_img.img_id: self._sub_image_selected(v)
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

    def get_sub_image_matched_points(self, img_id: str) -> list[MatchedPoint]:
        """
        获取子图像匹配点

        :param img_id: 子图像ID
        """
        matched_points = []
        with self._sub_image_lock:
            if img_id in self._sub_image_items:
                matched_points = self._sub_image_items[img_id].get_matched_points()
        return matched_points


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

    def select_existing_folder_path(self, caption: Optional[str] = '', directory: Optional[str] = '') -> str:
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

    def select_save_file_path(self,
            caption: Optional[str] = '', directory: Optional[str] = '', filter: Optional[str] = ''
        ) -> str:
        """
        通过UI选择文件

        :param caption: 窗口标题
        :param directory: 初始路径
        :param filter: 文件过滤器
        :return: 选择到的文件路径
        """
        if threading.current_thread() == threading.main_thread():
            (file_name, selected_filter) = QtWidgets.QFileDialog.getSaveFileName(self, caption, directory, filter)
            return file_name
        else:
            self._select_save_file_signal.emit(caption, directory, filter)
            with self._select_save_file_lock:
                return self._selected_save_file


    def set_matched_points_changed_callback(self, callback: Callable[[str, list[MatchedPoint]], None]):
        """
        设置匹配点变化回调函数

        :param callback: def callback(img_id: str, matched_points: list[MatchedPoint]) -> None
        """
        self._matched_points_changed_callback = callback


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
    def _select_folder_slot(self, caption: Optional[str] = '', directory: Optional[str] = '') -> str:
        """
        选择文件夹的槽函数
        """
        with self._select_folder_lock:
            self._selected_folder = QtWidgets.QFileDialog.getExistingDirectory(self, caption, directory)
            self.subImageFolderPath.setText(self._selected_folder)

    @pyqtSlot(str, str, str)
    def _select_save_file_slot(self, caption: Optional[str] = '', directory: Optional[str] = '', filter: Optional[str] = ''):
        """
        选择保存文件路径的槽函数

        :param caption: 对话框标题
        :param directory: 初始目录
        :param filter: 文件过滤器
        """
        with self._select_save_file_lock:
            (file_name, selected_filter) = QtWidgets.QFileDialog.getSaveFileName(self, caption, directory, filter)
            if not file_name.endswith(selected_filter):
                file_name += selected_filter
            self._selected_save_file = file_name


    def _sub_image_selected(self, img_id: str):
        """
        子图被选中的回调函数
        :param img_id: 子图ID
        """
        # 切换子图状态
        with self._sub_image_lock:
            curr_status = self._sub_image_items[img_id].get_status()
            if curr_status == SubImageStatus.SHOW_TRANSFORMED_LOCKED:
                # 从预览模式进入匹配点编辑模式
                for img in self._sub_image_items.keys():
                    self._sub_image_items[img].switch_to(
                        SubImageStatus.HIDE if img!= img_id else SubImageStatus.SHOW_ORIGINAL_MOVABLE
                    )
            else:
                # 退出预览模式
                for img in self._sub_image_items.keys():
                    self._sub_image_items[img].switch_to(SubImageStatus.SHOW_TRANSFORMED_LOCKED)
        self._main_scene.update()

    def _matched_points_changed(self, img_id: str, matched_points: list[MatchedPoint]) -> None:
        """
        匹配点发生修改的回调函数
        """
        if self._matched_points_changed_callback is not None:
            self._matched_points_changed_callback(img_id, matched_points)
