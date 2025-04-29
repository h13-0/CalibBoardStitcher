import cv2.typing
import numpy as np

class Box:
    def __init__(
            self,
            lt: tuple[float, float],
            rt: tuple[float, float],
            rb: tuple[float, float],
            lb: tuple[float, float]
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
        return Box(
            (lt[0][0], lt[1][0]),
            (rt[0][0], rt[1][0]),
            (rb[0][0], rb[1][0]),
            (lb[0][0], lb[1][0])
        )

    def is_intersect(self, box) -> bool:
        """
        判断当前方框是否与某一方框存在交叉

        :param box: 需要对比的方框
        :return: bool
        """
        def _get_edges(box: Box) -> list:
            """获取四边形的四条边（顶点按顺时针顺序连接）"""
            return [
                (box.lt, box.rt),
                (box.rt, box.rb),
                (box.rb, box.lb),
                (box.lb, box.lt)
            ]

        def _get_axes(edges: list) -> list:
            """生成分离轴（每条边的法线方向）"""
            axes = []
            for (p1, p2) in edges:
                # 计算边的向量
                edge = (p2[0] - p1[0], p2[1] - p1[1])
                # 生成法线向量（垂直于边，无需归一化）
                axis = (-edge[1], edge[0])
                axes.append(axis)
            return axes

        def _project(vertices: list, axis: tuple[float, float]) -> tuple[float, float]:
            """计算顶点在指定轴上的投影范围"""
            dots = [v[0] * axis[0] + v[1] * axis[1] for v in vertices]
            return (min(dots), max(dots))

        def _overlaps(proj1: tuple[float, float], proj2: tuple[float, float]) -> bool:
            """判断两个投影范围是否有重叠"""
            return not (proj1[1] < proj2[0] or proj2[1] < proj1[0])

        # 获取两个四边形的所有边
        edges1 = _get_edges(self)
        edges2 = _get_edges(box)
        # 生成所有需要检测的分离轴（两个四边形的边法线）
        axes = _get_axes(edges1) + _get_axes(edges2)
        # 获取两个四边形的顶点集合
        vertices1 = [self.lt, self.rt, self.rb, self.lb]
        vertices2 = [box.lt, box.rt, box.rb, box.lb]
        # 检查所有分离轴上的投影重叠情况
        for axis in axes:
            proj1 = _project(vertices1, axis)
            proj2 = _project(vertices2, axis)
            if not _overlaps(proj1, proj2):
                return False  # 存在分离轴，不相交
        return True  # 所有轴上均重叠，说明相交


    @property
    def vertex(self) -> list[tuple[float, float]]:
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
