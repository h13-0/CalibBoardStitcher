import json
import logging

from CalibBoardElements.Box import Box

class CalibBoardObj:
    def __init__(self,
        row_count: int, col_count: int,
        qr_pixel_size : int = 10, qr_border : int = 3
    ):
        """
        标定板对象信息

        :param row_count: 标定板黑白色块行数
        :param col_count: 标定板黑白色块列数
        :param qr_pixel_size: 二维码的像素块宽度，默认为10
        :param qr_border: 二维码白色外边界宽度，单位为qr_pixel_size的倍数，默认为3
        """
        self._row_count     = row_count
        self._col_count     = col_count
        self._qr_pixel_size = qr_pixel_size
        self._qr_border     = qr_border

    @staticmethod
    def from_json(json_data:str):
        """
        @brief: 从二维码中获取的json字符串获取校准板配置
        @return: CalibrationBoardConfig
        """
        result = None
        try:
            data = json.loads(json_data)
            row_count = data["rc"]
            col_count = data["cc"]
            qr_pixel_size = data.get("px_size", 10)
            qr_border = data.get("qr_border", 3)
            result = CalibBoardObj(
                row_count=row_count,
                col_count=col_count,
                qr_pixel_size=qr_pixel_size,
                qr_border=qr_border
            )
        except Exception as e:
            logging.error("generate CalibBoardObj from json failed, msg: " + str(e))
        return result

    def cal_qr_box(self, row_id: int, col_id: int) -> Box:
        """
        计算指定位置的二维码本体顶点

        :param row_id: 二维码行id
        :param col_id: 二维码列id
        :return:
        """
        border_size = self._qr_pixel_size * self._qr_border
        lt = [col_id * self.grid_size + border_size, row_id * self.grid_size + border_size]
        rt = [lt[0] + self.qr_size, lt[1] + 0]
        rb = [lt[0] + self.qr_size, lt[1] + self.qr_size]
        lb = [lt[0] + 0, lt[1] + self.qr_size]
        return Box(
            lt=lt,
            rt=rt,
            rb=rb,
            lb=lb
        )

    @property
    def row_count(self):
        return self._row_count

    @property
    def col_count(self):
        return self._col_count

    @property
    def qr_pixel_size(self):
        return self._qr_pixel_size

    @property
    def qr_border(self):
        return self._qr_border

    @property
    def grid_size(self) -> int:
        """
        根据字符串长度计算
        :return:
        """
        # TODO
        return (33 + self.qr_border * 2) * self._qr_pixel_size

    @property
    def qr_size(self) -> int:
        """
        根据字符串长度计算
        :return:
        """
        # TODO
        return (33) * self._qr_pixel_size

