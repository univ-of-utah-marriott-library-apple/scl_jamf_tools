#!/usr/bin/python

# Copyright (c) 2017 University of Utah Student Computing Labs. ################
# All Rights Reserved.
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appears in all copies and
# that both that copyright notice and this permission notice appear
# in supporting documentation, and that the name of The University
# of Utah not be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior
# permission. This software is supplied as is without expressed or
# implied warranties of any kind.
################################################################################

# cargo_ship.py #################################################
#
# A Python Tk application to view Jamf computer records.
#
#
#    1.0.0  2017.02.15      Initial public release. tjm
#
#    1.0.1  2017.04.11      Many tweaks. tjm
#                           management tools logging integrated
#                           login funtion much improved
#                           search function much improved
#                           display fields improved
#
#    1.0.2  2017.05.24      Added last inventory date. tjm
#
#    1.0.3  2018.1.xx       Added LDAP login logic. tjm
#                           Added multiprocess policy parsing
#
################################################################################

# notes: #######################################################################
#
#     py2app:
#     rm -rdf build dist ; /usr/bin/python setup.py py2app -s
#
#
#
#
################################################################################

from __future__ import print_function
from Tkinter import *
import tkFont
import ttk
import tkMessageBox
import subprocess
import os
import re
import urllib
import urllib2
import json
import base64
import locale
import sys
import platform
import webbrowser
import multiprocess
import time
import inspect
import ScrolledText
from xml.dom.minidom import parseString
from management_tools import loggers

class Summarize(object):
    """
    Store keys, manipulate keys, output script and build the package
    """

    def __init__(self, root, logger, jamf_hostname, jamf_username, jamf_password):
        """
        Initialize object and variables
        """
        self.root = root
        self.logger = logger
        self.jamf_hostname = jamf_hostname
        self.jamf_username = jamf_username
        self.jamf_password = jamf_password
        self.local_jamf_id = None

        self.computer_name_string = StringVar()
        self.fullname_string = StringVar()
        self.search_string = StringVar()
        self.status_string = StringVar()
        self.checkin_string = StringVar()
        self.id_string = StringVar()
        self.inventory_string = StringVar()

        self.status_string.set("Ready.")

        self.status_warning = ttk.Style()
        self.status_warning.configure('Warning.TLabel', foreground='red')

        self.status_normal = ttk.Style()
        self.status_normal.configure('Normal.TLabel', foreground='black')

        #
        # These methods are time intensive based on the number of each in your database
        self.jamf_policies = self.build_policies()
        self.jamf_profiles = self.build_profiles()

        self.build_ui()

    def build_ui(self):
        """
        Build UI
        """

        #
        # This is an encoded gif of the title image
        self.logo_image = '''\
        R0lGODlhWAJRAPcAAAEAAAwMDQMJCwwMEwUNExEOFQwSFAsVGwgVGhITExUVHBcZGhIPDScYGCch
        HA0aIgkYJRMdJBgcJQ8aLg0gKhUiKxwmLR0oLxciJxwmMh4pMRopOBouNSYmJiUoKjQqJyIrMyQr
        Nys0PCY0OTc1OjUyLyQfHlQREEc6OVUvMG0yNWYjJRQ1TSk3RDU8QiE+VFA9R3I5QjhGSjtTWDJI
        UxlMajFTay1TZ0JCQkdJS1lHSERMU0hVWlhYWFZVWFNOU2dHSnVISGhLU2lXWndYWXNPUGxkXEpa
        ZVdcZEtTbmlbYndbYmtacUtjaVlmakpld1hqdV1xd2RrbGxra2dlZXxsbHZmZ2tybndza2ZtdHhq
        c21zdGx1e2d2eXN0dHR7fHx8fXh4dltkV1VCOY4vNsQSMMcfO8chPMgjPpZMNJI8SKc7S846U8kq
        RIhaWJhWWpBJUahMT5NjW6lpV5daYYJcZ6ZYZIVoaZdoaId4eJR3eI9vcKVmZ61wdNFGXs9BWdJM
        Y9RSZ9RVatlnetdsRHqCfWqCfoSEfZSDeqWFejVokydumlFzjGh5hXR7g3p9gnN3h254kFJ8oYV9
        g4t3hNtugN13iHyDhHiFiWqGl3qIlXSJjnmUpWyRrFmMqE+Xw4ODg4KFioWLi4yNjImIhpSIioqS
        jZWUjYOMk4uNkoeKl4yTlIyUm4WVmJOUlJOWm5SanJycnJmXlpSMlKOZmqWRhpyhnaWjnbKnmoqa
        pZScopucooqWqZ2ipJikqZmotoyovKOkpKKlq6WqrKqqqqmopbSsqa2xrLSzraess6yytKu1ubK0
        tLS6vLi5ube2uLKus6mfpOKKmeGFlOSQnuaap+qrtsK7ur7Cvc/DvZSzyaa5x7a8wae91NO9w7zD
        xrjI1KzF2LfR5cXFxcfKysbN1MfT2tHR0d3d3djY2tHOzPDCyu/O0snZ5tXb5djj6tjo9crg8+np
        6ePn6+Tt9ez0+fT09Pzz9f////X3+vvv8eLd5QAAAAAAAAAAAAAAACH5BAAAAAAALAAAAABYAlEA
        AAj+APEJHEiwoMGDCBMqXMiwocOHECNKnEixosWLGDNq3Mixo8ePIEOKHEmypMmTKFOqXMmypcuX
        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
        vQCnx33q4W/yBmh97yBHAQ5KUAjm9z93QoYKKYC05UK8/lMoTjsDM1DABVTABGTAM4BABmzABXRA
        wGi8m1gHS1iHx7MEdtCLG4CAUxk9BeiUTjGA2ivB1Gu/FRQA0UOt9VtBqkM9kzs9q4O/+tu6Eug6
        FBiDEhhAA9y3dCCGWJCCKpCCUiCGLNs1KWDCIsw0IPyqe5DCKaTCKrSpwiu0Qp6ohkpgh0qovLzI
        h26ogANQv6gzFEMxQQFgONoTABSkPRRkAAnoABLsFPJ7wxQ8Qc97P4cjvQXYuvvDART4AUODwkI0
        xENExL54ggzwAAxIPzIUEYd7AIfTPoezxEt0OAlwgRzwAEz0xEzMxAVIPz/0w/tDAR0Yg2JIxFVk
        xVZ0xaEYvleUxVmkxVq0xVvExVzUxV3kxV70xV8ExmAUxmEkxpwICAAh/wtYTVAgRGF0YVhNUDw/
        eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+Cjx4Onht
        cG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUu
        Ni1jMTM4IDc5LjE1OTgyNCwgMjAxNi8wOS8xNC0wMTowOTowMSAgICAgICAgIj4KIDxyZGY6UkRG
        IHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+
        CiAgPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIvPgogPC9yZGY6UkRGPgo8L3g6eG1wbWV0
        YT4KPD94cGFja2V0IGVuZD0iciI/PgH//v38+/r5+Pf29fTz8vHw7+7t7Ovq6ejn5uXk4+Lh4N/e
        3dzb2tnY19bV1NPS0dDPzs3My8rJyMfGxcTDwsHAv769vLu6ubi3trW0s7KxsK+urayrqqmop6al
        pKOioaCfnp2cm5qZmJeWlZSTkpGQj46NjIuKiYiHhoWEg4KBgH9+fXx7enl4d3Z1dHNycXBvbm1s
        a2ppaGdmZWRjYmFgX15dXFtaWVhXVlVUU1JRUE9OTUxLSklIR0ZFRENCQUA/Pj08Ozo5ODc2NTQz
        MjEwLy4tLCsqKSgnJiUkIyIhIB8eHRwbGhkYFxYVFBMSERAPDg0MCwoJCAcGBQQDAgEAADs=
        '''

        self.root.title("Cargo Ship v1.0.3")

        self.mainframe = ttk.Frame(self.root)
        self.mainframe.grid(column=0, row=0, sticky=NSEW)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.geometry('+0+0')

        #
        # values for column widths
        single_width_column = 40
        double_width_column = 84

        #
        # position and display logo image
        self.logo_label = ttk.Label(self.mainframe)
        self.logo_photoimage = PhotoImage(data=self.logo_image)
        self.logo_label['image'] = self.logo_photoimage
        self.logo_label.grid(column=1, row=0, columnspan=10)

        ttk.Separator(self.mainframe, orient=HORIZONTAL).grid(row=30, columnspan=35, sticky=EW)

        #
        # these are the UI navigation elements, if there is a specific button or
        # extension attribute you want to feature it should be added in this section.
        ttk.Label(self.mainframe, text="Summarize:").grid(column=1, row=40, sticky=W)
        ttk.Button(self.mainframe, text="This Device", command=self.query_jamf_me).grid(column=1, row=40)
        ttk.Button(self.mainframe, text="Other ID", width=6, command=self.query_jamf_id).grid(column=1, row=40, sticky=E)

        self.host_entry = ttk.Entry(self.mainframe, width=10, textvariable=self.id_string)
        self.host_entry.config(font=('', 12, 'bold'))
        self.host_entry.grid(column=2, row=40, sticky=EW)

        ttk.Button(self.mainframe, text="Search Jamf", command=self.search_string_jamf).grid(column=3, row=40, sticky=E)
        self.search_entry = ttk.Entry(self.mainframe, width=20, textvariable=self.search_string)
        self.search_entry.config(font=('', 12, 'bold'))
        self.search_entry.grid(column=4, row=40, sticky=EW)

        ttk.Separator(self.mainframe, orient=HORIZONTAL).grid(row=55, columnspan=35, sticky=EW)

        ttk.Label(self.mainframe, text="Computer Name:").grid(column=1, row=60, sticky=E)
        self.cname_display = ttk.Entry(self.mainframe, width=31, state="readonly", textvariable=self.computer_name_string)
        self.cname_display.config(font=('', 12, 'bold'))
        self.cname_display.grid(column=2, row=60, sticky=EW)

        ttk.Label(self.mainframe, text="Last Checkin:").grid(column=3, row=60, sticky=E)
        self.checkin_display = ttk.Entry(self.mainframe, width=31, state="readonly", textvariable=self.checkin_string)
        self.checkin_display.config(font=('', 12, 'bold'))
        self.checkin_display.grid(column=4, row=60, sticky=EW)

        ttk.Label(self.mainframe, text="Last Inventory:").grid(column=3, row=70, sticky=E)
        self.inventory_display = ttk.Entry(self.mainframe, width=31, state="readonly", textvariable=self.inventory_string)
        self.inventory_display.config(font=('', 12, 'bold'))
        self.inventory_display.grid(column=4, row=70, sticky=EW)

        ttk.Label(self.mainframe, text="User's Name:").grid(column=1, row=70, sticky=E)
        self.uname_display = ttk.Entry(self.mainframe, width=31, state="readonly", textvariable=self.fullname_string)
        self.uname_display.config(font=('', 12, 'bold'))
        self.uname_display.grid(column=2, row=70, sticky=EW)

        ttk.Separator(self.mainframe, orient=HORIZONTAL).grid(row=150, columnspan=35, sticky=EW)

        #
        # theses are the large output panes
        ttk.Label(self.mainframe, text="Printers:", font="TkHeadingFont").grid(column=1, row=160, sticky=EW)
        self.printer_field = ScrolledText.ScrolledText(self.mainframe, width=single_width_column, height=15, wrap='none')
        self.printer_field.grid(column=1, row=165, pady=1, padx=1)

        ttk.Label(self.mainframe, text="Computer Groups:", font="TkHeadingFont").grid(column=2, row=160, sticky=EW)
        self.group_field = ScrolledText.ScrolledText(self.mainframe, width=single_width_column, height=15, wrap='none')
        self.group_field.grid(column=2, row=165, pady=1, padx=1)

        ttk.Label(self.mainframe, text="Profiles:", font="TkHeadingFont").grid(column=3, row=160, sticky=EW)
        self.jamf_profiles_field = ScrolledText.ScrolledText(self.mainframe, width=single_width_column, height=15, wrap='none')
        self.jamf_profiles_field.grid(column=3, row=165, pady=1, padx=1)

        ttk.Label(self.mainframe, text="Policies:", font="TkHeadingFont").grid(column=4, row=160, sticky=EW)
        self.jamf_policies_field = ScrolledText.ScrolledText(self.mainframe, width=single_width_column, height=15, wrap='none')
        self.jamf_policies_field.grid(column=4, row=165, pady=1, padx=1)

        ttk.Label(self.mainframe, text="Extension Attributes:", font="TkHeadingFont").grid(column=1, row=180, sticky=W)
        self.ea_field = ScrolledText.ScrolledText(self.mainframe, width=double_width_column, height=15, wrap='none')
        self.ea_field.grid(column=1, row=185, columnspan=2, pady=1, padx=1)

        ttk.Label(self.mainframe, text="Packages:", font="TkHeadingFont").grid(column=3, row=180, sticky=W)
        self.package_field = ScrolledText.ScrolledText(self.mainframe, width=double_width_column, height=15, wrap='none')
        self.package_field.grid(column=3, row=185, columnspan=2, pady=1, padx=1)

        ttk.Separator(self.mainframe, orient=HORIZONTAL).grid(row=290, columnspan=35, sticky=EW)

        #
        # status bar and quit button
        self.status_label = ttk.Label(self.mainframe, textvariable=self.status_string)
        self.status_label.grid(column=1, row=300, sticky=W, columnspan=50)

        ttk.Button(self.mainframe, text="Quit", command=self.root.destroy).grid(column=4, row=300, sticky=E)

    def search_string_jamf(self):
        """
        This method handles searching Jamf with a string
        """
        self.logger.info("%s: activated" % inspect.stack()[0][3])

        def double_click(*event):
            """
            handle clicks
            """

            #
            # when a click occurs, parse out ID from string and call query method
            selected = listbox.get(listbox.curselection())
            trim_select = re.search(r'\((.*)\)', selected).group(1)

            self.id_string.set(trim_select)
            self.query_jamf_id()

            self.root.lift()

        # you need to clear all the fields...
        self.reset_display()
        self.id_string.set("")

        if self.search_string.get() == "" or self.search_string.get().replace(" ", "") == "":
            if self.id_string.get():
                self.query_jamf_id()
                self.status_label.configure(style='Normal.TLabel')
                self.status_string.set("Searched for ID.")
                self.logger.info("%s: searched for ID: %r" % (inspect.stack()[0][3], self.id_string.get()))
            else:
                self.logger.error("%s: No search string" % inspect.stack()[0][3])
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("No search string entered.")

        else:
            self.logger.info("%s: searched for string: %r" % (inspect.stack()[0][3], self.search_string.get()))

            #
            # erase previous displayed values
#             self.reset_data()

            #
            # encode special characters included in search string
            url = self.jamf_hostname + '/JSSResource/computers/match/' + urllib.quote('*' + self.search_string.get() + '*')
            self.logger.info("%s: searched with url: %r" % (inspect.stack()[0][3], url))

            #
            # communicate with Jamf server
            try:
                request = urllib2.Request(url)
                request.add_header('Accept', 'application/json')
                request.add_header('Authorization', 'Basic ' + base64.b64encode(self.jamf_username + ':' + self.jamf_password))

                response = urllib2.urlopen(request)
                try:
                    response_json = json.loads(response.read())
                except Exception as exception_message:
                    self.logger.error("issue parsing JSON: %r" % exception_message)
                    return
                #
                # a non-200 response is bad, report and return
                if response.code != 200:
                    self.logger.error("%s: error from jss" % inspect.stack()[0][3])
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("%i returned." % response.code)
                    return

            #
            # handle various communication errors
            except urllib2.HTTPError, error:
                if error.code == 400:
                    self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Request error."))
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s" % (error.code, "Request error."))
                elif error.code == 401:
                    self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Authorization error."))
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s" % (error.code, "Authorization error."))
                elif error.code == 403:
                    self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Permissions error."))
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s" % (error.code, "Permissions error."))
                elif error.code == 404:
                    self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Resource not found."))
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s" % (error.code, "Resource not found."))
                elif error.code == 409:
                    contents = error.read()
                    error_message = re.findall(r"Error: (.*)<", contents)
                    print("HTTP code %i: %s %s %s" % (error.code, "Resource conflict.", error_message[0], self.id_string.get()))
                    self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Resource conflict. " + error_message[0]))
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s" % (error.code, "Resource conflict. " + error_message[0]))
                else:
                    self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Generic error."))
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s" % (error.code, "Generic error."))
                return
            except urllib2.URLError, error:
                self.logger.error("%s: Error contacting JSS." % (inspect.stack()[0][3]))
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("Error contacting JSS.")
                return
            except Exception as exception_message:
                self.logger.error("%s: Error querying Jamf. [%s]" % (inspect.stack()[0][3], exception_message))
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("Error querying Jamf. [%s]" % exception_message)
                return

            #
            # begin parsing data returned from Jamf
            self.status_label.configure(style='Normal.TLabel')
            self.status_string.set("%i matches returned." % len(response_json['computers']))
            self.logger.info("%s: %r" % (inspect.stack()[0][3], self.status_string.get()))


            search_font = tkFont.Font(font='TkDefaultFont')
            match_results = []
            max_length = 0
            #
            # parse each returned computer element, retaining Jamf ID and Computer name
            # properly format value to display
            # build a version of the computer name used to sort by
            #  these rules are for our environment and may have no effect in yours.
            #  if the name is in the format "labmac-1" the integer is expanded to -0001
            #  if the name is in the format "[lost] labmac-1" the sorting name is stored as
            #    "labmac-1a" to differentiate it from "labmac-1"
            # the values are added to a list containing the previously processed values as
            #   [sorting name, computer name, jamf id]
            for node in response_json['computers']:
                match_id = node['id']
                match_name = node['name']
                if not match_name:
                    match_name = "Not named."

                name_trim = match_name

                try:
                    number_part = re.search(r'(\d+)', name_trim).group(1)
                    number_free = "".join([i for i in name_trim if not i.isdigit()])
                    expanded_number = '{:04d}'.format(int(number_part))
                    expanded_x = number_free + expanded_number
                    name_trim = expanded_x
                except:
                    pass

                if "[" in name_trim:
                    name_trim = re.search(r']([ -]*)(.*)', name_trim).group(2)
                    name_trim = str(name_trim) + "a"

                match_results.append([name_trim, match_name, match_id])
                (string_width, string_height) = (search_font.measure(match_name +" (" + str(match_id) + ")"), search_font.metrics("linespace"))
                if max_length < string_width:
                    max_length = string_width

            #
            # if there were returned results, build and display search results window
            #
            #
            # position results window next to the main window, even if it has moved
            #  from the original location
            # while sorting the list based on the synthetic string,
            #  display the computer name and ID
            # bind clicks to function
            if match_results:

                search_window = Toplevel()

                split_geom = self.root.winfo_geometry().split("+")
                r_h = int(split_geom[0].split("x")[0])
                r_pos_x = int(split_geom[1])
                r_pos_y = int(split_geom[2])
                string_width = int(max_length + 22)

                search_window_geo = "%ix%i+%i+%i" % (string_width, 400, (r_h + r_pos_x + 10), (r_pos_y))
                search_window.geometry(search_window_geo)

                search_window.title("Search results")

                list_frame = ttk.Frame(search_window, width=string_width, height=400, padding=(4, 0, 0, 0))

                scrollbar = Scrollbar(list_frame)
                scrollbar.pack(side=RIGHT, fill=Y)

                listbox = Listbox(list_frame, bd=0, yscrollcommand=scrollbar.set, selectmode=SINGLE, width=190, height=400)
                listbox.pack()

                scrollbar.config(command=listbox.yview)

                list_frame.pack()

                for item in sorted(match_results):
                    insert_string = item[1] +" (" + str(item[2]) + ")"
                    listbox.insert(END, insert_string)

                listbox.bind("<<ListboxSelect>>", double_click)

                search_window.mainloop()

    def build_profiles(self):
        """
        Fetch and build profile data structures
        """
        #
        # communicate with Jamf and grab generic profile list
        # parse list, building dictionary along the way
        # this should proceed quickly.

        #
        # communicate with Jamf server
        self.logger.info("%s: activated" % inspect.stack()[0][3])
        try:
            url = self.jamf_hostname + '/JSSResource/osxconfigurationprofiles'
            request = urllib2.Request(url)
            request.add_header('Accept', 'application/json')
            request.add_header('Authorization', 'Basic ' + base64.b64encode(self.jamf_username + ':' + self.jamf_password))

            response = urllib2.urlopen(request)
            response_json = json.loads(response.read())

            #
            # a non-200 response is bad, report and return
            if response.code != 200:
                self.logger.error("%s: error from jss" % inspect.stack()[0][3])
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("%i returned." % response.code)
                return

        #
        # handle various communication errors
        except urllib2.HTTPError, error:
            if error.code == 400:
                self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Request error."))
                tkMessageBox.showerror("Error", ("HTTP code %i: %s " % (error.code, "Request error.")))
            elif error.code == 401:
                self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Authorization error."))
                tkMessageBox.showerror("Error", ("HTTP code %i: %s " % (error.code, "Authorization error.")))
            elif error.code == 403:
                self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Permissions error."))
                tkMessageBox.showerror("Error", ("HTTP code %i: %s " % (error.code, "Permissions error.")))
            elif error.code == 404:
                self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Resource not found."))
                tkMessageBox.showerror("Error", ("HTTP code %i: %s " % (error.code, "Resource not found.")))
            elif error.code == 409:
                contents = error.read()
                error_message = re.findall(r"Error: (.*)<", contents)
                self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Resource conflict. " + error_message[0]))
                tkMessageBox.showerror("Error", ("HTTP code %i: %s " % (error.code, "Resource conflict. " + error_message[0])))
            else:
                self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Generic error."))
                tkMessageBox.showerror("Error", ("HTTP code %i: %s " % (error.code, "Generic error.")))

            sys.exit()
        except urllib2.URLError, error:
            self.logger.error("%s: Error contacting JSS." % (inspect.stack()[0][3]))
            tkMessageBox.showerror("Error", "Error contacting JAMF server.")
            sys.exit()
        except Exception as exception_message:
            self.logger.error("%s: Error querying Jamf. [%s]" % (inspect.stack()[0][3], exception_message))
            tkMessageBox.showerror("Error", ("Error querying Jamf. [%s]" % exception_message))
            sys.exit()

        tmp_profiles = {}

        for item in response_json['os_x_configuration_profiles']:
            tmp_profiles[item["id"]] = item["name"]

        self.logger.info("%s: %i profiles" % (inspect.stack()[0][3], len(tmp_profiles)))
        self.logger.info("%s: complete" % inspect.stack()[0][3])
        return tmp_profiles

    def build_policies(self):
        """
        fetch and build policy data structures
        """
        #
        # communicate with Jamf and grab generic policy list
        #
        #             --- this is the slow bit ---
        # communicate with Jamf and grab each individual policy record
        #  with each record
        #   retain name, id and if the policy applies to all computers
        #   retain IDs of specific computers the policy applies to
        #   retain ID's and names of computer groups the policy applies to
        #  add these values as a list to previously processed policies
        # this will not proceed quickly.


        #
        # There have to be better ways to handle this...
        #
        # Split off account info, to limit the number of parameters going into the mapped funtion
        global local_jamf_hostname
        global local_jamf_password
        global local_jamf_username
        global local_logger

        local_jamf_hostname = self.jamf_hostname
        local_jamf_password = self.jamf_password
        local_jamf_username = self.jamf_username
        local_logger = self.logger

        def fetch_parse_policy(this_policy):
            """
            pull policy from jss and parse.
            does it make more sense to parse outside the function?!? speedwise?
            """
            local_logger.info("fetch_parse_policy: fetching policy #%s" % this_policy)

            #
            # communicate with Jamf server
            try:
                url = local_jamf_hostname + '/JSSResource/policies/id/'+ this_policy +'/subset/general&scope'
                request = urllib2.Request(url)
                request.add_header('Accept', 'application/json')
                request.add_header('Authorization', 'Basic ' + base64.b64encode(local_jamf_username + ':' + local_jamf_password))

                response = urllib2.urlopen(request)
                response_json = json.loads(response.read())

                #
                # a non-200 response is bad, report and return
                if response.code != 200:
                    local_logger.error("fetch_parse_policy: Unexpected response: %i" % response.code)
                    return None

            #
            # nowhere near enough error handling...
            # do we really need to exit? try the policy again? Report the error when the UI is drawn?
            # add policy to list, how? it's a single function...
            #
            #
            # return the policy with the name and set an error flag in the list?
            #   return([tmp_name, tmp_id, tmp_all, tmp_cs, tmp_cgroups, error_condition]) ?!?!?
            # check tmp_policies at the end for error flags?
            #   pop the bad policy off the list and note the error in the UI?
            #   quit exit and not the error in the dialog?
            #   have the ui check for error and color red for every machine?
            #   parse final list for errors "error-103"?
            #
            #
            #
            except Exception as exception_message:
                local_logger.error("fetch_parse_policy: Error querying Jamf. [%s] Exiting." % (exception_message))
                sys.exit()

            #
            # return the whole response, postpone processing until all data retrieved
            return response_json

        #
        # communicate with Jamf server
        self.logger.info("%s: activated" % inspect.stack()[0][3])
        try:
            url = self.jamf_hostname + '/JSSResource/policies'
            request = urllib2.Request(url)
            request.add_header('Accept', 'application/json')
            request.add_header('Authorization', 'Basic ' + base64.b64encode(self.jamf_username + ':' + self.jamf_password))

            response = urllib2.urlopen(request)
            response_json = json.loads(response.read())

            #
            # a non-200 response is bad, report and return
            if response.code != 200:
                self.logger.error("%s: error from jss" % inspect.stack()[0][3])
                self.status_string.set("%i returned." % response.code)
                return

        #
        # handle various communication errors
        except urllib2.HTTPError, error:
            if error.code == 400:
                self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Request error."))
                tkMessageBox.showerror("Error", ("HTTP code %i: %s " % (error.code, "Request error.")))
            elif error.code == 401:
                self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Authorization error."))
                tkMessageBox.showerror("Error", ("HTTP code %i: %s " % (error.code, "Authorization error.")))
            elif error.code == 403:
                self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Permissions error."))
                tkMessageBox.showerror("Error", ("HTTP code %i: %s " % (error.code, "Permissions error.")))
            elif error.code == 404:
                self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Resource not found."))
                tkMessageBox.showerror("Error", ("HTTP code %i: %s " % (error.code, "Resource not found.")))
            elif error.code == 409:
                contents = error.read()
                error_message = re.findall(r"Error: (.*)<", contents)
                self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Resource conflict. " + error_message[0]))
                tkMessageBox.showerror("Error", ("HTTP code %i: %s " % (error.code, "Resource conflict. " + error_message[0])))
            else:
                self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Generic error."))
                tkMessageBox.showerror("Error", ("HTTP code %i: %s " % (error.code, "Generic error.")))

            sys.exit()
        except urllib2.URLError, error:
            self.logger.error("%s: Error contacting JSS." % (inspect.stack()[0][3]))
            tkMessageBox.showerror("Error", "Error contacting JAMF server.")
            sys.exit()
        except Exception as exception_message:
            self.logger.error("%s: Error querying Jamf. [%s]" % (inspect.stack()[0][3], exception_message))
            tkMessageBox.showerror("Error", ("Error querying Jamf. [%s]" % exception_message))
            sys.exit()

        tmp_policies = []
        policy_count = len(response_json['policies'])
        self.logger.info("%s: %i policies" % (inspect.stack()[0][3], policy_count))

        policy_id_list = []
        for item in response_json['policies']:
            policy_id_list.append(str(item['id']))

        pool = multiprocess.Pool()

        start_time = time.time()

        tmp_policies = pool.map(fetch_parse_policy, policy_id_list)

        elapsed_time = time.time() - start_time
        self.logger.info("%s: Elapsed time spent fetching and parsing policies: %r" % (inspect.stack()[0][3], elapsed_time))


        #
        # postponed processing from mapped function
        # hoping for additional performance increases
        final_policies = []
        for item in tmp_policies:
            tmp_name = item['policy']['general']['name']
            tmp_id = item['policy']['general']['id']
            tmp_allcomputers = item['policy']['scope']['all_computers']

            tmp_scopecomputergroups = []
            for subpolicy in item['policy']['scope']['computer_groups']:
                tmp_scopecomputergroups.append(subpolicy['name'])

            tmp_scopecomputers = []
            for subpolicy in item['policy']['scope']['computers']:
                tmp_scopecomputers.append(subpolicy['id'])

            final_policies.append([tmp_name, tmp_id, tmp_allcomputers, tmp_scopecomputers, tmp_scopecomputergroups])


        self.logger.info("%s: complete" % inspect.stack()[0][3])
        return final_policies

    def query_jamf_me(self):
        """
        Query jamf about this particular machine
        """

        #
        # this method finds the UUID for the local machine
        # query's jamf and parses the ID from the record
        # and then calls the main query method
        # it's wasteful the first time it's called.
        self.logger.info("%s: activated" % inspect.stack()[0][3])
        if not self.local_jamf_id:

            if platform.system() == 'Darwin':
                local_uuid_raw = subprocess.check_output(["system_profiler", "SPHardwareDataType"])
                local_uuid = re.findall(r'Hardware UUID: (.*)', local_uuid_raw)[0]
            elif platform.system() == 'Windows':
                local_uuid_raw = subprocess.check_output("wmic CsProduct Get UUID")
                local_uuid_raw = local_uuid_raw.split("\r\r\n")[1]
                local_uuid = local_uuid_raw.split(" ")[0]
            else:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("Missing native UUID discovery.")
                return

            #
            # communicate with Jamf server
            try:
                url = self.jamf_hostname + '/JSSResource/computers/udid/' + local_uuid
                request = urllib2.Request(url)
                request.add_header('Accept', 'application/json')
                request.add_header('Authorization', 'Basic ' + base64.b64encode(self.jamf_username + ':' + self.jamf_password))

                response = urllib2.urlopen(request)
                response_json = json.loads(response.read())

                #
                # a non-200 response is bad, report and return
                if response.code != 200:
                    self.logger.error("%s: error from jss" % inspect.stack()[0][3])
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("%i returned." % response.code)
                    return

                self.local_jamf_id = response_json['computer']['general']['id']
                self.id_string.set(self.local_jamf_id)

            #
            # handle various communication errors
            except urllib2.HTTPError, error:
                if error.code == 400:
                    self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Request error."))
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s" % (error.code, "Request error."))
                elif error.code == 401:
                    self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Authorization error."))
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s" % (error.code, "Authorization error."))
                elif error.code == 403:
                    self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Permissions error."))
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s" % (error.code, "Permissions error."))
                elif error.code == 404:
                    self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Resource not found."))
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s" % (error.code, "Resource not found."))
                elif error.code == 409:
                    contents = error.read()
                    error_message = re.findall(r"Error: (.*)<", contents)
                    print("HTTP code %i: %s %s %s" % (error.code, "Resource conflict.", error_message[0], self.id_string.get()))
                    self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Resource conflict. " + error_message[0]))
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s" % (error.code, "Resource conflict. " + error_message[0]))
                else:
                    self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Generic error."))
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s" % (error.code, "Generic error."))
                return
            except urllib2.URLError, error:
                self.logger.error("%s: Error contacting JSS." % (inspect.stack()[0][3]))
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("Error contacting JSS.")
                return
            except Exception as exception_message:
                self.logger.error("%s: Error querying Jamf. [%s]" % (inspect.stack()[0][3], exception_message))
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("Error querying Jamf. [%s]" % exception_message)
                return

        else:
            self.logger.info("%s: local jamf id %r" % (inspect.stack()[0][3], self.local_jamf_id))
            self.id_string.set(self.local_jamf_id)

        self.query_jamf_id()

    def query_jamf_id(self):
        """
        Query jamf about other machine
        """

        #
        # requests full record from Jamf for a specific computer
        #  call display method and pass record
        self.logger.info("%s: activated" % inspect.stack()[0][3])
        self.reset_display()

        if not self.id_string.get():
            self.logger.error("%s: No JAMF ID set" % inspect.stack()[0][3])
            self.status_label.configure(style='Warning.TLabel')
            self.status_string.set("No JAMF ID set.")
            return
        else:
            self.logger.info("%s: Querying Jamf ID %s" % (inspect.stack()[0][3], self.id_string.get()))
            self.status_label.configure(style='Normal.TLabel')
            self.status_string.set("Querying Jamf ID %s." % self.id_string.get())

        #
        # communicate with Jamf server
        try:
            url = self.jamf_hostname + '/JSSResource/computers/id/' + self.id_string.get()

            request = urllib2.Request(url)
            request.add_header('Accept', 'application/json')
            request.add_header('Authorization', 'Basic ' + base64.b64encode(self.jamf_username + ':' + self.jamf_password))

            response = urllib2.urlopen(request)
            response_json = json.loads(response.read())

            #
            # a non-200 response is bad, report and return
            if response.code != 200:
                self.logger.error("%s: error from jss" % inspect.stack()[0][3])
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("%i returned." % response.code)
                return

        #
        # handle various communication errors
        except urllib2.HTTPError, error:
            if error.code == 400:
                self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Request error."))
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("HTTP code %i: %s" % (error.code, "Request error."))
            elif error.code == 401:
                self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Authorization error."))
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("HTTP code %i: %s" % (error.code, "Authorization error."))
            elif error.code == 403:
                self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Permissions error."))
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("HTTP code %i: %s" % (error.code, "Permissions error."))
            elif error.code == 404:
                self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Resource not found."))
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("HTTP code %i: %s" % (error.code, "Resource not found."))
            elif error.code == 409:
                contents = error.read()
                error_message = re.findall(r"Error: (.*)<", contents)
                print("HTTP code %i: %s %s %s" % (error.code, "Resource conflict.", error_message[0], self.id_string.get()))
                self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Resource conflict. " + error_message[0]))
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("HTTP code %i: %s" % (error.code, "Resource conflict. " + error_message[0]))
            else:
                self.logger.error("%s: HTTP code %i: %s" % (inspect.stack()[0][3], error.code, "Generic error."))
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("HTTP code %i: %s" % (error.code, "Generic error."))
            return
        except urllib2.URLError, error:
            self.logger.error("%s: Error contacting JSS." % (inspect.stack()[0][3]))
            self.status_label.configure(style='Warning.TLabel')
            self.status_string.set("Error contacting JSS.")
            return
        except Exception as exception_message:
            self.logger.error("%s: Error querying Jamf. [%s]" % (inspect.stack()[0][3], exception_message))
            self.status_label.configure(style='Warning.TLabel')
            self.status_string.set("Error querying Jamf. [%s]" % exception_message)
            return

        self.logger.info("%s: Queried Jamf ID %s" % (inspect.stack()[0][3], self.id_string.get()))
        self.display_info(response_json)

    def display_info(self, response_json):
        """
        format and display data in fields
        """

        #
        # performs the actual presentaion of data to the UI
        self.logger.info("%s: activated" % inspect.stack()[0][3])
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.utf8')
        except:
            pass

        #
        # clear large display columns
        self.ea_field.delete('0.0', END)
        self.printer_field.delete('0.0', END)
        self.group_field.delete('0.0', END)
        self.package_field.delete('0.0', END)
        self.jamf_profiles_field.delete('0.0', END)
        self.jamf_policies_field.delete('0.0', END)

        #
        # set StringVars
        self.computer_name_string.set(response_json['computer']['general']['name'])
        self.id_string.set(response_json['computer']['general']['id'])
        self.fullname_string.set(response_json['computer']['location']['real_name'])

        if response_json['computer']['general']['last_contact_time']:
            self.checkin_display.config(font=('', 12, 'bold'))
            self.checkin_string.set(response_json['computer']['general']['last_contact_time'])
        else:
            self.checkin_display.config(font=('', 12, 'normal italic'))
            self.checkin_string.set('No value')

        if response_json['computer']['general']['report_date']:
            self.inventory_display.config(font=('', 12, 'bold'))
            self.inventory_string.set(response_json['computer']['general']['report_date'])
        else:
            self.inventory_display.config(font=('', 12, 'normal italic'))
            self.inventory_string.set('No value')



        #
        # parse and display printers
        raw_printers = response_json['computer']['hardware']['mapped_printers']
        processed_printers = []
        for item in raw_printers:
            processed_printers.append(item['name'])

        printer_display = ""
        for index, item in enumerate(processed_printers):
            if index == len(processed_printers):
                printer_display += item
            else:
                printer_display += item + "\n"

        self.printer_field.insert('0.0', printer_display)
        self.printer_field.delete(END+'-2c', END)

        #
        # parse and display computer groups
        raw_groups = response_json['computer']['groups_accounts']['computer_group_memberships']
        fmt_groups = []
        for item in raw_groups:
            fmt_groups.append([item.lower(), item])
        group_display = ""
        for index, item in enumerate(sorted(fmt_groups)):
            if index == len(raw_groups):
                group_display += item[1]
            else:
                group_display += item[1] + "\n"
        self.group_field.insert('0.0', group_display)
        self.group_field.delete(END+'-2c', END)

        #
        # parse and display EA's
        #
        # initial pass
        #  retain lower case name (to sort), name and value
        #
        # display pass
        #  handle empty values as "No value"
        raw_eas = response_json['computer']['extension_attributes']
        fmt_eas = []
        for item in raw_eas:
            fmt_eas.append([item['name'].lower(), item['name'], item['value']])

        for item in sorted(fmt_eas, reverse=True):
            self.ea_field.tag_configure("BOLD", font='monoco 12 bold')
            self.ea_field.tag_configure("NORM", font='monoco 12 normal')
            self.ea_field.tag_configure("ITAL", font='monoco 12 italic')

            if "\n" in item[2]:
                self.ea_field.insert('1.0', ":" + str(item[2]), ('NORM'))
            elif not item[2]:
                self.ea_field.insert('1.0', "No value\n", ('ITAL'))
                self.ea_field.insert('1.0', ":", ('NORM'))
            else:
                self.ea_field.insert('1.0', ":" + str(item[2]) + "\n", ('NORM'))

            self.ea_field.insert('1.0', item[1], ('BOLD'))
        self.ea_field.delete(END+'-2c', END)


        #
        # parse and display profiles
        # configuration_profiles section only includes ID's, no useable names
        # with list of ID's
        #  consult previously generated dictionary for names
        raw_profiles = response_json['computer']['configuration_profiles']
        for item in sorted(raw_profiles, reverse=True):
            try:
                self.jamf_profiles_field.insert('1.0', self.jamf_profiles[item["id"]] + "\n")
            except:
                pass
        self.jamf_profiles_field.delete(END+'-2c', END)

        #
        # parse and display installed software
        raw_packages = response_json['computer']['software']
        self.package_field.tag_configure("BOLD", font='monoco 12 bold')
        self.package_field.tag_configure("NORM", font='monoco 12 normal')

        for item in sorted(raw_packages['installed_by_installer_swu'], cmp=locale.strcoll, reverse=True):
            self.package_field.insert('1.0', ':' + item + '\n', ('NORM'))
            self.package_field.insert('1.0', 'Installer', ('BOLD'))

        for item in sorted(raw_packages['installed_by_casper'], cmp=locale.strcoll, reverse=True):
            self.package_field.insert('1.0', ':' + item + '\n', ('NORM'))
            self.package_field.insert('1.0', 'Casper', ('BOLD'))
        self.package_field.delete(END+'-2c', END)

        #
        # parse and display policies
        #
        # parsing pass
        #  parse previously generate list of policies
        #   if the policy applies to all computers add it's name to new list
        #   if the current jamf ID appears in the list of specific computer the policy applies to, add the name to the list
        #   if one of the groups the computer belongs to appears in the list of groups the policy applies to, add it to the list
        #
        # sort and display the list.
        valid_policies = []
        for item in self.jamf_policies:
            for subitem in raw_groups:
                if subitem in item[4]:
                    if item[0] not in valid_policies:
                        valid_policies.append(item[0])

        fmt_policies = []
        for item in valid_policies:
            fmt_policies.append([item.lower(), item])


        for item in sorted(fmt_policies, reverse=True):
            self.jamf_policies_field.insert('1.0', item[1] + "\n")
        self.jamf_policies_field.delete(END+'-2c', END)



    def reset_display(self):
        """
        erase field contents
        """
        self.logger.info("%s: activated" % inspect.stack()[0][3])
        self.computer_name_string.set("")
        self.fullname_string.set("")
        self.checkin_string.set("")
        self.inventory_string.set("")

        self.ea_field.delete('0.0', END)
        self.printer_field.delete('0.0', END)
        self.group_field.delete('0.0', END)
        self.package_field.delete('0.0', END)
        self.jamf_profiles_field.delete('0.0', END)
        self.jamf_policies_field.delete('0.0', END)

def login(logger):
    """
    if the user has proper privleges, consider them an authorized user and proceed
    """
    def try_login():
        """
        jamf api call for login test
        """

        def call_jss(logger, api_call):
            """
            consolidate API calls to single function
            pass in logger and api call.
            """
            logger.info("%s: activated" % inspect.stack()[0][3])

            try:
                url = jamf_hostname.get() + '/JSSResource/' + api_call

                logger.info("%s called with %s" % (inspect.stack()[0][3], api_call))

                request = urllib2.Request(url)
                request.add_header('Accept', 'application/json')
                request.add_header('Authorization', 'Basic ' + base64.b64encode(jamf_username.get() + ':' + jamf_password.get()))

                response = urllib2.urlopen(request)

                logger.info("Code returned: %s %s" % (response.code, api_call))

                if response.code != 200:
                    logger.error("login: Invalid response from Jamf (" + api_call + ")")
                    tkMessageBox.showerror("Jamf login", "Invalid response from Jamf")
                    root.destroy() # clean up after yourself!
                    sys.exit()

                response_json = json.loads(response.read())

                return response_json

            #
            # handle various communication errors
            except urllib2.HTTPError, error:

                logger.error("Code returned: %s %s" % (response.code, api_call))

                if error.code == 401:
                    logger.error("%s: Invalid username or password. (%r) (%s)" % (inspect.stack()[0][3], jamf_username.get(), api_call))
                    tkMessageBox.showerror("Jamf login", "Invalid username or password.")
                else:
                    logger.error("%s: Error communicating with JSS. %s %s" % (inspect.stack()[0][3], jamf_hostname.get(), api_call))
                    tkMessageBox.showerror("Jamf login", "HTTP error from:\n%s" % jamf_hostname.get())
            except urllib2.URLError:
                logger.error("%s: Error contacting JSS: %s %s" % (inspect.stack()[0][3], jamf_hostname.get(), api_call))
                tkMessageBox.showerror("Jamf login", "Unable to contact:\n%s" % jamf_hostname.get())
            except Exception as exception_message:
                logger.error("%s: Generic error. (%r) %s" % (inspect.stack()[0][3], exception_message, api_call))
                tkMessageBox.showerror("Jamf login", "Generic error from %s." % jamf_hostname.get())

            #
            # handle bad condition exits here...
            logger.error("%s: Exiting, Error calling %s" % (inspect.stack()[0][3], api_call))
            sys.exit()

        logger.info("%s: activated" % inspect.stack()[0][3])

        try:
            # Attempt to verify LDAP users.
            #   1. Pull JSS acounts for users and groups
            #   2. Pull LDAP servers
            #   3. Build list of valid groups, those with appropriate rights
            #   4. Check each LDAP server for valid groups the user is a member of, login if found
            #   5. Fall back to jss user login, check account for appropriate rights

            jss_accounts = call_jss(logger, 'accounts')

            raw_ldap = call_jss(logger, 'ldapservers')
            ldap_servers = raw_ldap['ldap_servers']
            logger.info("JSS LDAP servers: %r" % ldap_servers)

            #
            # store list of user and group privileges
            user_list = jss_accounts['accounts']['users']
            group_list = jss_accounts['accounts']['groups']

            #
            # find groups on jss that have required_privileges
            valid_groups = []
            for item in group_list:
                raw_privs = call_jss(logger, 'accounts/groupid/' + str(item['id']))
                this_group_privs = raw_privs['group']['privileges']['jss_objects']

                count_privileges = len(required_privileges)

                for this_privilege in required_privileges:
                    if this_privilege in this_group_privs:
                        count_privileges -= 1

                if count_privileges == 0:
                    logger.info("%s is valid." % item['name'])
                    valid_groups.append([item['id'], item['name']])

            #
            # find servers with valid groups the user is a member of
            valid_servers = []
            for server in ldap_servers:
                for group in valid_groups:
                    raw_group_membership = call_jss(logger, 'ldapservers/id/' + str(server['id']) + '/group/' + urllib.quote(str(group[1])) + '/user/' + jamf_username.get())

                    if raw_group_membership['ldap_users']:
                        valid_servers.append(server['name'])

            #
            # if we found a valid server, proceed to app
            if valid_servers:
                logger.info('valid server found, login successful.')
                root.destroy() # clean up after yourself!
                return

            #
            # check users account privileges for required rights
            else:
                raw_privileges = call_jss(logger, 'accounts/username/' + jamf_username.get())
                user_privileges = raw_privileges['account']['privileges']['jss_objects']

                #
                # stop number of require privileges
                count_privileges = len(required_privileges)

                #
                # for every required privilege
                #  check if it's in user privileges
                #   decrement if yes
                # maintain list of missing require privileges
                missing_privileges = []

                for item in required_privileges:
                    if item in user_privileges:
                        count_privileges -= 1
                    else:
                        missing_privileges.append(item)

                #
                # if all require privileges accounted for, proceed
                # else alert and fail
                if count_privileges == 0:
                    logger.info("login: valid login. (%r)" % jamf_username.get())
                    root.destroy() # clean up after yourself!
                    return
                else:
                    logger.error("login: User %r lacks appropriate privileges: %r" % (jamf_username.get(), missing_privileges))
                    tkMessageBox.showerror("Jamf login", "User lacks appropriate privileges.\n%r" % missing_privileges)

        #
        # handle various communication errors
        except urllib2.HTTPError, error:

            logger.info("Code returned: %s" % error.code)

            if error.code == 401:
                logger.error("%s: Invalid username or password. (%r)" % (inspect.stack()[0][3], jamf_username.get()))
                tkMessageBox.showerror("Jamf login", "Invalid username or password.")
            else:
                logger.error("%s: Error communicating with JSS. %s" % (inspect.stack()[0][3], jamf_hostname.get()))
                tkMessageBox.showerror("Jamf login", "HTTP error from:\n%s" % jamf_hostname.get())
        except urllib2.URLError:
            logger.error("%s: Error contacting JSS: %s" % (inspect.stack()[0][3], jamf_hostname.get()))
            tkMessageBox.showerror("Jamf login", "Unable to contact:\n%s" % jamf_hostname.get())
        except Exception as exception_message:
            logger.error("%s: Generic error. (%r)" % (inspect.stack()[0][3], exception_message))
            tkMessageBox.showerror("Jamf login", "Generic error from %s." % jamf_hostname.get())

        sys.exit()

    #
    # This is really important. This list contains the required rights for the fields we need to access.
    required_privileges = ['Read Accounts', 'Read Buildings', 'Read Computers', 'Update Computers', 'Read Departments', 'Read User', 'Update User']

    root = Tk()
    jamf_username = StringVar()
    jamf_password = StringVar()
    jamf_hostname = StringVar()

    # customizable for specific deployment
    jamf_hostname.set("https://your.jamf.server:8443")

    #
    # build and display login screen
    root.title("Jamf Login")
    mainframe = ttk.Frame(root)
    mainframe.grid(column=0, row=0, sticky=NSEW)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.geometry('+0+0')

    ttk.Label(mainframe, text="Jamf Server:").grid(column=1, row=10, sticky=E)
    uname_entry = ttk.Entry(mainframe, width=30, textvariable=jamf_hostname)
    uname_entry.grid(column=2, row=10, sticky=EW)

    ttk.Label(mainframe, text="Username:").grid(column=1, row=20, sticky=E)
    uname_entry = ttk.Entry(mainframe, width=30, textvariable=jamf_username)
    uname_entry.grid(column=2, row=20, sticky=EW)

    ttk.Label(mainframe, text="Password:").grid(column=1, row=30, sticky=E)
    pword_entry = ttk.Entry(mainframe, width=30, textvariable=jamf_password, show="*")
    pword_entry.grid(column=2, row=30, sticky=EW)

    ttk.Button(mainframe, text="Quit", command=sys.exit).grid(column=2, row=70, padx=3)
    ttk.Button(mainframe, text="Login", default='active', command=try_login).grid(column=2, row=70, padx=3, sticky=E)

    if platform.system() == 'Darwin':
        tmpl = 'tell application "System Events" to set frontmost of every process whose unix id is {} to true'
        script = tmpl.format(os.getpid())
        output = subprocess.check_call(['/usr/bin/osascript', '-e', script])

    root.bind('<Return>', lambda event: try_login())

    uname_entry.focus()
    root.mainloop()

    return (jamf_hostname.get(), jamf_username.get(), jamf_password.get())

def main():

    logger = loggers.file_logger(name='cargoship')
    logger.info("Running Cargo Ship")
    logger.info("Level: Method/function: Message")


    jamf_hostname, jamf_username, jamf_password = login(logger)
    if not jamf_username:
        sys.exit(0)

    main_window = Tk()
    my_app = Summarize(main_window, logger, jamf_hostname, jamf_username, jamf_password)
    main_window.mainloop()

if __name__ == '__main__':
    main()
