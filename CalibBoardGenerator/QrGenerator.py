import qrcode
import numpy as np
from CalibBoardElements.QrObj import QrObj

class QrGenerator:
    def __init__(self):
        pass

    def gen_qr(self, qr_obj:QrObj, with_border: bool = True) -> np.ndarray:
        """
        根据指定的QrObj生成二维码图像

        :param qr_obj:
        :param with_border:
        :return:
        """
        border = qr_obj.qr_border if with_border else 0
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=qr_obj.qr_pixel_size,
            border=border
        )
        qr.add_data(qr_obj)
        qr.make(fit=True)
        img = qr.make_image(fill_color=(0, 0, 0), back_color=(255, 255, 255))
        return np.array(img)
