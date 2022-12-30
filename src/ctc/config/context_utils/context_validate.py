from __future__ import annotations

from ctc import spec


def _validate_context(context: spec.Context) -> None:
    """validate user-given context specification"""

    if isinstance(context, dict):
        if not set(context.keys()).issubset(spec.context_keys):
            raise Exception(
                'invalid keys for context: '
                + str(set(context.keys()) - set(spec.context_keys))
                + ', valid keys are: '
                + str(set(spec.context_keys))
            )

