import subprocess

import sys

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


def collect_cli_examples():

    cli_examples = []
    for subcommand, spec_reference in cli_run.command_index.items():
        command_spec = toolcli.resolve_command_spec(spec_reference)
        if command_spec.get('hidden', False):
            continue

        # collect non-hidden examples
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

        # convert examples into raw commands
        for example_str in example_strs:
            command_pieces = [sys.executable, '-m', 'ctc'] + list(subcommand)

            # handle internal quotes
            if '\'' in example_str:
                pieces = example_str.split('\'')
                for head, tail in zip(pieces[::2], pieces[1::2]):
                    command_pieces.extend(head.split(' '))
                    command_pieces.append(tail)
            else:
                command_pieces.extend(example_str.split(' '))

            command_pieces = [
                piece.strip('"') for piece in command_pieces if piece != ''
            ]

            cli_examples.append(command_pieces)

    return cli_examples


cli_examples = collect_cli_examples()


@pytest.mark.parametrize('cli_example', cli_examples)
def test_subcommand_examples(cli_example):

    max_example_time = 30

    exit_code = subprocess.call(cli_example, timeout=max_example_time)
    if exit_code != 0:
        raise Exception(
            'command failed with exit code '
            + str(exit_code)
            + ': '
            + ' '.join(cli_example)
        )
