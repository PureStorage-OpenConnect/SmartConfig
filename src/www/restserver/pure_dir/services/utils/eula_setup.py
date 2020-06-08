
from pure_dir.infra.apiresults import PTK_OKAY, result
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import g_base_dir
import os
from xml.dom.minidom import parse, parseString, Document


def pretty_print(data): return '\n'.join([line for line in parseString(
    data).toprettyxml(indent=' ' * 2).split('\n') if line.strip()])


def eula_content():
    res = result()
    doc = Document()
    status = False
    if os.path.exists(g_base_dir + "eula_agreement.xml") == False:
        eula = doc.createElement("eula")
        eulastatus = doc.createElement("eulastatus")
        eulastatus.setAttribute('isagree', status)
        doc.appendChild(eula)
        eula.appendChild(eulastatus)
        doc.appendChild(eula)
        o = open(g_base_dir + "eula_agreement.xml", "w")
        o.write(pretty_print(doc.toprettyxml(indent="")))
        o.close()
        doc.unlink()
    else:
        doc = parse(g_base_dir + "eula_agreement.xml")
        eulastatus = doc.getElementsByTagName('eulastatus')
        status = eulastatus[0].getAttribute('isagree')
    data = {"url": "eula/pdt.txt", "isagree": status}
    res.setResult(data, PTK_OKAY, "Success")
    return res


def eula_agreement(isagree):
    res = result()
    doc = parse(g_base_dir + "eula_agreement.xml")
    eula = doc.getElementsByTagName('eulastatus')
    eula_status = eula[0].setAttribute('isagree', isagree)
    o = open(g_base_dir + "eula_agreement.xml", "w")
    o.write(pretty_print(doc.toprettyxml(indent="")))
    o.close()
    doc.unlink()
    res.setResult(isagree, PTK_OKAY, "Success")
    return res
