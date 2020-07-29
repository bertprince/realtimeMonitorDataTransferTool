# -*- coding: utf-8 -*-
import time
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from watchdog.observers import Observer
from watchdog.events import *

a = r"C:\Users\123\Desktop\DisplacementMon\Test"


class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print("文件被修改了 %s" % event.src_path)

    def on_created(self, event):
        print("文件被创建了 %s" % event.src_path)


if __name__ == "__main__":
    path = a
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()
    observer.join()





