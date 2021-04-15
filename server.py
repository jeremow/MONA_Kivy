# -*- coding: utf-8 -*-

# SERVER POPUP LAYOUT
# Author: Jérémy Hraman
# Date: 23-03-2021
# Last Update: 23-03-2021

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
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


class ServerWindow(FloatLayout):

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

            stations_widget = stations_tab(server_info, network_list)
            self.add_widget(stations_widget)
