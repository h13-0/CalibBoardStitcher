from setuptools import setup, find_packages

setup(
    name='CalibBoardStitcher',
    version='0.1',
    packages=find_packages(),
    package_data={
        'CalibBoardStitcher': [
            'weights/detect.caffemodel',
            'weights/detect.prototxt',
            'weights/sr.caffemodel',
            'weights/sr.prototxt'
        ],
    },
    install_requires=[
    ],
    author='h13',
    author_email='makerh47@gmail.com',
    description='Calibration board generation and calibration tool.',
    url='https://github.com/h13-0/CalibBoardStitcher',
)
