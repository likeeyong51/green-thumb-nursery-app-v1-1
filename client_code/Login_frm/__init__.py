from ._anvil_designer import Login_frmTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from ..Signup_frm import Signup_frm

class Login_frm(Login_frmTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        # initialise an empty user dictionary
        self.new_user = {}

        # delay focus slightly to ensure the form is rendered first
        anvil.js.window.setTimeout(lambda: self.username_txb.focus(), 100)

    def login_btn_click(self, **event_args):
        """This method is called when the button is clicked"""
        if not(self.username_txb.text or self.password_txb.text):
            alert("Please enter username and password")
            return
            
        # get and format the username
        email_for_login = f"{self.item['username']}@nursery.com"
        # attempt a log in
        try:
            anvil.users.login_with_email(email_for_login, self.item['password'])
            # if login is successful, open with main app form
            anvil.open_form(
                'MainDashboard_frm',
                user_role = anvil.server.call('get_user_role', email_for_login),
                username  = self.item['username']
            )
        except anvil.users.AuthenticationFailed as e:
            alert(str(e))

    def signup_lnk_click(self, **event_args):
        """This method is called when the link is clicked"""
        # anvil.open_form('Signup')
        self.signup_pnl.clear()
        self.signup_pnl.add_component(Signup_frm(item=self.new_user))
        
        # show signup card
        self.signup_crd.visible = True
        
        
    def hide_signup_card(self, show=False):
        '''hide or show signup card'''
        self.signup_crd.visible = show