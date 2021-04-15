from pure_dir.infra.logging.logmanager import *
from pure_dir.infra.apiresults import *
from pure_dir.services.utils.kickstart import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import*
from xml.dom.minidom import *
import os
import os.path
import shutil
from pure_dir.infra.common_helper import *
from pure_dir.components.common import *
import hashlib


def md5sum(fname):
    """
    Returns the MD5 sum for the file
    :param fname:

    """
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
            hashed_version = hash_md5.hexdigest()
    file_version = fname[fname.rindex('/') + 1:]
    if os.path.exists(g_base_dir + 'file_version.xml'):
        doc = parse(g_base_dir + 'file_version.xml')
        versions = doc.getElementsByTagName("version")
        for version in versions:
            if version.getAttribute('name') == hashed_version:
                file_version = version.getAttribute('version')
        return file_version
    return file_version


def save_file(uploadfile, filepath):
    with open(filepath, "ab") as f:
        f.write(uploadfile.stream.read())


def import_image(uploadfile, image_type, image_sub_type, image_os_sub_type):
    """
     Import an iso, save to iso store
    :param uploadfile: Uploaded file
    :param iso_file:
    :param iso_image_type: image type
    """
    res = result()
    if image_os_sub_type:
        image_sub_type = image_os_sub_type
    if image_sub_type:
        filetype = image_sub_type
    else:
        filetype = image_type
    f_name = uploadfile.filename
    val = images_validate(f_name, filetype)
    if not val:
        res.setResult(True, PTK_NOTEXIST, "Invalid File")
        return res
    filepath = g_upload_path + "%s" % uploadfile.filename
    save_file(uploadfile, filepath)
    if image_sub_type:
        filetype = image_sub_type
    else:
        filetype = image_type
    version = md5sum(filepath)
    if not os.path.exists(g_base_dir + 'images.xml'):
        doc = Document()
        roottag = doc.createElement("images")
        newimage = doc.createElement("image")
        newimage.setAttribute('name', uploadfile.filename)
        newimage.setAttribute('type', filetype)
        newimage.setAttribute('version', version)
        roottag.appendChild(newimage)
        doc.appendChild(roottag)
    else:
        doc = parse(g_base_dir + 'images.xml')
        # Check if images already exists

        for image in doc.getElementsByTagName('image'):
            if image.getAttribute('name') == uploadfile.filename and image.getAttribute(
                    'type') == filetype and image.getAttribute('version') == version:
                res.setResult(True, PTK_OKAY, "Success")
                return res

        newimage = doc.createElement("image")
        newimage.setAttribute('name', uploadfile.filename)
        newimage.setAttribute('type', filetype)
        newimage.setAttribute('version', version)
        doc.childNodes[0].appendChild(newimage)
    fd = open(g_base_dir + 'images.xml', 'w')
    fd.write(pretty_print(doc.toprettyxml(indent="")))
    fd.close()
    res.setResult(True, PTK_OKAY, "Success")
    return res


def images_validate(uploadfile, imagetype):
    """
    Validate image type and images
    :param imagetype:
    :param uploadfile:

    """

    ext = uploadfile[-4:]
    if imagetype == 'MDS' and 'kickstart' not in uploadfile and 'm9' in uploadfile and ext == '.bin':
        return True
    elif imagetype == 'MDS-kickstart' and 'kickstart' in uploadfile and 'm9' in uploadfile and ext == '.bin':
        return True
    elif imagetype == 'Nexus 9k' and 'nxos' in uploadfile and ext == '.bin':
        return True
    elif imagetype == 'Nexus 5k' and 'n5000-uk9.' in uploadfile and ext == '.bin':
        return True
    elif imagetype == 'Nexus 5k-kickstart' and 'n5000-uk9-kickstart' in uploadfile and ext == '.bin':
        return True
    elif imagetype == 'ESXi' and ext == '.iso':
        return True
    elif imagetype == 'ESXi-kickstart' and ext == '.cfg':
        return True
    elif imagetype == 'RHEL' and ext == '.iso':
        return True
    elif imagetype == 'RHEL-kickstart' and ext == '.cfg':
        return True
    elif imagetype == 'UCS-infra' and 'k9-bundle-infra' in uploadfile and ('A.bin' in uploadfile or 'A.gbin' in uploadfile):
        return True
    elif imagetype == 'UCS-blade' and 'ucs-k9' in uploadfile and ('B.bin' in uploadfile or 'B.gbin' in uploadfile):
        return True
    elif imagetype == 'UCS-Rack' and 'ucs-k9' in uploadfile and ('C.bin' in uploadfile or 'C.gbin' in uploadfile):
        return True
    else:
        return False


def list_images(imagetype=''):
    """
    List iso store images
    :param imagetype:  (Default value = '')

    """
    res = result()
    obj = Images()
    images = obj.listimages(imagetype)
    res.setResult(images, PTK_OKAY, "Success")
    return res


def iso_binding(isofile, kickstart):
    isofilepath = g_upload_path + "/" + isofile
    if kickstart == "":
        if os.path.exists(g_upload_path + "/" + "bundle"):
            shutil.rmtree(g_upload_path + "/" + "bundle")
        os.makedirs(g_upload_path + "/" + "bundle")
        os.system("cp %s %s" % (isofilepath, g_upload_path + "/" + "bundle"))
        return True
    kickstartfilepath = g_upload_path + "/" + kickstart
    src = "/tmp/iso" + str(random.randrange(1000))
    os.makedirs(src)
    os.system("mount -o rw,loop %s %s " % (isofilepath, src))
    mount_path = "/mnt/system/uploads/" + isofile[:-4]
    shutil.copytree(src, mount_path)
    shutil.copy2(kickstartfilepath, mount_path + "/" + kickstart[:-4].upper() + ".cfg")
    os.system("umount %s" % src)
    if 'rhel' in isofile:
        pattern_ks = "x20Server.x86_64 quiet"
        pattern_default = "menu default"
        with open(mount_path + '/isolinux/isolinux.cfg', 'r') as infile, open(mount_path + '/isolinux/isolinux1.cfg', 'w') as outfile:
            for line in infile:
                if pattern_ks in line:
                    line = "  append initrd=initrd.img inst.repo=cdrom ks=cdrom:/" + \
                        kickstart[:-4].upper() + ".cfg" + "\n"
                    outfile.write(line)
                elif pattern_default not in line:
                    outfile.write(line)
        os.remove(mount_path + '/isolinux/isolinux.cfg')
        os.rename(mount_path + '/isolinux/isolinux1.cfg', mount_path + '/isolinux/isolinux.cfg')
        pattern_label = "^Install Red Hat Enterprise Linux"
        with open(mount_path + '/isolinux/isolinux.cfg', 'r') as infile, open(mount_path + '/isolinux/isolinux1.cfg', 'w') as outfile:
            for line in infile:
                if pattern_label in line:
                    line = line + "  menu default" + "\n"
                    outfile.write(line)
                else:
                    outfile.write(line)
        os.remove(mount_path + '/isolinux/isolinux.cfg')
        os.rename(mount_path + '/isolinux/isolinux1.cfg', mount_path + '/isolinux/isolinux.cfg')
        pattern_mod_default = "set default"
        with open(mount_path + '/EFI/BOOT/grub.cfg', 'r') as infile, open(mount_path + '/EFI/BOOT/grub1.cfg', 'w') as outfile:
            for line in infile:
                if pattern_mod_default in line:
                    line = 'set default="0"' + "\n"
                    outfile.write(line)
                else:
                    outfile.write(line)
        os.remove(mount_path + '/EFI/BOOT/grub.cfg')
        os.rename(mount_path + '/EFI/BOOT/grub1.cfg', mount_path + '/EFI/BOOT/grub.cfg')
        pattern_conf = "default"
        with open(mount_path + '/isolinux/grub.conf', 'r') as infile, open(mount_path + '/isolinux/grub1.conf', 'w') as outfile:
            for line in infile:
                if pattern_conf in line:
                    line = 'default=0' + "\n"
                    outfile.write(line)
                else:
                    outfile.write(line)
        os.remove(mount_path + '/isolinux/grub.conf')
        os.rename(mount_path + '/isolinux/grub1.conf', mount_path + '/isolinux/grub.conf')
        if os.path.exists(g_upload_path + "/" + "bundle"):
            shutil.rmtree(g_upload_path + "/" + "bundle")
        os.makedirs(g_upload_path + "/" + "bundle")
        bundle = g_upload_path + "/" + "bundle/" + isofile
        os.system(
            "genisoimage -U -r -v -T -J -joliet-long -V 'RHEL-7.6 Server.x86_64' -volset 'RHEL-7.6 Server.x86_64' -A 'RHEL-7.6 Server.x86_64' -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table -eltorito-alt-boot -e images/efiboot.img -no-emul-boot -o {} {}".format(bundle, mount_path))
        os.system(
            "implantisomd5 {}".format(bundle))
        # TODO checkisomd5
        # os.system(
        #   "checkisomd5 {}".format(bundle))
        shutil.rmtree(mount_path)
        return True
    else:
        pattern = "kernelopt"
        with open(mount_path + '/boot.cfg', 'r') as infile, open(mount_path + '/boot1.cfg', 'w') as outfile:
            for line in infile:
                if pattern in line:
                    line = "kernelopt=ks=cdrom:/" + kickstart.upper() + "\n"
                    outfile.write(line)
                else:
                    outfile.write(line)
        os.remove(mount_path + '/boot.cfg')
        os.rename(mount_path + '/boot1.cfg', mount_path + '/boot.cfg')
        if os.path.exists(g_upload_path + "/" + "bundle"):
            shutil.rmtree(g_upload_path + "/" + "bundle")
        os.makedirs(g_upload_path + "/" + "bundle")
        bundle = g_upload_path + "/" + "bundle/" + isofile
        os.system(
            "genisoimage -relaxed-filenames -J -R -o %s -b isolinux.bin -c boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table %s" %
            (bundle, mount_path))
        shutil.rmtree(mount_path)
        return True


def delete_image(imagename):
    """
    Delete an image from ISO Store
    :param imagename:

    """
    res = result()
    obj = Images()
    status = obj.deleteimage(imagename)
    if status:
        res.setResult(True, PTK_OKAY, "Success")
        return res
    else:
        res.setResult(False, PTK_INTERNALERROR, "File is not found")
        return res

# iso_binding("rhel-server-7.6-x86_64-dvd.iso","KS.cfg")
