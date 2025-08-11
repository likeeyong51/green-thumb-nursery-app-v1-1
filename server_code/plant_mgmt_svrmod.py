import anvil.files
from anvil.files import data_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime, timedelta
import json
import csv
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from anvil import BlobMedia

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#
@anvil.server.callable
def add_plant(plant_info):
    '''add a new plant and return the add status'''
    # if new plant
    if not app_tables.plant_inventory.get(name=plant_info['name']):
        # then add plant
        return app_tables.plant_inventory.add_row(**plant_info)

    # plant already exists
    return False

@anvil.server.callable
def record_sale(sale):
    '''records a transaction sale'''
    # CHECK if qty sold <= available stock
    plant = app_tables.plant_inventory.get(name=sale['plant_sold'])

    if sale['quantity_sold'] > plant['stock_qty']:
        # qty not available
        return False, plant['stock_qty']

    # CREATE a row in the Sales_Log table
    # retrieve user record
    print(sale['recorded_by'])
    sale['recorded_by'] = app_tables.users.get(email=f"{sale['recorded_by'].lower()}@nursery.com")
    # set plant sold
    sale['plant_sold'] = plant
    # SAVE to the sales_log table
    if app_tables.sales_log.add_row(**sale):
        # if SAVE successful, UPDATE the stock quantity in the Plant_inventory table
        plant['stock_qty'] -= sale['quantity_sold']
        return True, plant['stock_qty']  # sales transaction completed successfully

    return False, -1 # sales transaction failed

@anvil.server.callable
def get_plant_list():
    ''' retrieve and returns a list of plants from the inventory list'''
    plant_list = app_tables.plant_inventory.search()
    
    return plant_list if plant_list else False

@anvil.server.callable
def get_sales_list(date=None):
    '''retrieve and returns a list of sales from the sales log'''
    # fetch row based on date filter
    sales_row = (
        app_tables.sales_log.search(sale_date=date) if date
        else app_tables.sales_log.search() # or get everything
    )
    sales_data = []
    
    # build the inventory list
    for sale in sales_row or []:
        # build and append a single sale record for each sale_row
        plant = sale['plant_sold']  if sale['plant_sold'] else None
        user  = sale['recorded_by'] if sale['recorded_by'] else None
        
        sales_data.append({
            'plant_sold'   : plant['name'] if plant else 'Unknown',
            'quantity_sold': sale['quantity_sold'],
            'sale_date'    : sale['sale_date'],
            'recorded_by'  : user['email'].split('@')[0] if user else 'Unknown'
        })
    # print(sales_data)
    return sales_data if sales_data else False

@anvil.server.callable
def get_low_stock_list(threshold):
    # GET low-stock list based on threshold
    low_stock_list = app_tables.plant_inventory.search(
        stock_qty=q.less_than_or_equal_to(threshold)
    )

    return low_stock_list if low_stock_list else False

@anvil.server.callable
def download_low_stock_json(threshold):
    '''GENERATE and RETURN a downloadable blob containint low-stock list in JSON format'''
    # RETRIEVE the best-seller list
    rows = get_low_stock_list(threshold)
    if not rows:
        return False

    # build a list of dictionaries of the low-stock list
    data = [
        {
            'name'     : row['name'],
            'type'     : row['type'] if row['type'] else 'Uncategorised',
            'price'    : row['price'],
            'stock_qty': row['stock_qty']
        }
        for row in rows
    ]

    # CONVERTS the python list of dictionaries into a JSON-formatted string
    json_str = json.dumps(data, indent=4)

    # WRAP and RETURN a downlodable blob in JSON format
    return BlobMedia("application/json", json_str.encode('utf-8'), name="low_stock_report.json")

@anvil.server.callable
def download_low_stock_csv(threshold):
    '''GENERATE and RETURN a downloadable blob containint low-stock list in CSV format'''
    # RETRIEVE the best-seller list
    rows = get_low_stock_list(threshold)
    if not rows:
        return False
    # CREATE an in-memory text stream
    # this acts like a file but lives in the RAM - necessary for web apps
    output = io.StringIO()
    # INITIALISE a CSV writer that writes dictionaries to the output stream
    writer = csv.DictWriter(output, fieldnames=["name", "type", "price", "stock_qty"])
    # WRITE the header row to the CSV file
    writer.writeheader()
    # WRITE each dictionary in data as a row in the CSV
    # Each data is matched automatically to the fieldnames
    for row in rows:
        writer.writerow({
            'name'     : row['name'],
            'type'     : row['type'] if row['type'] else 'Uncategorised',
            'price'    : row['price'],
            'stock_qty': row['stock_qty']
        })

    # WRAP and RETURN a downlodable blob in CSV format
    return BlobMedia("text/csv", output.getvalue().encode('utf-8'), name="low_stock_report.csv")

@anvil.server.callable
def download_low_stock_pdf(threshold):
    '''GENERATE and RETURN a downloable blob containing low-stock list in PDF format'''
    # RETRIEVE low-stock list
    rows = get_low_stock_list(threshold)
    if not rows:
        return False
        
    # CREATE an in-memory binary stream to hold the PDF data
    buffer = io.BytesIO()
    # INITIALISES a ReportLab canvas object to draw on
    # and set the document size to standard A4 dimensions
    c = canvas.Canvas(buffer, pagesize=A4)
    # unpacks the A4 dimensions into width and height
    width, height = A4

    # SET font to Helvetica-Bold, size 17
    c.setFont("Helvetica-Bold", 17)
    # SET the initial vertical position (y) near the top of the page
    y = height - 50 # leaves a 50-pt margin from the top edge
    # get today's date: www dd-mm-yyyy
    today = datetime.today().strftime('%a %d-%m-%Y')
    # DRAW the title string at position (50, y), 50 is the left margin; y is the vertical position
    c.drawString(50, y, f"Low Stock Report (Threshold ≤ {threshold} on {today})")
    # SET font to Helvetica, size 12
    c.setFont("Helvetica", 12)
    # MOVE the y position down by 30 pts to leave space below the title
    y -= 30
    
    # LOOP through each item in the low-stock list
    for n, row in enumerate(rows, 1):
        # FORMAT a line of text with: Plant name (Stock Quantity), Plant Type, unit price (rounded to 2 decimal places)
        line = f"{n}. {row['name']} — Qty: {row['stock_qty']}, Type: {row['type'] if row['type'] else 'Uncategorised'}, Unit Price: ${row['price']:.2f}"
        # DRAW the formatted line at the current y position
        c.drawString(50, y, line)
        # MOVE the y postion down for the next line
        y -= 20
        # CHECKS if the y position is too close to the bottom of the page
        if y < 50: # if YES
            # STARTS a new page in the PDF
            c.showPage()
            # RESETS the y position to the top of the new page
            y = height - 50
    # FINALISES the PDF content and WRITES it into the buffer
    c.save()
    # RETURNS the PDF as a downloable blob in Anvil
    # "application/pdf" sets the MIME type
    # buffer.getvalue() extracts the binary content
    return BlobMedia("application/pdf", buffer.getvalue(), name="low_stock_report.pdf")

@anvil.server.callable
def get_best_sellers():
    # GET and determine the best sellers in the last 30 days
    # Get today's date
    today = datetime.today()

    # Subtract 30 days
    thirty_days_ago = today - timedelta(days=30)
    
    sale_list_30_days = app_tables.sales_log.search(
        sale_date=q.greater_than_or_equal_to(thirty_days_ago)
    )

    # AGGREGATE sales by plant
    plant_sales = {}
    for sale in sale_list_30_days:
        plant    = sale['plant_sold']
        quantity = sale['quantity_sold']

        if plant:
            plant_name = plant['name']
            unit_price = plant['price'] if plant['price'] else 0
            total_sale = quantity * unit_price
            
            if plant_name in plant_sales:
                plant_sales[plant_name]['total_quantity'] += quantity
                plant_sales[plant_name]['total_sales']    += total_sale
            else:
                plant_sales[plant_name]    = {
                    'total_quantity' : quantity,
                    'total_sales'    : total_sale,
                    'unit_price'     : unit_price
                }

    # CONVERT to sorted list of dicts
    sort_sales = sorted(
        [
            {
                'plant_name'  : name,
                'total_sold'  : sale_data['total_quantity'],
                'unit_price'  : f"{sale_data['unit_price']:.2f}",
                'total_sales' : round(sale_data['total_sales'], 2)
            }
            for name, sale_data in plant_sales.items()
        ],
        key = lambda x: x['total_sold'],
        reverse = True
    )
    # RETURN sorted best-seller sales list
    return sort_sales if sort_sales else False
    
@anvil.server.callable
def download_best_sellers_json():
    '''GENERATE and RETURN a downlodable blob containing the best-sellers list in JSON format'''
    # RETRIEVE the best-seller list
    data = get_best_sellers()
    # CONVERTS the python list of dictionaries into a JSON-formatted string
    json_str = json.dumps(data, indent=4)
    # WRAP and RETURN a downlodable blob in JSON format
    return BlobMedia("application/json", json_str.encode('utf-8'), name="best_sellers.json")

@anvil.server.callable
def download_best_sellers_csv():
    '''GENERATE and RETURN a downlodable blob containing the best-sellers list in CSV format'''
    # RETRIEVE the best-seller list
    data = get_best_sellers()
    # CREATE an in-memory text stream
    # this acts like a file but lives in the RAM - necessary for web apps
    output = io.StringIO()
    # INITIALISE a CSV writer that writes dictionaries to the output stream
    writer = csv.DictWriter(output, fieldnames=["plant_name", "total_sold", "unit_price", "total_sales"])
    # WRITE the header row to the CSV file
    writer.writeheader()
    # WRITE each dictionary in data as a row in the CSV
    # Each data is matched automatically to the fieldnames
    writer.writerows(data)
    # WRAP and RETURN a downlodable blob in CSV format
    return BlobMedia("text/csv", output.getvalue().encode('utf-8'), name="best_sellers.csv")

@anvil.server.callable
def download_best_sellers_pdf():
    '''GENERATE and RETURN a downloable blob containing the best-sellers list in PDF format'''
    # RETRIEVE best-selling list
    data = get_best_sellers()
    # CREATE an in-memory binary stream to hold the PDF data
    buffer = io.BytesIO()
    # INITIALISES a ReportLab canvas object to draw on
    # and set the document size to standard A4 dimensions
    c = canvas.Canvas(buffer, pagesize=A4)
    # unpacks the A4 dimensions into width and height
    width, height = A4

    # SET font to Helvetica-Bold, size 17
    c.setFont("Helvetica-Bold", 17)
    # SET the initial vertical position (y) near the top of the page
    y = height - 50 # leaves a 50-pt margin from the top edge
    # get today's date: www dd-mm-yyyy
    today = datetime.today().strftime('%a %d-%m-%Y')
    # DRAW the title string at position (50, y), 50 is the left margin; y is the vertical position
    c.drawString(50, y, f"Best Sellers Report ({today})")
    # SET font to Helvetica, size 12
    c.setFont("Helvetica", 12)
    # MOVE the y position down by 30 pts to leave space below the title
    y -= 30
    # LOOP through each item in the best seller list
    for n, item in enumerate(data, 1):
        # FORMAT a line of text with: Plant name, unit price, Quantity sold and Total Sales (rounded to 2 decimal places)
        line = f"{n}. {item['plant_name']} (${item['unit_price']}) = Qty:{item['total_sold']} sold, Total Sales:${item['total_sales']:.2f}"
        # DRAW the formatted line at the current y position
        c.drawString(50, y, line)
        # MOVE the y postion down for the next line
        y -= 20
        # CHECKS if the y position is too close to the bottom of the page
        if y < 50: # if YES
            # STARTS a new page in the PDF
            c.showPage()
            # RESETS the y position to the top of the new page
            y = height - 50
    # FINALISES the PDF content and WRITES it into the buffer
    c.save()
    # RETURNS the PDF as a downloable blob in Anvil
    # "application/pdf" sets the MIME type
    # buffer.getvalue() extracts the binary content
    return BlobMedia("application/pdf", buffer.getvalue(), name="best_sellers.pdf")

@anvil.server.callable
def download_best_sellers_pdf2():
    '''GENERATE and RETURN a downloadable blob containing the best-seller list in PDF'''
    # RETRIEVE the best-seller list
    data = get_best_sellers()
    # CREATE a buffer stream to hold the pdf data
    buffer = io.BytesIO()

    # Create PDF document
    # doc is the layout manager
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    # elements is a list of content blocks (title, table, etc)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    # paragrah creates styled text
    # get today's date: www dd-mm-yyyy
    today = datetime.today().strftime('%a %d-%m-%Y')
    title = Paragraph(f"Best Sellers Report ({today})", styles['Title'])
    elements.append(title)
    # spacer adds vertical space of 12pts
    elements.append(Spacer(1, 12))

    # prepare table: first row is the header, subsequent row is a best-seller entry
    # Table data: header + rows
    table_data = [["Plant Name", "Unit Price", "Quantity Sold", "Total Sales"]]
    for item in data:
        table_data.append([
            item['plant_name'],
            f"${item['unit_price']}",
            item['total_sold'],
            f"${item['total_sales']:.2f}"
        ])

    # Create table
    table = Table(table_data, colWidths=[150, 80, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)

    # Build PDF
    doc.build(elements)
    return BlobMedia("application/pdf", buffer.getvalue(), name="best_sellers.pdf")
