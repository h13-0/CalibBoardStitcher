from typing import Callable

from PyQt6.QtCore import QRectF, QPointF, QLineF
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsPixmapItem, QWidget, QGraphicsLineItem, QGraphicsScene


class CrosshairItem(QGraphicsItem):
    def __init__(self, pos: QPointF, parent=None):
        self._item_changed_callback = None
        super().__init__(parent)
        # 忽略视图变化
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
        self.size = 10
        self.setPos(pos)

    def boundingRect(self):
        # 定义项的边界矩形
        return QRectF(-self.size, -self.size, 2 * self.size, 2 * self.size)

    def paint(self, painter: QPainter, option, widget=None):
        # 绘制固定大小的十字
        pen = QPen(QColor(255, 0, 0), 1)  # 线宽固定为1像素
        painter.setPen(pen)
        # 水平线
        painter.drawLine(-self.size, 0, self.size, 0)
        # 垂直线
        painter.drawLine(0, -self.size, 0, self.size)

    def set_item_changed_callback(self, callback: Callable):
        self._item_changed_callback = callback

    def itemChange(self, change, value):
        if self._item_changed_callback is not None:
            self._item_changed_callback()
        return super().itemChange(change, value)

    def lock(self):
        """
        锁定十字准星，使其不可拖动
        """
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)

    def unlock(self):
        """
        解锁十字准星，允许拖动
        """
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)


class MatchedPointWidget(QWidget):
    def __init__(self,
            calib_board: QGraphicsPixmapItem, calib_board_pos: QPointF,
            sub_img: QGraphicsPixmapItem, sub_img_pos: QPointF,
            scene: QGraphicsScene
        ):
        super().__init__()
        self.cb_point = CrosshairItem(
            pos=calib_board_pos,
            parent=calib_board
        )
        self.sub_img_point = CrosshairItem(
            pos=sub_img_pos,
            parent=sub_img
        )
        self._scene = scene
        self.line = QGraphicsLineItem()
        self.cb_point.set_item_changed_callback(self._update_line_pos)
        self._update_line_pos()
        self._scene.addItem(self.line)


    def get_cb_point(self) -> tuple[float, float]:
        """
        获取标定板上匹配点坐标
        :return: tuple(x, y)
        """
        pos = self.cb_point.pos()
        return pos.x(), pos.y()

    def get_img_point(self) -> tuple[float, float]:
        """
        获取子图像上匹配点坐标
        :return: tuple(x, y)
        """
        pos = self.sub_img_point.pos()
        return pos.x(), pos.y()

    def _update_line_pos(self):
        """
        更新线段坐标
        """
        pos1 = self.sub_img_point.mapToScene(self.sub_img_point.boundingRect().center())
        pos2 = self.cb_point.mapToScene(self.cb_point.boundingRect().center())
        self.line.setLine(QLineF(pos1, pos2))
