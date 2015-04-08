import glob
from setuptools import setup

setup(
    name='zems',
    version='0.0.8',
    packages=['zems', 'zems.lib'],
    url='https://github.com/marijngiesen/zabbix-ems',
    license='GPL',
    author='Marijn Giesen',
    author_email='marijn@studio-donder.nl',
    description='ZEMS (Zabbix Extended Monitoring Scripts) is a tool to retrieve all sorts of metrics from '
                'applications and deliver it to Zabbix in a generic way.',
    entry_points={
        'console_scripts': [
            'zems = zems.main:main',
        ]
    },
    install_requires=['requests', 'enum34', 'commandr'],
    data_files=[
        ('config', glob.glob('config/*.conf')),
        ('config/zabbix', glob.glob('config/zabbix/*.conf')),
        ('templates', glob.glob('templates/*.xml')),
        # ('/usr/share/zems/doc/', ('README.md', 'LICENSE')),
    ]
)
