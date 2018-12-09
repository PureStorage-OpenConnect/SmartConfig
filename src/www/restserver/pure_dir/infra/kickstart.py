from pure_dir.infra.apiresults import *
from pure_dir.components.common import *

import os
image_dir = "/mnt/system/uploads/"
import shutil


class kickstart:
    def __init__(self):
        return

    def kickstart_iso(self):
        obj = Images()
        ret = obj.listimages("ESXi")
        res = parseResult(ret)
        iso_file = res['data'][0]
        print iso_file
        if not os.path.exists(image_dir + "esxi_cdrom_mount"):
            os.makedirs(image_dir + "esxi_cdrom_mount")
        ISO_PATH = image_dir + iso_file
        print ISO_PATH
        os.system(
            "mount -o rw,loop %s /mnt/system/uploads/esxi_cdrom_mount " % ISO_PATH)
        print "mount"
        shutil.copytree('/mnt/system/uploads/esxi_cdrom_mount/',
                        '/mnt/system/uploads/esxi_cdrom')
        print "copy"
        os.system("umount /mnt/system/uploads/esxi_cdrom_mount")
        print "umount"
        pattern = "kernelopt"
        with open('/mnt/system/uploads/esxi_cdrom/boot.cfg', 'r') as infile, open('/mnt/system/uploads/esxi_cdrom/boot1.cfg', 'w') as outfile:
            for line in infile:
                if pattern in line:
                    line = "kernelopt=/mnt/system/uploads/ks.cfg\n"
                    outfile.write(line)
                else:
                    outfile.write(line)
        os.remove('/mnt/system/uploads/esxi_cdrom/boot.cfg')
        os.rename('/mnt/system/uploads/esxi_cdrom/boot1.cfg',
                  '/mnt/system/uploads/esxi_cdrom/boot.cfg')
        os.system("genisoimage -relaxed-filenames -J -R -o v.iso -b isolinux.bin -c boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table /mnt/system/uploads/esxi_cdrom")
