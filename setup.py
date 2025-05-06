from setuptools import setup, find_packages

setup(
    name='CalibBoardStitcher',
    version='0.1',
    packages=find_packages(),
    package_dir={'CalibBoardStitcher': 'CalibBoardStitcher'},
    package_data={
        'CalibBoardStitcher': [
            'weights/*.caffemodel',
            'weights/*.prototxt',
            'hooks/*.py'
        ],
    },
    entry_points={
        "pyinstaller40": [
            "hook-dirs = CalibBoardStitcher:get_hook_dirs"
        ]
    },
    install_requires=[
        'altgraph',
        'colorama',
        'numpy',
        'opencv-contrib-python',
        'opencv-python',
        'pillow',
        'qrcode'
    ],
    author='h13',
    author_email='makerh47@gmail.com',
    description='Calibration board generation and calibration tool.',
    url='https://github.com/h13-0/CalibBoardStitcher',
)
