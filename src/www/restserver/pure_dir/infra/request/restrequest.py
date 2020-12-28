import json
import requests

from pure_dir.infra.logging.logmanager import *
from pure_dir.infra.apiresults import *


def generate_request(api, query_payload, body_payload, mod_name, method):
    obj = result()
    url = 'http://127.0.0.1/' + mod_name + "/" + api
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        pdata = eval(json.dumps(query_payload)) if len(
            query_payload) > 0 else query_payload
        bdata = body_payload

        if method == "GET":
            response = requests.get(url, params=pdata, headers=headers)
        elif method == "POST":
            response = requests.post(
                url, data=bdata, headers=headers, params=pdata)
        elif method == "DELETE":
            response = requests.delete(
                url, data=bdata, headers=headers, params=pdata)
        elif method == "PUT":
            response = requests.put(
                url, data=bdata, headers=headers, params=pdata)

        if response.status_code != 200:
            print("request failed")
            obj.setResult(None, PTK_NOTEXIST,
                          "Request Failed with code" + str(response.status_code))
            return obj

        response = response.json()
        obj.setResult(response, PTK_OKAY,
                      "Response received successfully")

    except requests.exceptions.RequestException as e:
        print(str(e))
        obj.setResult(None, PTK_NOTEXIST, "Request Failed with code" + str(e))
        return obj

    return obj
