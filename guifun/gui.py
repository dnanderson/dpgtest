#sudo apt-get install python3-tk
#pip install dearpygui numpy

import dearpygui.dearpygui as dpg
import math
import time
import threading
import numpy as np
import multiprocessing
import tests
import inspect
import importlib
from tkinter import filedialog

class Functions:
    def __init__(self):
        self.__t0 = None
        self.__datX = []
        self.__datY = []
        self.__nsamples = 0
        self.__thread_active = True
        self.labelX = ["X-axis"]
        self.labelY = ["Y-axis"]

    def data_reset(self):
        self.__datX = []
        self.__datY = []
        self.__t0 = None

    def stop_threads(self):
        self.__thread_active = False

    def data_update(self):
        frequency = 0.3
        while self.__thread_active:
            # Get new data sample. Note we need both x and y values
            # if we want a meaningful axis unit.
            if not self.__t0:
                self.__t0 = time.time()
            t = time.time() - self.__t0
            y = math.sin(2.0 * math.pi * frequency * t)
            self.__datX.append(t)
            self.__datY.append(y)

            # set the series x and y to the last nsamples
            dpg.set_value("series_tag", [self.__datX[-self.__nsamples:], self.__datY[-self.__nsamples:]])
            #dpg.fit_axis_data("x_axis")
            #dpg.fit_axis_data("y_axis")
            
            time.sleep(0.05)
        return False
    
    def checkbox(self):
        if dpg.get_value("checkbox"):
            self.__nsamples = 100
        else:
            self.__nsamples = 0


class TestLiveView:
    def __init__(self):
        self.__functions = Functions()

    def __gui_body(self):
        with dpg.window(label="Live View", tag="live_view", width=1000, height=800):
            dpg.add_button(label="Reset data", callback=self.__functions.data_reset)
            dpg.add_checkbox(label="Show last 100 samples", tag="checkbox", callback=self.__functions.checkbox)
            with dpg.plot(label="V1Mon Scaled", height=-1, width=-1):
                # optionally create legend
                dpg.add_plot_legend()

                # REQUIRED: create x and y axes, set to auto scale.
                dpg.add_plot_axis(dpg.mvXAxis, label=self.__functions.labelX[0], tag="x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label=self.__functions.labelY[0], tag="y_axis")
                
                # series belong to a y axis. Note the tag name is used in the update
                # function data_update
                dpg.add_line_series(x=list([]), y=list([]), label="V1Mon", parent="y_axis", tag="series_tag")


            
    def __process_start(self):
        thread = threading.Thread(target=self.__functions.data_update)
        thread.start()

    def __cleanup(self):
        self.__functions.stop_threads()

    def app_run(self):
        self.__gui_body()
        self.__process_start()
        self.__cleanup()

class TestSelector:
    """
    Presents an initial window used for selecting the tests to be run
    """
    def __init__(self):
        pass

    def start(self):
        self.param_window = None
        with dpg.window(label='Test Selector', tag='test_selector', width=500, height=500):
            dpg.add_text("Select a test entry point")
            dpg.add_listbox(list(tests.exported_tests.keys()), tag='test_sel_listbox', callback=self._selected_test)
            dpg.add_button(label='Refresh test list', callback=self._refresh_test_list)
    
    def _refresh_test_list(self, sender, app_data, user_data):
        global tests
        print(sender, app_data, user_data)
        tests = importlib.reload(tests)
        dpg.configure_item('test_sel_listbox', items=list(tests.exported_tests.keys()))

    def _selected_test(self, sender, app_data, user_data):
        if self.param_window is not None:
            dpg.delete_item(self.param_window)
        print(sender, app_data, user_data)
        ent = tests.exported_tests[app_data]
        sig = inspect.signature(ent)
        print(sig.parameters)
        print(inspect.getdoc(ent))
        for x, y in sig.parameters.items():
            print(x, y)
        self.param_window = dpg.add_child_window(label='Parameters', parent='test_selector')
        dpg.add_text(f'Enter Parameters for {app_data}', parent=self.param_window)






if __name__ == '__main__':
    dpg.create_context()
    dpg.create_viewport(title="QT", width=1280, height=1000)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    # app = TestLiveView()
    # app.app_run()
    app = TestSelector()
    app.start()
    dpg.start_dearpygui()
    dpg.destroy_context()