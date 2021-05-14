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
            server_info = args[0]
            info = server_info.split(':')
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
            error_title = Label(text='Wrong syntax of IP\n Press escape to correct.', font_size=60, pos_hint={'center_x': .5, 'center_y': .5})
            self.add_widget(error_title)
        else:
            # Main Interface of MONA imported from interface.py. Interface.py is a group of widgets useable to display
            # all different modules we want. You can choose the size, position here.

            # Here's an example of a network structure to test without server
            network_list = [['RD', ['SONA0', ['SHZ', 'SHN', 'SHE']], ['SONA1', ['SHZ', 'SHN', 'SHE']]],
                            ['MN', ['ALFM', ['SHZ', 'SHN', 'SHE']]]]

            # The structure has to be : [[ NETWORK_1, [ STATION_1, [ CHANNEL_1, CHANNEL_2, ...]],
            #                                         [ STATION 2, [ CHANNEL_1, CHANNEL_2, ...]]],
            #                            [ NETWORK_2, [ STATION_1, [ CHANNEL_1, ...]], ... ],
            #                            [ ... ]]

            # TREE SELECTION OF STATIONS
            tree_selection = ScrollView(size_hint=(.2, .65), pos=(0, 0))
            stations_widget, self.stations_active_list = stations_tab(server_info, network_list)
            tree_selection.add_widget(stations_widget)
            self.add_widget(tree_selection)

            # TAB CENTRAL
            tab_panel_central = TabbedPanel(do_default_tab=False, tab_pos='top_mid', tab_width=150, size_hint=(.8,.65))

            tab_time_central = TabbedPanelItem(text='TIME SIGNAL')

            self.layout = BoxLayout(orientation='vertical')
            self.button = Button(text="Update list of stations", size=(300, 40), size_hint=(None, None),
                                 pos_hint={'center_x': .5})
            self.t_curves = t_curves_tab(self.stations_active_list)

            self.layout.add_widget(self.button)
            self.layout.add_widget(self.t_curves)

            # Allow the update of the active_list of stations: the operation of doing it automatically is way more
            # complicated than just push a button with a callback on_release.
            self.button.bind(on_release=self.on_release_button)

            tab_time_central.add_widget(self.layout)

            tab_map_central = TabbedPanelItem(text='MAP')
            tab_map_central.add_widget(map_tab())

            tab_panel_central.add_widget(tab_time_central)
            tab_panel_central.add_widget(tab_map_central)

            self.add_widget(tab_panel_central)

            state_layout = ScrollView(size_hint=(.2, .35))

            states = [['Temperature Digitizer', '45°C', 0],
                      ['Temperature Outside', '-2°C', 1],
                      ['Intrusion', 'No', 1],
                      ['Solar Panels', 'Yes', 1],
                      ['Voltage', '12.2V', 1],
                      ['Current', '1.2A', 0]]

            self.state_station = 'SONA0'
            states_tree = StateTreeView(title='States of {}'.format(self.state_station), state_list=states)
            state_layout.add_widget(states_tree)
            self.add_widget(state_layout)

            # LAYOUT CENTRAL BOTTOM FOR ALARMS AND PSD
            layout_central_bottom = TabbedPanel(do_default_tab=False, tab_pos='top_mid', tab_width=150,
                                                size_hint=(.8, .35), pos_hint={'center_x': .5, 'center_y': .5})

            tab_alarms_layout = TabbedPanelItem(text='Alarms')

            tab_alarms_grid = GridLayout(cols=2)



            self.alarms_list = [['2021-04-23 12:07:12', 'SONA0 - Temp Digitizer - Too Hot'],
                                ['2021-04-23 12:02:42', 'SONA0 - Current - Too High'],
                                ['2021-04-22 08:24:53', 'ALFM - Current - Too High']]

            self.c_alarms_list = [['2021-04-20 21:16:55', 'SONA0 - Temperature Digitizer - Too Hot'],
                                  ['2021-04-22 16:36:42', 'SONA0 - Current - Too High'],
                                  ['2021-04-22 16:36:42', 'SONA0 - Current - Too High']]

            # ALARMS IN PROGRESS SCROLL TO BOTTOM VIEW
            in_progress_scroll_layout = ScrollView(size_hint=(.5, .9))
            in_progress_alarms_tree = AlarmTreeView(title='Alarms in progress', alarms_list=self.alarms_list,
                                                    check=True)
            in_progress_scroll_layout.add_widget(in_progress_alarms_tree)
            tab_alarms_grid.add_widget(in_progress_scroll_layout)

            # ALARMS COMPLETED SCROLL TO BOTTOM VIEW
            completed_scroll_layout = ScrollView(size_hint=(.5, .9))
            completed_alarms_tree = AlarmTreeView(title='Alarms completed', alarms_list=self.c_alarms_list, check=False)
            completed_scroll_layout.add_widget(completed_alarms_tree)
            tab_alarms_grid.add_widget(completed_scroll_layout)

            tab_alarms_layout.add_widget(tab_alarms_grid)

            complete_alarm_btn = Button(text='Finish checked alarms', size_hint=(.5, .1))
            tab_alarms_grid.add_widget(complete_alarm_btn)

            layout_central_bottom.add_widget(tab_alarms_layout)

            tab_PSD = TabbedPanelItem(text='PSD')
            layout_central_bottom.add_widget(tab_PSD)

            self.add_widget(layout_central_bottom)


    def on_release_button(self, btn):
        # To update the curves, we have to remove the widget and add it again just after
        self.layout.remove_widget(self.t_curves)
        self.t_curves = t_curves_tab(self.stations_active_list)
        self.layout.add_widget(self.t_curves)
