"""To compile and install locally run "python setup.py build_ext --inplace".
To install library to Python site-packages run "python -m pip install ."
To clean build artifacts run "python setup.py clean --all"
"""
import sys, sysconfig, platform
import shutil
import glob
from pathlib import Path
from setuptools import setup, Extension, Command

import numpy as np
from Cython.Build import cythonize

py_gil_disabled = sysconfig.get_config_var('Py_GIL_DISABLED')
use_limited_api = not py_gil_disabled and platform.python_implementation() == 'CPython' and sys.version_info >= (3, 12)
if use_limited_api:
    limited_api_args = {
        "py_limited_api": True,
        "define_macros": [("Py_LIMITED_API", "0x030C0000")],
    }
    options = {"bdist_wheel": {"py_limited_api": "cp312"}}
else:
    limited_api_args = {}
    options = {}

ext_modules = [
    Extension(
        'pycocoeval._mask',
        sources=['./common/maskApi.c', 'pycocoeval/_mask.pyx'],
        include_dirs=[np.get_include(), './common'],
        **limited_api_args
    )
]

try:
    readme = Path(__file__).parent.parent.joinpath("README.md").read_text("utf-8")
except FileNotFoundError:
    readme = ""

class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    
    description = 'Clean build artifacts'
    user_options = [
        ('all', 'a', 'remove all build output, not just temporary by-products')
    ]
    
    def initialize_options(self):
        self.all = None
    
    def finalize_options(self):
        pass
    
    def run(self):
        # Remove additional build artifacts
        dirs_to_remove = [
            'build',
            'dist',
            '*.egg-info',
            '__pycache__',
            '.eggs',
        ]
        
        files_to_remove = [
            'pycocoeval/_mask.c',  # Cython generated C file
            'pycocoeval/_mask*.so',  # Compiled extension (Linux/Mac)
            'pycocoeval/_mask*.pyd',  # Compiled extension (Windows)
        ]
        
        # Remove directories
        for pattern in dirs_to_remove:
            for path in glob.glob(pattern):
                if Path(path).is_dir():
                    print(f"Removing directory: {path}")
                    shutil.rmtree(path, ignore_errors=True)
        
        # Remove files
        for pattern in files_to_remove:
            for path in glob.glob(pattern):
                if Path(path).is_file():
                    print(f"Removing file: {path}")
                    Path(path).unlink()
        
        # Remove Cython generated files in pycocoeval directory
        pycocoeval_dir = Path('pycocoeval')
        if pycocoeval_dir.exists():
            for item in pycocoeval_dir.rglob('*.c'):
                if item.stem == '_mask':
                    print(f"Removing: {item}")
                    item.unlink()
            for item in pycocoeval_dir.rglob('*.so'):
                print(f"Removing: {item}")
                item.unlink()
            for item in pycocoeval_dir.rglob('*.pyd'):
                print(f"Removing: {item}")
                item.unlink()
            for item in pycocoeval_dir.rglob('__pycache__'):
                print(f"Removing directory: {item}")
                shutil.rmtree(item, ignore_errors=True)
        
        print("Clean completed!")


setup(
    name='pycocoeval',
    description='Official APIs for the MS-COCO dataset',
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/ppwwyyxx/cocoapi",
    license="FreeBSD",
    packages=['pycocoeval'],
    package_dir={'pycocoeval': 'pycocoeval'},
    python_requires='>=3.9',
    install_requires=[
        'numpy',
        'prettytable'
    ],
    extras_require={
        'all': ['matplotlib>=2.1.0'],
    },
    version='1.1.0',
    ext_modules=cythonize(ext_modules),
    cmdclass={
        'clean': CleanCommand,
    },
    options=options,
)
