import json
import math

import numpy as np

from CalibBoardElements.CalibBoardObj import CalibBoardObj

def safe_cos(img_vec, cb_vec):
    img_norm = np.linalg.norm(img_vec)
    cb_norm = np.linalg.norm(cb_vec)
    if img_norm == 0 or cb_norm == 0:
        return 0.0
    return np.dot(img_vec, cb_vec) / (img_norm * cb_norm)

class MatchedPoint:
    def __init__(self, img_id: str, cb_point: list[float, float], img_point: list[float, float]):
        self.img_id = img_id
        self.cb_point = cb_point
        self.img_point = img_point

    def __str__(self):
        return ("MatchedPoints: {} on CalibBoard and {} on image id: {}."
                .format(self.cb_point, self.img_point, self.img_id))

    def __repr__(self):
        return self.__str__()

    def dict(self) -> dict:
        return {
            "cb_point": self.cb_point,
            "img_point": self.img_point
        }

class CalibResult:
    def __init__(self, board_obj: CalibBoardObj):
        self._board_obj = board_obj
        self._matched_imgs = {}

    def add_matched_point(self, matched_point: MatchedPoint):
        """
        添加匹配点对

        :param matched_point: 匹配点
        """
        if matched_point.img_id not in self._matched_imgs:
            self._matched_imgs[matched_point.img_id] = []
        self._matched_imgs[matched_point.img_id].append(matched_point)

    def get_calib_board_obj(self) -> CalibBoardObj:
        """
        获取标定板配置对象

        :return: CalibBoardObj
        """
        return self._board_obj

    def get_matched_points(self) -> list[MatchedPoint]:
        """
        获取匹配点对

        :return: list[MatchedPoints]
        """
        matched_points = []

        for img_id in self._matched_imgs:
            matched_points.append(self._matched_imgs[img_id])

        return matched_points

    @staticmethod
    def load_from_file(file_path: str):
        """
        从json文件加载标定结果

        :param file_path: json文件路径
        :return: CalibResult
        """
        data = {}
        with open(file_path, "r") as f:
            data = json.load(f)

        board_obj = CalibBoardObj(
            row_count=data["row_count"],
            col_count=data["col_count"],
            qr_pixel_size=data["qr_pixel_size"],
            qr_border=data["qr_border"]
        )

        result = CalibResult(board_obj)

        for img_id in data["matched_images"]:
            matched_points = MatchedPoint(
                img_id,
                cb_point=data["matched_images"][img_id]["cb_point"],
                img_point=data["matched_images"][img_id]["img_point"],
            )
            result.add_matched_point(matched_points)

        return result

    def save(self, file_path: str):
        """
        保存标定数据到json文件

        :param file_path: json文件路径
        """
        result = {
            "row_count": self._board_obj.row_count,
            "col_count": self._board_obj.col_count,
            "qr_pixel_size": self._board_obj.qr_pixel_size,
            "qr_border": self._board_obj.qr_border,
            "matched_images": {}
        }

        for img_id in self._matched_imgs:
            result["matched_images"][img_id] = []
            for matched_point in self._matched_imgs[img_id]:
                result["matched_images"][img_id].append(matched_point.dict())

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)


    def calc_mean_sub_img_scale(self) -> float:
        """
        计算各子图相对于标准标定板中理论尺寸的平均倍数

        :return: 平均倍数
        """
        dist_on_img = 0
        dist_on_board = 0

        for img_id in self._matched_imgs:
            matched_points = self._matched_imgs[img_id]
            for i in range(len(matched_points)):
                for j in range(i + 1, len(matched_points)):
                    img_dx = matched_points[i].img_point[0] - matched_points[j].img_point[0]
                    img_dy = matched_points[i].img_point[1] - matched_points[j].img_point[1]
                    cb_dx = matched_points[i].cb_point[0] - matched_points[j].cb_point[0]
                    cb_dy = matched_points[i].cb_point[1] - matched_points[j].cb_point[1]

                    dist_on_img += math.sqrt(
                        math.pow(img_dx, 2) +
                        math.pow(img_dy, 2)
                    )
                    dist_on_board += math.sqrt(
                        math.pow(cb_dx, 2) +
                        math.pow(cb_dy, 2)
                    )

        return dist_on_img / dist_on_board


    def calc_mean_sub_img_rotation(self) -> float:
        """
        计算各子图相对于标准标定板的平均旋转角度

        :return: 平均旋转角度
        """
        dist_nums = 0
        angle_sum = 0

        for img_id in self._matched_imgs:
            matched_points = self._matched_imgs[img_id]
            for i in range(len(matched_points)):
                for j in range(i + 1, len(matched_points)):
                    img_dx = matched_points[i]["img_point"][0] - matched_points[j]["img_point"][0]
                    img_dy = matched_points[i]["img_point"][1] - matched_points[j]["img_point"][1]
                    cb_dx = matched_points[i]["cb_point"][0] - matched_points[j]["cb_point"][0]
                    cb_dy = matched_points[i]["cb_point"][1] - matched_points[j]["cb_point"][1]

                    cos = safe_cos([img_dx, img_dy], [cb_dx, cb_dy])
                    angle = math.degrees(math.acos(cos))
                    angle_sum += angle

                    dist_nums += 1

        return angle_sum / dist_nums


