import re
import pyudev
import logging
import os.path

class UdevRulesManager():
    ruleTemplate = {
        'ACTION': ('==', 'add'),
        'KERNEL': ('==', 'ttyACM[0-9]*'),
        'SUBSYSTEM': ('==', 'tty'),
        'TAG': ('+=', 'systemd'),
        'ATTRS': { 'serial': ('+=', '')},
        'ENV': { 'SYSTEMD_WANTS': ('=', 'PanduzaHA-ng-pppd@%n.service')}
    }
    
    def __init__(self):
        self.log = logging.getLogger("UdevRulesManager")
        self.context = pyudev.Context()
        self.udev_rules = []
        
    def import_rules(self, stream):
        for line in stream:
            rule = {}
            if isinstance(line, bytes):
                line = line.decode("utf-8") 
            self.log.debug(line)
            # Ignore comments and empty lines
            if not line.strip() or line.strip().startswith('#'):
                continue

            # Use cool regex
            rule_match = re.findall(r'(?:(?:(\w+)(?![\{\}]))|(?:(\w+)\{(\w+)\}))([+=]{1,2})(?:"([^"]*)")', line)
    
            if rule_match:
                for key1, key2, key3, sign, value in rule_match:
                    if key1:
                        rule[key1] = (sign, value)
                    elif key2:
                            if rule.get(key2) is None:
                                rule[key2] = {}
                            rule[key2][key3] = (sign, value)
                self.udev_rules.append(rule)
    
    def import_from_file(self, file_path='./90-PanduzaHA-ng.rules'):
        if not os.path.exists(file_path):
            self.log.error(f"{file_path} not found! No rules imported. I will try to create this file at the first rule addition.")
            return
        with open(file_path, 'r') as f:
            self.import_rules(f)

    def to_file(self, output_file='./90-PanduzaHA-ng.rules'):
        with open(output_file, 'w') as f:
            for rule in self.udev_rules:
                rule_str = ', '.join([f'{key}{value[0]}"{value[1]}"' for key, value in rule.items() if not isinstance(value, dict)])
                nested = {k:v for k,v in rule.items() if isinstance(v, dict)}
                flatened = {}
                for key, value in nested.items():
                    flatened = {f'{key}{{{key1}}}': nested_value for key1, nested_value in value.items()}
                    flatened_str = ', '.join([f'{key}{value[0]}"{value[1]}"' for key, value in flatened.items()])
                    rule_str = ', '.join([rule_str, flatened_str])
                
                f.write(rule_str + '\n')
    
    def getSerials(self):
        return [s[1] for s in [rule['ATTRS']['serial'] for rule in self.udev_rules]]
    
    def ruleExist(self, serial):
        return serial in self.getSerials()
        
    def addRule(self, serial):
        if serial in self.getSerials():
            self.log.warning(f"a rule with serial {serial} already exist")
            return
        import copy
        new_rule = copy.deepcopy(self.ruleTemplate)
        new_rule['ATTRS']['serial'] = (new_rule['ATTRS']['serial'][0], serial)
        self.udev_rules.append(new_rule)
        self.to_file()
        
    def removeRule(self, serial):
        rule = [r for r in self.udev_rules if r['ATTRS']['serial'][1] == serial]
        if len(rule) == 0:
            self.log.warning(f"rule with serial {serial} not found")
            return
        self.udev_rules.remove(rule[0])
        self.to_file()
        