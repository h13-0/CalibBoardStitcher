import json
import logging

import cv2.typing


from CalibBoardElements.Box import Box
from CalibBoardElements.QrObj import QrObj
from CalibBoardElements.CalibBoardObj import CalibBoardObj

class QrTarget(Box):
    def __init__(self, row_id: int, col_id: int, box: Box, board: CalibBoardObj):
        """
        检测到的二维码对象

        :param row_id: 二维码所在行号
        :param col_id: 二维码所在列号
        :param box: 二维码本体Box
        :param board: 标定板对象
        """
        super().__init__(box.lt, box.rt, box.rb, box.lb)
        self._row_id = row_id
        self._col_id = col_id
        self._board = board

    @property
    def row_id(self) -> int:
        return self._row_id

    @property
    def col_id(self) -> int:
        return self._col_id

    def get_board_obj(self) -> CalibBoardObj:
        return self._board

    @staticmethod
    def from_json(box: Box, json_data:str):
        """
        @brief: 从二维码中获取的json字符串获取校准板配置
        @return: CalibrationBoardConfig
        """
        result = None
        try:
            data = json.loads(json_data)
            board = CalibBoardObj.from_json(json_data)
            result = QrTarget(
                row_id=data["rid"],
                col_id=data["cid"],
                box=box,
                board=board
            )
        except Exception as e:
            logging.error("generate QrTarget from json failed, msg: " + str(e))
        return result
