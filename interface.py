# -*- coding: utf-8 -*-

# INTERFACE WIDGETS
# Author: Jérémy Hraman
# Date: 23-03-2021
# Last Update: 14-04-2021
import kivy_garden.mapview
from kivy.uix.button import Button
from kivy.uix.image import Image

# Tree View modules for selection of stations
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.treeview import TreeView, TreeViewNode
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy_garden.mapview import MapView
from kivy.uix.tabbedpanel import TabbedPanel

# Used for selection of time view
from kivy.uix.actionbar import *

# Graphics
from graph_utils import *


def stations_tab(info, network_list):
    active_list = []
    return NetworkTreeView(info, network_list, active_list), active_list


def XAT_tab():
    pass


def alarm_tab():
    pass


def map_tab():
    return MapView(lat=46.7734832, lon=103.2187417, zoom=6)


def t_curves_tab(active_list):
    t_layout = BoxLayout(orientation="vertical")
    t_figure = MatplotlibFigure([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], title='Mabite')
    t_layout.add_widget(t_figure.nav.actionbar)
    t_layout.add_widget(t_figure.fig.canvas)

    # for station in active_list:
    #     pass



    t_curves = Label(text=str(active_list))
    return t_layout


class TCurves(BoxLayout):
    pass

def f_curves_tab():
    pass


# STATIONS_TAB CLASSES 
class MyNodeChannel(BoxLayout):
    """
    Class MyNodeChannel allow to check boxes and returning information of which channel is active or not.
    It differs from MyNodeOther which doesn't include this checkbox functionality.
    """
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
        # align text of label to the right side for Channel because of alignment of the checkboxes
        self.label = Label(text=text, size_hint_x=0.2, halign="right")
        self.label.bind(size=self.label.setter('text_size'))
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
    """
    Class MyNodeOther is just present to display the networks and stations.
    It differs from MyNodeChannel which includes the checkbox functionality.
    """
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


class MyTreeNodeChannel(MyNodeChannel, TreeViewNode):
    """
    Double Heritage of MyNodeChannel and TreeViewNode
    """
    pass


class MyTreeNodeOther(MyNodeOther, TreeViewNode):
    """
    Double Heritage of MyNodeOther and TreeViewNode
    """
    pass


class NetworkTreeView(TreeView):
    """
    Class NetworkTreeView. Main Heritage from TreeView
    """
    def __init__(self, info, network_list, active_list):
        # To manage with the ScrollView, we have to put size_hint=(1, None) because theScrollView will decide of the
        # dimensions of the y-axis and we fully put the TreeView into the x-axis
        super(NetworkTreeView, self).__init__(root_options=dict(text=info), size_hint_x=1, size_hint_y=None)
        self.active_list = active_list
        # This parameter allow the Scrollview to work :
        self.bind(minimum_height=self.setter('height'))

        # Here is the representation of each node of our TreeView : Network / Station / Channel
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


# TAB CENTRAL : MAP AND T_CURVES

class TabCentral(TabbedPanel):
    def __init__(self, **kwargs):
        super(TabCentral, self).__init__(self, **kwargs)