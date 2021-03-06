# -*- coding: utf-8 -*-

#  Copyright IAG (c) 2021.

# GRAPH TOOLS WITH MATPLOTLIB FOR KIVY
# Author: Jérémy Hraman
# Date: 03-05-2021
# Last Update: 03-05-2021

import matplotlib
matplotlib.use('Kivy')

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import welch
import matplotlib.dates as mdates

from memory_profiler import profile


# Style sheet created for MatplotlibFigure which implements colors for a dark background and everything
plt.style.use('./css/MONA.mplstyle')


class MatplotlibFigure(BoxLayout):
    """
    class MatplotlibFigure to display graphs in the t_curves_graph
    It includes a toolbar
    """
    def __init__(self, **kwargs):

        self.name = kwargs.pop('name', '')
        split_name = self.name.split('.')
        if len(split_name) == 4:
            self.network = split_name[0]
            self.station = split_name[1]
            self.location = split_name[2]
            self.channel = split_name[3]
        else:
            self.network = split_name[0]
            self.station = split_name[1]
            self.location = ''
            self.channel = split_name[2]

        self.title = kwargs.pop('title', '')
        self.x_label = kwargs.pop('x_label', 'x')
        self.y_label = kwargs.pop('y_label', 'y')
        self.client = kwargs.pop('client', None)

        self.starttime = kwargs.pop('starttime', None)

        super(MatplotlibFigure, self).__init__()

        self.orientation = 'vertical'
        self.fig, self.ax = plt.subplots()
        # self.fig = plt.figure()
        # self.ax = self.fig.add_subplot(111)

        self.auto_moving_x = True
        self.auto_moving_y = True
        self.fig.clf()

        if self.client is not None:
            try:
                self.stream = self.client.get_waveforms(self.network, self.station, self.location, self.channel,
                                                    self.starttime-10, self.starttime)
            except AttributeError:
                print('No live data for this station')
                self.stream = None

            if self.stream is not None:

                self.tr = self.stream[0]
                start = self.tr.stats.starttime.matplotlib_date
                end = self.tr.stats.endtime.matplotlib_date

                self.t = np.linspace(start, end, self.tr.stats.npts)
                self.str_plot, = plt.plot(self.t, self.tr.data, 'b-', figure=self.fig)

                self.fig.patch.set_fill(False)

                self.fig.axes[0].xaxis_date()
                self.fig.axes[0].get_xaxis().set_major_locator(plt.LinearLocator(5))
                self.fig.axes[0].get_xaxis().set_major_formatter(mdates.DateFormatter("%Y-%m-%dT%H:%M:%S"))

                # size of ticks is defined here (impossible to change it in mplstyle sheet)
                self.fig.axes[0].tick_params(axis='both', which='major', labelsize=14)
                self.fig.axes[0].tick_params(axis='both', which='minor', labelsize=14)

            # self.ax.tick_params(axis='both', which='major', labelsize=14)
            # self.ax.tick_params(axis='both', which='minor', labelsize=14)

                self.ymin, self.ymax = self.fig.axes[0].get_ylim()
                # self.ymin, self.ymax = self.ax.get_ylim()

                self.xmin = self.stream[0].stats.starttime.matplotlib_date
                self.xmax = (self.stream[0].stats.starttime + 30).matplotlib_date
                self.delta_x = 30
                self.fig.axes[0].set_xlim(self.xmin, self.xmax)


                # self.ax.set_xlim(self.xmin, self.xmax)
                self.fig.canvas.draw()

                # PSD
                self.sr = self.stream[0].stats.sampling_rate
                self.f, self.psd = welch(x=self.tr.data, fs=self.sr)

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

                self.reset_btn = Button(text="Reset axis", size_hint=(None, 1))
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
                self.nav_layout.add_widget(self.reset_btn)
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

                self.reset_btn.bind(on_release=self.on_reset)
                self.zoomin_x.bind(on_release=self.on_zoomin_x)
                self.zoomout_x.bind(on_release=self.on_zoomout_x)
                self.goleft_x.bind(on_release=self.on_goleft_x)
                self.goright_x.bind(on_release=self.on_goright_x)
                self.zoomin_y.bind(on_release=self.on_zoomin_y)
                self.zoomout_y.bind(on_release=self.on_zoomout_y)
                self.goup_y.bind(on_release=self.on_goup_y)
                self.godown_y.bind(on_release=self.on_godown_y)

                self.add_widget(self.nav_layout)
            self.add_widget(self.fig.canvas)

    def get_data_from_client(self, endtime):
        if self.stream is not None:
            old_starttime = self.stream[0].stats.starttime
            old_endtime = self.stream[0].stats.endtime

            if (old_endtime-old_starttime) >= 270:
                self.stream.trim(old_starttime+10, old_endtime)

            self.stream += self.client.get_waveforms(self.network, self.station, self.location, self.channel,
                                                     old_endtime, endtime)
            self.stream.merge()

            self.tr = self.stream[0]

            start = self.tr.stats.starttime.matplotlib_date
            end = self.tr.stats.endtime.matplotlib_date

            self.t = np.linspace(start, end, self.tr.stats.npts)
            del old_starttime, old_endtime, start, end

    def update_figure(self, endtime):
        if self.stream is not None:
            self.str_plot.set_xdata(self.t)
            self.str_plot.set_ydata(self.tr.data)

            if self.auto_moving_x:
                if endtime - (self.starttime - 10) <= 30:
                    self.xmin = self.stream[0].stats.starttime.matplotlib_date
                    self.xmax = (self.stream[0].stats.starttime + 30).matplotlib_date
                else:
                    self.xmin = (endtime - 30).matplotlib_date
                    self.xmax = endtime.matplotlib_date

                if self.auto_moving_y:
                    self.ymin, self.ymax = self.fig.axes[0].get_ylim()

            self.fig.axes[0].set_xlim(self.xmin, self.xmax)
            self.fig.axes[0].set_ylim(self.ymin, self.ymax)

            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

            self.f, self.psd = welch(x=self.tr.data, fs=self.sr)

    def on_reset(self, btn):
        self.auto_moving_x = True
        self.auto_moving_y = True
        self.update_figure(self.stream[0].stats.endtime)

    def on_zoomin_x(self, btn):
        self.auto_moving_x = False
        center = (self.xmax + self.xmin) / 2
        delta = self.xmax - self.xmin
        delta *= 0.92
        delta /= 2
        self.xmin = center - delta
        self.xmax = center + delta
        self.fig.axes[0].set_xlim(self.xmin, self.xmax)
        self.fig.canvas.draw()
        del center, delta

    def on_zoomout_x(self, btn):
        self.auto_moving_x = False
        center = (self.xmax + self.xmin) / 2
        delta = self.xmax - self.xmin
        delta *= 1.08
        delta /= 2
        self.xmin = center - delta
        self.xmax = center + delta
        self.fig.axes[0].set_xlim(self.xmin, self.xmax)
        self.fig.canvas.draw()
        del center, delta

    def on_goleft_x(self, btn):
        self.auto_moving_x = False
        delta = self.xmax - self.xmin
        delta *= 0.1
        self.xmax -= delta
        self.xmin -= delta
        self.fig.axes[0].set_xlim(self.xmin, self.xmax)
        self.fig.canvas.draw()
        del delta

    def on_goright_x(self, btn):
        self.auto_moving_x = False
        delta = self.xmax - self.xmin
        delta *= 0.1
        self.xmax += delta
        self.xmin += delta
        self.fig.axes[0].set_xlim(self.xmin, self.xmax)
        self.fig.canvas.draw()
        del delta

    def on_zoomin_y(self, btn):
        self.auto_moving_y = False
        center = (self.ymax+self.ymin)/2
        delta = self.ymax-self.ymin
        delta *= 0.92
        delta /= 2
        self.ymin = center - delta
        self.ymax = center + delta
        self.fig.axes[0].set_ylim(self.ymin, self.ymax)
        self.fig.canvas.draw()
        del center, delta

    def on_zoomout_y(self, btn):
        self.auto_moving_y = False
        center = (self.ymax + self.ymin) / 2
        delta = self.ymax - self.ymin
        delta *= 1.08
        delta /= 2
        self.ymin = center - delta
        self.ymax = center + delta
        self.fig.axes[0].set_ylim(self.ymin, self.ymax)
        self.fig.canvas.draw()
        del center, delta

    def on_goup_y(self, btn):
        self.auto_moving_y = False
        delta = self.ymax - self.ymin
        delta *= 0.1
        self.ymax += delta
        self.ymin += delta
        self.fig.axes[0].set_ylim(self.ymin, self.ymax)
        self.fig.canvas.draw()
        del delta

    def on_godown_y(self, btn):
        self.auto_moving_y = False
        delta = self.ymax - self.ymin
        delta *= 0.1
        self.ymax -= delta
        self.ymin -= delta
        self.fig.axes[0].set_ylim(self.ymin, self.ymax)
        self.fig.canvas.draw()
        del delta

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


class PSDFigure(BoxLayout):
    def __init__(self, **kwargs):
        self.t_figures = kwargs.pop('t_figures', 'None')
        super(PSDFigure, self).__init__()

        self.all_psd = []
        if self.t_figures is not None and len(self.t_figures) != 0:
            for figure in self.t_figures:
                self.all_psd.append([figure.f, figure.psd])

        self.orientation = 'vertical'
        self.fig, _ = plt.subplots()

        self.nav_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=.2)

        self.reset_btn = Button(text="Reset axis", size_hint=(None, 1))
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

        self.nav_layout.add_widget(Label(text='PSD', size_hint=(.3, 1)))
        self.nav_layout.add_widget(self.reset_btn)
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

        self.reset_btn.bind(on_release=self.on_reset)
        self.zoomin_x.bind(on_release=self.on_zoomin_x)
        self.zoomout_x.bind(on_release=self.on_zoomout_x)
        self.goleft_x.bind(on_release=self.on_goleft_x)
        self.goright_x.bind(on_release=self.on_goright_x)
        self.zoomin_y.bind(on_release=self.on_zoomin_y)
        self.zoomout_y.bind(on_release=self.on_zoomout_y)
        self.goup_y.bind(on_release=self.on_goup_y)
        self.godown_y.bind(on_release=self.on_godown_y)

        self.add_widget(self.nav_layout)
        self.add_widget(self.fig.canvas)

    def get_data_from_figures(self, figures):

        pass

    def update_figure(self):
        for f_psd in self.all_psd:
            self.fig.axes[0].plot(f_psd[0], f_psd[1])

        self.fig.canvas.draw()
        # self.str_plot.set_xdata(self.f)
        # self.str_plot.set_ydata(self.all_psd)

        # if self.auto_moving_x:
        #     if endtime - (self.starttime - 10) <= 30:
        #         self.xmin = self.stream[0].stats.starttime.matplotlib_date
        #         self.xmax = (self.stream[0].stats.starttime + 30).matplotlib_date
        #     else:
        #         self.xmin = (endtime - 30).matplotlib_date
        #         self.xmax = endtime.matplotlib_date
        #
        #     if self.auto_moving_y:
        #         self.ymin, self.ymax = self.fig.axes[0].get_ylim()

        # self.fig.axes[0].set_xlim(self.xmin, self.xmax)
        # self.fig.axes[0].set_ylim(self.ymin, self.ymax)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

        # self.f, self.psd = plt.psd(self.tr.data, Fs=self.sr)

    def on_reset(self, btn):
        self.auto_moving_x = True
        self.auto_moving_y = True
        self.update_figure(self.stream[0].stats.endtime)

    def on_zoomin_x(self, btn):
        self.auto_moving_x = False
        center = (self.xmax + self.xmin) / 2
        delta = self.xmax - self.xmin
        delta *= 0.92
        delta /= 2
        self.xmin = center - delta
        self.xmax = center + delta
        self.fig.axes[0].set_xlim(self.xmin, self.xmax)
        self.fig.canvas.draw()
        del center, delta

    def on_zoomout_x(self, btn):
        self.auto_moving_x = False
        center = (self.xmax + self.xmin) / 2
        delta = self.xmax - self.xmin
        delta *= 1.08
        delta /= 2
        self.xmin = center - delta
        self.xmax = center + delta
        self.fig.axes[0].set_xlim(self.xmin, self.xmax)
        self.fig.canvas.draw()
        del center, delta

    def on_goleft_x(self, btn):
        self.auto_moving_x = False
        delta = self.xmax - self.xmin
        delta *= 0.1
        self.xmax -= delta
        self.xmin -= delta
        self.fig.axes[0].set_xlim(self.xmin, self.xmax)
        self.fig.canvas.draw()
        del delta

    def on_goright_x(self, btn):
        self.auto_moving_x = False
        delta = self.xmax - self.xmin
        delta *= 0.1
        self.xmax += delta
        self.xmin += delta
        self.fig.axes[0].set_xlim(self.xmin, self.xmax)
        self.fig.canvas.draw()
        del delta

    def on_zoomin_y(self, btn):
        self.auto_moving_y = False
        center = (self.ymax+self.ymin)/2
        delta = self.ymax-self.ymin
        delta *= 0.92
        delta /= 2
        self.ymin = center - delta
        self.ymax = center + delta
        self.fig.axes[0].set_ylim(self.ymin, self.ymax)
        self.fig.canvas.draw()
        del center, delta

    def on_zoomout_y(self, btn):
        self.auto_moving_y = False
        center = (self.ymax + self.ymin) / 2
        delta = self.ymax - self.ymin
        delta *= 1.08
        delta /= 2
        self.ymin = center - delta
        self.ymax = center + delta
        self.fig.axes[0].set_ylim(self.ymin, self.ymax)
        self.fig.canvas.draw()
        del center, delta

    def on_goup_y(self, btn):
        self.auto_moving_y = False
        delta = self.ymax - self.ymin
        delta *= 0.1
        self.ymax += delta
        self.ymin += delta
        self.fig.axes[0].set_ylim(self.ymin, self.ymax)
        self.fig.canvas.draw()
        del delta

    def on_godown_y(self, btn):
        self.auto_moving_y = False
        delta = self.ymax - self.ymin
        delta *= 0.1
        self.ymax -= delta
        self.ymin -= delta
        self.fig.axes[0].set_ylim(self.ymin, self.ymax)
        self.fig.canvas.draw()
        del delta
