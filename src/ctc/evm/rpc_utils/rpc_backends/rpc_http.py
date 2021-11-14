import json
import os

from ctc import config_utils
from .. import rpc_crud


_http_sessions = {}


def rpc_call_http(
    *,
    rpc_data=None,
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
    if rpc_data is None:
        rpc_data = rpc_crud.construct_rpc_data(
            method=method,
            parameters=parameters,
            batch_methods=batch_methods,
            batch_parameters=batch_parameters,
        )

    # perform request
    response = session.post(url=provider, data=json.dumps(rpc_data))
    response_data = response.json()

    if batch_parameters is not None:
        results = sorted(response_data, key=lambda r: r['id'])
        return [result['result'] for result in results]
    else:
        return response_data['result']


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

