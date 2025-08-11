from ._anvil_designer import AddPlant_frmTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import Notification

class AddPlant_frm(AddPlant_frmTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        # delay focus slightly to ensure the form is rendered first
        anvil.js.window.setTimeout(lambda: self.plant_name_txb.focus(), 100)

    def add_to_inventory_btn_click(self, **event_args):
        """This method is called when the button is clicked"""
        # CHECK for blank fields
        if not(
            self.plant_name_txb.text and 
            self.plant_type_drp.selected_value and 
            self.price_txb.text and self.item['price'] >= 0 and
            self.initial_stock_qty_txb.text and self.item['stock_qty'] >= 0
        ):
            # if any fields are blank, show error message
            alert('All fields cannot be empty. Please enter a new plant information again.')
            return # stop execution

        # otherwise, add new plant
        if anvil.server.call('add_plant', self.item):
            Notification('Your new plant was added successfully!').show()
        else:
            # plant exists already
            alert('Plant record exists already.  Please use edit plant feature to modify plant record.')

            # reset text fields
            self.plant_name_txb.text        = \
            self.price_txb.text             = \
            self.initial_stock_qty_txb.text = ''
            
            # reset dropdown plant type
            self.plant_type_drp.selected_value = None

