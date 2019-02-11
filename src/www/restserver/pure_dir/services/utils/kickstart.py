
import os
image_dir = "/mnt/system/uploads/"
import shutil
import random


class kickstart:
    def __init__(self):
        return

    def kickstart_iso(self, uploadfile, isofilename):
        s = os.listdir('/mnt/system/uploads/')
        for i in s:
            if i == isofilename:
                src = "/tmp/iso" + str(random.randrange(1000))
                os.makedirs(src)
                ISO_PATH = image_dir + isofilename
                os.system("mount -o rw,loop %s %s " % (ISO_PATH, src))
                mount_path = "/mnt/system/uploads/" + isofilename[:-4]
                shutil.copytree(src, mount_path)
                shutil.copy2("/mnt/system/uploads/" +
                             uploadfile.filename, mount_path)
                os.system("umount %s" % src)
                pattern = "kernelopt"
                print "******************", mount_path
                with open(mount_path + '/boot.cfg', 'r') as infile, open(mount_path + '/boot1.cfg', 'w') as outfile:
                    for line in infile:
                        if pattern in line:
                            line = "kernelopt=ks=cdrom:/" + uploadfile.filename.upper() + "\n"
                            outfile.write(line)
                        else:
                            outfile.write(line)
                f_path = image_dir + isofilename
                os.remove(mount_path + '/boot.cfg')
                os.rename(mount_path + '/boot1.cfg', mount_path + '/boot.cfg')
                os.system(
                    "genisoimage -relaxed-filenames -J -R -o %s -b isolinux.bin -c boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table %s" %
                    (f_path, mount_path))
                shutil.rmtree(mount_path)
                return True
        return False
