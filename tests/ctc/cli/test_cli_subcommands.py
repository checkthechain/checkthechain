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


# @pytest.mark.parametrize('spec_reference', list(cli_run.command_index.values()))
# def test_subcommands_have_examples(spec_reference):
#     command_spec = toolcli.resolve_command_spec(spec_reference)
#     assert (
#         command_spec.get('examples') is not None
#     ), 'missing examples for command for ' + str(spec_reference)
