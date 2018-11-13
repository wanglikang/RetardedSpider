# -*- coding: utf-8 -*-
import re
import time
import numpy  as np
import matplotlib.pyplot as plt
def testfunc1():
    fig = plt.figure()  # an empty figure with no axes
    fig.suptitle('No axes on this figure')  # Add a title so we know which it is

    fig, ax_lst = plt.subplots(2, 2)  # a figure with a 2x2 grid of Axes

    fig.show()

def testfunc2():
    data = {'a': np.arange(50),
            'c': np.random.randint(0, 50, 50),
            'd': np.random.randn(50)}
    data['b'] = data['a'] + 10 * np.random.randn(50)
    data['d'] = np.abs(data['d']) * 100

    plt.scatter('a', 'b', c='d', s='d', data=data)
    plt.xlabel('entry a')
    plt.ylabel('entry b')
    plt.show()
testfunc2()