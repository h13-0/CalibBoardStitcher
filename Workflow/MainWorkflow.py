import logging
import threading

from CalibBoardGenerator.BoardGenerator import BoardGenerator
from QtUI.CalibBoardStitcherUI import CalibBoardStitcherUI, ButtonClickedEvent

from CalibBoardStitcher.Stitcher import Stitcher
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

    def _gen_calib_board_img_task(self):
        self._ui.set_progress_bar_value(0)

        board_obj = CalibBoardObj(
            row_count=self._ui.get_row_count(),
            col_count=self._ui.get_col_count(),
            qr_pixel_size=self._ui.get_qr_pixel_size(),
            qr_border=self._ui.get_qr_border()
        )

        self._stitcher = Stitcher(board_obj)
        self._board_img = self._board_generator.gen_img(
            board_obj,
            progress_callback=lambda v: self._ui.set_progress_bar_value(int(v))
        )
        self._ui.set_progress_bar_value(100)
        self._ui.set_calib_board_img(self._board_img)

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
        self._ui.set_cb_changed_callback(
            ButtonClickedEvent.GEN_CALIB_BOARD_IMG_BTN_CLICKED,
            lambda: self._try_load_task(
                self._gen_calib_board_img_task,
                task_name="Generate CalibBoard image"
            ),
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
