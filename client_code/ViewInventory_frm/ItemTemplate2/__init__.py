from ._anvil_designer import ItemTemplate2Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ItemTemplate2(ItemTemplate2Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        # get plant list from current plant inventory
        self.plant_list = anvil.server.call('get_plant_list')
        # add a unique list of plant types to the dropdown list
        # by generating a set() of plant types, which allow for unique values only
        # and then converting it to a list()
        self.type_drp.items = list({
            plant['type'] for plant in self.plant_list
        })


    def edit_btn_click(self, **event_args):
        """This method is called when the button is clicked"""
        # enable the record fields
        if not self.name_txb.enabled:
            self.enable_update_fields()

            # original record first stored in self.item
            print(*self.item)
            
        else: # disable the record fields
            self.enable_update_fields(False)

        # edit confirmation completed via change event of the fields
    def enable_update_fields(self, enable=True):
            self.name_txb.enabled      = \
            self.type_drp.enabled      = \
            self.price_txb.enabled     = \
            self.stock_qty_txb.enabled = enable
            

    def plant_field_pressed_enter(self, **event_args):
        """allow user to update plant information"""
        if not(
            self.name_txb.text and 
            self.type_drp.selected_value and 
            self.price_txb.text and
            self.stock_qty_txb.text
        ):
            # if any fields are blank, show error message
            alert('All fields cannot be empty. Please enter a new plant information again.')
            return # ignore update process

        # GET updated information
        self.plant_update_info = {}
        self.plant_update_info['name']      = self.name_txb.text
        self.plant_update_info['type']      = self.type_drp.selected_value
        self.plant_update_info['price']     = int(self.price_txb.text)
        self.plant_update_info['stock_qty'] = int(self.stock_qty_txb.text)
        # print(self.plant_update_info)
        
        # validate price and stock qty
        if not isinstance(self.plant_update_info['price'], (int, float)) or self.plant_update_info['price'] < 0:
            alert("Price must be a non-negative number.")
            return
        if not isinstance(self.plant_update_info['stock_qty'], int) or self.plant_update_info['stock_qty'] < 0:
            alert("Stock quantity must be a non-negative number.")
            return
        
        # determine if field changes
        changes = self.update_plant_record(self.item, self.plant_update_info)
        
        if changes and anvil.server.call('update_plant_record', self.plant_update_info, self.item['name']):
            # print(changes)
            self.enable_update_fields(False)
            Notification('Update successful').show()
        else:
            Notification('No change made...').show()
        
    def update_plant_record(self, row, updated_fields):
        changes = {}

        for key, new_value in updated_fields.items():
            old_value = row[key]
            if old_value != new_value:
                # row[key] = new_value
                changes[key] = {'old': old_value, 'new': new_value}
    
        return changes  # Return a dict of what changed

    # def confirm_type_change_btn_click(self, **event_args):
    #     """This method is called when the button is clicked"""
    #     self.plant_field_pressed_enter()

    # def type_drp_change(self, **event_args):
    #     """This method is called when an item is selected"""
    #     # show confirm button to apply change of plant type
    #     new_type = self.type_drp.selected_value
    #     updated_fields = {'type': new_type}
    #     changes = self.update_plant_record(self.item, updated_fields)
    
    #     if changes:
    #         self.plant_field_pressed_enter()
    #         alert(f"Updated: {changes}")


    def delete_btn_click(self, **event_args):
        """This method is called when the button is clicked"""
        # confirm with user about deleting the record
        confirmed = alert('Are you sure you want to delete this record?',
                        buttons=[('Yes, True'), ('No', False)])
        
        if confirmed:
            # proceed to delete record
            if anvil.server.call('delete_plant_record', self.item)
                Notification('Deletion completed.').show()
                s
        else:
                alert('Record not found. Deletion unsuccessful.')
        else:
            Notification('Delete request cancelled.').show()