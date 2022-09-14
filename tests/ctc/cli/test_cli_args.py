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


@pytest.mark.parametrize('spec_reference', list(cli_run.command_index.values()))
def test_subcommand_options_use_dashes_not_underscores(spec_reference):
    command_spec = toolcli.resolve_command_spec(spec_reference)
    for arg in command_spec.get('args', []):
        name = arg['name']
        if isinstance(name, str):
            name_list = [name]
        else:
            name_list = name

        for subname in name_list:
            if subname.startswith('--') and '_' in subname:
                raise Exception(
                    'error in '
                    + spec_reference
                    + ' cli args should use dashes not underscores'
                )


@pytest.mark.parametrize('spec_reference', list(cli_run.command_index.values()))
def test_subcommands_use_export_instead_of_output(spec_reference):
    command_spec = toolcli.resolve_command_spec(spec_reference)
    problem_commands = []
    for arg in command_spec.get('args', []):
        if arg.get('name') == '--output':
            raise Exception(
                'these commands should use the name --export instead of --output: '
                + str(problem_commands)
            )
