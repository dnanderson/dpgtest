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
from collections import deque
import test_execution


class TestLiveView:
    def __init__(self):
        self._num_retained = 1000
        self._daty = deque(maxlen=self._num_retained)
        self._daty.extend([0] * self._num_retained)
        self._datx = [x for x in range(1000)]

    def show(self):
        with dpg.window(label="Live View", tag="live_view", width=1000, height=800):
            with dpg.child_window(width=1000, height=400, autosize_x=True):
                with dpg.plot(label="V1Mon Scaled", height=-1, width=-1):
                    # optionally create legend
                    dpg.add_plot_legend()

                    # REQUIRED: create x and y axes, set to auto scale.
                    dpg.add_plot_axis(dpg.mvXAxis, label='Time', tag="x_axis")
                    dpg.add_plot_axis(dpg.mvYAxis, label='Voltage', tag="y_axis")
                    
                    # series belong to a y axis. Note the tag name is used in the update
                    # function data_update
                    dpg.add_line_series(x=[], y=[], label="V1Mon", parent="y_axis", tag="series_tag")
            
            # Other widget ideas we need
            # A updatable counter for ctf / With clear?
            dpg.add_separator()
            dpg.add_text(tag='last_3_3v', default_value='3.3v')
            dpg.add_text(tag='last_12v', default_value='12v')
            dpg.add_text(tag='last_inta', default_value='0v')
            dpg.add_text(tag='last_state', default_value='0')
            # A widget showing the current executing test, past tests, and their progress
            # An updatable reading for 3.3/12v
            # An updatable reading for inta
            # A log window
    

    def upd_plot(self, new_values):
        self._daty.extend(new_values)
        dpg.set_value("series_tag", [list(self._datx), list(self._daty)])
        dpg.fit_axis_data("x_axis")

class TestSelector:
    """
    Presents an initial window used for selecting the tests to be run
    """
    def __init__(self):
        pass

    def start(self):
        self.param_window = None
        with dpg.window(label='Test Selector', tag='test_selector', width=500, height=500):

            dpg.add_input_text(label='Operator Name', tag='operator_name')
            dpg.add_separator()
            dpg.add_text("Select a test entry point")
            dpg.add_listbox(list(tests.exported_tests.keys()), tag='test_sel_listbox', callback=self._selected_test, num_items=15)
            dpg.add_input_text(label='DUT Serial', tag='dut_serial')
            dpg.add_input_int(label='Socket', default_value=0, tag='socket_val', min_value=0, max_value=2, min_clamped=True, max_clamped=True)
            dpg.add_button(label='Refresh test list', callback=self._refresh_test_list)
            dpg.add_button(label='Run Selected Test', callback=self._exec_selected_test)
    
    def _refresh_test_list(self, sender, app_data, user_data):
        global tests
        tests = importlib.reload(tests)
        dpg.configure_item('test_sel_listbox', items=list(tests.exported_tests.keys()))

    def _selected_test(self, sender, app_data, user_data):
        if self.param_window is not None:
            dpg.delete_item(self.param_window)
        ent = tests.exported_tests[app_data]
        sig = inspect.signature(ent)
        #print(sig.parameters)
        #print(inspect.getdoc(ent))
        #for x, y in sig.parameters.items():
        #    print(x, y)
        #self.param_window = dpg.add_child_window(label='Parameters', parent='test_selector')
        #dpg.add_text(f'Enter Parameters for {app_data}', parent=self.param_window)
    
    def _exec_selected_test(self):
        selected_test = dpg.get_value('test_sel_listbox')
        rn = tests.exported_tests[selected_test]
        tlv = TestLiveView()
        te = test_execution.TestExecution(tlv,
                                          dpg.get_value('socket_val'),
                                          dpg.get_value('dut_serial'),
                                          rn(),
                                          dpg.get_value('operator_name'))
        tlv.show()
        te.run()

    






if __name__ == '__main__':
    dpg.create_context()
    dpg.create_viewport(title="QT", width=1280, height=1000)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    #app = TestLiveView()
    #app.app_run()
    app = TestSelector()
    app.start()
    dpg.start_dearpygui()
    dpg.destroy_context()