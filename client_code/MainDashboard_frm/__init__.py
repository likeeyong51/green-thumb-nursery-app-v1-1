from ._anvil_designer import MainDashboard_frmTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..AddPlant_frm import AddPlant_frm
from ..RecordSale_frm import RecordSale_frm
from ..ViewInventory_frm import ViewInventory_frm
from ..GenerateReport_frm import GenerateReport_frm

class MainDashboard_frm(MainDashboard_frmTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        # GET user role
        self.role          = properties['user_role']
        self.username      = properties['username'].title()
        self.user_lbl.text = self.username
        
        if self.role == 'Manager':
            # show Add Plant option, which is accessible to managers and admin only
            # self.add_plant_btn.visible        = True
            # show Generate Report option, which is accessible to managers and admin only
            # self.generate_reports_btn.visible = True
            self.manager_crd.visible = True
        else:
            self.manager_crd.visible = False
            

    def add_plant_btn_click(self, **event_args):
        """show the add-plant screen"""
        self.load_pnl.clear()
        self.load_pnl.add_component(AddPlant_frm())

    def record_sale_btn_click(self, **event_args):
        """load the record-sale screen"""
        self.load_pnl.clear()
        self.load_pnl.add_component(RecordSale_frm(username=self.username))

    def inventory_btn_click(self, **event_args):
        """load the show-inventory screen"""
        self.sales_log_btn.visible      = True if not self.sales_log_btn.visible        else False
        self.view_inventory_btn.visible = True if not self.view_inventory_btn.visible   else False
        self.inventory_btn.icon         = 'fa:arrow-down' if self.sales_log_btn.visible else 'fa:arrow-right'

    def generate_report_btn_click(self, **event_args):
        """load the generate-report screen"""
        self.low_stock_btn.visible     = True if not self.low_stock_btn.visible   else False
        self.best_seller_btn.visible   = True if not self.best_seller_btn.visible else False
        self.generate_reports_btn.icon = 'fa:arrow-down' if self.low_stock_btn.visible else 'fa:arrow-right'
        
    def sales_log_btn_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.load_pnl.clear()
        self.load_pnl.add_component(ViewInventory_frm(show='sales'))

    def view_inventory_btn_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.load_pnl.clear()
        self.load_pnl.add_component(ViewInventory_frm(show='inventory'))

    def low_stock_btn_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.load_pnl.clear()
        self.load_pnl.add_component(GenerateReport_frm(show='low-stock'))

    def best_seller_btn_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.load_pnl.clear()
        self.load_pnl.add_component(GenerateReport_frm(show='best-seller'))

    def logout_btn_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.role = self.username = ''
        open_form('Login_frm')
        