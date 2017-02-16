class LDAP_record:
    """
    consume LDAP record and provide methods for accessing interesting data
    """
    def __init__(self, unid):
        self.error = False
        ldap_dict = {}

        #
        # request complete user record from LDAP
        cmd = "/Users/" + unid
        try:
            raw_data = subprocess.check_output(["/usr/bin/dscl", "/LDAPv3/your.ldap.server", "-read", cmd])
        except:
            self.error = True
            return

        #
        # begin parsing data into dictionary
        raw_data = string.replace(raw_data, '\n ', ' ')
        raw_data =  raw_data.split('\n')

        for line in raw_data:
            y = line.split(":")
            y = [x for x in y if 'dsAttrTypeNative' not in x]

            if len(y) == 2:
                key = y[0]
                value = y[1]
                value = value.lstrip()

            else:
                key = y[0]
                value = y[1:]
                value = [x for x in value if x]

            if key:
                ldap_dict[key] = value

        self.record = ldap_dict

    def is_student(self):
        try:
            if 'CurrentStudent' in self.record['Student']:
                return True
            else:
                return False
        except:
            return False

    def is_staff(self):
        try:
            if self.record['Employee']: return True
        except:
            return False

    def my_name(self):
        try:
            if self.record['gecos']:
                if len(self.record['gecos']) > 1:
                    return self.record['gecos']
                else:
#                     print "Beep!"
                    try:
                        if self.record['displayName']: return self.record['displayName']
                    except:
                        return None
        except:
            try:
                if self.record['displayName']: return self.record['displayName']
            except:
                return None

    def my_title(self):
        try:
            if self.record['title']: return self.record['title']
        except:
            return None

    def my_email(self):
        try:
            if self.record['mail']: return self.record['mail']
        except:
            try:
                if self.record['ExtensionAttribute4']: return self.record['ExtensionAttribute4']
            except:
                return None

    def my_phone(self):
        try:
            if self.record['telephoneNumber']: return self.record['telephoneNumber']
        except:
            return None

    def my_department(self):
        try:
            if self.record['department']: return self.record['department']
        except:
            return None

    def my_address(self):
        try:
            if self.record['streetAddress']: return self.record['streetAddress']
        except:
            return None

    #
    # diagnostic methods
    def print_full(self):
        for k, v in self.record.items():
            print ("%s > %r" % (k, v))

    def print_keys(self):
        return self.record.keys()



def ldap(self):
    """
    translate LDAP data from object into fields used in tugboat
    """
    try:
        self.status_label.configure(style='Normal.TLabel')
        self.status_string.set("LDAP selected.")

        if self.valid_unid():
            print("ldap %r" % self.endusername_string.get())
            this_person = LDAP_record(self.endusername_string.get())
            if not this_person.error:

                self.fullname_string.set(this_person.my_name())
                self.email_string.set(this_person.my_email())
                self.phone_string.set(this_person.my_phone())
                self.room_string.set(this_person.my_address())
                if this_person.my_title() is None:
                    if this_person.my_department() is None:
                        self.position_string.set("")
                    else:
                        self.position_string.set(this_person.my_department())
                else:
                    if this_person.my_department() is None:
                        self.position_string.set(this_person.my_title())
                    else:
                        self.position_string.set(this_person.my_title() + "/" + this_person.my_department())
                if self.division_string.get():
                    self.division_string.set('None')
                if self.building_string.get():
                    self.building_string.set('None')
            else:
                self.status_label.configure(style='Warning.TLabel')
                self.status_string.set("LDAP error, no record found for uNID.")
                self.reset_data()
        else:
            self.status_label.configure(style='Warning.TLabel')
            self.status_string.set("Error setting LDAP Mode, no valid uNID.")
            self.reset_user()
            return
    except ValueError:
        self.status_label.configure(style='Warning.TLabel')
        self.status_string.set("Error setting LDAP Mode.")
        return
