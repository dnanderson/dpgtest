import multiprocessing as mp
from multiprocessing import connection
import threading
import time
import dataclasses
from typing import Callable
from PySide6 import QtWidgets, QtCore
import numpy as np
import logging


SAMPLE_BLOCK_SIZE = 101


@dataclasses.dataclass
class TestContext:
    tsocket: int 
    serial: str
    operator: str
    sm: mp.RawArray
    sm_c: mp.Condition
    conn: connection.Connection


# Handles details related to the currently running process executing a top level
# test, and also has references to the main GUI to update data related to the
# live view of the executing test

# Details -> Needs a ipc method for communicating large floating point arrays
## Probably shared memory here
# Needs an ipc method for communicating the state of the running tests
## Probably use a pipe here
# Needs an ipc method for communicating various other information, like current power 
## Probably use a pipe
# rail measurements or whether certain events have happened
## Probably use a pipe
# Basically a really generic means of communicating random things
# Needs an ipc method for logging data 

class TestExecution:
    def __init__(self, guiref, tsocket, serial, entry, operator, name='Default Name'):
        self.sm = mp.RawArray('f', SAMPLE_BLOCK_SIZE)
        self.sm_c = mp.Condition(lock=mp.Lock())
        self.con, self.conn2 = mp.Pipe()
        self.ctx = TestContext(tsocket, serial, operator, self.sm, self.sm_c, self.conn2)
        self.name = name
        self.entry = entry
        self.guiref = guiref


        self._condthr_close = threading.Event()
        self._connthr_close = threading.Event()
        self.sm_worker = SmWorker(self.sm, self.sm_c, self._condthr_close)
        self.conn_worker = ConnWorker(self.con, self._connthr_close)
        self._sm_worker_thr = QtCore.QThread()
        self._conn_worker_thr = QtCore.QThread()

        self.sm_worker.moveToThread(self._sm_worker_thr)
        self.conn_worker.moveToThread(self._conn_worker_thr)
        self._sm_worker_thr.started.connect(self.sm_worker.run)
        self._conn_worker_thr.started.connect(self.conn_worker.run)
        self._sm_worker_thr.finished.connect(self._sm_worker_thr.deleteLater)
        self._conn_worker_thr.finished.connect(self._conn_worker_thr.deleteLater)
        self.sm_worker.finished.connect(self.sm_worker.deleteLater)
        self.conn_worker.finished.connect(self.conn_worker.deleteLater)
        self.sm_worker.progress.connect(guiref.update_generic)
        self.conn_worker.progress.connect(guiref.update_generic)


    def run(self):
        kwargs = {'context': self.ctx}
        self.proc = mp.Process(group=None, target=self.entry, kwargs=kwargs, name=self.name)
        self.proc.start()
        self._sm_worker_thr.start()
        #self._conn_worker_thr.start()
    
    def finalize(self):
        self._condthr_close.set()
        self._connthr_close.set()
        self._condthr.join()
        self._connthr.join()


class SmWorker(QtCore.QObject):
    finished = QtCore.Signal()
    progress = QtCore.Signal(object)

    def __init__(self, sm, sm_c, closeevent):
        super().__init__()
        self.sm = sm
        self.sm_c = sm_c
        self.closeevent = closeevent

    def run(self):
        """
        Some long running task
        """
        while True:
            time.sleep(0.05)
            t = np.linspace(0, 10, 101)
            self.progress.emit(np.sin(t + time.time()))
            logging.debug('bug')
        self.finished.emit()
    

class ConnWorker(QtCore.QObject):
    finished = QtCore.Signal()
    progress = QtCore.Signal(object)

    def __init__(self, conn, closeevent):
        super().__init__()
        self.conn = conn
        self.closeevent = closeevent

    def run(self):
        """
        Some long running task
        """
        for i in range(5):
            time.sleep(1)
            self.progress.emit([i + 1])
        self.finished.emit()

if __name__ == '__main__':
    pass
    
