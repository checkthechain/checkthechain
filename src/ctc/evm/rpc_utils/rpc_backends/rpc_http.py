import json
import os



_http_sessions = {}


def rpc_call_http(method, parameters, provider=None, decode_result=True):

    # assemble payload
    data = {
        'jsonrpc': '2.0',
        'method': method,
        'params': parameters,
        'id': 1,
    }

    # get session
    session = _get_http_session(provider=provider)

    # perform request
    response = session.post(url=provider, data=json.dumps(data))
    response_data = response.json()
    result = response_data['result']

    return result


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

