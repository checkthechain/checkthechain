import subprocess

import pytest
import toolcli

from ctc.cli import cli_run


@pytest.mark.parametrize('spec_reference', list(cli_run.command_index.values()))
def test_subcommands_have_spec(spec_reference):
    command_spec = toolcli.resolve_command_spec(spec_reference)
    assert isinstance(command_spec, dict), 'missing command_spec for ' + str(
        spec_reference
    )
    allowed_keys = set(toolcli.CommandSpec.__annotations__.keys())
    actual_keys = set(command_spec.keys())
    assert set(actual_keys).issubset(
        allowed_keys
    ), 'keys not allowed in ' + str(spec_reference)


@pytest.mark.parametrize('spec_reference', list(cli_run.command_index.values()))
def test_subcommands_have_help(spec_reference):
    command_spec = toolcli.resolve_command_spec(spec_reference)
    assert (
        command_spec.get('help') is not None
    ), 'missing help for command for ' + str(spec_reference)
    for arg_spec in command_spec.get('args', []):
        assert (
            arg_spec.get('help') is not None
        ), 'missing help for arg in ' + str(spec_reference)


@pytest.mark.parametrize('spec_reference', list(cli_run.command_index.values()))
def test_subcommands_have_examples(spec_reference):
    command_spec = toolcli.resolve_command_spec(spec_reference)
    assert (
        command_spec.get('examples') is not None
    ), 'missing examples for command for ' + str(spec_reference)


@pytest.mark.parametrize('subcommand_spec', list(cli_run.command_index.items()))
def test_subcommand_examples(subcommand_spec):

    # TODO: make a toolcli function to extract the examples

    subcommand, spec_reference = subcommand_spec
    command_spec = toolcli.resolve_command_spec(spec_reference)

    if command_spec.get('hidden', False):
        return

    # collect examples
    example_strs = []
    examples = command_spec.get('examples', [])
    if isinstance(examples, list):
        example_strs = examples
    elif isinstance(examples, dict):
        for example_str, example_data in examples.items():
            if isinstance(example_data, str):
                example_strs.append(example_str)

            elif isinstance(example_data, dict):

                if (
                    example_data.get('runnable', True)
                    and not example_data.get('long', False)
                    and not example_data.get('skip', False)
                ):
                    example_strs.append(example_str)

    max_example_time = 8

    for example_str in example_strs:
        command_pieces = ['python3', '-m', 'ctc'] + list(subcommand)
        command_pieces.extend(example_str.split(' '))
        command_pieces = [
            piece.strip('"') for piece in command_pieces if piece != ''
        ]
        exit_code = subprocess.call(command_pieces, timeout=max_example_time)
        if exit_code != 0:
            raise Exception(
                'command failed with exit code '
                + str(exit_code)
                + ': '
                + ' '.join(command_pieces)
            )
