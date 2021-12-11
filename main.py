import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os, sys, time
import subprocess

CREATE_NO_WINDOW = 0x08000000
class Handler(FileSystemEventHandler):
    def on_any_event(self, event):
        if "\\" in event.src_path:
            print("First")
            sliced_path = event.src_path.split("\\")
        else:
            print("Second")
            sliced_path = event.src_path.split("/")
        if sliced_path[-1] != "index.transit": return
        print(event.event_type)
        print(event.src_path)
        subprocess.run("git add images/", creationflags=CREATE_NO_WINDOW)
        subprocess.run("git add index.transit", creationflags=CREATE_NO_WINDOW)
        subprocess.run(f"git commit -m \"New update at: {time.time()}\"", creationflags=CREATE_NO_WINDOW)
        subprocess.run("git push", creationflags=CREATE_NO_WINDOW)


CURRENT_DIR = ""
if __name__ == "__main__":
    _, INPUT = sys.argv
    if not INPUT:
        print('Usage: python main.py INPUT')
        exit(1)
    os.chdir(INPUT)
    os.system("git pull")
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = INPUT
    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()