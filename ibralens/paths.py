import os
import sys

APP_NAME = "IBRA LENS"
VERSION = "1.1.0"
REPO = "ibrata2/ibra-lens"


def base_dir():
    """مجلد البرنامج (بجانب exe عند التنصيب، أو جذر المشروع أثناء التطوير)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def res_dir():
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", base_dir())
    return os.path.dirname(os.path.abspath(__file__))


def asset(name):
    p = os.path.join(res_dir(), "assets", name)
    if not os.path.exists(p):
        p = os.path.join(res_dir(), "ibralens", "assets", name)
    return p


def models_dir():
    env = os.environ.get("IBRALENS_MODELS")
    if env:
        return env
    return os.path.join(base_dir(), "models")


def data_dir():
    root = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), ".local", "share")
    d = os.path.join(root, "IBRA LENS")
    os.makedirs(d, exist_ok=True)
    return d
