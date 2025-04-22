import enum
import logging
import math
import os
import time

import cv2.typing
import numpy as np

from CalibBoardStitcher.Elements import Box, CalibBoardObj
from CalibBoardStitcher.Detector import QrDetector
from CalibBoardStitcher.Generator import BoardGenerator
from CalibBoardStitcher.CalibResult import MatchedPoint, CalibResult
from CalibBoardStitcher.Utils import logging_config

class Stitcher:
    def __init__(self, board:CalibBoardObj):
        self._board = board
        self._qr_detector = QrDetector()

        # 生成标定板标准图像以及相关参数信息
        board_generator = BoardGenerator()
        #self._board_img = None
        #self._board_img = board_generator.gen_img(board)

    @property
    def board_cfg(self) -> CalibBoardObj:
        return self._board

    def detect_calib_board_cells(self):

        pass

    def match(self, img:cv2.typing.MatLike, img_id: str) -> list[MatchedPoint]:
        matched_points = []
        # 1. Try to find Qr Code.
        qr_targets = self._qr_detector.detect(img)
        if len(qr_targets) > 0:
            for target in qr_targets:
                # 1.1 获取该二维码在标准标定板中的位置
                cb_box = self._board.calc_qr_box(row_id=target.row_id, col_id=target.col_id)

                for i in range(4):
                    cb_point = cb_box.vertex[i]
                    qr_point = target.vertex[i]
                    matched_points.append(
                        MatchedPoint(img_id, cb_point, qr_point)
                    )
        else:
            # TODO
            pass

        return matched_points

    class StitchMethod(enum.Enum):
        FULL_COVER = "full_cover"  # 直接将整张子图覆盖拼接，覆盖优先级为列表靠后图像覆盖靠前的图像
        GRID_COVER = "grid_cover"  # 将MatchedPoints插分为网格，然后将子图按照网格切割后覆盖拼接

    def stitch_full_gen_wrapped_partial(self,
            partial_img: cv2.typing.MatLike,
            matched_points: list[MatchedPoint]
        ) -> tuple[cv2.typing.MatLike, Box]:
        """
        生成完整仿射变换后的子图

        :param partial_img: 待拼接的子图
        :param matched_points: 匹配点对
        :return: RGBA四通道图像
        """
        # 0. 预处理数据
        ## 0.1 生成与partial_img等大小的mask
        partial_h, partial_w = partial_img.shape[0:2]
        #partial_mask = np.ones((partial_h, partial_w), dtype= np.uint8) # 0.01s
        ## 0.2 为partial_img添加透明通道
        if partial_img.shape[2] == 3:
            b, g, r = cv2.split(partial_img)
            alpha = np.ones((partial_h, partial_w), dtype= np.uint8) * 255
            partial_img = cv2.merge((b, g, r, alpha))

        # 1. 计算变换矩阵均值
        src_points = np.array([point.img_point for point in matched_points])
        dst_points = np.array([point.cb_point for point in matched_points])
        m, inliers = cv2.estimateAffine2D(src_points, dst_points) #0.0001s

        # 2. 计算仿射后的图像区域，并划定ROI加速运算
        transformed_box = Box(
            lt=[0, 0], rt=[partial_w - 1, 0],
            rb=[partial_w - 1, partial_h - 1], lb=[0, partial_h - 1]
        ).warp_affine(m)
        ## 仿射后子图在大图中的ROI顶点
        pos_x1 = math.floor(min([point[0] for point in transformed_box.vertex]))
        pos_x2 = math.ceil(max([point[0] for point in transformed_box.vertex]))
        pos_y1 = math.floor(min([point[1] for point in transformed_box.vertex]))
        pos_y2 = math.ceil(max([point[1] for point in transformed_box.vertex]))

        # 3. 对ROI区域进行仿射，加速仿射运算
        ## 3.1 重新计算变换矩阵
        dst_points = np.array([[point.cb_point[0] - pos_x1, point.cb_point[1] - pos_y1] for point in matched_points])
        m, inliers = cv2.estimateAffine2D(src_points, dst_points) #0.0001s

        ## 4.2 执行仿射变换
        start = time.perf_counter()
        partial_img = cv2.warpAffine(partial_img, m, (pos_x2 - pos_x1 + 1, pos_y2 - pos_y1 + 1))   # 0.0018s
        end = time.perf_counter()
        logging.debug("cv2.warpAffine() spend: {}".format(end - start))

        return partial_img, transformed_box


    def stitch_full_cover(self,
        base_img: cv2.typing.MatLike, base_img_mask: cv2.typing.MatLike,
        partial_img: cv2.typing.MatLike, matched_points: list[MatchedPoint]
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

        # 1. 对子图进行仿射变换
        wrapped_partial, pos = self.stitch_full_gen_wrapped_partial(partial_img, matched_points)

        ## 1.1 将位置转换为整数
        pos_l = math.floor(pos.left)
        pos_r = math.ceil(pos.right)
        pos_t = math.floor(pos.top)
        pos_b = math.ceil(pos.bottom)
        ## 1.2 计算主图像ROI区域
        roi_l = max(pos_l, 0)
        roi_r = min(pos_r, base_w - 1)
        roi_t = max(pos_t, 0)
        roi_b = min(pos_b, base_h - 1)

        # 2. 将变换后的子图按照覆盖方式拼接回原图像
        base_img_roi = base_img[roi_t:roi_b + 1, roi_l:roi_r + 1]
        wrapped_partial_roi = wrapped_partial[roi_t - pos_t:roi_b - pos_t + 1, roi_l - pos_l:roi_r - pos_l + 1, 0:3]
        wrapped_mask_roi = wrapped_partial[roi_t - pos_t:roi_b - pos_t + 1, roi_l - pos_l:roi_r - pos_l + 1, 3]
        wrapped_mask_roi_bool = wrapped_mask_roi == 255
        base_img_roi[wrapped_mask_roi_bool] = wrapped_partial_roi[wrapped_mask_roi_bool] #0.03

        return base_img, base_img_mask

    def stitch_to(self,
            base_img: cv2.typing.MatLike, base_img_mask: cv2.typing.MatLike,
            partial_img: cv2.typing.MatLike, matched_points: list[MatchedPoint],
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


def calibration(calib_img_dir: str, export_json: str="", export_img: str=""):
    """
    执行校准

    :param calib_img_dir: 标定板图像文件夹
    :param export_json: 导出Json格式的校准结果，值为路径，为空不导出
    :param export_img: 导出拼接后的图像，值为路径，为空不导出
    :return:
    """
    stitcher = None
    base_img = None
    base_mask = None
    calib_result = None

    for file in os.listdir(calib_img_dir):
        file_path = os.path.join(calib_img_dir, file)
        img = cv2.imread(file_path)

        # 尝试寻找图像中的二维码，并获取配置信息
        if stitcher is None:
            stitcher = Stitcher.from_qr_img(img)
            if stitcher:
                calib_result = CalibResult(board_obj=stitcher.board_cfg)

    # 执行标定算法
    for file in os.listdir(calib_img_dir):
        file_path = os.path.join(calib_img_dir, file)
        img = cv2.imread(file_path)
        if base_img is None:
            base_img = np.zeros(stitcher.board_cfg.img_shape, dtype=np.uint8)
            base_mask = np.zeros(base_img.shape[0:2], dtype=np.uint8)

        start = time.perf_counter()
        matched_points = stitcher.match(img, file) #0.1655s
        end = time.perf_counter()
        logging.info("stitcher.match() spend: {}".format(end - start))

        for matched_point in matched_points:
            logging.info(matched_point)
            calib_result.add_matched_point(matched_point)

        if len(export_img) > 0 and len(matched_points) > 0:
            # 找到匹配点对，进行拼接
            start = time.perf_counter()
            base_img, base_mask = stitcher.stitch_full_cover(base_img, base_mask, img, matched_points)
            end = time.perf_counter()
            logging.info("stitcher.stitch_full_cover() spend: {}".format(end - start))

    if len(export_img) > 0:
        cv2.imwrite(export_img, base_img)

    if len(export_json) > 0:
        calib_result.save(export_json)


def stitch(img_dir: str, json_file: str, export_img: str=""):
    calib_result = CalibResult.load_from_file(json_file)

    board_obj = calib_result.get_calib_board_obj()
    stitcher = Stitcher(board_obj)

    base_img = np.zeros(board_obj.img_shape, dtype=np.uint8)
    base_mask = np.zeros(base_img.shape[0:2], dtype=np.uint8)

    for img_id in calib_result.get_matched_img_id():
        file_path = os.path.join(img_dir, img_id)
        if not os.path.exists(file_path):
            continue
        img = cv2.imread(file_path)

        matched_points = calib_result.get_matched_points(img_id)
        start = time.perf_counter()
        base_img, base_mask = stitcher.stitch_full_cover(base_img, base_mask, img, matched_points)
        end = time.perf_counter()
        logging.info("stitcher.stitch_full_cover() spend: {}".format(end - start))

    if len(export_img) > 0:
        cv2.imwrite(export_img, base_img)


if __name__ == "__main__":
    logging_config()
    #calibration(calib_img_dir="../datasets/stitch0306", export_json="./temp/0306.json", export_img="./temp/0306.jpg")
    calibration(calib_img_dir="../datasets/20250417", export_json="./temp/250417.json", export_img="./temp/250417.jpg")
    #calibration(calib_img_dir="../datasets/0415sz/1", export_json="./temp/0415_sz.json", export_img="./temp/0415_sz.jpg")
    #stitch(img_dir="../datasets/0416", json_file="./temp/0415.json", export_img="./temp/0416.jpg")
    #stitch(img_dir="../datasets/0415sz/4", json_file="./temp/0415_sz.json", export_img="./temp/0415_sz_pcb.jpg")

