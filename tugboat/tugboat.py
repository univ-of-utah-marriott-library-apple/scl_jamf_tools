#!/usr/bin/python
# -*- coding: utf-8 -*-

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

# tugboat.py #################################################
#
# A Python Tk application to edit Jamf computer records.
#
#
#    1.5.0  2017.02.15      Initial public release. tjm
#
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
import tkSimpleDialog
import tkMessageBox
import ttk
import os
import re
import subprocess
import urllib
import urllib2
import xml.etree.cElementTree as ET
from xml.dom.minidom import parseString
import socket
import platform
import base64
import json
import webbrowser
import inspect
if platform.system() == 'Darwin':
    import pexpect

class Computer(object):
    """
    Store GUI and data structures describing jamf computer records
    """
    def __init__(self, root, jamf_hostname, jamf_username, jamf_password):
        """
        initialize variables and data structures
        """
        self.root = root
        self.jamf_hostname = jamf_hostname
        self.jamf_password = jamf_password
        self.jamf_username = jamf_username
        self.local_jamf_id = None

        self.hostname = ""
        self.divisions = []
        self.buildings = []
        self.platform = None
        self.will_offboard = False
        self.jamf_management = ""

        self.username_string = StringVar()
        self.fullname_string = StringVar()
        self.department_string = StringVar()
        self.position_string = StringVar()
        self.email_string = StringVar()
        self.phone_string = StringVar()
        self.building_string = StringVar()
        self.room_string = StringVar()
        self.assettag_string = StringVar()
        self.barcode_string = StringVar()
        self.status_string = StringVar()
        self.id_string = StringVar()
        self.search_string = StringVar()
        self.computer_name_string = StringVar()

        self.username_string.set("")
        self.fullname_string.set("")
        self.position_string.set("")
        self.email_string.set("")
        self.phone_string.set("")
        self.room_string.set("")
        self.assettag_string.set("")
        self.status_string.set("Ready.")
        self.computer_name_string.set("")

        self.status_warning = ttk.Style()
        self.status_warning.configure('Warning.TLabel', foreground='red')

        self.status_normal = ttk.Style()
        self.status_normal.configure('Normal.TLabel', foreground='black')

        self.highlight_button = ttk.Style()
        self.highlight_button.configure('Highlight.TButton', foreground='green')

        self.dim_text = ttk.Style()
        self.dim_text.configure('Dim.TLabel', foreground='gray50')

        self.black_text = ttk.Style()
        self.black_text.configure('Black.TLabel', foreground='black')

        self.status_subtle = ttk.Style()
        self.status_subtle.configure('Subtle.TLabel', foreground='maroon')

        self.hostname = (socket.gethostname()).split(".")[0]
        self.divisions = self.populate_menu('departments')
        self.buildings = self.populate_menu('buildings')

        self.build_ui()


    def build_ui(self):
        """
        describe UI, fields, buttons, etc
        """

        #
        # This is an encoded gif of the title image
        self.logo_image = '''\
        R0lGODlhWAJRAPcAAAEAAAQECgYJCgwMDQgHCBMODQ4QDhERDg0OEQUHFREOEw4REgoTGhITFBQV
        GhUZGxsbHBkXGCcXFR0iHiwkHRwdIxYZJhAVLyIcIxwjJRcpNiUlJSQlKyUqLCwrLCknJzQqKCgr
        NjMtNSwyOTMzNTM0Ozs7PDk3ODYyK1ExFWo3Ekc3KUQ7OlY0LF8rKD9DPHdIGnBJGUpEO1ZJOVdJ
        LHZLJXBRMHdhNxknQicqRS01RTM1Qjs8Qzg6Ry86VRkvWEQ9REk+TGYzQD1DSDlFVTlTY0NCQ0RD
        S0xLTEtHR1NLSVhSS0hJVlJNU1ROWExTWFVSVFtUVFlZWVdVWkhTSGhXSGRaWXFQS2pkXXdoVEtV
        Z1dZZlFUa2VdZFVpbmxra2dlZ3Rpamdpdnx9fXd2d3FzcFJjWaE0MMQSMMcfO8chPMgjPtQyOPow
        OolXG4xRF5llHLBtGYhYJ5ZbJ4lVM5hmKYlmN5doN5NsMKhrJqd0KrZ4Kah4N7Z7NqxqN6VZKMh4
        L+BXLc46U8kqRPwxRoZnRpByT613TIt3bq51bpNYTtFGXtBFVch0TtRTaNJMY9lnevNvVXCNe1aP
        bj+EbriFObmEKsiIKNmZK8WIN8qUOdiYNtGPLOSZMNujOdymMOmmK/WqKPq1KueoN+2zOfW1NPS0
        O/u6PPm5N/OsN+CYG/7FOf/MMbKLTI+Idq+PbrCrcJSRYMeWRs6QT9mlRc+nVeeqRuyzRve5RO6y
        UcySbNOrbuyza+iTUv3FRfvOUPXKbv/rZHJ3hVZxkYF+hdtugN13iHiJh3ajmjOL5kiS342NjYeE
        hpycnJiVl5CQjrKUjJGpl7ColJadpqqqqqWnqLi4uLa2tbGwrpqjp9CYjuKKmeGFlOyXkc2wkPiq
        k8q3rPKxsOaap7XKne3Pj9TKtvLMruvZobu6w9m9xLjGyMXFxcfKydHR0d3d3dbV19LQz/DCyvnF
        w+zVzObk2vjt0Nrd5+np6eXm5fj16/T09Pzz9f////f3+uzu8d3h5yH5BAAAAAAALAAAAABYAlEA
        AAj+APkJHEiwoMGDCBMO1PdKRQoVgGzlojWLjgULCaj1E/KnHr93AufVoycNm8B+/PzhU8iypcuX
        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
        RXatYVEc4fS1X6tJYfhlV+YIAHbNrRlMDAJOjqk9GiNghmrgPyVGKH1QU5Uxgu3F4z9OGCb+U84K
        B3GIh0WIB24IBz/5h5hkmkK64W5jV6vJrdq9Xem01FJMY2sTJDiuGAImYAF4SSXoAlcogzGgQHcQ
        YkBGqHtYSiMmE1aW5dUR5LfkLH4Ih3iYB0EoZCr2E2eIrg0ARfmNuquJQdqtxWMWpEqu5GUeYWVr
        Zul04+RIjgJeANHUAiwQhmkYAzD44WuwhnZY5Vl+tdJohgf+AkQIDXJmZ5nxUzVQgzSQ53mm53q2
        53v+ToMYu2V+iAdjiId42AZjmIeEAQNlewAYZY7phObpnMFaTGOGliNPXuhqvgwCtgAk+AIywEp4
        cId8QOJ2BumQbud96AcP3IeTNmmSTmmVPumWbumU9sB82OC+EIdiiIdiWOSadQACQIEISNoz5lkj
        C1o5ouZqJlACnj1cxdwEiIANAAGG+AJmmAZwGGeRtuqrbmdBZZ2Z9hOKIQDuyduwbt9pRowCdtEG
        mAAeaIItKBhnqAZrYAd4eId1wAZsWAd88Id8wOq95uu+Zs1GmWhlkz3nkIA6I6tnwIZrQId2oIfo
        9evHhuzINlBsYIZniAxnaIZmqIZyaAd38FjJBu0V0BZt1tTq0Tbt00bt1Fbt1WbtBQ4IACH/C1hN
        UCBEYXRhWE1QPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtj
        OWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUg
        WE1QIENvcmUgNS42LWMxMzggNzkuMTU5ODI0LCAyMDE2LzA5LzE0LTAxOjA5OjAxICAgICAgICAi
        PgogPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1z
        eW50YXgtbnMjIj4KICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIi8+CiA8L3JkZjpSREY+
        CjwveDp4bXBtZXRhPgo8P3hwYWNrZXQgZW5kPSJyIj8+Af/+/fz7+vn49/b19PPy8fDv7u3s6+rp
        6Ofm5eTj4uHg397d3Nva2djX1tXU09LR0M/OzczLysnIx8bFxMPCwcC/vr28u7q5uLe2tbSzsrGw
        r66trKuqqainpqWko6KhoJ+enZybmpmYl5aVlJOSkZCPjo2Mi4qJiIeGhYSDgoGAf359fHt6eXh3
        dnV0c3JxcG9ubWxramloZ2ZlZGNiYWBfXl1cW1pZWFdWVVRTUlFQT05NTEtKSUhHRkVEQ0JBQD8+
        PTw7Ojk4NzY1NDMyMTAvLi0sKyopKCcmJSQjIiEgHx4dHBsaGRgXFhUUExIREA8ODQwLCgkIBwYF
        BAMCAQAAOw==
        '''

        self.root.title("Tugboat")

        self.mainframe = ttk.Frame(self.root)

        self.mainframe.grid(column=0, row=0, sticky=NSEW)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.geometry('+0+0')

        #
        # position and display logo image
        self.logo_label = ttk.Label(self.mainframe)
        self.logo_photoimage = PhotoImage(data=self.logo_image)
        self.logo_label['image'] = self.logo_photoimage
        self.logo_label.grid(column=1, row=0, columnspan=4)

        ttk.Separator(self.mainframe, orient=HORIZONTAL).grid(row=30, columnspan=35, sticky=EW)

        #
        # these are the elements of the Navigation section of the UI
        ttk.Label(self.mainframe, text="Discovery Method:").grid(column=1, row=100, sticky=E)
        ttk.Button(self.mainframe, text="This Device", style='Highlight.TButton', command=self.query_jamf_me).grid(column=2, row=100, sticky=W)

        ttk.Button(self.mainframe, text="Search Jamf", command=self.search_string_jamf).grid(column=2, row=100, sticky=E)
        self.search_entry = ttk.Entry(self.mainframe, width=25, textvariable=self.search_string)
        self.search_entry.grid(column=3, row=100, columnspan=2, sticky=W)

        ttk.Label(self.mainframe, text="Jamf ID:                ").grid(column=4, row=100, sticky=E)
        self.id_entry = ttk.Entry(self.mainframe, width=6, textvariable=self.id_string)
        self.id_entry.grid(column=4, row=100, sticky=E)

        if platform.system() == 'Darwin':
            ttk.Label(self.mainframe, text="User Selection:").grid(column=1, row=150, sticky=E)
            ttk.Button(self.mainframe, text="Top User (Admin Req.)", command=self.usage).grid(column=2, row=150, sticky=W)

        #
        # If you are considering adding UI elements to communicate with user database, place them here
        #

        ttk.Separator(self.mainframe, orient=HORIZONTAL).grid(row=300, columnspan=5, sticky=EW)

        #
        # these are the elements of the General section of the UI
        ttk.Label(self.mainframe, text="Computer Name:").grid(column=1, row=320, sticky=E)
        self.computername_entry = ttk.Entry(self.mainframe, textvariable=self.computer_name_string)
        self.computername_entry.grid(column=2, row=320, sticky=EW)

        ttk.Label(self.mainframe, text="Asset Tag:").grid(column=1, row=340, sticky=E)
        self.assettag_entry = ttk.Entry(self.mainframe, textvariable=self.assettag_string)
        self.assettag_entry.grid(column=2, row=340, sticky=EW)

        ttk.Label(self.mainframe, text="Bar Code:").grid(column=3, row=340, sticky=E)
        self.barcode_entry = ttk.Entry(self.mainframe, textvariable=self.barcode_string)
        self.barcode_entry.grid(column=4, row=340, sticky=EW)

        ttk.Separator(self.mainframe, orient=HORIZONTAL).grid(row=500, columnspan=5, sticky=EW)

        #
        # these are the elements of the User and Location section of the UI
        ttk.Label(self.mainframe, text="Username:").grid(column=1, row=550, sticky=E)
        self.endusername_entry = ttk.Entry(self.mainframe, textvariable=self.username_string)
        self.endusername_entry.grid(column=2, row=550, sticky=EW)

        ttk.Label(self.mainframe, text="Full Name:").grid(column=3, row=550, sticky=E)
        self.fullname_entry = ttk.Entry(self.mainframe, width=31, textvariable=self.fullname_string)
        self.fullname_entry.grid(column=4, row=550, sticky=EW)

        ttk.Label(self.mainframe, text="Department:").grid(column=1, row=600, sticky=E)
        self.division_combobox = ttk.Combobox(self.mainframe, width=31, state="readonly", textvariable=self.department_string)
        self.division_combobox['values'] = self.divisions
        self.division_combobox.current(0)
        self.division_combobox.grid(column=2, row=600, sticky=EW)

        ttk.Label(self.mainframe, text="Position:").grid(column=3, row=600, sticky=E)
        self.position_entry = ttk.Entry(self.mainframe, width=31, textvariable=self.position_string)
        self.position_entry.grid(column=4, row=600, sticky=EW)

        ttk.Label(self.mainframe, text="Email:").grid(column=1, row=650, sticky=E)
        self.email_entry = ttk.Entry(self.mainframe, width=31, textvariable=self.email_string)
        self.email_entry.grid(column=2, row=650, sticky=EW)

        ttk.Label(self.mainframe, text="Phone:").grid(column=3, row=650, sticky=E)
        self.phone_entry = ttk.Entry(self.mainframe, width=31, textvariable=self.phone_string)
        self.phone_entry.grid(column=4, row=650, sticky=EW)

        ttk.Label(self.mainframe, text="Building:").grid(column=1, row=700, sticky=E)
        self.building_combobox = ttk.Combobox(self.mainframe, width=31, state="readonly", textvariable=self.building_string)
        self.building_combobox['values'] = self.buildings
        self.building_combobox.current(0)
        self.building_combobox.grid(column=2, row=700, sticky=EW)

        ttk.Label(self.mainframe, text="Room:").grid(column=3, row=700, sticky=E)
        self.room_entry = ttk.Entry(self.mainframe, width=31, textvariable=self.room_string)
        self.room_entry.grid(column=4, row=700, sticky=EW)

        ttk.Separator(self.mainframe, orient=HORIZONTAL).grid(row=800, columnspan=5, sticky=EW)

        #
        # these are the elements of the Administration section of the UI
        ttk.Label(self.mainframe, text="Open in Jamf:").grid(column=1, row=850, sticky=E)
        ttk.Button(self.mainframe, text="Device", command=self.open_id_web).grid(column=2, row=850, sticky=W)
        ttk.Button(self.mainframe, text="User", command=self.open_user_web).grid(column=2, row=850)
        ttk.Button(self.mainframe, text="Search", command=self.open_search_web).grid(column=2, row=850, sticky=E)

        self.jamf_management_label = ttk.Label(self.mainframe, text="Managed by Jamf:                     ")
        self.jamf_management_label.grid(column=4, row=850, sticky=E)
        self.jamf_management_btn = ttk.Button(self.mainframe, text="True", width=6, command=lambda: self.jamf_management_btn.config(text="False") if self.jamf_management_btn.config('text')[-1] == 'True' else self.jamf_management_btn.config(text="True"))
        self.jamf_management_btn.grid(column=4, row=850, sticky=E)

        ttk.Separator(self.mainframe, orient=HORIZONTAL).grid(row=1000, columnspan=5, sticky=EW)

        self.status_label = ttk.Label(self.mainframe, textvariable=self.status_string)
        self.status_label.grid(column=1, row=1100, sticky=W, columnspan=4)

        ttk.Button(self.mainframe, text="Reset", width=6, command=self.reset_data).grid(column=4, row=1100, sticky=W)
        ttk.Button(self.mainframe, text="Quit", width=6, command=self.root.destroy).grid(column=4, row=1100)

        self.submit_btn = ttk.Button(self.mainframe, text="Modify", width=7, command=self.submit)
        self.submit_btn.grid(column=4, row=1100, sticky=E)

        #
        # this loop adds a small amount of space around each UI element, changing the value will significantly change the final size of the window
        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=3, pady=3)

    def open_user_web(self):
        """
        Open currently displayed user record in jamf
        """

        #
        # in order to open the user in a browser you need the user's Jamf ID
        # in order to get the ID you need to open the user's record on Jamf
        if not self.username_string.get():
            self.status_label.configure(style='Warning.TLabel')
            self.status_string.set("No user available.")
            return

        url = self.jamf_hostname+ '/JSSResource/users/name/' + self.username_string.get()
        url = urllib.quote(url, ':/()')

        request = urllib2.Request(url)
        request.add_header('Accept', 'application/json')
        request.add_header('Authorization', 'Basic ' + base64.b64encode(self.jamf_username + ':' + self.jamf_password))

        response = urllib2.urlopen(request)
        response_json = json.loads(response.read())

        if response.code != 200:
            self.status_label.configure(style='Warning.TLabel')
            self.status_string.set("%i returned." % response.code)
            return

        jamf_user_id = response_json['user']['id']

        if jamf_user_id:
            url_formatted = self.jamf_hostname+ "/users.html?id=" + str(jamf_user_id) + "&o=r"
            webbrowser.open_new_tab(url_formatted)
            self.status_label.configure(style='Normal.TLabel')
            self.status_string.set("Opened URL for User.")

        else:
            self.status_label.configure(style='Warning.TLabel')
            self.status_string.set("No user available.")

    def open_id_web(self):
        """
        Open currently displayed computer record in jamf
        """
        if self.id_string.get():
            url_formatted = self.jamf_hostname+ "/computers.html?id=" + self.id_string.get() + "&o=r"
            webbrowser.open_new_tab(url_formatted)
            self.status_label.configure(style='Normal.TLabel')
            self.status_string.set("Opened URL for ID.")

        else:
            self.status_label.configure(style='Warning.TLabel')
            self.status_string.set("No ID available.")

    def open_search_web(self):
        """
        Open currently displayed search in jamf
        """
        if self.search_string.get():
            url_formatted = self.jamf_hostname+ "/computers.html?queryType=Computers&query=*" + self.search_string.get() + "*"
            webbrowser.open_new_tab(url_formatted)
            self.status_label.configure(style='Normal.TLabel')
            self.status_string.set("Opened URL for search.")

        else:
            self.status_label.configure(style='Warning.TLabel')
            self.status_string.set("No search string entered.")

    def reset_user(self):
        """
        Reset user data structures to blank
        """

        self.username_string.set("")
        self.fullname_string.set("")
        self.department_string.set("")
        self.position_string.set("")
        self.email_string.set("")
        self.phone_string.set("")
        self.building_string.set("")
        self.room_string.set("")

    def reset_data(self):
        """
        reset all data structures to blank
        """

        if inspect.stack()[1][3] == "__call__":
            self.id_string.set("")
            self.search_string.set("")

        self.computer_name_string.set("")
        self.assettag_string.set("")
        self.barcode_string.set("")
        self.username_string.set("")
        self.fullname_string.set("")
        self.department_string.set("")
        self.position_string.set("")
        self.email_string.set("")
        self.phone_string.set("")
        self.building_string.set("")
        self.room_string.set("")

        self.status_label.configure(style='Normal.TLabel')
        self.status_string.set("Data reset.")

    def display_user(self):
        """
        Print current data structures, useful for debugging
        """
        print("Current user information")
        print("\tGeneral")
        print("\t\tComputer name : %s" % self.computer_name_string.get())
        print("\t\tAsset Tag     : %s" % self.assettag_string.get())
        print("\t\tBar code      : %s\n" % self.barcode_string.get())

        print("\tUser and Location")
        print("\t\tEnduser       : %s" % self.username_string.get())
        print("\t\tFullname      : %s" % self.fullname_string.get())
        print("\t\tDepartment    : %s" % self.department_string.get())
        print("\t\tPosition      : %s" % self.position_string.get())
        print("\t\tEmail         : %s" % self.email_string.get())
        print("\t\tPhone         : %s" % self.phone_string.get())
        print("\t\tBuilding      : %s" % self.building_string.get())
        print("\t\tRoom          : %s\n" % self.room_string.get())

        print("Other :")
        print("\tJamf ID : %s" % self.id_string.get())
        print("\tStatus  : %s\n" % self.status_string.get())

        return

    def check_submit(self):
        """
        precheck required fields for valid content
        """

        #
        # if you plan on adding additional fields, you'll likely want to add them to this
        # method to be sure they contain valid values before submitting.
        bad_fields = []

#         if not self.assettag_string.get():
#             bad_fields.append("Asset Tag")

        if not self.id_string.get():
            bad_fields.append("Jamf ID")

        if not self.username_string.get():
            bad_fields.append("Username")

        if not self.fullname_string.get():
            bad_fields.append("Full Name")

        if not bad_fields:
            # We're good.
            return True
        else:
            if len(bad_fields) >= 5:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("Many empty fields!")
                return False
            else:
                bad_fields = ", ".join(bad_fields)
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("Empty fields: %s" % bad_fields)
                return False

    def submit(self):
        """
        submit current data structures to jamf
        """

        if not self.check_submit():
            return

        try:
            self.status_label.configure(style='Normal.TLabel')
            self.status_string.set("Submitting...")

            jamf_url = self.jamf_hostname+ '/JSSResource/computers/id/' + self.id_string.get()

            #
            # These are the individual fields associated with UI elements
            # If you add additional fields to the UI, you will need to add corresponding
            # XML elements form them to be submitted back to the Jamf database.
            top = ET.Element('computer')

            general = ET.SubElement(top, 'general')

            computer_name_xml = ET.SubElement(general, 'name')
            computer_name_xml.text = self.computer_name_string.get()

            asset_tag_xml = ET.SubElement(general, 'asset_tag')
            asset_tag_xml.text = self.assettag_string.get()

            barcode_xml = ET.SubElement(general, 'barcode_1')
            barcode_xml.text = self.barcode_string.get()

            location = ET.SubElement(top, 'location')

            username_xml = ET.SubElement(location, 'username')
            username_xml.text = self.username_string.get()

            email_xml = ET.SubElement(location, 'email_address')
            email_xml.text = self.email_string.get()

            realname_xml = ET.SubElement(location, 'real_name')
            realname_xml.text = self.fullname_string.get()

            phone_xml = ET.SubElement(location, 'phone')
            phone_xml.text = self.phone_string.get()

            building_xml = ET.SubElement(location, 'building')
            building_xml.text = self.building_string.get()

            room_xml = ET.SubElement(location, 'room')
            room_xml.text = self.room_string.get()

            position_xml = ET.SubElement(location, 'position')
            position_xml.text = self.position_string.get()

            department_xml = ET.SubElement(location, 'department')
            department_xml.text = self.department_string.get()

            #
            # these are the fields that enable removing machines
            # from management quotas.
#             if self.jamf_management_btn.config('text')[-1] == 'True'
#                 remote_management = ET.SubElement(general, 'remote_management')
#                 managed_xml       = ET.SubElement(remote_management, 'managed')
#                 managed_xml.text  = 'true'
#             else
#                 remote_management = ET.SubElement(general, 'remote_management')
#                 managed_xml       = ET.SubElement(remote_management, 'managed')
#                 managed_xml.text  = 'false'


#             print(ET.tostring(top))

            #
            # comminicating with the Jamf database and putting the XML structure
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            request = urllib2.Request(jamf_url, data=ET.tostring(top))
            base64string = base64.b64encode('%s:%s' % (self.jamf_username, self.jamf_password))
            request.add_header("Authorization", "Basic %s" % base64string)
            request.add_header('Content-Type', 'text/xml')
            request.get_method = lambda: 'PUT'
            response = opener.open(request)

            self.status_label.configure(style='Normal.TLabel')
            self.status_string.set(str(response.code) + " Submitted.")
            return

        except urllib2.HTTPError, error:
            if error.code == 400:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("HTTP code %i: %s " % (error.code, "Request error."))
            elif error.code == 401:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("HTTP code %i: %s " % (error.code, "Authorization error."))
            elif error.code == 403:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("HTTP code %i: %s " % (error.code, "Permissions error."))
            elif error.code == 404:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("HTTP code %i: %s " % (error.code, "Resource not found."))
            elif error.code == 409:
                contents = error.read()
                error_message = re.findall(r"Error: (.*)<", contents)
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("HTTP code %i: %s " % (error.code, "Resource conflict. " + error_message[0]))
            else:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("HTTP code %i: %s " % (error.code, "Generic error."))

            return
        except urllib2.URLError, error:
            self.status_label.configure(style='Warning.TLabel')
            self.status_string.set("Error contacting Jamf.")
            return
        except Exception as exception_message:
            self.status_label.configure(style='Warning.TLabel')
            self.status_string.set("Error submitting to Jamf. [%s]" % exception_message)
            return

    def usage(self):
        """
        Calculate which valid user uses this computer the most
        """
        #
        # this method uses the pexpect module, if you have issues with the module you'll need to remove this method.
        try:
            #
            # aquire admin password
            password = tkSimpleDialog.askstring("Password", "Enter admin password:", show='*', parent=self.root)

            if not password:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("Canceled Top User.")
                return

            cmd_output = []
            try:
                #
                # utilizing the
                child = pexpect.spawn('bash', ['-c', '/usr/bin/sudo -k /usr/sbin/ac -p'])

                exit_condition = False
                while not exit_condition:
                    result = child.expect(['\n\nPass', 'Password:', 'sudo', pexpect.EOF, pexpect.TIMEOUT])

                    cmd_output.append(child.before)
                    cmd_output.append(child.after)
                    if result == 0:
                        child.sendline(password)
                    elif result == 1:
                        child.sendline(password)
                    elif result == 2:
                        self.status_label.configure(style='Warning.TLabel')
                        self.status_string.set("Incorrect admin password.")
                        return
                    elif result == 3:
                        exit_condition = True
                    elif result == 4:
                        exit_condition = True
                    else:
                        print("Unknown error. Exiting.")
                        exit_condition = True

            except Exception as exception_message:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("Error submitting to Jamf. [%s]" % exception_message)
                return

            #
            # begin parsing out useful content
            checked_output = []
            for index, content in enumerate(cmd_output):
                if isinstance(content, basestring):
                    if "System\r\nAdministrator." in content:
                        pass
                    elif not content:
                        pass
                    elif content == "Password:":
                        pass
                    else:
                        checked_output.append(content)

            #
            # begin parsing out users and time data from output
            users_raw = []
            for super_item in checked_output:
                sub_item = super_item.split("\r\n")
                for user in sub_item:
                    if user:
                        user = user.strip()
                        users_raw.append(user)

            users = [item for item in users_raw if item]

            grid = {}

            #
            # build dictionary of output
            for item in users:
                match = re.search(r'^(\w*)\s*(\d*.\d*)', item)
                grid[match.group(1)] = match.group(2)

            login_total = float(grid['total'])

            #
            # remove various admin/management accounts
            try:
                del grid['total']
            except Exception:
                pass

            try:
                del grid['admin']
            except Exception:
                pass

            try:
                del grid['root']
            except Exception:
                pass

            try:
                del grid['_mbsetupuser']
            except Exception:
                pass

            try:
                del grid['radmind']
            except Exception:
                pass

            try:
                del grid['Guest']
            except Exception:
                pass

            #
            # calculate time percentages of remaining users
            for item in grid:
                temp = float(grid[item])
                grid[item] = temp / login_total

            # sort the remaining users, based on percentage
            grid_sorted = sorted(grid, key=grid.__getitem__, reverse=True)

            #
            # if there are still valid users, continue
            if grid_sorted:

                #
                # select the top user.
                self.username_string.set(grid_sorted[0])
                high_user_percentge = int(grid[grid_sorted[0]]* 100)
                self.status_label.configure(style='Normal.TLabel')
                self.status_string.set(str(high_user_percentge) + "% user selected.")
                return
            else:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("Error selecting highest usage user, no eligible users")
                return

        except ValueError:
            self.status_label.configure(style='Warning.TLabel')
            self.status_string.set("Error setting Usage Mode.")
            return

    def button_state(self):
        """
        sets buttons to the correct state
        """

        #
        # This method is used to enable/disable specific buttons, based on OS, etc.
        #
        # You want to use the Combobox option of state='disabled'.
        #
        # There are three options for state as follows:
        #
        #     state='normal' which is the fully functional Combobox.
        #     state='readonly' which is the Combobox with a value, but can't be changed (directly).
        #     state='disabled' which is where the Combobox cannot be interacted with.
        #
        # self.highlight_button = ttk.Style()
        # self.highlight_button.configure('Highlight.TButton', foreground='red')
        # ttk.Button(self.mainframe, text="Query this system", style='Highlight.TButton', command= lambda: self.query_jamf_me()).grid(column=2, row=20, padx =3, sticky=W)

        if self.platform == "Mac":
            self.jamf_management_btn.configure(state="normal")

        else:
            self.jamf_management_btn.configure(state="disabled")

    def query_jamf_id(self):
        """
        query jamf for specific computer record
        """
        self.reset_data()

        try:

            self.status_label.configure(style='Normal.TLabel')
            self.status_string.set("ID Mode selected.")

            #
            # request specific jamf computer record
            url = self.jamf_hostname+ '/JSSResource/computers/id/' + self.id_string.get()
            request = urllib2.Request(url)
            request.add_header('Accept', 'application/json')
            request.add_header('Authorization', 'Basic ' + base64.b64encode(self.jamf_username + ':' + self.jamf_password))

            response = urllib2.urlopen(request)
            response_json = json.loads(response.read())

            if response.code != 200:
                self.status_string.set("%i returned." % response.code)
                return

            #
            # begin populating display strings
            self.computer_name_string.set(response_json['computer']['general']['name'])
            self.assettag_string.set(response_json['computer']['general']['asset_tag'])
            self.barcode_string.set(response_json['computer']['general']['barcode_1'])
            self.username_string.set(response_json['computer']['location']['username'])

            self.email_string.set(response_json['computer']['location']['email_address'])
            self.fullname_string.set(response_json['computer']['location']['real_name'])
            self.phone_string.set(response_json['computer']['location']['phone'])
            self.room_string.set(response_json['computer']['location']['room'])
            self.building_string.set(response_json['computer']['location']['building'])
            self.position_string.set(response_json['computer']['location']['position'])
            self.department_string.set(response_json['computer']['location']['department'])
            self.platform = response_json['computer']['general']['platform']

            self.jamf_management = response_json['computer']['general']['remote_management']['managed']

            if self.jamf_management is True:
                self.jamf_management_btn.configure(text="True")
            elif self.jamf_management is False:
                self.jamf_management_btn.configure(text="False")
            else:
                print("else Jamf managment: %r" % self.jamf_management)

            #
            # if you desire to add EA's you will need to find each by parsing all of the EA's
            #

            # jss_purpose_raw = response_json['computer']['extension_attributes']
            # for ea in jss_purpose_raw:
            #     if ea['name'] == 'EA1':
            #         self.ea1_string.set(ea['value'])
            #     elif ea['name'] == 'EA2':
            #         self.ea2_string.set(ea['value'])
            #     elif ea['name'] == 'EA3':
            #         self.ea3_string.set(ea['value'])
            #
            #  etc
            #

        #
        # handle communication errors
        except urllib2.HTTPError, error:
            if error.code == 400:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("HTTP code %i: %s " % (error.code, "Request error."))
            elif error.code == 401:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("HTTP code %i: %s " % (error.code, "Authorization error."))
            elif error.code == 403:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("HTTP code %i: %s " % (error.code, "Permissions error."))
            elif error.code == 404:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("HTTP code %i: %s " % (error.code, "Resource not found."))
            elif error.code == 409:
                contents = error.read()
                error_message = re.findall(r"Error: (.*)<", contents)
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("HTTP code %i: %s " % (error.code, "Resource conflict. " + error_message[0]))
            else:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("HTTP code %i: %s " % (error.code, "Generic error."))

            return
        except urllib2.URLError, error:
            self.status_label.configure(style='Warning.TLabel')
            self.status_string.set("Error contacting Jamf.")
            return
        except Exception as exception_message:
            self.status_label.configure(style='Warning.TLabel')
            self.status_string.set("Error querying Jamf. [%s]" % exception_message)
            return

        self.status_label.configure(style='Normal.TLabel')
        self.status_string.set("Jamf returned info for ID %s." % self.id_string.get())
        self.button_state()

    def query_jamf_me(self):
        """
        Query jamf about this particular machine
        """

        #
        # this method finds the UUID for the local machine
        # query's jamf and parses the ID from the record
        # and then calls the main query method
        # it's wasteful the first time it's called.
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
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("%i returned." % response.code)
                    return

                self.local_jamf_id = response_json['computer']['general']['id']
                self.id_string.set(self.local_jamf_id)

            #
            # handle various communication errors
            except urllib2.HTTPError, error:
                if error.code == 400:
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s " % (error.code, "Request error."))
                elif error.code == 401:
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s " % (error.code, "Authorization error."))
                elif error.code == 403:
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s " % (error.code, "Permissions error."))
                elif error.code == 404:
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s " % (error.code, "Resource not found."))
                elif error.code == 409:
                    contents = error.read()
                    error_message = re.findall(r"Error: (.*)<", contents)
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s " % (error.code, "Resource conflict. " + error_message[0]))
                else:
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s " % (error.code, "Generic error."))

                return
            except urllib2.URLError, error:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("Error contacting JAMF server.")
                return
            except Exception as exception_message:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("Error querying Jamf. [%s]" % exception_message)
                return

        else:
            self.id_string.set(self.local_jamf_id)

        self.query_jamf_id()

    def populate_menu(self, menu_choice):
        """
        builds list from static data source in jamf
        """

        #
        # this method builds lists that can then be used to build combobox or popup menus from
        # departments, buildings, sites
        url = self.jamf_hostname + '/JSSResource/' + menu_choice
        request = urllib2.Request(url)
        request.add_header('Accept', 'application/json')
        request.add_header('Authorization', 'Basic ' + base64.b64encode(self.jamf_username + ':' + self.jamf_password))

        response = urllib2.urlopen(request)
        response_json = json.loads(response.read())

        if response.code != 200:
            return

        menu_items = ['None']
        for item in response_json[menu_choice]:
            menu_items.append(item.get('name'))
        return menu_items

    def populate_ea_menu(self, ea_id):
        """
        builds list from extension attribute in jamf
        """

        #
        # this method builds lists that can then be used to build combobox or popup menus from EA's
        url = self.jamf_hostname + '/JSSResource/computerextensionattributes/id/' + str(ea_id)
        request = urllib2.Request(url)
        request.add_header('Accept', 'application/json')
        request.add_header('Authorization', 'Basic ' + base64.b64encode(self.jamf_username + ':' + self.jamf_password))

        response = urllib2.urlopen(request)
        response_json = json.loads(response.read())

        if response.code != 200:
            return

        choices = response_json['computer_extension_attribute']['input_type']['popup_choices']
        choices = ['None'] + choices
        return choices

    def search_string_jamf(self):
        """
        This method handles searching Jamf with a string
        """
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

        if self.search_string.get() == "" or self.search_string.get().replace(" ", "") == "":
            if self.id_string.get():
                self.query_jamf_id()
                self.status_label.configure(style='Normal.TLabel')
                self.status_string.set("Searched for ID.")
            else:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("No search string entered.")

        else:
            #
            # erase previous displayed values
#             self.reset_data()

            #
            # encode special characters included in search string
            url = self.search_string.get()
            url = urllib.quote(url, ':/()')
            url = self.jamf_hostname + '/JSSResource/computers/match/*' + url + '*'
            url = urllib.quote(url, ':/()')

            #
            # communicate with Jamf server
            try:
                request = urllib2.Request(url)
                request.add_header('Authorization', 'Basic ' + base64.b64encode(self.jamf_username + ':' + self.jamf_password))

                response = urllib2.urlopen(request)

                #
                # a non-200 response is bad, report and return
                if response.code != 200:
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("%i returned." % response.code)
                    return

            #
            # handle various communication errors
            except urllib2.HTTPError, error:
                if error.code == 400:
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s " % (error.code, "Request error."))
                elif error.code == 401:
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s " % (error.code, "Authorization error."))
                elif error.code == 403:
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s " % (error.code, "Permissions error."))
                elif error.code == 404:
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s " % (error.code, "Resource not found."))
                elif error.code == 409:
                    contents = error.read()
                    error_message = re.findall(r"Error: (.*)<", contents)
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s " % (error.code, "Resource conflict. " + error_message[0]))
                else:
                    self.status_label.configure(style='Warning.TLabel')
                    self.status_string.set("HTTP code %i: %s " % (error.code, "Generic error."))

                return
            except urllib2.URLError, error:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("Error contacting JAMF server.")
                return
            except Exception as exception_message:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("Error querying Jamf. [%s]" % exception_message)
                return

            #
            # begin parsing data returned from Jamf
            jamf_dom = parseString(response.read())
            self.status_label.configure(style='Normal.TLabel')
            self.status_string.set("%i matches returned." % int(jamf_dom.getElementsByTagName('size')[0].childNodes[0].nodeValue))

            match_results = []

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

            for node in jamf_dom.getElementsByTagName('computer'):
                match_id = int(node.getElementsByTagName('id')[0].childNodes[0].nodeValue)
                try:
                    match_name = node.getElementsByTagName('name')[0].childNodes[0].nodeValue
                except:
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

                search_window_geo = "%ix%i+%i+%i" % (190, 400, (r_h + r_pos_x + 10), (r_pos_y))
                search_window.geometry(search_window_geo)

                search_window.title("Search results")

                list_frame = ttk.Frame(search_window, width=190, height=400, padding=(4, 0, 0, 0))

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


def login():
    """
    if the user has proper privleges, consider them an authorized user and proceed
    """
    def try_login():
        """
        jamf api call for login test
        """
        try:
            url = jamf_hostname.get() + '/JSSResource/accounts/username/' + jamf_username.get()
            request = urllib2.Request(url)
            request.add_header('Accept', 'application/json')
            request.add_header('Authorization', 'Basic ' + base64.b64encode(jamf_username.get() + ':' + jamf_password.get()))

            response = urllib2.urlopen(request)

            if response.code != 200:
                tkMessageBox.showerror("Jamf login", "Invalid response from Jamf")
                root.destroy() # clean up after yourself!
                sys.exit()

            response_json = json.loads(response.read())

            #
            # store list of user privileges
            user_privileges = response_json['account']['privileges']['jss_objects']

            #
            # stop number of require privileges
            count_privileges = len(required_privileges)

            #
            # for every required privilege
            #  check if it's in user privileges
            #   decrement if yes
            for item in required_privileges:
                if item in user_privileges:
                    count_privileges -= 1

            #
            # if all require privileges accounted for, proceed
            # else alert and fail
            if count_privileges == 0:
                root.destroy() # clean up after yourself!
                return
            else:
                tkMessageBox.showerror("Jamf login", "User lacks appropriate privileges.")

        except:
            tkMessageBox.showerror("Jamf login", "Invalid username or password.")
            sys.exit()

        sys.exit()

    #
    # This is really important. This list contains the required rights.
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

    jamf_hostname, jamf_username, jamf_password = login()
    if not jamf_username:
        sys.exit(0)

    root = Tk()
    my_app = Computer(root, jamf_hostname, jamf_username, jamf_password)

    root.mainloop()

if __name__ == '__main__':
    main()
