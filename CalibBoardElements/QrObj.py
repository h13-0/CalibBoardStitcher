import json
import logging

from CalibBoardElements.Box import Box
from CalibBoardElements.CalibBoardObj import CalibBoardObj

class QrObj(Box):
    def __init__(self, row_id: int, col_id: int, board: CalibBoardObj):
        """
        二维码对象，包含二维码所需要容纳的所有信息

        :param row_id: 二维码所在行号
        :param col_id: 二维码所在列号
        :param board: 标定板对象
        """
        lt, rt, rb, lb = board.cal_qr_box(row_id, col_id).vertex
        super().__init__(lt, rt, rb, lb)
        self._row_id = row_id
        self._col_id = col_id
        self._board = board

    def __str__(self) -> str:
        return self.gen_json_str()

    def gen_json_str(self) -> str:
        """
        生成二维码中的json字符串

        :note: 生成的json键值规范可见文档，键值按照ASCII码进行排序
        :return: str
        """
        data = {
            "cid"       : self._col_id,
            "rid"       : self._row_id,
            "rc"        : self._board.row_count,
            "cc"        : self._board.col_count,
            "px_size"   : self._board.qr_pixel_size,
            "qr_border" : self._board.qr_border
        }
        sorted_data = {}
        for key in sorted(data.keys()):
            sorted_data[key] = data[key]
        return json.dumps(sorted_data)

    @staticmethod
    def from_json(json_data:str):
        """
        @brief: 从二维码中获取的json字符串生成二维码对象
        @return: QrObj
        """
        result = None
        try:
            data = json.loads(json_data)
            board = CalibBoardObj.from_json(json_data)
            result = QrObj(
                row_id=data["rid"],
                col_id=data["cid"],
                board=board
            )
        except Exception as e:
            logging.error("generate QrObj from json failed, msg: " + str(e))
        return result

    @property
    def row_id(self):
        return self._row_id

    @property
    def col_id(self):
        return self._col_id

    @property
    def qr_pixel_size(self):
        return self._board.qr_pixel_size

    @property
    def qr_border(self):
        return self._board.qr_border
