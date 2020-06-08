from setuptools import find_packages, setup

setup(name="puremicroframework",
      version = "1.0",
      description = "common framework",
      author = "Abhilash",
      platforms = ["any"],
      license = "BSD",
      packages = find_packages(),
      install_requires = ["Flask==1.0", "requests==2.20.1", "PyYAML", "urllib3==1.21.1", "wsgiref==0.1.2", "connexion==1.1.14", "ucsmsdk==0.9.3.1","yamlreader==3.0.4","pyaml==17.8.0", "isc_dhcp_leases==0.8.1","purestorage==1.11.3","python-crontab==2.2.5",  "pycsco==0.3.5" , "ntplib==0.3.3", "pytz==2017.3", "dicttoxml==1.7.4", "python-slugify==1.2.4", "filelock==2.0.13", "pycrypto==2.6.1", "croniter==0.3.20", "jsonschema==3.0.1", "Jinja2==2.10.3","lxml==4.4.1", "requests_toolbelt", "netaddr", "scapy", "enum34==1.1.6", "pycparser==2.19", "configparser==4.0.2", "contextlib2==0.6.0", "Werkzeug==0.16.0", "openpyxl==2.6.4", "Pillow==6.2.2"],
      #install_requires = ["Flask==0.10.1", "requests==2.9.1", "PyYAML", "wsgiref==0.1.2", "connexion==1.1.14", "ucsmsdk==0.9.3.1","yamlreader==3.0.4","pyaml==17.8.0", "isc_dhcp_leases==0.8.1","purestorage==1.11.3","python-crontab==2.2.5",  "pycsco==0.3.5" , "ntplib==0.3.3", "pytz==2017.3", "dicttoxml==1.7.4", "python-slugify==1.2.4", "filelock==2.0.13", "pycrypto==2.6.1", "croniter==0.3.20", "lxml", "requests_toolbelt", "netaddr", "urllib3", "scapy", "netmiko==2.4.2"],
      )
