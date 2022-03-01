from __future__ import annotations

import os
import shutil

from . import fourbyte_spec
from . import io_utils
from . import scrape_utils


def local_function_signatures_exist() -> bool:
    path = fourbyte_spec.get_default_path('function_signatures')
    return os.path.isfile(path)


def local_event_signatures_exist() -> bool:
    path = fourbyte_spec.get_default_path('event_signatures')
    return os.path.isfile(path)


async def async_build_function_signatures_dataset() -> list[
    fourbyte_spec.Entry
]:

    path = fourbyte_spec.get_default_path('function_signatures')

    # get current signatures and max_id
    if os.path.isfile(path):
        old_signatures = io_utils.load_function_signatures()
        max_id = max(signature['id'] for signature in old_signatures)
    else:
        old_signatures = []
        max_id = None

    # gather new signatures
    new_signatures = await scrape_utils.async_scrape_function_signatures(
        min_id=max_id,
    )

    # write to file
    temp_path = path + '__new.json'
    old_path = path + '__old.json'
    signatures = old_signatures + new_signatures
    print('saving to', path)
    signatures = io_utils.save_function_signatures(
        signatures=signatures,
        path=temp_path,
        verbose=False,
    )
    if os.path.isfile(path):
        shutil.move(path, old_path)
    shutil.move(temp_path, path)
    if os.path.isfile(old_path):
        os.remove(old_path)
    print('dataset built with', len(signatures), 'signatures')

    return signatures


async def async_build_event_signatures_dataset() -> list[fourbyte_spec.Entry]:

    path = fourbyte_spec.get_default_path('event_signatures')

    # get current signatures and max_id
    if os.path.isfile(path):
        old_signatures = io_utils.load_event_signatures()
        max_id = max(signature['id'] for signature in old_signatures)
    else:
        old_signatures = []
        max_id = None

    # gather new signatures
    new_signatures = await scrape_utils.async_scrape_event_signatures(
        min_id=max_id,
    )

    # write to file
    temp_path = path + '__new.json'
    old_path = path + '__old.json'
    signatures = old_signatures + new_signatures
    print('saving to', path)
    signatures = io_utils.save_event_signatures(
        signatures=signatures,
        path=temp_path,
        verbose=False,
    )
    if os.path.isfile(path):
        shutil.move(path, old_path)
    shutil.move(temp_path, path)
    if os.path.isfile(old_path):
        os.remove(old_path)
    print('dataset built with', len(signatures), 'signatures')

    return signatures

