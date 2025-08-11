from ._anvil_designer import Splash_frmTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import js
from anvil.js import get_dom_node

class Splash_frm(Splash_frmTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.timer_1.interval = 0.5 # 1 sec interval per tick
        self.time             = 2 # 2 secs countdown

        # Delay before triggering animation
        # anvil.js.window.setTimeout(self.start_animation, 1500)
        self.role = "splash-container"


    def timer_1_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        if self.time == 0:
            # Add animation class to splash container
            get_dom_node(self).classList.add("splash-logo")#"splash-screen")

            # Wait for animation to finish, then open login form
            js.window.setTimeout(self.go_to_login, 2000)
            # open_form('Login_frm')
        else:
            self.time -= self.timer_1.interval

    def go_to_login(self):
        open_form('Login_frm')