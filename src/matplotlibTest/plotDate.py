# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from matplotlib.dates import (YEARLY,MINUTELY, DateFormatter,
                              rrulewrapper, RRuleLocator, drange)
import time
import numpy as np
import matplotlib.dates  as mdates
from datetime import datetime


def example():
    # Fixing random state for reproducibility
    np.random.seed(19680801)

    # tick every 5th easter
    rule = rrulewrapper(YEARLY, byeaster=1, interval=5)
    loc = RRuleLocator(rule)
    formatter = DateFormatter('%m/%d/%y')
    date1 = datetime.date(1952, 1, 1)
    date2 = datetime.date(2004, 4, 12)
    delta = datetime.timedelta(days=100)

    dates = drange(date1, date2, delta)
    print(dates)
    s = np.random.rand(len(dates))  # make up some random y values

    fig, ax = plt.subplots()
    plt.plot_date(dates, s)
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=75, labelsize=10)

    plt.show()

def myTest():
    xdata = ["2018-01-02", "2018-01-03",
             "2018-01-04", "2018-01-05",
             "2018-01-06", "2018-01-07",
             "2018-01-08", "2018-01-09",
             "2018-01-10", "2018-01-11",
             "2018-01-12"]
    # xdata = [712588., 712688.,
    #          712788., 712888.,
    #          712988., 713088.,
    #          713188., 713288.,
    #          713388., 713488.,
    #          713588.,]
    ydata = [5424.455042071198, 5437.436073513513,
             5443.326118918919, 5453.535032397408,
             5465.99996972973,  5470.846144864865,
             5442.501206486487, 5329.997431351351,
             5311.448544864865, 5312.012034594594,
             5312.620194384449]

    rule = rrulewrapper(MINUTELY, byeaster=1, interval=5)
    loc = RRuleLocator(rule)

    formatter = DateFormatter('%Y-%m-%d')
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    xx = [datetime.strptime(x, '%Y-%m-%d') for x in xdata]
    print(xx)
    plt.plot_date(xx, ydata)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(formatter)
    plt.gcf().autofmt_xdate()
    plt.show()


myTest()
