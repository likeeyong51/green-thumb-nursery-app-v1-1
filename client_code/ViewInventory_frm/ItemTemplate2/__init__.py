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
        plant_list = anvil.server.call('get_plant_list')
        # add a unique list of plant types to the dropdown list
        # by generating a set() of plant types, which allow for unique values only
        # and then converting it to a list()
        self.type_drp.items = list({
            plant['type'] for plant in plant_list
        })
