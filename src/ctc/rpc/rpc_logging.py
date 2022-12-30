from __future__ import annotations

from ctc import spec


_rpc_logger_state = {
    'logger_setup': False,
}


def setup_rpc_logger() -> None:
    import loguru
    from ctc import config

    if not _rpc_logger_state['logger_setup']:

        # get logging path
        rpc_log_path = config.get_rpc_requests_log_path()

        # enqueue makes logging non-blocking for async compatibility
        loguru.logger.remove()
        loguru.logger.add(
            rpc_log_path,
            enqueue=True,
            rotation='10 MB',
            format='{time} {message}',
        )

        _rpc_logger_state['logger_setup'] = True


def log_rpc_request(
    request: spec.RpcRequest, provider: spec.ProviderReference
) -> None:
    try:
        import loguru
    except ImportError:
        import warnings

        warnings.warn(
            'to use logging must install loguru, use `pip install loguru`'
        )
        return

    setup_rpc_logger()

    if isinstance(request, dict):
        loguru.logger.info(
            'request  ' + request['method'] + ' id=' + str(request['id'])
        )
    elif isinstance(request, list):
        entries = '\n'.join(
            '    ' + subrequest['method'] + ' id=' + str(subrequest['id'])
            for subrequest in request
        )
        loguru.logger.info('bulk request\n' + entries)
    else:
        raise Exception('cannot log request, unknown request type')


def log_rpc_response(
    *,
    response: spec.RpcResponse,
    request: spec.RpcRequest,
    provider: spec.ProviderReference,
) -> None:
    import loguru

    setup_rpc_logger()

    if isinstance(request, dict):
        loguru.logger.info(
            'response ' + request['method'] + ' id=' + str(request['id'])
        )
    elif isinstance(request, list):
        entries = '\n'.join(
            '    ' + subrequest['method'] + ' id=' + str(subrequest['id'])
            for subrequest in request
        )
        loguru.logger.info('bulk response\n' + entries)

