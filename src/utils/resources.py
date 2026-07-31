import sys
from pathlib import Path


def resource_path(*parts: str) -> Path:
    """
    Resolve a path to a bundled resource, working both from source and when packaged by PyInstaller
    One-file builds unpack data under sys._MEIPASS at runtime
    From source the base is the repository root (this file is src/utils/resources.py)
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent.parent.parent

    return base.joinpath(*parts)
