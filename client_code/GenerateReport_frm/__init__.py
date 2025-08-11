from ._anvil_designer import GenerateReport_frmTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class GenerateReport_frm(GenerateReport_frmTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        show = properties['show']

        if show == 'low-stock':
            '''reveal low stock report'''
            self.low_stock_crd.visible    = True
            self.best_sellers_crd.visible = False
            # delay focus slightly to ensure the form is rendered first
            anvil.js.window.setTimeout(lambda: self.threshold_txb.focus(), 100)
            
        else:
            self.low_stock_crd.visible    = False
            self.best_sellers_crd.visible = True

            self.show_best_sellers()
            
    def show_best_sellers(self):
        """
        calculates and displays a summary of which plants have 
        sold the most units in the last 30 days
        """
        # GET best-seller list from 30 days ago
        sale_list_30_days_ago = anvil.server.call('get_best_sellers')

        if not sale_list_30_days_ago or len(sale_list_30_days_ago) == 0:
            alert('No best seller in the last 30 days')
            return
            
        # populate best seller grid
        self.best_seller_rpnl.items = [sale for sale in sale_list_30_days_ago]
        # self.download_bs_report_btn.enabled = True
        self.file_format_drp2.visible = True #if not self.file_format_drp2.visible else False

    def generate_btn_click(self, **event_args):
        """
        generates and displays a list of all plants where 
        the stock quantity is below a certain threshold
        """
        # GET and VALIDATE threshold qty
        if self.threshold_txb.text == '':
            alert('Threshold cannot be empty.')
            return
        
        try:
            threshold_val = int(self.threshold_txb.text)
        except:
            alert('Threshold must be a valid integer.')
            return
        
        if threshold_val < 0:
            alert('Threshold must be greater than or equal to zero.')
            return

        # GET low-stock report
        self.threshold = threshold_val
        self.low_stock_list = anvil.server.call('get_low_stock_list', threshold_val)

        if not self.low_stock_list or len(self.low_stock_list) == 0:
            alert('Low-stock list is not available.  Please try a different threshold number.')
            self.threshold_txb.focus()
            return
        
        # show low-stock list
        self.low_stock_rpnl.items = [plant for plant in self.low_stock_list]
        # self.download_ls_report_btn.enabled = True
        self.file_format_drp.visible = True #if not self.file_format_drp.visible else False

    def download_ls_report_btn_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.file_format_drp.visible = True if not self.file_format_drp.visible else False

    def download_bs_report_btn_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.file_format_drp2.visible = True if not self.file_format_drp2.visible else False

    def file_format_drp_change(self, **event_args):
        """This method is called when an item is selected"""
        if self.file_format_drp.selected_value is None:
            alert('Please select a file format to download')
            return

        file_format = self.file_format_drp.selected_value

        if file_format == 'JSON':
            # GENERATE json file
            media = anvil.server.call('download_low_stock_json', self.threshold)
        elif file_format == 'CSV':
            # GENERATE csv file
            media = anvil.server.call('download_low_stock_csv', self.threshold)
        else:
            # GENERATE pdf file
            media = anvil.server.call('download_low_stock_pdf', self.threshold)

        if media:
            anvil.media.download(media)
        else:
            alert('No low-stock items found.')

    def file_format_drp2_change(self, **event_args):
        """This method is called when an item is selected"""
        if self.file_format_drp2.selected_value is None:
            alert('Please select a file format to download')
            return

        file_format = self.file_format_drp2.selected_value

        if file_format == 'JSON':
            # GENERATE json file
            media = anvil.server.call('download_best_sellers_json')
        elif file_format == 'CSV':
            # GENERATE csv file
            media = anvil.server.call('download_best_sellers_csv')
        else:
            # GENERATE pdf file
            media = anvil.server.call('download_best_sellers_pdf2')

        # DOWNLOAD report
        if media:
            anvil.media.download(media)
        else:
            alert('No best-seller items found.')