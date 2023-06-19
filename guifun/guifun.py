import dearpygui.dearpygui as dpg
dpg.create_context()

import threading

from math import sin

from collections import deque

import time


def generate_data(datax, datay, start):
    for x in range(start, start+10):
        datay.append(sin(x))

def update_plot():
    data_x = [x for x in range(100)]
    data_y = deque([], maxlen=100)
    dpg.add_line_series(data_x, list(data_y), tag='line', parent='testp')
    start = 0
    while True:
        generate_data(data_x, data_y, start)
        dpg.set_value('line', [data_x, list(data_y)])
        start += 10
        time.sleep(.5)

with dpg.window():
    with dpg.plot(label="Line Test", height=400, width=500, tag='plottest', ):
        
        xaxis = dpg.add_plot_axis(dpg.mvXAxis, label="x")
        yaxis = dpg.add_plot_axis(dpg.mvYAxis, label="y", tag='testp')
        
dpg.create_viewport(width=900, height=600, title='Updating plot data')
dpg.setup_dearpygui()
thread = threading.Thread(target=update_plot)
thread.start()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()