import cv2.typing
import numpy as np

class Box:
    def __init__(
            self,
            lt: cv2.typing.Point2f, rt: cv2.typing.Point2f,
            rb: cv2.typing.Point2f, lb: cv2.typing.Point2f
    ):
        """
        基础方框对象，只存储顶点信息

        :param lt: 左上顶点坐标
        :param rt: 右上顶点坐标
        :param rb: 右下顶点坐标
        :param lb: 左下顶点坐标
        """
        self._vertex = {
            "lt": lt,
            "rt": rt,
            "rb": rb,
            "lb": lb
        }

    def warp_affine(self, M: cv2.typing.MatLike):
        """
        按照仿射矩阵计算旋转后的Box

        :param M: 仿射矩阵
        :return: 仿射后的Box
        """
        lt, rt, rb, lb = [self._vertex["lt"], self._vertex["rt"], self._vertex["rb"], self._vertex["lb"]]
        lt = np.dot(M, np.array([[lt[0]], [lt[1]], [1]]))
        rt = np.dot(M, np.array([[rt[0]], [rt[1]], [1]]))
        rb = np.dot(M, np.array([[rb[0]], [rb[1]], [1]]))
        lb = np.dot(M, np.array([[lb[0]], [lb[1]], [1]]))
        return Box(lt, rt, rb, lb)

    @property
    def vertex(self) -> list[cv2.typing.Point2f, cv2.typing.Point2f, cv2.typing.Point2f, cv2.typing.Point2f]:
        return [self._vertex["lt"], self._vertex["rt"], self._vertex["lb"], self._vertex["rb"]]

    @property
    def lt(self):
        return self._vertex["lt"]

    @property
    def rt(self):
        return self._vertex["rt"]

    @property
    def rb(self):
        return self._vertex["rb"]

    @property
    def lb(self):
        return self._vertex["lb"]

    @property
    def top(self):
        return self._vertex["lt"][1]

    @property
    def left(self):
        return self._vertex["lt"][0]

    @property
    def bottom(self):
        return self._vertex["rb"][1]

    @property
    def right(self):
        return self._vertex["rb"][0]
