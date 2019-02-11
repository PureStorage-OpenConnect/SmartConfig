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
    uploadfile.save(filepath)
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
    elif imagetype == 'UCS-infra' and 'k9-bundle-infra' in uploadfile and 'A.bin' in uploadfile:
        return True
    elif imagetype == 'UCS-blade' and 'ucs-k9' in uploadfile and 'B.bin' in uploadfile:
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
    shutil.copy2(kickstartfilepath, mount_path)
    os.system("umount %s" % src)
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

# iso_binding("VMware-VMvisor-Installer-6.0.0.update01-3029758.x86_6411.iso","")
