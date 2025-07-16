import logging
import subprocess
import urllib.request
import os, sys, time, datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

script_file = __file__ or __name__ if '__main__' in __name__ else None
if script_file:
    script_dir = os.path.dirname(script_file)
else:
    print("Could not determine the script file.")
    exit()

logging.basicConfig(level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=f'{script_dir}/syncer.logs', filemode='w+')
logger = logging.getLogger(__name__)

try:
    # Attempt to get the username using os.getlogin()
    USERNAME = os.getlogin()
except OSError:
    # If os.getlogin() fails, fall back to environment variables
    USERNAME = os.getenv('USER', os.getenv('USERNAME'))
logger.info(f"Username: {USERNAME}")
def check_internet_connection():
    try:
        urllib.request.urlopen("http://www.google.com")
        return True
    except:
        return False

CREATE_NO_WINDOW = 0x08000000
class Handler(FileSystemEventHandler):
    def on_any_event(self, event):
        if ".git" in event.src_path or ".gitignore" in event.src_path:
            # logger.info("\tGit directory or ignore file detected, skipping...")
            return
        if event.event_type != "modified":
            # logger.info(f"\tSkipping other event type detected, skipping...")
            return
        subprocess.run("git pull", shell=True)
        if "\\" in event.src_path:
            # logger.info("Windows path")
            if "\\logseq\\bak" in event.src_path:
                return
            sliced_path = event.src_path.split("\\")
        else:
            # logger.info("Linux path")
            if "/logseq/bak/" in event.src_path:
                return
            sliced_path = event.src_path.split("/")
        logger.info(f"Path: {event.src_path}, EventType: {event.event_type}")
        subprocess.run("git add .", shell=True)
        subprocess.run(f"git commit -m \"{USERNAME}: New update at: {datetime.datetime.now()}\"", shell=True)
        subprocess.run("git push", shell=True)

CURRENT_DIR = ""
if __name__ == "__main__":
    _, INPUT = sys.argv
    if not INPUT:
        logger.info('Usage: python main.py INPUT')
        exit(1)
    os.chdir(INPUT)
    while not check_internet_connection():
        logger.info("No internet")
        time.sleep(5)
    logger.info("Got internet")
    os.system("git pull")

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