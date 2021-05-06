# -*- coding: utf-8 -*-

#  Copyright IAG (c) 2021.

# GRAPH TOOLS WITH MATPLOTLIB FOR KIVY
# Author: Jérémy Hraman
# Date: 03-05-2021
# Last Update: 03-05-2021

import matplotlib
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')

import numpy as np
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvas, NavigationToolbar
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

import matplotlib.pyplot as plt


class MatplotlibFigure:
    """
    class MatplotlibFigure to display graphs
    """
    def __init__(self, x_data, y_data, **kwargs):
        self.x = x_data
        self.y = y_data

        try:
            self.title = kwargs.pop('title')
        except KeyError:
            self.title = ''
        try:
            self.x_label = kwargs.pop('x_label')
        except KeyError:
            self.x_label = 'x'
        try:
            self.y_label = kwargs.pop('y_label')
        except KeyError:
            self.y_label = 'y'

        self.fig, self.ax = plt.subplots()

        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)
        self.ax.set_title(self.title)

        self.ax.plot(self.x, self.y)

        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('key_press_event', self.on_keypress)
        self.fig.canvas.mpl_connect('key_release_event', self.on_keyup)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motionnotify)
        self.fig.canvas.mpl_connect('resize_event', self.on_resize)
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.fig.canvas.mpl_connect('figure_enter_event', self.on_figure_enter)
        self.fig.canvas.mpl_connect('figure_leave_event', self.on_figure_leave)
        self.fig.canvas.mpl_connect('close_event', self.on_close)

        # MODIF FAITE PAR JEREMY LE 05/05/21 POUR SUPPRIMER LE LOGO DANS kivy/uix/actionbar.py l.274
        self.nav = NavigationToolbar(self.fig.canvas, title=self.title)


    def on_press(self, event):
        print('press released from test', event.x, event.y, event.button)

    def on_release(self, event):
        print('release released from test', event.x, event.y, event.button)

    def on_keypress(self, event):
        print('key down', event.key)

    def on_keyup(self, event):
        print('key up', event.key)

    def on_motionnotify(self, event):
        print('mouse move to ', event.x, event.y)

    def on_resize(self, event):
        print('resize from mpl ', event.width, event.height)

    def on_scroll(self, event):
        print('scroll event from mpl ', event.x, event.y, event.step)

    def on_figure_enter(self, event):
        print('figure enter mpl')

    def on_figure_leave(self, event):
        print('figure leaving mpl')

    def on_close(self, event):
        print('closing figure')

#     def.
#
# N = 5
# menMeans = (20, 35, 30, 35, 27)
# menStd = (2, 3, 4, 1, 2)

# ind = np.arange(N)  # the x locations for the groups
# width = 0.35       # the width of the bars
#
# fig, ax = plt.subplots()
# rects1 = ax.bar(ind, menMeans, width, color='r', yerr=menStd)
#
# womenMeans = (25, 32, 34, 20, 25)
# womenStd = (3, 5, 2, 3, 3)
# rects2 = ax.bar(ind + width, womenMeans, width, color='y', yerr=womenStd)
#
# # add some text for labels, title and axes ticks
# ax.set_ylabel('Scores')
# ax.set_title('Scores by group and gender')
# ax.set_xticks(ind + width)
# ax.set_xticklabels(('G1', 'G2', 'G3', 'G4', 'G5'))
# ax.legend((rects1[0], rects2[0]), ('Men', 'Women'))



# def autolabel(rects):
#     # attach some text labels
#     for rect in rects:
#         height = rect.get_height()
#         ax.text(rect.get_x() + rect.get_width() / 2., 1.05 * height,
#                 '%d' % int(height), ha='center', va='bottom')
#


# canvas = fig.canvas
#
#
# def callback(instance):
#     autolabel(rects1)
#     autolabel(rects2)
#     canvas.draw()


# class MatplotlibTest(App):
#     title = 'Matplotlib Test'
#
#     def build(self):
#         fl = BoxLayout(orientation="vertical")
#         a = Button(text="press me", height=40, size_hint_y=None)
#         a.bind(on_press=callback)
#
#         fl.add_widget(nav1.actionbar)
#         fl.add_widget(canvas)
#         fl.add_widget(a)
#         return fl
#
# if __name__ == '__main__':
#     MatplotlibTest().run()
