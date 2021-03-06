import os
import sys
import glob
from itertools import chain

from .env import check_env_flag
from .cuda import WITH_CUDA, CUDA_HOME


def gather_paths(env_vars):
    return list(chain(*(os.getenv(v, '').split(':') for v in env_vars)))

is_conda = 'conda' in sys.version or 'Continuum' in sys.version
conda_dir = os.path.join(os.path.dirname(sys.executable), '..')

WITH_CUDNN = False
CUDNN_LIB_DIR = None
CUDNN_INCLUDE_DIR = None
if WITH_CUDA and not check_env_flag('NO_CUDNN'):
    lib_paths = list(filter(bool, [
        os.getenv('CUDNN_LIB_DIR'),
        os.path.join(CUDA_HOME, 'lib'),
        os.path.join(CUDA_HOME, 'lib64'),
        '/usr/lib/x86_64-linux-gnu/',
        '/usr/lib/powerpc64le-linux-gnu/',
        '/usr/lib/aarch64-linux-gnu/',
    ] + gather_paths([
        'LIBRARY_PATH',
    ]) + gather_paths([
        'LD_LIBRARY_PATH',
    ])))
    include_paths = list(filter(bool, [
        os.getenv('CUDNN_INCLUDE_DIR'),
        os.path.join(CUDA_HOME, 'include'),
        '/usr/include/',
    ] + gather_paths([
        'CPATH',
        'C_INCLUDE_PATH',
        'CPLUS_INCLUDE_PATH',
    ])))
    if is_conda:
        lib_paths.append(os.path.join(conda_dir, 'lib'))
        include_paths.append(os.path.join(conda_dir, 'include'))
    for path in lib_paths:
        if path is None or not os.path.exists(path):
            continue
        if glob.glob(os.path.join(path, 'libcudnn*')):
            CUDNN_LIB_DIR = path
            break
    for path in include_paths:
        if path is None or not os.path.exists(path):
            continue
        if os.path.exists((os.path.join(path, 'cudnn.h'))):
            CUDNN_INCLUDE_DIR = path
            break
    if not CUDNN_LIB_DIR or not CUDNN_INCLUDE_DIR:
        CUDNN_LIB_DIR = CUDNN_INCLUDE_DIR = None
    else:
        WITH_CUDNN = True
