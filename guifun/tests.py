import math
import time
import numpy as np


class TestBase:

    def __init__():
        pass


class TestOne:
    "This is a doc string"
    def __init__(self): # This can be used to init from somewhere else
        pass

    def __call__(self, context):
        sm_c = context.sm_c
        sm = context.sm
        conn = context.conn
        t0 = time.time()
        t = t0
        while True:
            with sm_c:
                t = np.linspace(0, 10, 101)
                # Shift the sinusoid as a function of time.
                x = np.sin(t + time.time())
                






exported_tests = {
    'Bleh' : TestOne,
}
