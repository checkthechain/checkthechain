from .. import rpc_constructors
from .. import rpc_digestors
from .. import rpc_request


async def async_shh_version(provider=None):
    request = rpc_constructors.construct_shh_version()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_shh_version(
        response=response,
        provider=provider,
    )


async def async_shh_post(topics, payload, priority, ttl, provider=None):
    request = rpc_constructors.construct_ssh_post(
        topics=topics,
        payload=payload,
        priority=priority,
        ttl=ttl,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_shh_post(
        response=response,
        provider=provider,
    )


async def async_shh_new_identity(provider=None):
    request = rpc_constructors.construct_ssh_new_identity()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_ssh_new_identity(
        response=response,
        provider=provider,
    )


async def async_shh_has_identity(address, provider=None):
    request = rpc_constructors.construct_shh_has_identity(address=address)
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_shh_has_identity(
        response=response,
        provider=provider,
    )


async def async_shh_new_group(provider=None):
    request = rpc_constructors.construct_ssh_new_group()
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_ssh_new_group(
        response=response,
        provider=provider,
    )


async def async_shh_add_to_group(address, provider=None):
    request = rpc_constructors.construct_ssh_add_to_group(address=address)
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_ssh_add_to_group(
        response=response,
        provider=provider,
    )


async def async_shh_new_filter(receiver, topics, provider=None):
    request = rpc_constructors.construct_shh_new_filter(
        receiver=receiver, topics=topics
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_shh_new_filter(
        response=response,
        provider=provider,
    )


async def async_shh_uninstall_filter(filter_id, provider=None):
    request = rpc_constructors.construct_shh_uninstall_filter(
        filter_id=filter_id
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_shh_uninstall_filter(
        response=response,
        provider=provider,
    )


async def async_shh_get_filter_changes(filter_id, provider=None):
    request = rpc_constructors.construct_ssh_get_filter_changes(
        filter_id=filter_id,
    )
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_ssh_get_filter_changes(
        response=response,
        provider=provider,
    )


async def async_shh_get_messages(filter_id, provider=None):
    request = rpc_constructors.construct_ssh_get_messages(filter_id=filter_id)
    response = await rpc_request.async_send(request, provider=provider)
    return rpc_digestors.digest_ssh_get_messages(
        response=response,
        provider=provider,
    )

