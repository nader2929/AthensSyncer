import logging
import subprocess
import urllib.request
import os, sys, time, platform
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

PLATFORM=f"{platform.platform()}"
print(PLATFORM)
def check_internet_connection():
    try:
        urllib.request.urlopen("http://www.google.com")
        return True
    except:
        return False

CREATE_NO_WINDOW = 0x08000000
class Handler(FileSystemEventHandler):
    def on_any_event(self, event):
        subprocess.run("git pull", shell=True)
        if event.event_type != "modified":
            return
        if "\\" in event.src_path:
            # print("Windows path")
            if "\\logseq\\bak" in event.src_path:
                return
            sliced_path = event.src_path.split("\\")
        else:
            # print("Linux path")
            if "/logseq/bak" in event.src_path:
                return
            sliced_path = event.src_path.split("/")
        # print(event.src_path)
        subprocess.run("git add .", shell=True)
        subprocess.run(f"git commit -m \"{PLATFORM}: New update at: {time.time()}\"", shell=True)
        subprocess.run("git push", shell=True)

CURRENT_DIR = ""
if __name__ == "__main__":
    _, INPUT = sys.argv
    if not INPUT:
        print('Usage: python main.py INPUT')
        exit(1)
    os.chdir(INPUT)
    while not check_internet_connection():
        print("No internet")
        time.sleep(5)
    print("Got internet")
    os.system("git pull")
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = INPUT
    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()