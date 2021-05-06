# -*- coding: utf-8 -*-

# SERVER POPUP LAYOUT
# Author: Jérémy Hraman
# Date: 23-03-2021
# Last Update: 23-03-2021

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader, TabbedPanelItem
from interface import *

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
            tree_selection = ScrollView(size_hint=(.2, .5), pos=(0, 0))
            stations_widget, self.stations_active_list = stations_tab(server_info, network_list)
            tree_selection.add_widget(stations_widget)
            self.add_widget(tree_selection)

            # TAB CENTRAL
            tab_panel_central = TabbedPanel(do_default_tab=False, tab_pos='top_mid', tab_width=150)

            tab_time_central = TabbedPanelItem(text='TIME SIGNAL')

            layout = GridLayout(cols=1)
            self.text_label = Label(text=str(self.stations_active_list), size_hint=(1, 0.5))
            self.t_curves = t_curves_tab(self.stations_active_list)
            self.button = Button(text="Update", size_hint=(1, 0.5), pos=(100, 100))
            layout.add_widget(self.text_label)
            layout.add_widget(self.t_curves)
            layout.add_widget(self.button)
            self.button.bind(on_release=self.on_release_button)

            tab_time_central.add_widget(layout)

            tab_map_central = TabbedPanelItem(text='MAP')
            tab_map_central.add_widget(map_tab())

            tab_panel_central.add_widget(tab_time_central)
            tab_panel_central.add_widget(tab_map_central)

            self.add_widget(tab_panel_central)

    def on_release_button(self, btn):
        self.text_label.text = str(self.stations_active_list)
        print(self.text_label.text)
