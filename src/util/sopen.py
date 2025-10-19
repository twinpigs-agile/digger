# REGISTER_DOCTEST
import os
from typing import BinaryIO
from fs.zipfs import ZipFS


def smart_open(path: str | os.PathLike[str]) -> BinaryIO:
    """
    Opens a file transparently, supporting access to files inside ZIP archives.

    Examples:
        >>> import zipfile, tempfile
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     # Create a regular file
        ...     file_path = os.path.join(tmpdir, "file.txt")
        ...     with open(file_path, "wb") as f:
        ...         _ = f.write(b"regular content")
        ...     mixed_path = file_path.replace("/", "\\\\")  # simulate mixed slashes
        ...     with smart_open(mixed_path) as f:
        ...         assert f.read() == b"regular content"
        ...     # Create a zip archive with a file inside
        ...     zip_path = os.path.join(tmpdir, "archive.zip")
        ...     with zipfile.ZipFile(zip_path, "w") as zf:
        ...         _ = zf.writestr("inner.txt", "zip content")
        ...     zip_inner_path = zip_path.replace("\\\\", "/") + "/inner.txt"
        ...     with smart_open(zip_inner_path) as f:
        ...         assert f.read() == b"zip content"
    """
    path_str = str(path).replace("\\", "/")
    zip_marker = ".zip/"
    if zip_marker in path_str:
        zip_path, inner_path = path_str.split(zip_marker, 1)
        zip_path += ".zip"
        zip_path = os.path.abspath(os.path.expanduser(zip_path))
        zip_fs = ZipFS(zip_path)
        return zip_fs.openbin(inner_path)
    else:
        return open(os.path.abspath(os.path.expanduser(path_str)), "rb")
