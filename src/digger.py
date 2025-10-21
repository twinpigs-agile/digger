import argparse
import sys
from current_version import VERSION

MAIN_ASSETS = True  # Sign to use main set of assets, not the test assets

SUPPORTED_LANGUAGES = {"en": "en_US", "ru": "ru_RU"}
LANGUAGE = "en_US"


def process_cmdline() -> int:
    parser = argparse.ArgumentParser(
        prog="python-gamedata-prj",
        usage=f"%(prog)s [options]\npython-gamedata-prj {VERSION}",
    )
    parser.add_argument(
        "--list-lang",
        action="store_true",
        help="list supported languages and exit",
    )
    parser.add_argument(
        "--lang",
        type=str,
        default="en",
        help="language code to use (default: en)",
    )
    args = parser.parse_args()
    if args.list_lang:
        print("Supported languages:")
        for lang in SUPPORTED_LANGUAGES:
            print(f" - {lang}")
        return 0
    if args.lang not in SUPPORTED_LANGUAGES:
        print(
            f"Error: unsupported language '{args.lang}'. Supported languages are: {', '.join(SUPPORTED_LANGUAGES)}",
            file=sys.stderr,
        )
    global LANGUAGE
    LANGUAGE = SUPPORTED_LANGUAGES[args.lang]
    import settings

    getattr(settings, "LANGUAGE", LANGUAGE)  # Avoiding flake8 problems

    from game.main import main

    return main()


if __name__ == "__main__":
    sys.exit(process_cmdline())
