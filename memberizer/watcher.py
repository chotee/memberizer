import os
import sys
from fcntl import fcntl, F_NOTIFY, DN_MODIFY, DN_CREATE
from signal import signal, pause, SIGIO
import py

import logging

import logging
log = logging.getLogger('m2a.'+__name__)


def find_changed_file(directory_name):
    """I find which files where changed in a directory."""
    def file_sorter(a,b):
        """I sort files so that last changed comes first."""
        if a.mtime() < b.mtime():
            return 1
        return -1
    def file_filter(a):
        if a.check(dir=1):
            return False
        return True

    fn = directory_name.listdir(fil=file_filter, sort=file_sorter)[0]
    log.info("Selected file is '%s'", fn)
    return fn

def directory_watcher(dir_to_watch):
    """I watch a directory and return the file that was changed in the directory."""
    dir_to_watch = py.path.local(dir_to_watch)
    changed_file = []
    def handler(signum, frame):
        log.debug("Detected directory change.")
        changed_file.append(find_changed_file(dir_to_watch))
    try:
        fd = os.open(unicode(dir_to_watch), os.O_RDONLY)
        fcntl(fd, F_NOTIFY, DN_MODIFY|DN_CREATE)
        signal(SIGIO, handler)
        log.info("Watching for new file in '%s'", dir_to_watch)
        pause()
        return changed_file.pop()
    except KeyboardInterrupt:
        log.fatal("Got CTRL-C. Ending process.")
        sys.exit()