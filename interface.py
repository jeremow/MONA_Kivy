# -*- coding: utf-8 -*-

# INTERFACE WIDGETS
# Author: Jérémy Hraman
# Date: 23-03-2021
# Last Update: 20-05-2021

# Tree View modules for selection of stations
from kivy.metrics import dp
from kivy.uix.checkbox import CheckBox
from kivy.uix.treeview import TreeView, TreeViewNode
from kivy.uix.scrollview import ScrollView
# TODO: add the size scaling with Slider
# from kivy.uix.slider import Slider
from kivy_garden.mapview import MapView
from kivy.uix.tabbedpanel import TabbedPanel

# Used for selection of time view
from kivy.uix.gridlayout import GridLayout

# Graphics
from graph_utils import *
from obspy import UTCDateTime


def stations_tab(info, network_list):
    active_list = []
    return NetworkTreeView(info, network_list, active_list), active_list


def map_tab():
    return MapView(lat=46.7734832, lon=103.2187417, zoom=6)


def t_curves_tab(active_list, t_figures, **kwargs):
    # add the scroll view inside of the central tab of t_curves, only accept 1 widget, we have to create a BoxLayout to
    # put all the other figures
    client = kwargs.pop('client', None)
    t_layout = ScrollView(size_hint=(1, 1), pos=(0, 0), do_scroll_x=True)

    # The dict with rows is here to adapt the graphs to
    dict_row_min = {}
    for i in range(0, len(active_list)):
        dict_row_min[i] = 250

    graph_layout = GridLayout(cols=1, size_hint_y=None, rows_minimum=dict_row_min)
    graph_layout.bind(minimum_height=graph_layout.setter('height'))  # allow ScrollView to work properly

    # we create a leftovers list which will be all the figures we have to create after checking the ones we already have
    leftovers_active_list = active_list.copy()
    # we store the figures we will delete from the list
    figures_to_delete = []
    for station_t_figure in t_figures:
        if station_t_figure.name in active_list:
            graph_layout.add_widget(station_t_figure)
            leftovers_active_list.remove(station_t_figure.name)
        else:
            # don't delete directly because it fucked up the loop
            figures_to_delete.append(station_t_figure)

    # must be deleted here only
    for figure in figures_to_delete:
        t_figures.remove(figure)
        del figure
    del figures_to_delete

    # now we create the new figures which were added afterwards and add it to the list of figures
    starttime = UTCDateTime()
    for station in leftovers_active_list:
        if client is not None:
            t_figure = MatplotlibFigure(name=station, title=station, client=client, starttime=starttime)
        else:
            t_figure = MatplotlibFigure(name=station, title=station)
        t_figures.append(t_figure)
        graph_layout.add_widget(t_figure)
    del leftovers_active_list

    t_layout.add_widget(graph_layout)

    return t_layout


def f_curves_tab():
    pass


# STATIONS_TAB CLASSES

class MyNodeNetwork(BoxLayout):
    """
    Class MyNodeNetwork allow to check boxes and returning information of which channel is active or not.
    """
    def __init__(self, **kwargs):
        self.text = kwargs.pop('text', 'None')
        self.network = kwargs.pop('network', 'None')
        self.active_list = kwargs.pop('active_list', 'None')
        self.full_name = kwargs.pop('full_name', 'None')
        self.check = kwargs.pop('check')
        self.is_station = kwargs.pop('is_station')
        super(MyNodeNetwork, self).__init__(**kwargs)

        self.orientation = 'horizontal'

        # make height reasonable
        self.size_hint_y = None
        self.height = dp(25)

        # make the parts of the node
        # align text of label to the right side for Channel because of alignment of the checkboxes
        if self.check:
            self.label = Label(text=self.text, size_hint_x=0.2, halign="right")
        else:
            self.label = Label(text=self.text, size_hint_x=0.2, halign="center")
        self.label.bind(size=self.label.setter('text_size'))
        self.add_widget(self.label)

        if self.check:
            self.checkbox = CheckBox(size_hint_x=0.1, color=(1, 1, 1, 3.5))  # alpha=3.5 to make it more visible
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


class MyTreeNodeNetwork(MyNodeNetwork, TreeViewNode):
    """
    Double Heritage of MyNodeNetwork and TreeViewNode
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
            network_node = self.add_node(MyTreeNodeNetwork(text=net_name, check=False, is_station=False))

            for station in network[1:]:
                station_name = station[0]
                station_node = self.add_node(MyTreeNodeNetwork(text=station_name, network=net_name,
                                                               check=False, is_station=True), network_node)

                for channel in station[1]:
                    full_name = net_name + '.' + station_name + '.' + channel
                    self.add_node(MyTreeNodeNetwork(text=channel, full_name=full_name,
                                                    active_list=active_list, check=True, is_station=False), station_node)


# TAB CENTRAL : MAP AND T_CURVES

class TabCentral(TabbedPanel):
    def __init__(self, **kwargs):
        super(TabCentral, self).__init__(**kwargs)


# ALARM VIEW BOTTOM CENTRAL
class MyNodeAlarm(BoxLayout):
    """
    Class MyNodeAlarm allow to check boxes and update the alarms list from in progress to completed.
    """
    def __init__(self, **kwargs):
        self.text = kwargs.pop('text', 'None')
        self.alarms_list = kwargs.pop('alarms_list')
        self.check = kwargs.pop('check')
        self.check_list = kwargs.pop('check_list')
        self.alarm = kwargs.pop('alarm')
        super(MyNodeAlarm, self).__init__(**kwargs)
        self.orientation = 'horizontal'

        # make height reasonable
        self.size_hint_y = None
        self.height = dp(25)

        # make the parts of the node
        # align text of label to the right side for Channel because of alignment of the checkboxes
        self.label = Label(text=self.text, size_hint_x=0.9, halign="left")
        self.label.bind(size=self.label.setter('text_size'))
        self.add_widget(self.label)

        if self.check:
            self.checkbox = CheckBox(size_hint_x=0.1, color=(1, 1, 1, 3.5)) # alpha=3.5 to make it more visible
            self.add_widget(self.checkbox)
            self.checkbox.bind(active=self.on_checkbox_active)

    def on_checkbox_active(self, checkbox_obj, is_active):
        if is_active:
            self.check_list.append(self.alarm)
            print(self.check_list)
        else:
            try:
                self.check_list.remove(self.alarm)
            except ValueError:
                pass


class MyTreeNodeAlarm(MyNodeAlarm, TreeViewNode):
    """
    Double Heritage of MyNodeAlarm and TreeViewNode
    """
    pass


class AlarmTreeView(TreeView):
    """
    Class AlarmTreeView. Main Heritage from TreeView
    """
    def __init__(self, title, alarms_list, check, check_list):
        # To manage with the ScrollView, we have to put size_hint=(1, None) because theScrollView will decide of the
        # dimensions of the y-axis and we fully put the TreeView into the x-axis
        super(AlarmTreeView, self).__init__(root_options=dict(text=title), size_hint_x=1, size_hint_y=None)
        self.alarms_list = alarms_list
        self.check_list = check_list
        self.check = check
        # This parameter allow the Scrollview to work :
        self.bind(minimum_height=self.setter('height'))

        # Here is the representation
        for alarm in self.alarms_list:
            alarm_type = '{} | {}'.format(alarm[0], alarm[1])
            self.add_node(MyTreeNodeAlarm(text=alarm_type, alarm=alarm[2], alarms_list=self.alarms_list,
                                          check=self.check, check_list=self.check_list))


# STATE VIEW LEFT BOTTOM
class MyNodeState(BoxLayout):
    """
    Class MyNodeState allow to see the state of the station.
    """
    def __init__(self, **kwargs):
        self.text = kwargs.pop('text', 'None')

        super(MyNodeState, self).__init__(**kwargs)

        self.orientation = 'horizontal'

        # make height reasonable
        self.size_hint_y = None
        self.height = dp(25)

        # make the parts of the node
        # align text of label to the right side for Channel because of alignment of the checkboxes
        self.label = Label(text=self.text, size_hint_x=0.9, halign="left", markup=True)
        self.label.bind(size=self.label.setter('text_size'))
        self.add_widget(self.label)


class MyTreeNodeState(MyNodeState, TreeViewNode):
    """
    Double Heritage of MyNodeState and TreeViewNode
    """
    pass


class StateTreeView(TreeView):
    """
    Class StateTreeView. Main Heritage from TreeView
    """
    def __init__(self, title, state_list):
        # To manage with the ScrollView, we have to put size_hint=(1, None) because theScrollView will decide of the
        # dimensions of the y-axis and we fully put the TreeView into the x-axis
        super(StateTreeView, self).__init__(root_options=dict(text=title), size_hint_x=1, size_hint_y=None)
        self.state_list = state_list
        # This parameter allow the Scrollview to work :
        self.bind(minimum_height=self.setter('height'))

        # Here is the representation of each node
        for state in self.state_list:
            # state[0]: type of state
            # state[1]: state
            # state[2]: 0 or 1 (normal or problem for color)
            if state[2] == 0:
                color = '00ff00'
            else:
                color = 'ff0000'
            state_text = '{0}: [color={2}]{1}[/color]'.format(state[0], state[1], color)
            self.add_node(MyTreeNodeState(text=state_text))
