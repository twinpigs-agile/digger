"""
Import this file ONLY after setting the LANGUAGE variable in the main module!
You should assign a locale name to it ("en_US", "ru_RU", etc.)
If you initialise the locale somewhere else, still do it before the first
import of settings and use something like:
setattr(sys.modules["__main__"], "LANGUAGE", "en_US")
"""

import os.path
import gettext
import sys

MAIN_MODULE = sys.modules["__main__"]

# Keep this flag enabled
NO_DISPLAY_ON_TEST = True
ASSERT_VIEW_ZOOM = 32

NO_REAL_VIDEO = False

if NO_DISPLAY_ON_TEST and not hasattr(MAIN_MODULE, "MAIN_ASSETS"):
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    NO_REAL_VIDEO = True

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = getattr(sys, "_MEIPASS", SRC_DIR)  # PyInstaller support

LOCALES_DIR = os.path.join(SRC_DIR, "locales")

ASSETS_DIR = "assets" if hasattr(MAIN_MODULE, "MAIN_ASSETS") else "test_assets"

if hasattr(sys, "_MEIPASS"):  # pragma: no cover
    ASSETS_DIR = os.path.join(getattr(sys, "_MEIPASS"), "assets.zip", ASSETS_DIR)
else:
    ASSETS_DIR = os.path.join(os.path.dirname(SRC_DIR), ASSETS_DIR)

print("ASSETS_DIR =", ASSETS_DIR)


def asset_path(asset: str) -> str:
    return os.path.join(ASSETS_DIR, asset)


if SRC_DIR not in sys.path:  # pragma: no cover
    sys.path.append(SRC_DIR)

LANGUAGE = getattr(MAIN_MODULE, "LANGUAGE", "en_US")

TRANSLATION = gettext.translation(
    "messages", localedir=LOCALES_DIR, languages=[LANGUAGE]
)
_ = TRANSLATION.gettext
