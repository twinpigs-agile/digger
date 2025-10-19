# REGISTER_DOCTEST
import os
from typing import Union
from io import BytesIO
import pygame
from fs.zipfs import ZipFS


def load_image(path: Union[str, os.PathLike[str]]) -> pygame.Surface:
    """
    Loads an image from a regular file or from inside a ZIP archive.

    Examples:
        >>> import tempfile, zipfile, pygame
        >>> _ = pygame.init()
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     # Create a regular image file
        ...     file_path = os.path.join(tmpdir, "image.png")
        ...     pygame.image.save(pygame.Surface((10, 10)), file_path)
        ...     mixed_path = file_path.replace("/", "\\\\")  # simulate mixed slashes
        ...     img1 = load_image(mixed_path)
        ...     assert isinstance(img1, pygame.Surface)
        ...
        ...     # Create a zip archive with an image inside
        ...     zip_path = os.path.join(tmpdir, "archive.zip")
        ...     with zipfile.ZipFile(zip_path, "w") as zf:
        ...         zf.write(file_path, "inner.png")
        ...     zip_inner_path = zip_path.replace("\\\\", "/") + "/inner.png"
        ...     img2 = load_image(zip_inner_path)
        ...     assert isinstance(img2, pygame.Surface)
    """
    path_str = str(path).replace("\\", "/")
    zip_marker = ".zip/"
    if zip_marker in path_str:
        zip_path, inner_path = path_str.split(zip_marker, 1)
        zip_path += ".zip"
        zip_path = os.path.abspath(os.path.expanduser(zip_path))
        zip_fs = ZipFS(zip_path)
        with zip_fs.openbin(inner_path) as f:
            return pygame.image.load(BytesIO(f.read()))
    else:
        full_path = os.path.abspath(os.path.expanduser(path_str))
        return pygame.image.load(full_path)
