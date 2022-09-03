"""
https://eips.ethereum.org/EIPS/eip-712
https://eips.ethereum.org/EIPS/eip-191

TODO:
- handle nested struct types
"""

from __future__ import annotations

import typing

from ctc import spec
from .. import formats
from .. import abis
from .. import hashes
from . import signature_creation
from . import signature_recovery


def eip712_hash(
    struct_data: typing.Mapping[str, typing.Any],
    *,
    struct_type: spec.Eip712StructType,
    domain: typing.Mapping[str, typing.Any],
    output_format: spec.BinaryFormat = 'prefix_hex',
) -> spec.Data:
    """encode structured data message for use with EIP-712"""
    as_bytes = (
        '\x19\x01'.encode()
        + get_domain_separator(domain, 'binary')
        + _hash_struct(struct_data=struct_data, struct_type=struct_type)
    )
    return hashes.keccak(as_bytes, output_format)


def eip712_sign(
    struct_data: typing.Mapping[str, typing.Any],
    *,
    private_key: spec.Data,
    struct_type: spec.Eip712StructType,
    domain: typing.Mapping[str, typing.Any],
) -> tuple[int, int, int]:

    message_hash = eip712_hash(
        struct_data=struct_data,
        struct_type=struct_type,
        domain=domain,
    )

    if domain.get('chain_id') is not None:
        chain_id = domain.get('chain_id')
    elif domain.get('chainId') is not None:
        chain_id = domain.get('chainId')
    else:
        chain_id = None

    return signature_creation.sign_message_hash(
        message_hash=message_hash,
        private_key=private_key,
        chain_id=chain_id,
    )


def eip712_verify(
    signature: spec.Signature,
    *,
    struct_data: typing.Mapping[str, typing.Any],
    struct_type: spec.Eip712StructType,
    domain: typing.Mapping[str, typing.Any],
    public_key: spec.Data | None = None,
    address: spec.Data | None = None,
) -> bool:

    message_hash = eip712_hash(
        struct_data=struct_data,
        struct_type=struct_type,
        domain=domain,
    )

    return signature_recovery.verify_signature(
        signature=signature,
        message_hash=message_hash,
        public_key=public_key,
        address=address,
    )


def _hash_struct(
    struct_data: typing.Mapping[str, typing.Any],
    struct_type: spec.Eip712StructType,
) -> bytes:
    """compute struct hash for use with EIP-712"""
    return hashes.keccak(
        _hash_struct_type(struct_type)
        + _encode_struct_data(struct_data=struct_data, struct_type=struct_type),
        'binary',
    )


def _hash_struct_type(struct_type: spec.Eip712StructType) -> bytes:
    """compute struct type hash for use with EIP-712"""

    struct_fields_str = ','.join(
        type + ' ' + name for name, type in struct_type['fields'].items()
    )
    struct_type_str = struct_type['name'] + '(' + struct_fields_str + ')'
    return hashes.keccak_text(struct_type_str, 'binary')


def _encode_struct_data(
    struct_data: typing.Mapping[str, typing.Any],
    struct_type: spec.Eip712StructType,
) -> bytes:
    """encode struct data for use with EIP-712"""

    all_encoded = bytes()
    for name, type in struct_type['fields'].items():
        item = _encode_datum(value=struct_data[name], type=type)
        all_encoded += item
    return all_encoded


def _encode_datum(value: typing.Any, type: spec.ABIDatatypeStr) -> bytes:
    """encode scalar datum for use with EIP-712"""

    if '[' in type:
        # array
        scalar_type = type[: type.index('[')]
        encoded = bytes()
        for subvalue in value:
            encoded += _encode_datum(subvalue, scalar_type)
        return hashes.keccak(encoded, 'binary')
    elif type == 'bool':
        return abis.encode_types(int(value), 'uint256')
    elif type == 'address':
        return abis.encode_types(formats.convert(value, 'integer'), 'uint160')
    elif type.startswith('int'):
        return abis.encode_types(value, 'int256')
    elif type.startswith('uint'):
        return abis.encode_types(value, 'uint256')
    elif type.startswith('bytes') and type[5:].isdecimal():
        return typing.cast(bytes, value) + b'\x00' * (32 - len(value))
    elif type == 'bytes':
        return hashes.keccak(value, 'binary')
    elif type == 'string':
        return hashes.keccak_text(value, 'binary')
    elif type == 'struct':
        raise NotImplementedError('nested struct encoding')
    else:
        raise Exception('type encoding unknown')


@typing.overload
def get_domain_separator(
    domain: typing.Mapping[str, typing.Any],
    output_format: typing.Literal['binary'],
    *,
    custom_fields: typing.Mapping[str, spec.ABIDatatypeStr] | None = None,
) -> bytes:
    ...


@typing.overload
def get_domain_separator(
    domain: typing.Mapping[str, typing.Any],
    output_format: typing.Literal['prefix_hex', 'raw_hex'],
    *,
    custom_fields: typing.Mapping[str, spec.ABIDatatypeStr] | None = None,
) -> str:
    ...


@typing.overload
def get_domain_separator(
    domain: typing.Mapping[str, typing.Any],
    output_format: typing.Literal['integer'] = 'integer',
    *,
    custom_fields: typing.Mapping[str, spec.ABIDatatypeStr] | None = None,
) -> int:
    ...


def get_domain_separator(
    domain: typing.Mapping[str, typing.Any],
    output_format: spec.BinaryFormat = 'prefix_hex',
    *,
    custom_fields: typing.Mapping[str, spec.ABIDatatypeStr] | None = None,
) -> spec.Data:
    """compute domain separator for use with EIP-712"""

    # template of standard EIP-712 fields
    domain_separator_fields: typing.Mapping[str, spec.ABIDatatypeStr] = {
        'name': 'string',
        'version': 'string',
        'chainId': 'uint256',
        'verifyingContract': 'address',
        'salt': 'bytes32',
    }

    # convert snake case to camel case
    if 'chain_id' in domain and 'chainId' in domain:
        raise Exception('should only specify one of chain_id or chainId')
    if 'verifying_contract' in domain and 'verifyingContract' in domain:
        raise Exception(
            'should only specify one of verifying_contract or verifyingContract'
        )
    if 'chain_id' in domain:
        domain = {
            (k if k != 'chain_id' else 'chainId'): v for k, v in domain.items()
        }
    if 'verifying_contract' in domain:
        domain = {
            (k if k != 'verifying_contract' else 'verifyingContract'): v
            for k, v in domain.items()
        }

    # add in custom fields if present
    if custom_fields is not None:
        domain_separator_fields = dict(domain_separator_fields, **custom_fields)

    # adjust type for whichever domain fields are present
    domain_separator_fields = {
        k: v for k, v in domain_separator_fields.items() if k in domain
    }

    # create domain separator struct type
    domain_separator_type: spec.Eip712StructType = {
        'name': 'EIP712Domain',
        'fields': domain_separator_fields,
    }

    # ensure that no extra fields are present in domain
    for key in domain.keys():
        if key not in domain_separator_fields:
            raise Exception('unrecognized domain_separator field: ' + str(key))

    # compute struct hash of domain
    as_bytes = _hash_struct(
        struct_data=domain,
        struct_type=domain_separator_type,
    )
    return formats.convert(as_bytes, output_format)
