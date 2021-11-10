import json
import os

from ctc import config_utils


_http_sessions = {}


def rpc_call_http(
    method=None,
    parameters=None,
    batch_methods=None,
    batch_parameters=None,
    provider=None,
):

    if provider is None:
        provider = config_utils.get_config()['export_provider']

    # get session
    session = _get_http_session(provider=provider)

    # build request data
    data = _build_request_data(
        method=method,
        parameters=parameters,
        batch_methods=batch_methods,
        batch_parameters=batch_parameters,
    )

    # perform request
    response = session.post(url=provider, data=json.dumps(data))
    response_data = response.json()

    if batch_parameters is not None:
        results = sorted(response_data, key=lambda r: r['id'])
        return [result['result'] for result in results]
    else:
        return response_data['result']


def _build_request_data(
    method=None, parameters=None, batch_methods=None, batch_parameters=None
):

    # assemble payload
    if parameters is not None:
        return {
            'jsonrpc': '2.0',
            'method': method,
            'params': parameters,
            'id': 1,
        }

    elif batch_parameters is not None:

        if method is None and batch_methods is None:
            raise Exception('must specify method or batch_methods')
        if batch_methods is None:
            batch_methods = [method for b in range(len(batch_parameters))]
        ids = range(1, len(batch_parameters) + 1)

        data = []
        for id, method, parameters in zip(ids, batch_methods, batch_parameters):
            datum = {
                'jsonrpc': '2.0',
                'method': method,
                'params': parameters,
                'id': id,
            }
            data.append(datum)

        return data

    else:
        raise Exception('must specify parameters or batch_parameters')


def _get_http_session(provider):

    # ensure sessions are not shared across processes
    pid = os.getpid()
    session_id = (pid, provider)

    if provider not in _http_sessions:
        import requests
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry

        session = requests.Session()

        retry = Retry(connect=10, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        _http_sessions[session_id] = session

    return _http_sessions[session_id]

