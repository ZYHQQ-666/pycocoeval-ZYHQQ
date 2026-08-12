import sys
import numpy as np

# 1. 动态劫持：强制让整个 Python 环境底层的 _mask 都指向你的 native 扩展
# 这样不需要去改工具代码，也能保证它绝对使用你修改的 IoU 逻辑
import pycocoeval._mask as native
sys.modules['pycocotools._mask'] = native

from pycocoeval.coco import COCO
from pycocoeval.cocoeval import COCOeval

print("--- 重新验证 AP 计算：使用真实引发 Bug 的非对称坐标 ---")

# 2. 换上 test_iou 中验证失败的那组坐标
gt_data = {
    "images": [{"id": 1, "width": 100, "height": 100}],
    "annotations": [
        {
            "id": 1, 
            "image_id": 1, 
            "category_id": 1, 
            "bbox": [10, 20, 30, 40], # x, y, w, h
            "area": 1200,             # 真实面积 30 * 40 = 1200
            "iscrowd": 0
        }
    ],
    "categories": [{"id": 1, "name": "target"}]
}

pred_data = [
    # 预测框与真实框完全一样
    {"image_id": 1, "category_id": 1, "bbox": [10, 20, 30, 40], "score": 0.9}
]

coco_gt = COCO()
coco_gt.dataset = gt_data
coco_gt.createIndex()
coco_dt = coco_gt.loadRes(pred_data)

import os
old_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')

coco_eval = COCOeval(coco_gt, coco_dt, 'bbox')
coco_eval.evaluate()
coco_eval.accumulate()
coco_eval.summarize()

sys.stdout = old_stdout

# 3. 严格验证 AP@75，因为如果你底层算出是 0.6，AP@75 必定直接挂掉（等于 0.0）
# AP@50 的判定规则是：只要预测框和真实框的 IoU 大于或等于 0.5，建议对比ap50:95或者ap75
actual_ap_75 = coco_eval.stats[0] # 0:ap50:95; 1:ap50; 2:ap75
expected_ap_75 = 1.0 # 因为我们给的测试数据是完全重合的框，所以无论哪个ap都要取1

passed = np.isclose(actual_ap_75, expected_ap_75)

print(f"验证结果: 预期 AP@75={expected_ap_75:.4f}, 你的工具计算出={actual_ap_75:.4f}")

assert passed, "成功复现问题！check_ap.py 现在已经能正确暴露出你的 AP 计算错误了！"
