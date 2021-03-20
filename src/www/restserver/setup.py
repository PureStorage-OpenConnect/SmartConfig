from setuptools import find_packages, setup

setup(name="puremicroframework",
      version = "1.0",
      description = "common framework",
      author = "Abhilash",
      platforms = ["any"],
      license = "BSD",
      packages = find_packages(),
      install_requires = ["Flask==1.1.2", "requests==2.24.0", "PyYAML", "urllib3==1.25.9",  "connexion==2.7.0","yamlreader==3.0.4","pyaml==20.4.0", "isc_dhcp_leases==0.9.1", "ucsmsdk==0.9.10", "purestorage==1.19.0","purity_fb","python-crontab==2.5.1", "ntplib==0.3.4", "pytz==2020.1", "dicttoxml==1.7.4", "python-slugify==4.0.1", "filelock==2.0.13", "pycrypto==2.6.1", "croniter==0.3.34", "jsonschema==3.0.1", "Jinja2==2.11.3","lxml==4.5.1", "requests_toolbelt==0.9.1", "netaddr", "scapy==2.4.3", "enum34==1.1.10", "pycparser==2.19", "configparser==5.0.0", "contextlib2==0.6.0", "Werkzeug==0.16.0", "openpyxl==3.0.4", "Pillow==7.2.0", "paramiko==2.7.1", "xmltodict==0.12.0", "netmiko==3.1.1", "connexion[swagger-ui]"]
     
      )
