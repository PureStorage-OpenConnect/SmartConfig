from pure_dir.infra.request.restrequest import generate_request


def PDTReset_request():
    body_payload = {}
    query_payload = {}
    return generate_request('PDTReset', query_payload, body_payload, 'pdt', 'GET')


def System_request():
    body_payload = {}
    query_payload = {}
    return generate_request('System', query_payload, body_payload, 'pdt', 'GET')


def NetworkInfo_request():
    body_payload = {}
    query_payload = {}
    return generate_request('NetworkInfo', query_payload, body_payload, 'pdt', 'GET')


def Logs_request(jobid):
    body_payload = {}
    query_payload = {'jobid': jobid}
    return generate_request('Logs', query_payload, body_payload, 'pdt', 'GET')


def ImportWorkflow_request(uploadfile):
    body_payload = {}
    query_payload = {}
    return generate_request('ImportWorkflow', query_payload, body_payload, 'pdt', 'POST')


def ListImages_request(imagetype):
    body_payload = {}
    query_payload = {'imagetype': imagetype}
    return generate_request('ListImages', query_payload, body_payload, 'pdt', 'GET')
