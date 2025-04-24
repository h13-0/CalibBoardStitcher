import logging
from collections.abc import Callable

import cv2
import numpy as np

from CalibBoardStitcher.Elements import CalibBoardObj
from CalibBoardStitcher.Elements import QrObj
from .QrGenerator import QrGenerator

class BoardGenerator:
    def gen_img(self, board:CalibBoardObj, progress_callback: Callable[[float], None]=None) -> cv2.typing.MatLike:
        """
        按照标定板配置生成标定板图像

        :param board:  标定板配置
        :param progress_callback: 进度回调函数，接收参数为float类型，值域[0, 100]
        :return: 标定板图像
        """
        qr_generator = QrGenerator(board)

        # 输出图像
        result = None
        result_imgs = []
        # 黑白格尺寸
        grid_size = board.grid_size
        for i in range(board.row_count):
            # 按行生成
            ## 每行的子图
            row_img = None
            grid_imgs = []
            for j in range(board.col_count):
                # 生成每格的图像
                grid_img = None
                if(
                    (i % 2) * (j % 2) == 1 or
                    ((i + 1) % 2) * ((j + 1) % 2) == 1
                ):
                    # 交错生成黑白格
                    # 当前为白格，生成二维码
                    qr_obj = QrObj(
                        row_id=i,
                        col_id=j,
                        board_obj=board
                    )
                    grid_img = qr_generator.gen_qr(qr_obj)
                else:
                    # 交错生成黑白格
                    # 当前为黑格
                    grid_img = np.zeros((grid_size, grid_size, 3), np.uint8)
                grid_imgs.append(grid_img)
                # 更新进度
                if progress_callback:
                    progress_callback((i * board.col_count + j + 1) * 100 / (board.row_count * board.col_count))
            # 合并该行子图
            result_imgs.append(
                np.concatenate(
                    tuple(grid_imgs), axis=1
                )
            )
        # 合并完整图像
        result = np.concatenate(tuple(result_imgs), axis=0)
        return result

def main():
    logging.basicConfig(
        format="[%(levelname)s]: %(asctime)s %(name)s line: %(lineno)d - %(message)s",
        datefmt="%Y-%M-%D %H:%M:%S",
        level=logging.DEBUG
    )
    board_cfg = CalibBoardObj(
        row_count=32,
        col_count=43
    )
    generator = BoardGenerator()
    img = generator.gen_img(board_cfg)
    logging.debug("img size: " + str(img.shape))

    # 保存高质量图像
    #cv2.imwrite("./temp/CalibrationBoard.jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
    # 无压缩保存图像
    cv2.imwrite("./temp/CalibrationBoard.png", img, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])


if __name__ == "__main__":
    main()
