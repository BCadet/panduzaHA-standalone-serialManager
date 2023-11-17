from setuptools import setup
import os

setup(
    name='panduzaHA-serialPPPManager',
    version='0.1',
    packages=['panduzaHA-serialPPPManager'],
    scripts=['manager.py'],
    data_files=[
        ('/etc/panduza/panduzaHA-serialPPPManager', ['host_files/90-PanduzaHA-ng.rules', 'host_files/PanduzaHA-ng-pppd@.service']),
    ],
)

def create_symlink(src, dst):
    try:
        os.symlink(src, dst)
    except OSError as e:
        print(f"Failed to create symlink from {src} to {dst}. Error: {e}")

# Create symlink to /home/ after installation
create_symlink('/etc/panduza/panduzaHA-serialPPPManager/90-PanduzaHA-ng.rules', '/etc/udev/rules.d/90-PanduzaHA-ng.rules')
create_symlink('/etc/panduza/panduzaHA-serialPPPManager/PanduzaHA-ng-pppd@.service', '/etc/systemd/system/PanduzaHA-ng-pppd@.service')
os.chown('/etc/panduza/panduzaHA-serialPPPManager/90-PanduzaHA-ng.rules', os.getuid(), os.getgid())
os.chown('/etc/panduza/panduzaHA-serialPPPManager/PanduzaHA-ng-pppd@.service', os.getuid(), os.getgid())