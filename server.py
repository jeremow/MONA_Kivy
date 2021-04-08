# -*- coding: utf-8 -*-

# SERVER POPUP LAYOUT
# Author: Jérémy Hraman
# Date: 23-03-2021
# Last Update: 23-03-2021

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label

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
        info = args[0].split(':')
        try:
            self.ip_address = info[0]
            self.port = info[1]
        except IndexError:
            error_title = Label(text='Wrong syntax of IP\n Press escape to correct.', font_size=60, pos_hint={'center_x': .5, 'center_y': .5})
            self.add_widget(error_title)
