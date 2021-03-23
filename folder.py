# -*- coding: utf-8 -*-

# FOLDER LAYOUT
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


class FolderWindow(FloatLayout):

    def __init__(self, *args, **kwargs):
        super(FolderWindow, self).__init__(**kwargs)
        path = args[0]
        main_title = Label(text='MONA - FOLDER', font_size=60, pos_hint={'center_x': .5, 'center_y': .5})
        self.add_widget(main_title)
