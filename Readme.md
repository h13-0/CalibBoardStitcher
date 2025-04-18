# 图像标定拼接工具
一个支持二次开发的图像标定与拼接工具。
![](docs/imgs/CalibBoardStitcher.jpg)

## 软件功能
- [x] 标定板生成
- [x] 子图标定与拼接
- [x] 拼接结果微调
  - [x] 主视图中修改标定点
  - [ ] 增删标定点
  - [ ] 右侧列表中手动添加未自动匹配的图像

## 软件使用流程
1. 进入 `标定板生成` 页面，根据需要生成指定参数的标定板
2. 采集若干子图像，并按需为子图像进行重命名，可见附注 `使用技巧——图像id` 
3. 进入 `标定板标定` 页面，点击 `加载子图像序列` 按钮，选定子图像所在文件夹
4. 点击 `执行自动匹配` 按钮，进行预匹配
5. 在左侧主图像中检查拼接结果，使用如下方法之一微调匹配点
    1. 双击主图像中需要微调的图像，手动调节锚点(已完成)
    2. 右侧列表中双击图像，手动添加图像或调节锚点(未完成)
6. 导出拼接结果(`*.json`文件)
7. 按照如下二次开发方式进行开发

## 二次开发
二次开发时需要导入本项目。
```python
import numpy as np
import cv2

# 按照路径导入 `Stitcher.py` 中的Stitcher类
from xxx.CalibBoardStitcher.Stitcher import Stitcher
# 按照路径导入 `CalibResult.py` 中的CalibResult类
from xxx.CalibBoardResult.CalibResult import CalibResult

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

## 附注
### 使用技巧——图像id
本软件在 `软件使用流程` 的步骤3导入子图像序列时，会将图像名作为图像id; 而后该图像id会始终保持于步骤6、7的导出拼接结果和二次开发中。
因此建议在使用本软件标注前，可以自行将子图像文件重命名为有意义的格式，例如： `${行id}_${列id}.jpg` 等。随后在进行二次开发时可以直接依照 `${行id}_${列id}.jpg` 的格式指定传入图像的id。

### 使用技巧——精度提升

