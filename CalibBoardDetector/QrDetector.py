import json

import cv2

from CalibBoardElements.QrTarget import QrTarget
from CalibBoardElements.Box import Box

class QrDetector:
    def __init__(self):
        self._qr_coder = cv2.wechat_qrcode_WeChatQRCode(
            "./weights/detect.prototxt",
            "./weights/detect.caffemodel",
            "./weights/sr.prototxt",
            "./weights/sr.caffemodel"
        )


    def detect(self, img:cv2.typing.MatLike) -> list[QrTarget]:
        """
        从图像中检测二维码

        :param img: 待检图像，不考虑摄像头畸变
        :return: 由 `QrTarget` 构成的列表
        """
        results = []

        content, points = self._qr_coder.detectAndDecode(img)
        for i in range(len(content)):
            box = Box(points[i][0].tolist(), points[i][1].tolist(), points[i][2].tolist(), points[i][3].tolist())
            results.append(
                QrTarget.from_json(box, content[i])
            )

        return results

def main():
    detector = QrDetector()

    # img = cv2.imread(r"./temp/test.jpg")
    img = cv2.imread(r"./temp/Image-0034.png")

    detector.detect(img)

if __name__ == "__main__":
    main()