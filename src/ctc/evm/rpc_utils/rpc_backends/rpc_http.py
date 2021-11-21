import json
import os

from ctc import config_utils


_http_sessions = {}


def rpc_call_http(*, rpc_request, provider=None):

    if provider is None:
        provider = config_utils.get_config()['export_provider']

    # get session
    session = _get_http_session(provider=provider)

    # perform request
    response = session.post(url=provider, data=json.dumps(rpc_request))
    response_data = response.json()

    if isinstance(rpc_request, (list, tuple)):
        responses_by_id = {r['id']: r['result'] for r in response_data}
        return [responses_by_id[subrequest['id']] for subrequest in rpc_request]
    else:
        return response_data['result']


def _get_http_session(provider):

    # ensure sessions are not shared across processes
    pid = os.getpid()
    session_id = (pid, provider)

    if session_id not in _http_sessions:
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

