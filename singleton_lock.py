#!/usr/bin/env python3
"""
Singleton lock to prevent multiple instances running
"""
import os
import sys
import fcntl

LOCK_FILE = "/tmp/digiseller_check.lock"

def acquire_lock():
    """Acquire exclusive lock, return False if already locked"""
    lock_fp = open(LOCK_FILE, 'w')
    try:
        fcntl.flock(lock_fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_fp.write(str(os.getpid()))
        lock_fp.flush()
        return lock_fp
    except (IOError, OSError):
        lock_fp.close()
        return None

def release_lock(lock_fp):
    """Release lock and close file"""
    if lock_fp:
        fcntl.flock(lock_fp.fileno(), fcntl.LOCK_UN)
        lock_fp.close()
        try:
            os.unlink(LOCK_FILE)
        except:
            pass

# Example usage:
# lock = acquire_lock()
# if not lock:
#     print("Already running, exiting")
#     sys.exit(1)
# 
# try:
#     # ... do work ...
# finally:
#     release_lock(lock)
