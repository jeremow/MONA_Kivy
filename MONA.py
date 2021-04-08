# -*- coding: utf-8 -*-

# MONA - MONitoring App for MONgolian Stations of the IAG
# Created by Jérémy Hraman, Davaa
# Date: 23-03-2021
# Last Update: 23-03-2021

import kivy

import css.config

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.pagelayout import PageLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown

from server import *
from folder import *

import os
import platform
import win32api

kivy.require('2.0.0')


class Connection(FloatLayout):

    def __init__(self, **kwargs):
        super(Connection, self).__init__(**kwargs)

        self.logo = Image(source='css/logo.jpg', pos_hint={'center_x': .3, 'center_y': .7})
        self.main_title = Label(text='MONA', font_size=60, pos_hint={'center_x': .6, 'center_y': .7})
        self.subtitle = Label(text='MONitoring App for MONgolian Stations of IAG',
                         font_size=14, pos_hint={'center_x': .6, 'center_y': .65})
        self.footer = Label(text='v0.1 - Developed by Naraa and Jérémy Hraman',
                       font_size=14, pos_hint={'center_x': .5, 'center_y': .05})

        self.server_btn = Button(text='CONNECT TO SERVER', size_hint=(.25, .15),
                            background_color=(.3, .6, .7, 1),
                            pos_hint={'x': .0625, 'y': .2})
        self.server_btn.bind(on_release=self.connect_to_server)

        self.folder_btn = Button(text='CONNECT TO FOLDER', size_hint=(.25, .15),
                            background_color=(.3, .6, .7, 1),
                            pos_hint={'x': .375, 'y': .2})

        if platform.system() == 'Windows':
            self.folder_btn.bind(on_release=self.select_volume)
        else:
            self.folder_btn.bind(on_release=self.connect_to_folder)

        self.files_btn = Button(text='UPLOAD FILES', size_hint=(.25, .15),
                           background_color=(.3, .6, .7, 1),
                           pos_hint={'x': .6875, 'y': .2})
        self.files_btn.bind(on_release=self.upload_files)

        self.server_input = False
        self.folder_input = False
        self.file_input = False

        self.add_widget(self.logo)
        self.add_widget(self.main_title)
        self.add_widget(self.subtitle)
        self.add_widget(self.server_btn)
        self.add_widget(self.folder_btn)
        self.add_widget(self.files_btn)
        self.add_widget(self.footer)

    def connect_to_server(self, server_btn):
        layout = FloatLayout()

        server_info = TextInput(text="0.0.0.0:8000", multiline=False, size_hint=(.9, .3),
                                pos_hint={'center_x': .5, 'center_y': .6})
        connect_btn = Button(text="Connect", size_hint=(.4, .3),
                             pos_hint={'center_x': .25, 'center_y': .25})
        close_btn = Button(text="Cancel", size_hint=(.4, .3),
                           pos_hint={'center_x': .75, 'center_y': .25})

        layout.add_widget(server_info)
        layout.add_widget(connect_btn)
        layout.add_widget(close_btn)

        # Instantiate the modal popup and display
        popup = Popup(title='Server connection',
                      content=layout,
                      size_hint=(None, None), size=(300, 200))
        popup.open()

        # Attach close button press with popup.dismiss action

        connect_btn.bind(on_release=lambda info: self.open_server_window(info=server_info.text))
        close_btn.bind(on_press=popup.dismiss)

    def open_server_window(self, info):
        layout = ServerWindow(info)
        popup = Popup(title='MONA - Server - {}'.format(info),
                      content=layout,
                      size_hint=(1, 1))
        popup.open()

    def select_volume(self, obj):

        choose_volume_layout = FloatLayout()

        volumes = win32api.GetLogicalDriveStrings()
        volumes = volumes.split('\000')[:-1]
        for i, element in enumerate(volumes):
            volumes[i] = element.replace('/', '')

        dropdown = DropDown()
        for i in range(len(volumes)):
            # When adding widgets, we need to specify the height manually
            # (disabling the size_hint_y) so the dropdown can calculate
            # the area it needs.

            btn = Button(text=volumes[i], size_hint_y=None, height=20)

            # for each button, attach a callback that will call the select() method
            # on the dropdown. We'll pass the text of the button as the data of the
            # selection.
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))

            # then add the button inside the dropdown
            dropdown.add_widget(btn)

        # create a big main button
        main_button = Button(text='Choose the Volume', size_hint=(.7, .3),
                             pos_hint={'center_x': .5, 'center_y': .7})

        # show the dropdown menu when the main button is released
        # note: all the bind() calls pass the instance of the caller (here, the
        # mainbutton instance) as the first argument of the callback (here,
        # dropdown.open.).
        main_button.bind(on_release=dropdown.open)

        # one last thing, listen for the selection in the dropdown list and
        # assign the data to the button text.
        dropdown.bind(on_select=lambda instance, x: setattr(main_button, 'text', x))

        connect_btn = Button(text="Confirm selection", size_hint=(.7, .3),
                             pos_hint={'center_x': .5, 'center_y': .3})

        choose_volume_layout.add_widget(main_button)
        choose_volume_layout.add_widget(connect_btn)

        popup_volume = Popup(title='Volume chooser',
                             content=choose_volume_layout,
                             size_hint=(None, None), size=(300, 200))
        popup_volume.open()

        # Attach close button press with popup.dismiss action

        connect_btn.bind(on_release=lambda info: self.connect_to_folder(volume=main_button.text))

    def connect_to_folder(self, volume=''):

        layout = FloatLayout()

        folder_info = FileChooserListView(rootpath=volume, size_hint=(1, .75),
                                          pos_hint={'center_x': .5, 'center_y': .6})

        connect_btn = Button(text="Connect", size_hint=(.2, .1),
                             pos_hint={'center_x': .25, 'center_y': .1})
        close_btn = Button(text="Cancel", size_hint=(.2, .1),
                           pos_hint={'center_x': .75, 'center_y': .1})

        layout.add_widget(folder_info)
        layout.add_widget(connect_btn)
        layout.add_widget(close_btn)

        # Instantiate the modal popup and display
        popup = Popup(title='Folder connection',
                      content=layout,
                      size_hint=(1, 1))
        popup.open()

        # Attach close button press with popup.dismiss action
        connect_btn.bind(on_release=lambda info: self.open_folder_window(path=folder_info.path))
        close_btn.bind(on_press=popup.dismiss)

    def open_folder_window(self, path):
        layout = FolderWindow(path)
        popup = Popup(title='MONA - Folder - {}'.format(path),
                      content=layout,
                      size_hint=(1, 1))
        popup.open()


    def upload_files(self, obj):
        pass


class MONA(App):
    def build(self):
        return Connection(size_hint=(1, 1))


if __name__ == '__main__':
    MONA().run()
