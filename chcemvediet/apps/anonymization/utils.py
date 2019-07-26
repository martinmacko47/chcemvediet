import tempfile
import shutil
from contextlib import contextmanager


@contextmanager
def temporary_directory(*args, **kwargs):
    directory_name = tempfile.mkdtemp(*args, **kwargs)
    try:
        yield directory_name
    finally:
        shutil.rmtree(directory_name)
