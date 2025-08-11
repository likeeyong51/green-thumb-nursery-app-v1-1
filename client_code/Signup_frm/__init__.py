from ._anvil_designer import Signup_frmTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import Notification

class Signup_frm(Signup_frmTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.item['firstname'] = \
        self.item['lastname']  = \
        self.item['emp_id']    = \
        self.item['role']      = \
        self.item['password']  = None
        # populate dropdown list items from role table
        self.role_drp.items = [r['role'] for r in anvil.server.call('get_user_roles')]

        # delay focus slightly to ensure the form is rendered first
        anvil.js.window.setTimeout(lambda: self.firstname_txb.focus(), 100)

    def signup_btn_click(self, **event_args):
        """This method is called when the button is clicked"""
        # check if any of the required fields (firstname, role and password) is empty
        if not all([
            self.item['firstname'], 
            self.item['lastname'], 
            self.item['emp_id'], 
            self.item['role'], 
            self.item['password'],
            self.item['confirmed_password']
        ]):
            alert("All fields are required.")
            return
        # if passwords entered is inconsistent
        if self.item['password'] != self.item['confirmed_password']:
            alert("Your passwords do not match. Please enter your passwords again.")
            return

        try:
            new_user, username = anvil.server.call(
                'signup_user', 
                self.item['firstname'], 
                self.item['lastname'], 
                self.item['emp_id'], 
                self.item['role'], 
                self.item['password'])
            
            if new_user:
                # if signup is successful, notify user with success message
                alert(f'Account created successfully!\nYour username is {username}. Please log in.')
            else:
                # signup failed
                Notification(f'{username} account exists.  Please log in').show()
            # go back to the login form
            # anvil.open_form('Login')
            # hide signup card
            get_open_form().hide_signup_card()
                
        except Exception as e:
            alert(str(e))

    def cancel_btn_click(self, **event_args):
        """hide signup card"""
        get_open_form().hide_signup_card()

    def check_password_match(self, **event_args):
        '''As a user enters the passwords, it check if the password and 
           confirmed password matches and show a relevant indicator'''
        if self.password_txb.text != self.confirmed_password_txb.text:
            # show mismatched indicator
            self.confirmed_password_txb.role    = 'outlined-error'
            self.conf_pass_check_lbl.icon       = 'fa:ban'
            self.conf_pass_check_lbl.foreground = 'red'
            
        if self.password_txb.text == self.confirmed_password_txb.text:
            # show matched indicator
            self.confirmed_password_txb.role    = 'outlined'
            self.conf_pass_check_lbl.icon       = 'fa:check'
            self.conf_pass_check_lbl.foreground = 'green'
            