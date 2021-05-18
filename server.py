# -*- coding: utf-8 -*-

# SERVER POPUP LAYOUT
# Author: Jérémy Hraman
# Date: 23-03-2021
# Last Update: 23-03-2021

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader, TabbedPanelItem
from interface import *
from kivy.graphics.instructions import Canvas
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock

import xml.etree.ElementTree as ET
import os


# class ServerSeisComP3:
#
#     def __init__(self, ip_address, port):
#         self.ip_address = ip_address
#         self.port = port
#
#     def connect_to_server(self):
#         pass
#
#     def get_stations(self):
#         pass


class ServerWindow(GridLayout):

    def __init__(self, *args, **kwargs):
        super(ServerWindow, self).__init__(**kwargs)

        # Verification of the ip address, throw an error if IP is not 4 numbers distinguish by a point
        # Port is separated by ':'
        try:
            self.server_info = args[0]
            info = self.server_info.split(':')
            self.ip_address = info[0]
            self.ip_address = self.ip_address.split('.')
            if len(self.ip_address) != 4:
                raise IndexError
            else:
                for i, nb in enumerate(self.ip_address):
                    self.ip_address[i] = int(nb)
            self.port = int(info[1])
        except IndexError:
            # Display the error message in case of an error in the writing of the IP
            error_title = Label(text='Wrong syntax of IP\n Press escape to correct.', font_size=60,
                                pos_hint={'center_x': .5, 'center_y': .5})
            self.add_widget(error_title)
        else:
            # Main Interface of MONA imported from interface.py. Interface.py is a group of widgets useable to display
            # all different modules we want. You can choose the size, position here.

            # Here's an example of a network structure to test with the server 0.0.0.0:8000

            network_list = []
            try:
                config_server = ET.parse('config/server/{}.xml'.format(self.server_info.replace(':', '.')))
                config_server_root = config_server.getroot()

                for network in config_server_root:
                    network_name = network.attrib['name']
                    station_list = []
                    for station in config_server_root.findall("./network[@name='{0}']/station".format(network_name)):
                        station_name = station.attrib['name']
                        station_list.append(station_name)
                        channel_list = []
                        for channel in config_server_root.findall("./network[@name='{0}']/"
                                                                  "station[@name='{1}']/"
                                                                  "channel".format(network_name, station_name)):
                            channel_list.append(channel.attrib['name'])

                        station_list.append(channel_list)
                    network_list.append([network_name, station_list])
            except FileNotFoundError:
                print('Config file of server missing.')

            # The structure has to be : [[ NETWORK_1, [ STATION_1, [ CHANNEL_1, CHANNEL_2, ...]],
            #                                         [ STATION 2, [ CHANNEL_1, CHANNEL_2, ...]]],
            #                            [ NETWORK_2, [ STATION_1, [ CHANNEL_1, ...]], ... ],
            #                            [ ... ]]

            # TREE SELECTION OF STATIONS
            tree_selection = ScrollView(size_hint=(.2, .65), pos=(0, 0))
            self.stations_widget, self.stations_active_list = stations_tab(self.server_info, network_list)
            tree_selection.add_widget(self.stations_widget)
            self.add_widget(tree_selection)
            self.selected_node = self.stations_widget.selected_node

            # TAB CENTRAL
            tab_panel_central = TabbedPanel(do_default_tab=False, tab_pos='top_mid', tab_width=150, size_hint=(.8, .65))

            tab_time_central = TabbedPanelItem(text='TIME SIGNAL')

            self.layout = BoxLayout(orientation='vertical')
            self.update_time_button = Button(text="Update list of stations", size=(300, 40),
                                             size_hint=(None, None), pos_hint={'center_x': .5})
            self.t_curves = t_curves_tab(self.stations_active_list)

            self.layout.add_widget(self.update_time_button)
            self.layout.add_widget(self.t_curves)

            # Allow the update of the active_list of stations: the operation of doing it automatically is way more
            # complicated than just push a button with a callback on_release.
            self.update_time_button.bind(on_release=self.on_release_button)

            tab_time_central.add_widget(self.layout)

            tab_map_central = TabbedPanelItem(text='MAP')
            tab_map_central.add_widget(map_tab())

            tab_panel_central.add_widget(tab_time_central)
            tab_panel_central.add_widget(tab_map_central)

            self.add_widget(tab_panel_central)

            # LAYOUT LEFT BOTTOM FOR STATE
            self.state_layout = ScrollView(size_hint=(.2, .35))

            self.states = []
            self.state_network = 'None'
            self.state_station = 'None'

            self.states_tree = StateTreeView(title='States of {}'.format(self.state_station), state_list=self.states)
            self.state_layout.add_widget(self.states_tree)
            self.add_widget(self.state_layout)

            # LAYOUT CENTRAL BOTTOM FOR ALARMS AND PSD
            layout_central_bottom = TabbedPanel(do_default_tab=False, tab_pos='top_mid', tab_width=150,
                                                size_hint=(.8, .35), pos_hint={'center_x': .5, 'center_y': .5})

            tab_alarms_layout = TabbedPanelItem(text='Alarms')

            tab_alarms_grid = GridLayout(cols=2)

            self.nc_alarms_list = []
            self.c_alarms_list = []

            Clock.schedule_once(self.update_alarms)

            # ALARMS IN PROGRESS SCROLL TO BOTTOM VIEW
            self.in_progress_scroll_layout = ScrollView(size_hint=(.5, .9))
            self.in_progress_alarms_tree = AlarmTreeView(title='Alarms in progress', alarms_list=self.nc_alarms_list,
                                                         check=True)
            self.in_progress_scroll_layout.add_widget(self.in_progress_alarms_tree)
            tab_alarms_grid.add_widget(self.in_progress_scroll_layout)

            # ALARMS COMPLETED SCROLL TO BOTTOM VIEW
            self.completed_scroll_layout = ScrollView(size_hint=(.5, .9))
            self.completed_alarms_tree = AlarmTreeView(title='Alarms completed', alarms_list=self.c_alarms_list,
                                                       check=False)
            self.completed_scroll_layout.add_widget(self.completed_alarms_tree)
            tab_alarms_grid.add_widget(self.completed_scroll_layout)

            tab_alarms_layout.add_widget(tab_alarms_grid)

            self.complete_alarm_btn = Button(text='Finish checked alarms', size_hint=(.5, .1))
            tab_alarms_grid.add_widget(self.complete_alarm_btn)

            layout_central_bottom.add_widget(tab_alarms_layout)

            tab_PSD = TabbedPanelItem(text='PSD')
            layout_central_bottom.add_widget(tab_PSD)

            self.add_widget(layout_central_bottom)

            Clock.schedule_interval(self.on_selected_node, 0.5)
            Clock.schedule_interval(self.update_states, 30)
            Clock.schedule_interval(self.update_alarms, 30)
            Clock.schedule_interval(self.update_curves, 10)

    def on_release_button(self, btn):
        # To update the number of stations in curves, we have to remove the widget and add it again just after
        self.layout.remove_widget(self.t_curves)
        self.t_curves = t_curves_tab(self.stations_active_list)
        self.layout.add_widget(self.t_curves)

    def on_selected_node(self, dt):
        if self.selected_node is not self.stations_widget.selected_node:
            self.selected_node = self.stations_widget.selected_node
            if self.selected_node.is_station:
                self.state_network = self.selected_node.network
                self.state_station = self.selected_node.text
                Clock.schedule_once(self.update_states)

    def update_states(self, dt):
        self.states = []
        try:
            states_server = ET.parse('log/server/{}_states.xml'.format(self.server_info.replace(':', '.')))
            states_server_root = states_server.getroot()
            for state in states_server_root.findall("./network[@name='{0}']/station[@name='{1}']/"
                                                    "state".format(self.state_network, self.state_station)):
                self.states.append([state.attrib['name'], state.attrib['value'], int(state.attrib['problem'])])
        except FileNotFoundError:
            pass

        self.state_layout.remove_widget(self.states_tree)
        self.states_tree = StateTreeView(title='States of {}'.format(self.state_station), state_list=self.states)
        self.state_layout.add_widget(self.states_tree)

    def update_curves(self, dt):
        pass

    def update_alarms(self, dt):
        # nc_alarms_list: non-completed alarms list ; c_alarms_list: completed one
        self.nc_alarms_list = []
        self.c_alarms_list = []
        try:
            alarms_server = ET.parse('log/server/{}_alarms.xml'.format(self.server_info.replace(':', '.')))
            alarms_server_root = alarms_server.getroot()

            # display all the ongoing alarms
            for alarm in alarms_server_root.findall("./ongoing/alarm"):
                alarm_name = alarm.attrib['station'] + ' - ' + \
                             alarm.attrib['state'] + ' - ' + \
                             alarm.attrib['detail']
                alarm_datetime = alarm.attrib['datetime'][1:5] + '-' + alarm.attrib['datetime'][5:7] + '-' + \
                                 alarm.attrib['datetime'][7:9] + ' ' + alarm.attrib['datetime'][10:12] + ':' + \
                                 alarm.attrib['datetime'][12:14] + ':' + alarm.attrib['datetime'][14:]

                self.nc_alarms_list.append([alarm_datetime, alarm_name])

            # display the 20 last completed alarms
            for alarm in alarms_server_root.findall("./completed/alarm")[-20:]:
                alarm_name = alarm.attrib['station'] + ' - ' + \
                             alarm.attrib['state'] + ' - ' + \
                             alarm.attrib['detail']
                alarm_datetime = alarm.attrib['datetime'][1:5] + '-' + alarm.attrib['datetime'][5:7] + '-' + \
                                 alarm.attrib['datetime'][7:9] + ' ' + alarm.attrib['datetime'][10:12] + ':' + \
                                 alarm.attrib['datetime'][12:14] + ':' + alarm.attrib['datetime'][14:]

                self.c_alarms_list.append([alarm_datetime, alarm_name])

        except FileNotFoundError:
            pass
        self.nc_alarms_list.reverse()
        self.c_alarms_list.reverse()

        self.in_progress_scroll_layout.remove_widget(self.in_progress_alarms_tree)
        self.completed_scroll_layout.remove_widget(self.completed_alarms_tree)

        self.in_progress_alarms_tree = AlarmTreeView(title='Alarms in progress', alarms_list=self.nc_alarms_list,
                                                     check=True)
        self.completed_alarms_tree = AlarmTreeView(title='Alarms completed', alarms_list=self.c_alarms_list,
                                                   check=False)

        self.in_progress_scroll_layout.add_widget(self.in_progress_alarms_tree)
        self.completed_scroll_layout.add_widget(self.completed_alarms_tree)
