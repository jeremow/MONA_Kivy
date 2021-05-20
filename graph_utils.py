# -*- coding: utf-8 -*-

#  Copyright IAG (c) 2021.

# GRAPH TOOLS WITH MATPLOTLIB FOR KIVY
# Author: Jérémy Hraman
# Date: 03-05-2021
# Last Update: 03-05-2021

import matplotlib
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

import matplotlib.pyplot as plt

from obspy import read, read_inventory
from obspy.core import UTCDateTime

# Style sheet created for MatplotlibFigure which implements colors for a dark background and everything
plt.style.use('./css/MONA.mplstyle')


class MatplotlibFigure(BoxLayout):
    """
    class MatplotlibFigure to display graphs in the t_curves_graph
    It includes a toolbar
    """
    def __init__(self, **kwargs):

        self.name = kwargs.pop('name', '')
        self.title = kwargs.pop('title', '')
        self.x_label = kwargs.pop('x_label', 'x')
        self.y_label = kwargs.pop('y_label', 'y')

        super(MatplotlibFigure, self).__init__()

        self.orientation = 'vertical'
        self.fig, self.ax = plt.subplots()
        self.fig.clf()

        stream = read('RD.SONA1..SHZ.D.2020.001')
        stream.plot(color='blue', grid_color=(0, 1, 1), transparent=True,
                    fig=self.fig, dpi=200,
                    starttime=stream[0].stats.starttime, endtime=stream[0].stats.starttime+20)
        self.fig.patch.set_fill(False)
        self.fig.tight_layout()

        self.xmin, self.xmax = self.fig.axes[0].get_xlim()
        self.ymin, self.ymax = self.fig.axes[0].get_ylim()

        # EVENTUAL EVENTS THAT CAN BE CAUGHT
        # self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        # self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        # self.fig.canvas.mpl_connect('key_press_event', self.on_keypress)
        # self.fig.canvas.mpl_connect('key_release_event', self.on_keyup)
        # self.fig.canvas.mpl_connect('motion_notify_event', self.on_motionnotify)
        # self.fig.canvas.mpl_connect('resize_event', self.on_resize)
        # self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        # self.fig.canvas.mpl_connect('figure_enter_event', self.on_figure_enter)
        # self.fig.canvas.mpl_connect('figure_leave_event', self.on_figure_leave)
        # self.fig.canvas.mpl_connect('close_event', self.on_close)

        # CREATION OF NAV TOOLBAR DIRECTLY IN MLPFIGURE
        self.nav_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=.2)

        self.zoomin_x = Button(background_normal='css/icons/png/zoomin_x.png',
                               background_down='css/icons/png/zoomin_x_down.png',
                               border=(0, 0, 0, 0), size=(45, 45), size_hint=(None, 1))
        self.zoomout_x = Button(background_normal='css/icons/png/zoomout_x.png',
                                background_down='css/icons/png/zoomout_x_down.png',
                                border=(0, 0, 0, 0), size=(45, 45), size_hint=(None, 1))
        self.goleft_x = Button(background_normal='css/icons/png/x_goleft.png',
                               background_down='css/icons/png/x_goleft_down.png',
                               border=(0, 0, 0, 0), size=(45, 45), size_hint=(None, 1))
        self.goright_x = Button(background_normal='css/icons/png/x_goright.png',
                                background_down='css/icons/png/x_goright_down.png',
                                border=(0, 0, 0, 0), size=(45, 45), size_hint=(None, 1))

        self.zoomin_y = Button(background_normal='css/icons/png/zoomin_y.png',
                               background_down='css/icons/png/zoomin_y_down.png',
                               border=(0, 0, 0, 0), size=(45, 45), size_hint=(None, 1))
        self.zoomout_y = Button(background_normal='css/icons/png/zoomout_y.png',
                                background_down='css/icons/png/zoomout_y_down.png',
                                border=(0, 0, 0, 0), size=(45, 45), size_hint=(None, 1))
        self.goup_y = Button(background_normal='css/icons/png/y_goup.png',
                             background_down='css/icons/png/y_goup_down.png',
                             border=(0, 0, 0, 0), size=(45, 45), size_hint=(None, 1))
        self.godown_y = Button(background_normal='css/icons/png/y_godown.png',
                               background_down='css/icons/png/y_godown_down.png',
                               border=(0, 0, 0, 0), size=(45, 45), size_hint=(None, 1))

        self.nav_layout.add_widget(Label(text=self.title, size_hint=(.3, 1)))
        self.nav_layout.add_widget(Label(text='X-axis', size_hint=(.1, 1)))
        self.nav_layout.add_widget(self.zoomin_x)
        self.nav_layout.add_widget(self.zoomout_x)
        self.nav_layout.add_widget(self.goleft_x)
        self.nav_layout.add_widget(self.goright_x)
        self.nav_layout.add_widget(Label(text=' | Y-axis', size_hint=(.1, 1)))
        self.nav_layout.add_widget(self.zoomin_y)
        self.nav_layout.add_widget(self.zoomout_y)
        self.nav_layout.add_widget(self.goup_y)
        self.nav_layout.add_widget(self.godown_y)

        self.zoomin_x.bind(on_release=self.on_zoomin_x)
        self.zoomout_x.bind(on_release=self.on_zoomout_x)
        self.goleft_x.bind(on_release=self.on_goleft_x)
        self.goright_x.bind(on_release=self.on_goright_x)
        self.zoomin_y.bind(on_release=self.on_zoomin_y)
        self.zoomout_y.bind(on_release=self.on_zoomout_y)
        self.goup_y.bind(on_release=self.on_goup_y)
        self.godown_y.bind(on_release=self.on_godown_y)

        # self.nav =
        self.add_widget(self.nav_layout)

        self.add_widget(self.fig.canvas)

    def on_zoomin_x(self, btn):
        center = (self.xmax + self.xmin) / 2
        delta = self.xmax - self.xmin
        delta *= 0.92
        delta /= 2
        self.xmin = center - delta
        self.xmax = center + delta
        self.fig.axes[0].set_xlim(self.xmin, self.xmax)
        self.fig.canvas.draw()

    def on_zoomout_x(self, btn):
        center = (self.xmax + self.xmin) / 2
        delta = self.xmax - self.xmin
        delta *= 1.08
        delta /= 2
        self.xmin = center - delta
        self.xmax = center + delta
        self.fig.axes[0].set_xlim(self.xmin, self.xmax)
        self.fig.canvas.draw()

    def on_goleft_x(self, btn):
        delta = self.xmax - self.xmin
        delta *= 0.1
        self.xmax -= delta
        self.xmin -= delta
        self.fig.axes[0].set_xlim(self.xmin, self.xmax)
        self.fig.canvas.draw()

    def on_goright_x(self, btn):
        delta = self.xmax - self.xmin
        delta *= 0.1
        self.xmax += delta
        self.xmin += delta
        self.fig.axes[0].set_xlim(self.xmin, self.xmax)
        self.fig.canvas.draw()

    def on_zoomin_y(self, btn):
        center = (self.ymax+self.ymin)/2
        delta = self.ymax-self.ymin
        delta *= 0.92
        delta /= 2
        self.ymin = center - delta
        self.ymax = center + delta
        self.fig.axes[0].set_ylim(self.ymin, self.ymax)
        self.fig.canvas.draw()

    def on_zoomout_y(self, btn):
        center = (self.ymax + self.ymin) / 2
        delta = self.ymax - self.ymin
        delta *= 1.08
        delta /= 2
        self.ymin = center - delta
        self.ymax = center + delta
        self.fig.axes[0].set_ylim(self.ymin, self.ymax)
        self.fig.canvas.draw()

    def on_goup_y(self, btn):
        delta = self.ymax - self.ymin
        delta *= 0.1
        self.ymax += delta
        self.ymin += delta
        self.fig.axes[0].set_ylim(self.ymin, self.ymax)
        self.fig.canvas.draw()

    def on_godown_y(self, btn):
        delta = self.ymax - self.ymin
        delta *= 0.1
        self.ymax -= delta
        self.ymin -= delta
        self.fig.axes[0].set_ylim(self.ymin, self.ymax)
        self.fig.canvas.draw()

    # EVENTUAL EVENTS THAT CAN BE CAUGHT
    # def on_press(self, event):
    #     print('press released from test', event.x, event.y, event.button)
    #
    # def on_release(self, event):
    #     print('release released from test', event.x, event.y, event.button)
    #
    # def on_keypress(self, event):
    #     print('key down', event.key)
    #
    # def on_keyup(self, event):
    #     print('key up', event.key)
    #
    # def on_motionnotify(self, event):
    #     print('mouse move to ', event.x, event.y)
    #
    # def on_resize(self, event):
    #     print('resize from mpl ', event.width, event.height)
    #
    # def on_scroll(self, event):
    #     print('scroll event from mpl ', event.x, event.y, event.step)
    #
    # def on_figure_enter(self, event):
    #     print('figure enter mpl')
    #
    # def on_figure_leave(self, event):
    #     print('figure leaving mpl')
    #
    # def on_close(self, event):
    #     print('closing figure')
