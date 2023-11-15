from nicegui import ui
import serial
import serial.tools.list_ports
import pyudev
import logging
import re

ports = list(serial.tools.list_ports.comports())
result = []
context = pyudev.Context()

logging.basicConfig(level=logging.DEBUG)
formatter      = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger("dashboard")
log.setLevel(logging.DEBUG)
# log.addHandler(logging.StreamHandler())

def parse_udev_rules(file_path):
    global log
    rules = []
    with open(file_path, 'r') as f:
        for line in f:
            log.info(line)
            rule = {}
            # Ignore comments and empty lines
            if not line.strip() or line.strip().startswith('#'):
                continue

            # Use regular expression to handle quotes around values
            rule_match = re.findall(r'(?:(?:(\w+)(?![\{\}]))|(?:(\w+)\{(\w+)\}))(?:[+=]+)(?:"([^"]*)")', line)
    
            if rule_match:
                for key1, key2, key3, value in rule_match:
                    if key1:
                        rule[key1] = value
                    elif key2:
                            if rule.get(key2) is None:
                                rule[key2] = {}
                            rule[key2][key3] = value
                rules.append(rule)
    return rules

def modify_udev_parameter(rules, parameter, new_value):
    for rule in rules:
        if parameter in rule:
            rule[parameter] = new_value

def append_udev_rule(rules, new_rule):
    rules.append(new_rule)

def remove_udev_rule(rules, rule_to_remove):
    rules[:] = [rule for rule in rules if rule != rule_to_remove]

def write_udev_rules(file_path, rules):
    with open(file_path, 'w') as f:
        for rule in rules:
            rule_str = ' '.join([f'{key}={value}' for key, value in rule.items()])
            f.write(rule_str + '\n')

file_path = '/etc/udev/rules.d/90-PanduzaHA-ng.rules'
udev_rules = parse_udev_rules(file_path)
log.info(udev_rules)
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
    result.append(port_info)
    # Use pyudev to get USB information for a specific port
    

grid = ui.aggrid({
    'columnDefs': [
        {'headerName': 'Name', 'field': 'name', 'checkboxSelection': True},
        {'headerName': 'Vendor ID', 'field': 'vendor_id'},
        {'headerName': 'Product ID', 'field': 'product_id'},
        {'headerName': 'Serial', 'field': 'serial_number'},
        {'headerName': 'Description', 'field': 'description'},
    ],
    'rowData': result,
    'rowSelection': 'multiple',
})

with ui.row().classes("items-center justify-between w-full"):
    ui.button(icon="arrow_downward")
    ui.button(icon="arrow_upward")

grid = ui.aggrid({
    'columnDefs': [
        {'headerName': 'Name', 'field': 'name', 'checkboxSelection': True},
        {'headerName': 'Vendor ID', 'field': 'vendor_id'},
        {'headerName': 'Product ID', 'field': 'product_id'},
        {'headerName': 'Serial', 'field': 'serial_number'},
        {'headerName': 'Description', 'field': 'description'},
    ],
    'rowData': [],
    'rowSelection': 'multiple',
})



ui.run(dark=True, title="PanduzaHA-ng serialManager")