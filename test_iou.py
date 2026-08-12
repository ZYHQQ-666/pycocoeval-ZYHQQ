import numpy as np
import pycocoeval._mask as native
from pycocoeval import mask as fixed
from pycocotools import mask as official

print("Python 扩展：", native.__file__)

cases = [
    ("完全相同", [10, 20, 30, 40], [10, 20, 30, 40], 1.0),
    ("完全分离", [0, 0, 10, 10], [20, 20, 10, 10], 0.0),
    ("部分重叠", [0, 0, 10, 10], [5, 5, 10, 10], 1.0 / 7.0),
    ("小框被包含", [2, 2, 2, 2], [0, 0, 10, 10], 0.04),
]

for name, detection, ground_truth, expected in cases:
    result = float(fixed.iou(
        [detection], [ground_truth], [0]
    )[0, 0])

    reference = float(official.iou(
        [detection], [ground_truth], [0]
    )[0, 0])

    passed = (
        np.isclose(result, expected)
        and np.isclose(result, reference)
        and 0.0 <= result <= 1.0
    )

    print(
        f"{name}: pycocoeval={result:.8f}, "
        f"官方={reference:.8f}, "
        f"{'通过' if passed else '失败'}"
    )

    assert passed, f"{name}测试失败"

print("全部 IoU 测试通过")
