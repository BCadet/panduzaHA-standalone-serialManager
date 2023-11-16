import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger("PanduzaHA-ng serial PPP Manager")

from nicegui import app, ui
import serial
import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())
port_infos = []

templateRow = {
    'name': 'device not available',
    'description': "",
    'vendor_id': '',
    'product_id': '',
    'serial_number': ''
}

from UdevRulesManager import UdevRulesManager
rulesManager = UdevRulesManager()
rulesManager.import_from_file()
# log.info(udev_rules)

import pyudev
context = pyudev.Context()
# Iterate through the ports
for port in ports:
    device = pyudev.Devices.from_device_file(context, port.device)
    port_info = {
        'name': port.device,
        'description': port.description,
        'vendor_id': device.get('ID_VENDOR_ID'),
        'product_id': device.get('ID_MODEL_ID'),
        'serial_number': device.get('ID_SERIAL_SHORT')
    }
    port_infos.append(port_info)
    
def update_tables():
    available = [p for p in port_infos if not rulesManager.ruleExist(p['serial_number'])]
    enabled = [p for p in port_infos if rulesManager.ruleExist(p['serial_number'])]
    for serial in rulesManager.getSerials():
        if serial in [s for s in [p['serial_number'] for p in enabled]]:
            continue
        import copy
        unknown_port = copy.deepcopy(templateRow)
        unknown_port["serial_number"] = serial
        enabled.append(unknown_port)
    grid_available.options['rowData'] = available
    grid_enabled.options['rowData'] = enabled
    grid_available.update()
    grid_enabled.update()
    
async def add_rules():
    rows = await grid_available.get_selected_rows()
    if rows:
        for row in rows:
            log.debug(f"add rule for {row['serial_number']}")
            rulesManager.addRule(row['serial_number'])
            update_tables()
            
async def remove_rules():
    rows = await grid_enabled.get_selected_rows()
    if rows:
        for row in rows:
            log.debug(f"remove rule for {row['serial_number']}")
            rulesManager.removeRule(row['serial_number'])
            update_tables()

with ui.card().classes('w-full'):
    with ui.row().classes('w-full'):
        ui.label("available devices")
        ui.element('q-space')
        ui.button("add to PPP service", icon="add", on_click=add_rules)
    grid_available = ui.aggrid({
        'title': "Avaialble devices",
        'columnDefs': [
            {'headerName': 'Name', 'field': 'name', 'checkboxSelection': True},
            {'headerName': 'Vendor ID', 'field': 'vendor_id'},
            {'headerName': 'Product ID', 'field': 'product_id'},
            {'headerName': 'Serial', 'field': 'serial_number'},
            {'headerName': 'Description', 'field': 'description'},
        ],
        'rowData': [],
        'rowSelection': 'multiple',
        'auto_size_columns': True,
    }).classes('max-h-40')
        
        

def import_file(imported):
    rulesManager.import_rules(imported.content)
    update_tables()
    rulesManager.to_file()
    ui.notify(f'Successfully imported {imported.name}')

def manual_serial():
    rulesManager.addRule(userSerial.value)
    update_tables()

with ui.card().classes('w-full'):
    with ui.row().classes('w-full'):
        ui.label("devices registerd to PanduzaHA-ng PPP service")
        ui.element('q-space')
        ui.button("remove from PPP service", icon="remove", on_click=remove_rules)
    grid_enabled = ui.aggrid({
        'columnDefs': [
            {'headerName': 'Name', 'field': 'name', 'checkboxSelection': True},
            {'headerName': 'Vendor ID', 'field': 'vendor_id'},
            {'headerName': 'Product ID', 'field': 'product_id'},
            {'headerName': 'Serial', 'field': 'serial_number'},
            {'headerName': 'Description', 'field': 'description'},
        ],
        'rowData': [],
        'rowSelection': 'multiple',
        'auto_size_columns': True,
    }).classes('max-h-40')

with ui.row().classes("items-center justify-between w-full"):
    ui.element('q-space')
    ui.upload(label='import rules file', auto_upload=True,
              on_upload=lambda e:import_file(e)
              ).props('flat bordered accept=.rules')
    ui.button('SAVE AS', on_click=lambda: ui.download('./90-PanduzaHA-ng.rules'))
    ui.element('q-space')
    userSerial = ui.input(label='User Serial', placeholder="add serial manually")
    ui.button("add user defined Serial", on_click=manual_serial)
    ui.element('q-space')

update_tables()

ui.run(dark=True, title="PanduzaHA-ng serialManager")