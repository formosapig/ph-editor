# conftest.py
import os

def pytest_sessionstart(session):
    os.system('cls' if os.name == 'nt' else 'clear')