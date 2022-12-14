import logging
import subprocess
import os, sys, time
import urllib.request
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def check_internet_connection():
    try:
        urllib.request.urlopen("http://www.google.com")
        return True
    except:
        return False

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
        subprocess.run("git add images/", shell=True)
        subprocess.run("git add index.transit", shell=True)
        subprocess.run(f"git commit -m \"{os.getlogin()}: New update at: {time.time()}\"", shell=True)
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
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()