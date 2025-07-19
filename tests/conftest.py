# ph-editor\tests\conftest.py
import os

import pytest


def pytest_sessionstart(session):
    os.system("cls" if os.name == "nt" else "clear")
