# -*- coding: utf-8 -*-

# SERVER FUNCTIONS TO CONNECT TO A DB
# Author: Jérémy Hraman
# Date: 23-03-2021
# Last Update: 23-03-2021

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

class ServerSeisComP3:

    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port

    def connect_to_server(self):
        pass

    def get_stations(self):
        pass


class ServerWindow(FloatLayout):

    def __init__(self, *args, **kwargs):
        super(ServerWindow, self).__init__(**kwargs)
        info = args[0]
        main_title = Label(text='MONA', font_size=60, pos_hint={'center_x': .6, 'center_y': .7})
        self.add_widget(main_title)
