def dbase(self):
    """
    sample method to parse databse info into fields useable by tugboat
    """
    #
    # Staff database
    #

    try:
        if self.valid_unid():
            pass
        else:
            self.status_label.configure(style='Warning.TLabel')
            self.status_string.set("Error searching database, no valid uNID.")
            self.reset_user()
            return

        self.status_label.configure(style='Normal.TLabel')
        self.status_string.set("Marriott Staff database selected.")

        try:
            db = MySQLdb.connect(host="your.mysql.server",  # your host, usually localhost
                                 user="your_user",          # your username
                                 passwd="your_password",    # your password
                                 db="your_db")              # name of the data base
        except:
            self.status_label.configure(style='Warning.TLabel')
            self.status_string.set("Error connecting to database.")
            return

        staff = db.cursor()
        supervisor  = db.cursor()
        division = db.cursor()
        department  = db.cursor()
        staff.execute("""SELECT name_last, name_first, division_id, department_id,email, phone, campusAddr FROM staff WHERE unid = '%s';""" % self.endusername_string.get())
        if int(staff.rowcount) == 0:
            self.status_label.configure(style='Warning.TLabel')
            self.status_string.set("Error querying specific staff.")
            db.close()
            return
        else:
            for row in staff.fetchall():
                self.fullname_string.set(row[1] + " " + row[0])
                my_division = row[2]
                my_dept     = row[3]
                self.email_string.set(row[4])
                self.phone_string.set(row[5])
                self.room_string.set(row[6])

        supervisor.execute("""SELECT supervisor_unid FROM staff_supervisors WHERE staff_unid = '%s';""" % self.endusername_string.get())
        if int(supervisor.rowcount) == 0:
            self.status_label.configure(style='Warning.TLabel')
            self.status_string.set("Error querying supervisor.")
            db.close()
            return
        else:
            for row in supervisor.fetchall():
                self.supervisor_endusername_string.set(row[0])
                break

        division.execute("""SELECT name FROM division WHERE id = '%s';""" % my_division)
        if int(division.rowcount) == 0:
            self.status_label.configure(style='Warning.TLabel')
            self.status_string.set("Error querying division.")
            db.close()
            return
        else:
            for row in division.fetchall():
                division_name = row[0]

        department.execute("""SELECT name FROM department WHERE id = '%s';""" % my_dept)
        if int(division.rowcount) == 0:
            self.status_label.configure(style='Warning.TLabel')
            self.status_string.set("Error querying department.")
            db.close()
            return
        else:
            for row in department.fetchall():
                department_name = row[0]

        db.close()

        #
        # sets popup menus to correct values
        self.division_string.set(division_name)
        self.position_string.set(department_name)

        if inspect.stack()[1][3] == "__call__":
            self.previous_unid = []

        self.supervisor_btn.configure(state="enabled")
#             self.super_down_btn.configure(state="disabled")

        return

    except ValueError:
        self.status_label.configure(style='Warning.TLabel')
        self.status_string.set("Error setting dbase Mode.")
        db.close()
        return
