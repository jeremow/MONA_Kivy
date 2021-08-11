# -*- coding: utf-8 -*-

# SERVER POPUP LAYOUT
# Author: Jérémy Hraman
# Date: 23-03-2021
# Last Update: 23-03-2021

from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.popup import Popup
from interface import *
from kivy.clock import Clock

import xml.etree.ElementTree as ET

from obspy.clients.seedlink import Client
from obspy.clients.seedlink.seedlinkexception import SeedLinkException
from obspy import UTCDateTime
import time
from os import getpid
from psutil import Process

from threading import Thread  # Work with Thread to avoid freezing windows
import gc


class ServerSeisComP3(Client):
    """
    ServerSeisComP3 class
    """
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = int(port)
        super(ServerSeisComP3, self).__init__(server=self.ip_address, port=self.port)

    def connect_to_server(self, network, station, location, channel, starttime, endtime):
        time.sleep(1)
        connection = Popup(title='MONA - Server - {}'.format(self.ip_address),
                           content=Label(text='Connection in progress'),
                           size_hint=(.5, .2), auto_dismiss=False)
        connection.open()
        try:
            _ = self.get_waveforms(network, station, location, channel, starttime, endtime)
            info = Label(text='Connection to Server Successful')

        except SeedLinkException:
            info = Label(text='Config file is not matching with the SeedLink Server')

        connection.dismiss()
        Popup(title='MONA - Server - {}'.format(self.ip_address),
              content=info,
              size_hint=(.5, .2)).open()


class ServerWindow(GridLayout):

    def __init__(self, *args, **kwargs):
        super(ServerWindow, self).__init__(**kwargs)

        # Verification of the ip address, throw an error if IP is not 4 numbers distinguish by a point
        # Port is separated by ':'
        try:
            self.server_info = args[0]
            info = self.server_info.split(':')
            self.ip_address = info[0]
            try:
                self.port = info[1]
            except IndexError:
                self.port = '18000'

        except IndexError:
            # Display the error message in case of an error in the writing of the IP
            error_title = Label(text='Wrong syntax of IP\n Press escape to correct.', font_size=60,
                                pos_hint={'center_x': .5, 'center_y': .5})
            self.add_widget(error_title)
        else:
            # Main Interface of MONA imported from interface.py. Interface.py is a group of widgets useable to display
            # all different modules we want. You can choose the size, position here.

            self.client = ServerSeisComP3(self.ip_address, self.port)

            network_list = []
            try:
                config_server = ET.parse('config/server/{}.xml'.format(self.ip_address + '.' + self.port))
                config_server_root = config_server.getroot()
                net_nb = 0
                for network in config_server_root:
                    network_name = network.attrib['name']
                    network_list.append([network_name])
                    for station in config_server_root.findall("./network[@name='{0}']/station".format(network_name)):
                        station_name = station.attrib['name']
                        channel_list = []
                        for channel in config_server_root.findall("./network[@name='{0}']/"
                                                                  "station[@name='{1}']/"
                                                                  "channel".format(network_name, station_name)):
                            if channel.attrib['location'] == '':
                                channel_list.append(channel.attrib['name'])
                            else:
                                channel_list.append(channel.attrib['location'] + '.' + channel.attrib['name'])

                        network_list[net_nb].append([station_name, channel_list])
                    net_nb += 1

                s_network = network_list[0][0]
                s_station = network_list[0][1][0]
                s_locchan = network_list[0][1][1][0].split('.')
                if len(s_locchan) == 2:
                    s_location = s_locchan[0]
                    s_channel = s_locchan[1]
                else:
                    s_location = ''
                    s_channel = s_locchan[0]

                s_time = UTCDateTime() - 10
                Thread(target=self.client.connect_to_server,
                       args=(s_network, s_station, s_location, s_channel, s_time, s_time + 2)).start()

            except FileNotFoundError:
                print('Config file of server missing.')
            except IndexError:
                print('Verify the config file, no station found')

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
            # self.t_figures will store the reference of the class MatplotlibFigure to avoid creating again
            # MatplotlibFigure for nothing when updating the list of stations from the NetworkTreeView to the t_curves
            # tab.
            self.t_figures = []
            self.layout = BoxLayout(orientation='vertical')
            self.update_time_button = Button(text="Update list of stations", size=(300, 40),
                                             size_hint=(None, None), pos_hint={'center_x': .5})

            self.t_curves = t_curves_tab(self.stations_active_list, self.t_figures, client=self.client)

            self.layout.add_widget(self.update_time_button)
            self.layout.add_widget(self.t_curves)

            # Allow the update of the active_list of stations: the operation of doing it automatically is way more
            # complicated than just push a button with a callback on_release.
            # self.update_time_button.bind(on_release=self.on_release_t_curves)
            self.update_time_button.bind(on_release=self.on_release_t_curves) # test with thread

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
            self.nc_alarms_list_checked = []
            self.in_progress_alarms_tree = AlarmTreeView(title='Alarms in progress', alarms_list=self.nc_alarms_list,
                                                         check=True, check_list=self.nc_alarms_list_checked)
            self.in_progress_scroll_layout.add_widget(self.in_progress_alarms_tree)
            tab_alarms_grid.add_widget(self.in_progress_scroll_layout)

            # ALARMS COMPLETED SCROLL TO BOTTOM VIEW
            self.completed_scroll_layout = ScrollView(size_hint=(.5, .9))
            self.completed_alarms_tree = AlarmTreeView(title='Alarms completed', alarms_list=self.c_alarms_list,
                                                       check=False, check_list=[])
            self.completed_scroll_layout.add_widget(self.completed_alarms_tree)
            tab_alarms_grid.add_widget(self.completed_scroll_layout)

            tab_alarms_layout.add_widget(tab_alarms_grid)

            self.complete_alarm_btn = Button(text='Finish checked alarms', size_hint=(.5, .1))
            self.complete_alarm_btn.bind(on_release=self.complete_alarms)
            tab_alarms_grid.add_widget(self.complete_alarm_btn)

            layout_central_bottom.add_widget(tab_alarms_layout)

            tab_PSD = TabbedPanelItem(text='PSD')

            self.psd_layout = BoxLayout()
            self.psd_fig, _ = plt.subplots()
            self.auto_moving_x = True
            self.auto_moving_y = True
            self.psd_fig.clf()

            self.psd_xmin = 0.001
            self.psd_xmax = 1
            self.psd_ymin = 0
            self.psd_ymax = 1

            self.psd_plot, = plt.plot(0, 0, figure=self.psd_fig)

            self.psd_fig.axes[0].tick_params(axis='both', which='major', labelsize=14)
            self.psd_fig.axes[0].tick_params(axis='both', which='minor', labelsize=14)

            self.delta_x = self.psd_xmax - self.psd_xmin
            self.psd_fig.axes[0].set_xlim(self.psd_xmin, self.psd_xmax)
            self.psd_ymin, self.psd_ymax = self.psd_fig.axes[0].get_ylim()

            self.psd_fig.canvas.draw()


            # self.psd_figure = PSDFigure(t_figures=self.t_figures)
            self.psd_layout.add_widget(self.psd_fig.canvas)
            tab_PSD.add_widget(self.psd_layout)

            layout_central_bottom.add_widget(tab_PSD)

            self.add_widget(layout_central_bottom)

            # on_selected_node_thread = ServerThread(self.on_selected_node, 0.5)
            # update_states_thread = ServerThread(self.update_states, 30)
            # update_alarms_thread = ServerThread(self.update_alarms, 30)
            # update_curves_thread = ServerThread(self.update_curves, 10)

            # self.endtime = UTCDateTime()
            # update_time_thread = ServerThread(self.update_time, 10)
            # self.get_data_thread = ServerThread(self.get_data, 10)
            self.update_figures_thread = ServerThread(self.get_data, self.update_figures, self.update_psd, dt=8)

            # on_selected_node_thread.start()
            # update_states_thread.start()
            # update_alarms_thread.start()
            # update_time_thread.start()
            # self.get_data_thread.start()
            self.update_figures_thread.start()

            Clock.schedule_interval(self.on_selected_node, 0.5)
            Clock.schedule_interval(self.update_states, 30)
            Clock.schedule_interval(self.update_alarms, 30)
            Clock.schedule_interval(self.garbage_collect, 30)

    def on_release_t_curves(self, btn):
        # To update the number of stations in curves, we have to remove the widget and add it again just after

        self.layout.remove_widget(self.t_curves)

        # self.get_data_thread.terminate()
        self.update_figures_thread.terminate()
        del self.update_figures_thread

        self.t_curves.children[0].clear_widgets()
        self.t_curves.clear_widgets()
        del self.t_curves
        self.t_curves = t_curves_tab(self.stations_active_list, self.t_figures, client=self.client)

        # self.get_data_thread = ServerThread(self.get_data, 10)
        self.update_figures_thread = ServerThread(self.get_data, self.update_figures, dt=8)
        # self.get_data_thread.start()
        self.update_figures_thread.start()

        self.layout.add_widget(self.t_curves)

    def on_selected_node(self, dt):
        if self.selected_node is not self.stations_widget.selected_node:
            self.selected_node = self.stations_widget.selected_node
            try:
                if self.selected_node.is_station:
                    self.state_network = self.selected_node.network
                    self.state_station = self.selected_node.text
                    Clock.schedule_once(self.update_states)
            except AttributeError:
                pass

    def update_states(self, dt):
        self.states = []
        try:
            states_server = ET.parse('log/server/{}_states.xml'.format(self.ip_address + '.' + self.port))
            states_server_root = states_server.getroot()
            for state in states_server_root.findall("./network[@name='{0}']/station[@name='{1}']/"
                                                    "state".format(self.state_network, self.state_station)):
                self.states.append([state.attrib['name'], state.attrib['value'], int(state.attrib['problem'])])
            del states_server, states_server_root
        except FileNotFoundError:
            pass

        self.state_layout.remove_widget(self.states_tree)
        self.states_tree.clear_widgets()
        del self.states_tree
        self.states_tree = StateTreeView(title='States of {}'.format(self.state_station), state_list=self.states)
        self.state_layout.add_widget(self.states_tree)

    def get_data(self, endtime):
        for figure in self.t_figures:
            figure.get_data_from_client(endtime)

    def update_figures(self, endtime):
        for figure in self.t_figures:
            figure.update_figure(endtime)

    def update_psd(self, dt):
        self.psd_fig.clf()
        for figure in self.t_figures:
            plt.plot(figure.f, figure.psd, figure=self.psd_fig)

        if len(self.t_figures) != 0:
            self.psd_fig.axes[0].set_xlim(self.psd_xmin, self.psd_xmax)
            self.psd_fig.axes[0].set_ylim(self.psd_ymin, self.psd_ymax)

        self.psd_fig.canvas.draw()
        self.psd_fig.canvas.flush_events()

    def update_alarms(self, dt):
        # nc_alarms_list: non-completed alarms list ; c_alarms_list: completed one
        self.nc_alarms_list = []
        self.c_alarms_list = []
        try:
            alarms_server = ET.parse('log/server/{}_alarms.xml'.format(self.ip_address + '.' + self.port))
            alarms_server_root = alarms_server.getroot()

            # display all the ongoing alarms
            for alarm in alarms_server_root.findall("./ongoing/alarm"):
                alarm_name = alarm.attrib['station'] + ' - ' + \
                             alarm.attrib['state'] + ' - ' + \
                             alarm.attrib['detail']
                alarm_dt = alarm.attrib['datetime']
                alarm_datetime = alarm_dt[1:5] + '-' + alarm_dt[5:7] + '-' + \
                                 alarm_dt[7:9] + ' ' + alarm_dt[10:12] + ':' + \
                                 alarm_dt[12:14] + ':' + alarm_dt[14:]

                self.nc_alarms_list.append([alarm_datetime, alarm_name, alarm.attrib])

            # display the 20 last completed alarms
            for alarm in alarms_server_root.findall("./completed/alarm")[-20:]:
                alarm_name = alarm.attrib['station'] + ' - ' + \
                             alarm.attrib['state'] + ' - ' + \
                             alarm.attrib['detail']
                alarm_dt = alarm.attrib['datetime']
                alarm_datetime = alarm_dt[1:5] + '-' + alarm_dt[5:7] + '-' + \
                                 alarm_dt[7:9] + ' ' + alarm_dt[10:12] + ':' + \
                                 alarm_dt[12:14] + ':' + alarm_dt[14:]

                self.c_alarms_list.append([alarm_datetime, alarm_name, alarm.attrib])
            del alarms_server, alarms_server_root, alarm_name, alarm_dt, alarm_datetime

        except FileNotFoundError:
            pass
        self.nc_alarms_list.reverse()
        self.c_alarms_list.reverse()

        self.in_progress_scroll_layout.remove_widget(self.in_progress_alarms_tree)
        self.completed_scroll_layout.remove_widget(self.completed_alarms_tree)
        self.in_progress_alarms_tree.clear_widgets()
        self.completed_alarms_tree.clear_widgets()
        del self.in_progress_alarms_tree
        del self.completed_alarms_tree

        self.in_progress_alarms_tree = AlarmTreeView(title='Alarms in progress', alarms_list=self.nc_alarms_list,
                                                     check=True, check_list=self.nc_alarms_list_checked)
        self.completed_alarms_tree = AlarmTreeView(title='Alarms completed', alarms_list=self.c_alarms_list,
                                                   check=False, check_list=[])

        self.in_progress_scroll_layout.add_widget(self.in_progress_alarms_tree)
        self.completed_scroll_layout.add_widget(self.completed_alarms_tree)

    def complete_alarms(self, btn):
        try:
            alarms_server = ET.parse('log/server/{}_alarms.xml'.format(self.server_info.replace(':', '.')))
            alarms_server_root = alarms_server.getroot()
            for checked_alarm in self.nc_alarms_list_checked:
                self.nc_alarms_list_checked.remove(checked_alarm)
                alarm_to_move = alarms_server_root.find("./ongoing/alarm[@id='{}']".format(checked_alarm['id']))
                alarms_server_root[1][-1].tail = '\n\t\t'
                alarms_server_root[1].text = "\n\t\t"
                alarms_server_root[1].append(alarm_to_move)
                alarms_server_root[0].remove(alarm_to_move)
                alarms_server_root[0][-1].tail = "\n\t"
                alarms_server_root[0].text = "\n\t\t"
                alarms_server_root[0].tail = '\n\n\t'

            alarms_server.write('log/server/{}_alarms.xml'.format(self.server_info.replace(':', '.')))

            Clock.schedule_once(self.update_alarms)

        except FileNotFoundError:
            pass

    def garbage_collect(self, dt):
        print('GC_Start:', Process(getpid()).memory_info().rss / 1024 ** 2, 'MB')
        gc.collect()


class ServerThread(Thread):
    def __init__(self, *functions, dt=0.0):
        Thread.__init__(self)
        self.functions = functions
        self.endtime = UTCDateTime()
        self.dt = dt
        self.daemon = True
        self._running = True

    def terminate(self):
        self._running = False

    def run(self):
        while self._running:
            self.endtime = UTCDateTime()
            for function in self.functions:
                function(self.endtime)
                time.sleep(1.5)
            time.sleep(self.dt)
