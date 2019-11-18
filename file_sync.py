#!/usr/bin/python
import sys
import time
import ntpath
import os
import re
import platform

from subprocess import call
from shutil import copy
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Git root path for files to push to remote.
DIR_FOR_GIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Files to synchronize.
SYNC_FILE_LIST = []
with open(os.path.join(DIR_FOR_GIT, 'file_list.txt'), 'r') as f:
    SYNC_FILE_LIST = [os.path.join(DIR_FOR_GIT, line.strip()) for line in f]

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        src_path = event.src_path.replace('\\', '/')
        if src_path in SYNC_FILE_LIST:
            print(f'{src_path} changed. Syncing...')
            copy(src_path, DIR_FOR_GIT)
            os.chdir(DIR_FOR_GIT)
            git_add_cmd = 'git add -A'
            git_commit_cmd = 'git commit -m ' + \
                re.escape('Update '+os.path.basename(src_path))
            if platform.system() == 'Windows':
                git_commit_cmd = 'git commit -m Update.'
            git_pull_cmd = 'git pull origin master'
            git_push_cmd = 'git push origin master'
            call(
                git_add_cmd + '&&' +
                git_commit_cmd + '&&' +
                git_pull_cmd + '&&' +
                git_push_cmd,
                shell=True
            )
            print('Sync complete')


if __name__ == '__main__':
    observer = Observer()
    event_handler = FileChangeHandler()

    for file_path in SYNC_FILE_LIST:
        observer.schedule(event_handler, path=os.path.dirname(
            file_path), recursive=False)

    observer.start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
