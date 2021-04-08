# -*- coding: utf-8 -*-

# FOLDER LAYOUT
# Author: Jérémy Hraman
# Date: 23-03-2021
# Last Update: 23-03-2021

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
import os


class FolderWindow(FloatLayout):
    def __init__(self, *args, **kwargs):
        super(FolderWindow, self).__init__(**kwargs)

        self.folder = args[0]
        self.list_files = self.get_tree(self.folder)
        self.rel_path(self.folder)

        main_title = Label(text='MONA - FOLDER', font_size=60, pos_hint={'center_x': .5, 'center_y': .5})
        self.add_widget(main_title)

    def get_tree(self, path):
        # create a list of file and sub directories
        # names in the given directory
        list_files = os.listdir(path)
        all_files = []
        # Iterate over all the entries
        for entry in list_files:
            # Create full path
            full_path = os.path.join(path, entry)
            # If entry is a directory then get the list of files in this directory
            if os.path.isdir(full_path):
                all_files = all_files + self.get_tree(full_path)
            else:
                all_files.append(full_path)
        return all_files

    def rel_path(self, root_path):
        for i, element in enumerate(self.list_files):
            self.list_files[i] = os.path.relpath(element, root_path)
