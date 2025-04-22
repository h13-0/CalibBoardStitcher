# 图像标定拼接工具
一个支持二次开发的图像标定与拼接工具。
UI前端可见：[https://github.com/h13-0/CalibBoardStitcherUI](https://github.com/h13-0/CalibBoardStitcherUI)

## 二次开发
二次开发时需要导入本项目。
```python
import numpy as np
import cv2

# 导入Stitcher类
from CalibBoardStitcher.Stitcher import Stitcher
# 导入CalibResult类
from CalibBoardStitcher.CalibResult import CalibResult

# Step1: 从上述第6步导出的json文件中加载标定结果
calib_result = CalibResult.load_from_file("xxx.json")

# Step2: 实例化CalibBoardObj和Stitcher
board_obj = calib_result.get_calib_board_obj()
stitcher = Stitcher(board_obj)

# 使用目的1: 将所有子图拼接为大图(与下方目的二选一即可)
## Step3.1: 生成空白大图和对应Mask(Mask为非0时表示对应位置有图像)
base_img = np.zeros(board_obj.img_shape, dtype=np.uint8)
base_mask = np.zeros(base_img.shape[0:2], dtype=np.uint8)
for img_id, cv2_img in your_cv2_imgs:
    # img_id的tips可见附注 `使用技巧——图像id` 章节
    matched_points = calib_result.get_matched_points(img_id)
    # 获得的图像为BGR三通道
    base_img, base_mask = stitcher.stitch_full_cover(base_img, base_mask, cv2_img, matched_points)

# 使用目的2: 获得单张子图变换后的位置和图像
## Step3.1: 执行单张图像的变换
matched_points = calib_result.get_matched_points(img_id)
transformed, box = stitcher.stitch_full_gen_wrapped_partial(cv2_img, matched_points)
## Step3.2: 处理变换后的图像
print(f"transformed img pos {box.lt} to {box.rb}")
## 注意：获得到的图像为BGRA四通道，Alpha通道用于避免边缘锯齿黑边
cv2.imshow("transformed", transformed)
```

## 文档
软件文档：
- [二次开发接口](docs/标定算法调用接口(Stitcher).md)
- [二维码数据定义文档](docs/标定算法调用接口(Stitcher).md)
- [导出数据定义](docs/导出数据定义.md)

## 性能指标
以下性能基于 `Intel i5-12400` 进行测试。

