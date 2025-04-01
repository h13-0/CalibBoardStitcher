import enum
import logging
import math
import os
import time
from idlelib.browser import transform_children

import cv2.typing
import numpy as np

from CalibBoardElements.Box import Box
from CalibBoardElements.CalibBoardObj import CalibBoardObj
from CalibBoardElements.QrTarget import QrTarget
from CalibBoardDetector.QrDetector import QrDetector
from CalibBoardGenerator.BoardGenerator import BoardGenerator
from Utils.Utils import logging_config

class MatchedPoints:
    def __init__(self, img_id: str, cb_point: list[float, float], img_point: list[float, float]):
        self.img_id = img_id
        self.cb_point = cb_point
        self.img_point = img_point

    def __str__(self):
        return ("MatchedPoints: {} on CalibBoard and {} on image id: {}."
                .format(self.cb_point, self.img_point, self.img_id))


class Stitcher:
    def __init__(self, board:CalibBoardObj):
        self._board = board
        self._qr_detector = QrDetector()

        # 生成标定板标准图像以及相关参数信息
        board_generator = BoardGenerator()
        self._board_img = board_generator.gen_img(board)

    def detect_calib_board_cells(self):

        pass

    def match(self, img:cv2.typing.MatLike, img_id: str) -> list[MatchedPoints]:
        matched_points = []
        # 1. Try to find Qr Code.
        qr_targets = self._qr_detector.detect(img)
        if len(qr_targets) > 0:
            for target in qr_targets:
                # 1.1 获取该二维码在标准标定板中的位置
                cb_box = self._board.cal_qr_box(row_id=target.row_id, col_id=target.col_id)

                for i in range(4):
                    cb_point = cb_box.vertex[i]
                    qr_point = target.vertex[i]
                    matched_points.append(
                        MatchedPoints(img_id, cb_point, qr_point)
                    )
        else:
            # TODO
            pass

        return matched_points

    class StitchMethod(enum.Enum):
        FULL_COVER = "full_cover"  # 直接将整张子图覆盖拼接，覆盖优先级为列表靠后图像覆盖靠前的图像
        GRID_COVER = "grid_cover"  # 将MatchedPoints插分为网格，然后将子图按照网格切割后覆盖拼接

    def stitch_full_cover(self,
        base_img: cv2.typing.MatLike, base_img_mask: cv2.typing.MatLike,
        partial_img: cv2.typing.MatLike, matched_points: list[MatchedPoints]
    ) -> tuple[cv2.typing.MatLike, cv2.typing.MatLike]:
        """
        直接将整张子图覆盖拼接到大图中

        :param base_img: 待拼接到的大图
        :param base_img_mask: 大图mask
        :param partial_img: 待拼接的子图
        :param matched_points: 匹配点对
        :return: tuple[base, mask], 分别为拼接好的图像和mask
        """
        # 0. 获取必要参数
        base_h, base_w = base_img.shape[0:2]

        # 1. 生成与partial_img等大小的mask
        partial_h, partial_w = partial_img.shape[0:2]
        partial_mask = np.ones((partial_w, partial_h),dtype= np.uint8) # 0.01s

        # 2. 计算变换矩阵均值
        src_points = np.array([point.img_point for point in matched_points])
        dst_points = np.array([point.cb_point for point in matched_points])
        m, inliers = cv2.estimateAffine2D(src_points, dst_points) #0.0001s

        # 3. 计算仿射后的图像区域，并划定ROI加速运算
        transformed_box = Box(
            lt=[0, 0], rt=[partial_w - 1, 0],
            rb=[partial_w - 1, partial_h - 1], lb=[0, partial_h - 1]
        ).warp_affine(m)
        left = math.floor(min([point[0] for point in transformed_box.vertex]))
        right = math.ceil(max([point[0] for point in transformed_box.vertex]))
        top = math.floor(min([point[1] for point in transformed_box.vertex]))
        button = math.ceil(max([point[1] for point in transformed_box.vertex]))

        # 4. 对partial_mask和partial_img同时进行仿射变换
        start = time.perf_counter()
        partial_mask = cv2.warpAffine(partial_mask, m, (base_w, base_h)) #0.669s
        partial_img = cv2.warpAffine(partial_img, m, (base_w, base_h))   #0.669s
        end = time.perf_counter()
        logging.info("cv2.warpAffine() spend: {}".format(end - start))

        # 4. 将变换后的子图拼接回原图像
        base_img_roi = base_img[top:button+1, left:right+1]
        partial_img_roi = partial_img[top:button+1, left:right+1]
        partial_mask_roi = partial_mask[top:button+1, left:right+1]
        partial_mask_roi_bool = partial_mask_roi != 0
        base_img_roi[partial_mask_roi_bool] = partial_img_roi[partial_mask_roi_bool] #0.03

        return base_img, base_img_mask

    def stitch_to(self,
        base_img: cv2.typing.MatLike, base_img_mask: cv2.typing.MatLike,
        partial_img: cv2.typing.MatLike, matched_points: list[MatchedPoints],
        method: StitchMethod = StitchMethod.FULL_COVER
    ) -> tuple[cv2.typing.MatLike, cv2.typing.MatLike]:
        """
        按照指定方式拼接单个图像

        :param base_img: 待拼接到的图像
        :param base_img_mask: 待拼接到的图像的mask，为1的部分表示已存在子图
        :param partial_img: 带拼接的子图像
        :param matched_points: 子图匹配到的坐标点位
        :param method: 拼接方法
        :return: tuple[base, mask], 分别为拼接好的图像和mask
        """



        pass




    #
    # def stitch(self,
    #     stitched_img_w: int, stitched_img_h: int,
    #     partial_img: list[cv2.typing.MatLike], matched_points: list[list[MatchedPoints]],
    #     bg_color: tuple=(0, 0, 0), method: StitchMethod=StitchMethod.FULL_COVER
    # ) -> cv2.typing.MatLike:
    #     """
    #     按照指定方式拼接图像
    #
    #     :param stitched_img_w:
    #     :param stitched_img_h:
    #     :param partial_img:
    #     :param matched_points:
    #     :param bg_color:
    #     :param method:
    #     :return:
    #     """
    #
    #     if method == Stitcher.StitchMethod.FULL_COVER:
    #         return self.stitch_full_cover(partial_img, matched_points, bg_color)
    #     else:
    #         logging.error("Unsupported stitching method.")
    #         return None
    #
    # def stitch_full_cover(self,
    #     partial_img: list[cv2.typing.MatLike], matched_points: list[list[MatchedPoints]],
    #     bg_color: tuple=(0, 0, 0)
    # ) -> cv2.typing.MatLike:
    #     """
    #     直接将整张子图覆盖拼接，覆盖优先级为列表靠后图像覆盖靠前的图像
    #
    #     :param partial_img: 子图列表
    #     :param matched_points: 与子图列表对应的拼接点
    #     :param bg_color: 背景填充
    #     :return: 拼接后的图像
    #     """




    @staticmethod
    def from_qr_img(img:cv2.typing.MatLike):
        qr_detector = QrDetector()
        qr_targets = qr_detector.detect(img)
        if len(qr_targets) > 0:
            return Stitcher(
                board=qr_targets[0].get_board_obj()
            )
        else:
            logging.error("QR code not found.")
            return None


def main():
    stitcher = None
    base_img = None
    base_mask = None
    base_dir = "../datasets/stitch20250313/"

    for file in os.listdir(base_dir):
        file_path = os.path.join(base_dir, file)
        img = cv2.imread(file_path)
        if stitcher is None:
            stitcher = Stitcher.from_qr_img(img)

        if stitcher is not None:
            if base_img is None:
                base_img = np.zeros_like(stitcher._board_img, dtype=np.uint8)
                base_mask = np.zeros(base_img.shape[0:2], dtype=np.uint8)

            start = time.perf_counter()
            matched_points = stitcher.match(img, file) #0.1655s
            end = time.perf_counter()
            logging.info("stitcher.match() spend: {}".format(end - start))

            for matched in matched_points:
                logging.info(matched)

            if len(matched_points) > 0:
                start = time.perf_counter()
                base_img, base_mask = stitcher.stitch_full_cover(base_img, base_mask, img, matched_points)
                end = time.perf_counter()
                logging.info("stitcher.stitch_full_cover() spend: {}".format(end - start))



    #cv2.imshow("result", base_img)
    cv2.imwrite("./temp/base_img.jpg", base_img)

if __name__ == "__main__":
    logging_config()
    main()
