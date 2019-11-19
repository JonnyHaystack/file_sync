#!/usr/bin/python
import time
import os
import re
import platform

from subprocess import call
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Git root path for files to push to remote.
DIR_FOR_GIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Files to synchronize.
SYNC_FILE_LIST = []
with open(os.path.join(DIR_FOR_GIT, 'file_list.txt'), 'r') as f:
    for line in f:
        path = os.path.realpath(os.path.join(DIR_FOR_GIT, line.strip()))
        SYNC_FILE_LIST.append(path)
print(SYNC_FILE_LIST)


def sync(pathname):
    print(f'{pathname} changed. Syncing...')
    os.chdir(DIR_FOR_GIT)
    git_add_cmd = 'git add -A'
    git_commit_cmd = 'git commit -m ' + \
        re.escape('Update ' + os.path.basename(pathname))
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


class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(event)
        src_path = event.src_path.replace('\\', '/')
        if src_path in SYNC_FILE_LIST:
            sync(src_path)

    def on_moved(self, event):
        print(event)
        dest_path = event.dest_path.replace('\\', '/')
        if dest_path in SYNC_FILE_LIST:
            sync(dest_path)

    def on_created(self, event):
        print(event)
        src_path = event.src_path.replace('\\', '/')
        if src_path in SYNC_FILE_LIST:
            sync(src_path)


if __name__ == '__main__':
    observer = Observer()
    event_handler = FileChangeHandler()

    for file_path in SYNC_FILE_LIST:
        observer.schedule(
            event_handler,
            path=os.path.dirname(os.path.realpath(file_path)),
            recursive=False,
        )

    observer.start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
