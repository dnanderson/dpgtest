#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os        # For strerror
import mmap      # For setting up a shared memory region
import ctypes    # For doing the actual wrapping of librt & rwlock
import platform  # To figure which architecture we're running in
import time

if platform.system() != 'Windows':
    raise Exception("Unsupported operating system.")

from ctypes import windll, wintypes, Structure  # nopep8
k32 = windll.kernel32

# Augment the Win32 functions we need
API_W32 = [
    ('CreateMutexA', [wintypes.LPCVOID, wintypes.BOOL, wintypes.LPCSTR], wintypes.HANDLE),  # nopep8
    ('WaitForSingleObject', [wintypes.HANDLE, wintypes.DWORD], wintypes.DWORD),
    ('WaitForMultipleObjects', [wintypes.DWORD, wintypes.LPVOID,
                                wintypes.BOOL, wintypes.DWORD], wintypes.DWORD),
    ('ReleaseMutex', [wintypes.HANDLE], wintypes.BOOL),
    ('CloseHandle', [wintypes.HANDLE], wintypes.BOOL)
]


def augment_function(library, name, argtypes, restype):
    function = getattr(library, name)
    function.argtypes = argtypes
    function.restype = restype

for function, argtypes, restype in API_W32:
    augment_function(k32, function, argtypes, restype)

INFINITE = 0xFFFFFFFF
SHORT_SLEEP = 0.10


def acquire_mutex(handle, milliseconds=INFINITE):
    r = k32.WaitForSingleObject(handle, milliseconds)
    if r in (0, 0x80):
        # No distinction is made between normally acquired (0) and acquired
        # because another owning process terminated without releasing (0x80)
        return True
    elif r == 0x102:
        # Timeout
        return False
    else:
        # Wait failed
        raise ctypes.WinError()


def acquire_mutexes(handles, milliseconds=INFINITE, wait_all=True):
    n_handles = len(handles)
    handle_array_type = ctypes.c_void_p * n_handles
    handles = handle_array_type(*handles)
    r = k32.WaitForMultipleObjects(n_handles, handles, bool(wait_all), milliseconds)
    if 0x0 <= r <= n_handles-1 or 0x80 <= r <= 0x80 + n_handles-1:
        # No distinction is made between normally acquired (0) and acquired
        # because another owning process terminated without releasing (0x80)
        return True
    elif r == 0x102:
        # Timeout
        return False
    else:
        # Wait failed
        raise ctypes.WinError()


# By default, mutexes are not inherited when a new process is created.
# We need to provide security attributes that allow the mutexes to be
# shared by the synchronized processes. For more detail, see:
# https://msdn.microsoft.com/en-us/library/windows/desktop/aa379560(v=vs.85).aspx

# SECURITY_ATTRIBUTES struct used for enabling shared mutexes between processes
class SecurityAttributes(Structure):
    _fields_ = [("nLength", wintypes.DWORD),
                ("lpSecurityDescriptor", wintypes.LPVOID),
                ("bInheritHandle", wintypes.BOOL)]


class RWLock(object):
    def __init__(self, tag):
        self.pid = os.getpid()

        try:
            # Define these guards so we know which attribution has failed
            buf, wr_mutex, rd_mutex, mtag = None, None, None, None

            mtag = f"rwlock-{tag}"

            # File descriptors are not shared across processes on Windows,
            # but an alternative is to use named shared memory:
            # https://msdn.microsoft.com/en-us/library/windows/desktop/aa366551(v=vs.85).aspx
            # Setting the underlying mmap fd to 0, will force it to use named
            # shared memory accessible via the provided memory tag.  Also, mmap
            # allocates page sized chunks, and the data structures we use are
            # smaller than a page. Therefore, we request a whole page
            buf = mmap.mmap(0, mmap.PAGESIZE, mtag)
            buf.seek(0)

            # Number of readers and the ID of the process that holds
            # the writer mutex; it has value 0 if the mutex is not taken
            writer_pid = ctypes.c_int.from_buffer(buf)
            offset = ctypes.sizeof(ctypes.c_int)
            n_readers = ctypes.c_int.from_buffer(buf, offset)

            sa = SecurityAttributes(ctypes.sizeof(SecurityAttributes), None, True)
            rd_mutex = k32.CreateMutexA(ctypes.byref(sa), False, f"mt-rd-{tag}".encode())
            wr_mutex = k32.CreateMutexA(ctypes.byref(sa), False, f"mt-wr-{tag}".encode())

            # Finally initialize this instance's members
            self._buf = buf
            self._rd_mutex = rd_mutex
            self._wr_mutex = wr_mutex
            self._writer_pid = writer_pid
            self._n_readers = n_readers
    
        except:
            if rd_mutex:
                k32.CloseHandle(rd_mutex)
            if wr_mutex:
                k32.CloseHandle(wr_mutex)
            if buf:
                try:
                    buf.close()
                except:
                    pass
            raise

    def acquire_read(self, timeout=None):
        """acquire_read([timeout=None])

        Request a read lock, returning True if the lock is acquired;
        False otherwise. If provided, *timeout* specifies the number of
        seconds to wait for the lock before cancelling and returning False.
        """
        milliseconds = INFINITE if timeout is None else int(0)
        time_wait = 0.0
        while True:
            if acquire_mutex(self._rd_mutex, milliseconds):
                if self._writer_pid.value == 0:
                    self._n_readers.value += 1
                    k32.ReleaseMutex(self._rd_mutex)
                    return True
                k32.ReleaseMutex(self._rd_mutex)
            if timeout is not None and time_wait >= timeout:
                return False
            time.sleep(SHORT_SLEEP)
            time_wait += SHORT_SLEEP

    def try_acquire_read(self):
        """Try to obtain a read lock, immediately returning True if
        the lock is acquired; False otherwise.
        """
        return self.acquire_read(timeout=0.0)

    # If provided, timeout is used as an approximate time limit for execution
    def _wait_readers(self, timeout):
        # Wait until active readers complete
        milliseconds = INFINITE if timeout is None else 0
        while True:
            acquire_mutex(self._rd_mutex, milliseconds)
            if self._n_readers.value == 0:
                k32.ReleaseMutex(self._rd_mutex)
                return True
            elif timeout is not None:
                if timeout < 0.0:
                    # Change the PID that holds the write mutex back to zero
                    # and release the write mutex as timeout expired
                    self._writer_pid.value = 0
                    k32.ReleaseMutex(self._wr_mutex)
                    k32.ReleaseMutex(self._rd_mutex)
                    return False
                timeout -= SHORT_SLEEP
            k32.ReleaseMutex(self._rd_mutex)
            time.sleep(SHORT_SLEEP)

    def acquire_write(self, timeout=None):
        """acquire_write([timeout=None])

        Request a write lock, returning True if the lock is acquired;
        False otherwise. If provided, *timeout* specifies the number of
        seconds to wait for the lock before cancelling and returning False.
        """
        milliseconds = INFINITE
        if timeout is not None:
            start = time.clock()
            milliseconds = int(timeout * 1000)
        # Timeout is first used to acquire both writer and reader mutexes
        if acquire_mutexes([self._wr_mutex, self._rd_mutex]):
            # block new readers
            self._writer_pid.value = int(self.pid)
            k32.ReleaseMutex(self._rd_mutex)
            # Compute the remaining time before timeout expires
            time_remain = None if timeout is None else timeout - (time.clock() - start)
            return self._wait_readers(time_remain)
        else:
            return False

    def try_acquire_write(self):
        """Try to obtain a write lock. Return True immediately if
        the lock can be acquired; False otherwise.
        """
        return self.acquire_write(timeout=0.0)

    def release(self):
        """Release a previously acquired read/write lock.
        """
        acquire_mutex(self._rd_mutex)
        if self._writer_pid.value != self.pid:
            if self._n_readers.value == 0:
                k32.ReleaseMutex(self._rd_mutex)
                raise ValueError(
                    'Tried to release a released lock'
                )
            self._n_readers.value -= 1
            k32.ReleaseMutex(self._rd_mutex)
        else:
            self._writer_pid.value = 0
            k32.ReleaseMutex(self._rd_mutex)
            k32.ReleaseMutex(self._wr_mutex)
    
    def close(self):
        k32.CloseHandle(self._rd_mutex)
        k32.CloseHandle(self._wr_mutex)
        del self._wr_mutex
        del self._rd_mutex
        del self._writer_pid
        del self._n_readers
        self._buf.close()
