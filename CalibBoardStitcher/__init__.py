import os
from pathlib import Path
from .CalibResult import MatchedPoint, CalibResult
from .Detector import QrDetector
from .Elements import Box, CalibBoardObj, QrObj, QrTarget
from .Generator import BoardGenerator, QrGenerator
from .Stitcher import Stitcher
from .weights import *

__all__ = (
    'MatchedPoint',
    'CalibResult',
    'QrDetector',
    'Box',
    'CalibBoardObj',
    'QrObj',
    'QrTarget',
    'BoardGenerator',
    'QrGenerator',
    'Stitcher'
)

def get_hook_dirs():
    return [str(os.path.join(Path(__file__).parent, "hooks"))]
