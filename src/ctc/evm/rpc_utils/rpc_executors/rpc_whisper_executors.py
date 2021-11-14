from .. import rpc_backends


def shh_version(provider=None):
    return rpc_backends.rpc_call(
        method='shh_version',
        provider=provider,
        parameters=[],
    )


def shh_post(topics, payload, priority, ttl, provider=None):

    parameters = {
        'topics': topics,
        'payload': payload,
        'priority': priority,
        'ttl': ttl,
    }

    return rpc_backends.rpc_call(
        method='shh_post',
        provider=provider,
        parameters=[parameters],
    )


def shh_new_identity(provider=None):
    return rpc_backends.rpc_call(
        method='shh_newIdentity',
        provider=provider,
        parameters=[],
    )


def shh_has_identity(address, provider=None):
    return rpc_backends.rpc_call(
        method='shh_hasIdentity',
        provider=provider,
        parameters=[address],
    )


def shh_new_group(provider=None):
    return rpc_backends.rpc_call(
        method='shh_newGroup',
        provider=provider,
        parameters=[],
    )


def shh_add_to_group(address, provider=None):
    return rpc_backends.rpc_call(
        method='shh_addToGroup',
        provider=provider,
        parameters=[address],
    )


def shh_new_filter(receiver, topics, provider=None):
    parameters = {
        'to': receiver,
        'topics': topics,
    }
    return rpc_backends.rpc_call(
        method='shh_newFilter',
        provider=provider,
        parameters=[parameters],
    )


def shh_uninstall_filter(filter_id, provider=None):
    return rpc_backends.rpc_call(
        method='shh_uninstallFilter',
        parameters=[filter_id],
        provider=provider,
    )


def shh_get_filter_changes(filter_id, provider=None):
    return rpc_backends.rpc_call(
        method='shh_getFilterChanges',
        parameters=[filter_id],
        provider=provider,
    )


def shh_get_messages(filter_id, provider=None):
    return rpc_backends.rpc_call(
        method='shh_getMessages',
        parameters=[filter_id],
        provider=provider,
    )

