from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene

from CalibBoardResult.CalibResult import MatchedPoint
from QtUI.Widgets.MatchedPointWidget import MatchedPointWidget


class SubImagePixmapItem(QGraphicsPixmapItem):
    def __init__(self, pixmap: QGraphicsPixmapItem, pos: tuple[float, float]=(0, 0)):
        super().__init__(pixmap)
        self.setPos(pos[0], pos[1])
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True)
        self._double_clicked_callback = None
        self._matched_point_widgets = []

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

    def lock(self):
        """
        锁定对象，禁止拖动
        """
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, False)

    def unlock(self):
        """
        取消锁定对象，允许拖动
        """
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable)

    def set_double_clicked_callback(self, callback: callable):
        """
        设置双击事件回调

        :param callback: 回调函数
        """
        self._double_clicked_callback = callback

    def set_matched_points(self,
            calib_board: QGraphicsPixmapItem,
            matched_points: list[MatchedPoint],
            scene: QGraphicsScene,
        ):
        """
        设置子图像的匹配点对，作为控件，本函数仅能在主线程中调用。

        :param calib_board: 标定板的PixmapItem对象
        :param matched_points: 匹配点列表
        :param scene: 子图像和标定板图像所处于的QGraphicsScene
        """

        for matched_point in matched_points:
            self._matched_point_widgets.append(
                MatchedPointWidget(
                    calib_board=calib_board,
                    calib_board_pos=QPointF(matched_point.cb_point[0], matched_point.cb_point[1]),
                    sub_img=self,
                    sub_img_pos=QPointF(matched_point.img_point[0], matched_point.img_point[1]),
                    scene=scene
                )
            )


    def mouseDoubleClickEvent(self, event):
        if self._double_clicked_callback is not None:
            self._double_clicked_callback()
        event.accept()