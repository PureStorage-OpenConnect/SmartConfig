from setuptools import find_packages, setup

setup(name="puremicroframework",
      version = "1.0",
      description = "common framework",
      author = "Abhilash",
      platforms = ["any"],
      license = "BSD",
      packages = find_packages(),
      install_requires = ["Flask==0.10.1", "requests==2.20.0", "PyYAML", "wsgiref==0.1.2", "connexion==1.1.14", "ucsmsdk==0.9.3.1","yamlreader==3.0.4","pyaml==17.8.0", "isc_dhcp_leases==0.8.1","purestorage==1.11.3","python-crontab==2.2.5",  "pycsco==0.3.5" , "ntplib==0.3.3", "pytz==2017.3", "dicttoxml==1.7.4", "python-slugify==1.2.4", "filelock==2.0.13", "pycrypto==2.6.1", "croniter==0.3.20", "lxml", "requests_toolbelt", "netaddr", "urllib3", "scapy"],
      )
