from setuptools import setup

setup(
    name='zems',
    version='0.0.3',
    packages=['zems', 'zems.lib'],
    url='https://github.com/marijngiesen/zabbix-ems',
    license='GPL',
    author='Marijn Giesen',
    author_email='marijn@studio-donder.nl',
    description='ZEMS (Zabbix-ems) is a tool to retrieve all sorts of metrics from applications and deliver it to Zabbix in a generic way.',
    entry_points={
        'console_scripts': [
            'zems = zems.main:main',
        ]
    },
    requires=['requests', 'MySQLdb', 'enum34', 'commandr']
)
