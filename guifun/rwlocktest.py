from __future__ import print_function

import os
import time

from multiprocessing import Pool, freeze_support, Process, shared_memory
from rwlock import RWLock
import mmap
import ctypes
import random
from fasteners import InterProcessReaderWriterLock
import atomics
from struct import pack, unpack

# class TestProc(Process):
#     def run(self):
#         # l = InterProcessReaderWriterLock('lockfile')
#         l = RWLock('mylock')
#         buf = mmap.mmap(0, mmap.PAGESIZE, 'mymem2')
#         buf.seek(0)
#         for x in range(200):
#             l.acquire_write()
#             intval = ctypes.c_int.from_buffer(buf)
#             intval.value += 1
#             l.release()
#             time.sleep(0.001)
#         time.sleep(.02)
#         print('done here first')
#         for x in range(200):
#             l.acquire_write()
#             intval = ctypes.c_int.from_buffer(buf)
#             intval.value -= 1
#             l.release()
#             time.sleep(0.001)
#         print('done here second')

class TestProc(Process):
    def run(self):
        buf2 = mmap.mmap(0, mmap.PAGESIZE, 'mymem2')
        buf = memoryview(buf2)

        # shmem = shared_memory.SharedMemory('mymem2', create=False, size=4096)
        # buf = shmem.buf
        x = 0.0 
        with atomics.atomicview(buffer=buf[0:8], atype=atomics.BYTES) as a:
            for x in range(20000):
                x += 1
                b = pack('d', x)
                a.store(b)
        print('done here first')
        # shmem.close()

class TestProcRead(Process):
    def run(self):
        # l = InterProcessReaderWriterLock('lockfile')
        # l = RWLock('mylock')
        buf = mmap.mmap(0, mmap.PAGESIZE, 'mymem2')
        offset = self._args[0]
        value = self._args[1]
        buf.seek(0)
        for x in range(100):
            # l.acquire_read()
            with atomics.atomicview(buffer=buf[0:8], atype=atomics.BYTES) as a:
                x = a.load()
                
            floatval = unpack('d', x)
            print(floatval)
            # intval = ctypes.c_int.from_buffer(buf)
            # print(intval.value)
            # l.release()
            time.sleep(0.04)



if __name__ == '__main__':
    freeze_support()

    buf = mmap.mmap(0, mmap.PAGESIZE, 'mymem2')

    # r = RWLock()
    children = 1
    procs = []
    values = b'deadbeef'
    proc = TestProcRead(args=(0,0))
    procs.append(proc)
    proc.start()
    proc = TestProc(args=(0,0))
    procs.append(proc)
    proc.start()
    proc = TestProc(args=(0,0))
    procs.append(proc)
    proc.start()
    
    for p in procs:
        p.join()
    
    intval = ctypes.c_float.from_buffer(buf)
    print(intval.value)
    del intval
    buf.close()

    print('done')