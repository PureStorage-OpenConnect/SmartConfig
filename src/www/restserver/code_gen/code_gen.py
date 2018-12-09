# codegen to generate client code
import os
import yaml
import json
from yamlreader import yaml_load
from collections import OrderedDict

def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def get_yaml_list():
    yamls = []
    yamls.append({'apispec':'../pure_dir/services/apps/pdt/api/system_api.yaml', 'codeloc': '../pure_dir/services/apps/pdt/client/','filename': 'pdtclient.py', 'basepath':'pdt'} )
    yamls.append({'apispec':'../pure_dir/services/apps/pdt/api/orchestration.yaml', 'codeloc': '../pure_dir/services/apps/pdt/client/','filename': 'pdtclient.py', 'basepath':'pdt'} )

    return yamls


def print_method(gf, methodname, parameters, module_type, mod_name):
    pmlist = ""
    query_payload= "\tquery_payload = { " 
    body_payload = "\tbody_payload = {}" 
    for parameter  in parameters:
	pmlist = pmlist +  parameter['name'] + ", "
	
        if parameter['in'] == "body":
		body_payload = "\tbody_payload = json.dumps(" + parameter['name'] + ")"

	if parameter['in'] == "query":
		 if 'schema' not in parameter:
               		query_payload= query_payload + "'" +parameter['name'] + "' :" + parameter['name'] + ","
		 else:
               		query_payload= query_payload + "'" +parameter['name'] + "' :json.dumps(" + parameter['name'] + "),"


    query_payload = query_payload[:-1]
    query_payload += "}" 

    if len(parameters) > 0:
	pmlist = pmlist[:-2]

    gf.write ("\n")
    gf.write ("def " + methodname +"_request("+ pmlist +"):\n")
    gf.write(body_payload+"\n")
    gf.write(query_payload+"\n")
    gf.write( "\treturn generate_request('"+methodname+"', query_payload, body_payload ,'"+ mod_name +"', '"+module_type+"')\n")
   

def parse_spec(data, gf, basepath):
    dt = json.loads(json.dumps(data))
    #print dt
    gf.write("import json\n")
    gf.write("from pure_dir.infra.request.restrequest import*\n") 
    for methodname, value in dt['paths'].items():
	if 'post' in value:
		 if 'parameters' in dt['paths'][methodname]['post']: 
		 	parameters = dt['paths'][methodname]['post']['parameters']
		 else:
			parameters = []	
		 print_method(gf, methodname[1:],  parameters, 'POST', basepath)

	if 'get'  in value:
		if 'parameters' in dt['paths'][methodname]['get']:
		 	parameters = dt['paths'][methodname]['get']['parameters']
		else:
			parameters = []
		print_method(gf, methodname[1:],  parameters, 'GET', basepath)

        if 'delete' in value:
		if 'parameters' in dt['paths'][methodname]['delete']:
			parameters = dt['paths'][methodname]['delete']['parameters']
		else:
			parameters = []
		print_method(gf, methodname[1:],  parameters, 'DELETE', basepath)

	if 'put' in value:
		if 'parameters' in dt['paths'][methodname]['put']:
			parameters = dt['paths'][methodname]['put']['parameters']
		else:
			parameters = []
                print_method(gf, methodname[1:],  parameters, 'PUT', basepath)
	
	
def generate_code():
    for fi in get_yaml_list():
	os.system("rm -f %s" % (fi['codeloc'] + fi['filename']))

    for fi in get_yaml_list():
    	gf = open( fi['codeloc'] + fi['filename'],"a+")
  	with open(fi['apispec']) as f:
		dataMap = ordered_load(f, yaml.SafeLoader)
		parse_spec(dataMap, gf, fi['basepath'])
		gf.close()

if __name__ == "__main__":
	generate_code()
