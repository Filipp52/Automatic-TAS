"""Запустите это файл"""
import subprocess
import time
from settings import get_msc_date
import threading


def run_backpy():
    old_date = ""
    while True:
        if old_date != get_msc_date():
            old_date = get_msc_date()
            subprocess.run(["python", "main_back.py"])
        time.sleep(3600)


threading.Thread(target=run_backpy).start()
subprocess.run(["python", "main_front.py"])
