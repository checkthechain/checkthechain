import pytest
import toolcli

from ctc.cli import cli_run


@pytest.mark.parametrize('spec_reference', list(cli_run.command_index.values()))
def test_subcommands_verbose_can_use_single_v(spec_reference):
    command_spec = toolcli.resolve_command_spec(spec_reference)
    for arg in command_spec.get('args', []):
        if arg.get('name') == '--verbose':
            raise Exception(
                'in '
                + str(spec_reference)
                + ' should use both --verbose AND -v for cli args'
            )
