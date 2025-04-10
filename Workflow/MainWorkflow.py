import logging
import math
import os.path
import threading
import time

import cv2
import numpy as np

from CalibBoardDetector.QrDetector import QrDetector
from CalibBoardGenerator.BoardGenerator import BoardGenerator
from QtUI.CalibBoardStitcherUI import CalibBoardStitcherUI, ButtonClickedEvent

from CalibBoardStitcher.Stitcher import Stitcher, stitch
from CalibBoardElements.CalibBoardObj import CalibBoardObj

class MainWorkflow:
    def __init__(self, ui:CalibBoardStitcherUI, stop_event:threading.Event):
        self._ui = ui
        self._stop_event = stop_event
        self._main_thread = None

        # 任务锁
        self._task_mutex = threading.Lock()
        self._task_name = ""

        # 标定板拼接对象
        self._board_obj = None
        self._stitcher = None
        self._board_generator = BoardGenerator()
        self._board_img = None

        # 子图像序列
        self._sub_image_paths = []

    def _gen_calib_board_img_task(self):
        """
        生成标定板图像的task
        """
        self._ui.set_progress_bar_value(0)

        board_obj = CalibBoardObj(
            row_count=self._ui.get_row_count(),
            col_count=self._ui.get_col_count(),
            qr_pixel_size=self._ui.get_qr_pixel_size(),
            qr_border=self._ui.get_qr_border()
        )

        self._board_img = self._board_generator.gen_img(
            board_obj,
            progress_callback=lambda v: self._ui.set_progress_bar_value(int(v))
        )
        self._ui.set_progress_bar_value(100)
        self._ui.set_calib_board_img(self._board_img)

    def _update_transformed_sub_image(self):
        pass

    def _load_sub_image_seq_task(self, folder: str):
        """
        从指定路径加载子图像序列的task

        :param folder: 文件夹路径
        """
        self._ui.set_progress_bar_value(0)
        self._sub_image_paths = []

        if folder is None:
            logging.error("No folder selected.")
            return
        logging.info("Loading sub image sequence from folder {}.".format(folder))

        file_list = os.listdir(folder)
        file_num = len(file_list)
        for i in range(file_num):
            file_name = file_list[i]
            file_path = os.path.join(folder, file_name)
            try:
                self._ui.add_sub_image(file_name, file_path)
                self._ui.set_progress_bar_value(int((i + 1) / file_num * 100))
                self._sub_image_paths.append(file_path)
            except Exception as e:
                logging.error(f"load image: {file_path} failed with msg: {str(e)}")
            if self._stop_event.is_set():
                break
        self._ui.set_progress_bar_value(100)

    def _exec_auto_match_task(self):
        """
        执行自动关键点匹配
        """
        self._ui.set_progress_bar_value(0)

        stitcher = None
        board_obj = None
        qr_detector = QrDetector()
        img_nums = len(self._sub_image_paths)
        # 检出二维码数量
        qr_nums = 0
        # 检出二维码总尺寸，用于计算平均大小
        qr_code_total_size = 0

        # 遍历子图像并匹配关键点
        base_img = None
        base_mask = None
        results = {"matched_points": {}}
        for i in range(img_nums):
            file_path = self._sub_image_paths[i]
            file_name = os.path.basename(file_path)
            img = cv2.imread(file_path)
            # 尝试初始化board_obj，并统计放大系数
            for qr_target in qr_detector.detect(img):
                if board_obj is None:
                    board_obj = qr_target.get_board_obj()
                    stitcher = Stitcher(board_obj)
                qr_nums += 1
                qr_code_total_size += (
                    (
                        math.sqrt(
                            math.pow(qr_target.lt[0] - qr_target.rt[0], 2) +
                            math.pow(qr_target.lt[1] - qr_target.rt[1], 2)
                        ) +
                        math.sqrt(
                            math.pow(qr_target.rt[0] - qr_target.rb[0], 2) +
                            math.pow(qr_target.rt[1] - qr_target.rb[1], 2)
                        ) +
                        math.sqrt(
                            math.pow(qr_target.rb[0] - qr_target.lb[0], 2) +
                            math.pow(qr_target.rb[1] - qr_target.lb[1], 2)
                        ) +
                        math.sqrt(
                            math.pow(qr_target.lb[0] - qr_target.lt[0], 2) +
                            math.pow(qr_target.lb[1] - qr_target.lt[1], 2)
                        )
                    ) / 4.0
                )

            if stitcher is not None:
                if base_img is None:
                    base_img = np.zeros(stitcher.board_cfg.img_shape, dtype=np.uint8)
                    base_mask = np.zeros(base_img.shape[0:2], dtype=np.uint8)
                    results["base_width"] = base_img.shape[1]
                    results["base_height"] = base_img.shape[0]

                start = time.perf_counter()
                matched_points = stitcher.match(img, file_name)
                end = time.perf_counter()
                logging.info("stitcher.match() spend: {}".format(end - start))

                for matched in matched_points:
                    logging.info(matched)

                # 找到匹配点对，进行拼接
                if len(matched_points) > 0:
                    start = time.perf_counter()
                    base_img, base_mask = stitcher.stitch_full_cover(base_img, base_mask, img, matched_points)
                    end = time.perf_counter()
                    logging.info("stitcher.stitch_full_cover() spend: {}".format(end - start))

                    results["matched_points"][file_name] = []
                    for p in matched_points:
                        results["matched_points"][file_name].append(p.dict())

            self._ui.set_progress_bar_value(int((i + 1) / img_nums * 80))

        if stitcher is not None:
            # 同步结果到UI
            ## 同步放大后的标准标定板图像
            board_img = self._board_generator.gen_img(
                board_obj,
                progress_callback=lambda v: self._ui.set_progress_bar_value(int(v / 5) + 80)
            )
            calib_board_scale = board_obj.qr_size / qr_code_total_size / qr_nums
            board_img = cv2.resize(board_img, (0, 0), fx=calib_board_scale, fy=calib_board_scale)
            self._ui.set_calib_board_img(board_img)
        else:
            self._ui.set_progress_bar_value(0)
            logging.error(f"No QrCode found in total {img_nums} images.")


    def _do_task(self, task):
        task()
        self._task_mutex.release()

    def _try_load_task(self, task, task_name: str, wait: bool=False) -> bool:
        succ = False
        if self._task_mutex.acquire(blocking=wait):
            self._task_name = task_name
            thread = threading.Thread(target=self._do_task, args=(task, ))
            thread.daemon = True
            thread.start()
            succ = True
        if not succ:
            logging.warning("Task: {} is running".format(self._task_name))
        return succ


    def _main(self):
        """
        当前工作流的主逻辑，不应当在主线程中使用
        """
        self._ui.set_btn_clicked_callback(
            ButtonClickedEvent.GEN_CALIB_BOARD_IMG_BTN_CLICKED,
            lambda : self._try_load_task(
                self._gen_calib_board_img_task,
                task_name="Generate CalibBoard image task"
            ),
        )
        self._ui.set_btn_clicked_callback(
            ButtonClickedEvent.LOAD_SUB_IMG_SEQ_BTN_CLICKED,
            lambda : self._try_load_task(
                lambda : self._load_sub_image_seq_task(
                    folder=self._ui.select_folder("选择子图像序列文件夹")
                ),
                task_name="Load sub image sequence task"
            ),
        )
        self._ui.set_btn_clicked_callback(
            ButtonClickedEvent.EXEC_AUTO_MATCH_BTN_CLICKED,
            lambda : self._try_load_task(
                self._exec_auto_match_task,
                task_name="Auto match task"
            )
        )

        while not self._stop_event.is_set():
            pass




    def run(self, block:bool = False):
        """
        启动工作流
        :param block: 是否在当前线程工作, 配合UI使用时应当为 `False`
        """
        if block:
            self._main()
        else:
            self._main_thread = threading.Thread(target = self._main)
            self._main_thread.start()
