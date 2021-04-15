# -*- coding: utf-8 -*-

# INTERFACE WIDGETS
# Author: Jérémy Hraman
# Date: 23-03-2021
# Last Update: 14-04-2021

from kivy.uix.button import Button
from kivy.uix.image import Image

# Tree View modules for selection of stations
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.treeview import TreeView, TreeViewNode

# Used for selection of time view
from kivy.uix.actionbar import *


def stations_tab(info, network_list):
    active_list = []
    return NetworkTreeView(info, network_list, active_list)


def XAT_tab():
    pass


def alarm_tab():
    pass


def map_tab():
    pass


def t_curves_tab():
    pass


def f_curves_tab():
    pass


class MyNodeChannel(BoxLayout):

    def __init__(self, **kwargs):
        text = kwargs.pop('text', 'None')
        self.active_list = kwargs.pop('active_list')
        self.full_name = kwargs.pop('full_name')
        super(MyNodeChannel, self).__init__(**kwargs)
        self.orientation = 'horizontal'

        # make height reasonable
        self.size_hint_y = None
        self.height = dp(25)

        # make the parts of the node
        self.label = Label(text=text, size_hint_x=0.2)
        self.checkbox = CheckBox(size_hint_x=0.1, color=(1, 1, 1, 3.5))  # alpha=3.5 to make it more visible

        # add the parts to the BoxLayout
        self.add_widget(self.label)
        self.add_widget(self.checkbox)

        self.checkbox.bind(active=self.on_checkbox_active)

    def on_checkbox_active(self, checkbox_obj, is_active):
        if is_active:
            self.active_list.append(self.full_name)
        else:
            try:
                self.active_list.remove(self.full_name)
            except ValueError:
                pass



class MyNodeOther(BoxLayout):

    def __init__(self, **kwargs):
        text = kwargs.pop('text', 'None')
        super(MyNodeOther, self).__init__(**kwargs)
        self.orientation = 'horizontal'

        # make height reasonable
        self.size_hint_y = None
        self.height = dp(25)

        # make the parts of the node
        self.label = Label(text=text, size_hint_x=0.2)

        # add the parts to the BoxLayout
        self.add_widget(self.label)


class MyTreeNodeOther(MyNodeOther, TreeViewNode):
    pass


class MyTreeNodeChannel(MyNodeChannel, TreeViewNode):
    pass


class NetworkTreeView(TreeView):
    def __init__(self, info, network_list, active_list):
        super(NetworkTreeView, self).__init__(root_options=dict(text=info))
        for network in network_list:
            net_name = network[0]
            network_node = self.add_node(MyTreeNodeOther(text=net_name))

            for station in network[1:]:
                station_name = station[0]
                station_node = self.add_node(MyTreeNodeOther(text=station_name), network_node)

                for channel in station[1]:
                    full_name = net_name + '.' + station_name + '.' + channel
                    self.add_node(MyTreeNodeChannel(text=channel, full_name=full_name,
                                                    active_list=active_list), station_node)


