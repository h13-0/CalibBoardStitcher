import time

import cv2.typing
import qrcode
import numpy as np

from CalibBoardElements.CalibBoardObj import CalibBoardObj
from CalibBoardElements.QrObj import QrObj

class QrGenerator:
    def __init__(self, board_obj: CalibBoardObj):
        self._qr_version = board_obj.calc_qr_version()

    def gen_qr(self, qr_obj:QrObj) -> cv2.typing.MatLike:
        """
        根据指定的QrObj生成二维码图像

        :param qr_obj:
        :param with_border:
        :return: cv2.typing.MatLike
        """
        qr = qrcode.QRCode(
            version=self._qr_version,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=qr_obj.qr_pixel_size,
            border=qr_obj.qr_border
        )
        qr.add_data(qr_obj)
        qr.make(fit=False)
        img = qr.make_image(fill_color=(0, 0, 0), back_color=(255, 255, 255))
        return np.array(img)
