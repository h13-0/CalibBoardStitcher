from CalibBoardElements.Box import Box

class CellObj(Box):
    def __init__(self, color: str, **kwargs):
        """
        棋盘格单元对象

        :param color: 棋盘格颜色
        :param lt: 左上顶点坐标
        :param rt: 右上顶点坐标
        :param rb: 右下顶点坐标
        :param lb: 左下顶点坐标
        """
        super().__init__(**kwargs)
        self._color = color

    @property
    def color(self):
        return self._color
