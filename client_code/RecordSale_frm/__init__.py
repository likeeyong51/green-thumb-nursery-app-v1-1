from ._anvil_designer import RecordSale_frmTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import date

class RecordSale_frm(RecordSale_frmTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.item = {}
        self.item['recorded_by'] = properties['username']
        
        # get plant list from current plant inventory
        plant_list = anvil.server.call('get_plant_list')
        # add it to the dropdown item list
        self.plant_drp.items = [plant['name'] for plant in plant_list]
        
        # delay focus until form loads properly
        anvil.js.window.setTimeout(lambda: self.plant_drp.focus(), 100)

    def record_sale_btn_click(self, **event_args):
        """This method is called when the button is clicked"""
        # CHECK for valid sale quantity: must be a positive number
        if self.item['quantity_sold'] <= 0:
            alert('Quantity sold must be a positive number')
            return

        # RECORD sale transaction
        # SET current date of the transaction
        self.item['sale_date'] = date.today() #.strftime('%d/%m/%Y')
        status, qty = anvil.server.call('record_sale', self.item)
        
        if status: # successful
            Notification(f'Sale transaction recorded successfully! we still have {qty} in stock.').show()
        elif qty > 0: # qty is -1 => quantity specified is more than what's available in the inventory
                alert(f'Quantity not available.  We only have {qty} in stock')
        else: # transaction recording failed
            alert('Sale recording unsuccessful.  Please try again or consult with the administrator.')

        # reset ui
        self.plant_drp.selected_value = None
        self.qty_txb.text = ''
        # put focus back on the dropdown menu
        self.plant_drp.focus()
        
