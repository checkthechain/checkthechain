from __future__ import annotations

import os
import re
import tempfile

import pytest

import ctc


def get_readme_examples():

    path = get_readme_path()
    if not os.path.exists(path):
        return {'python': [], 'bash': []}

    else:

        with open(get_readme_path(), 'r') as f:
            content = f.read()

        return {
            'python': re.findall('```python\n(.+?)```\n', content, re.DOTALL),
            'bash': re.findall('```bash\n(.+?)```\n', content, re.DOTALL),
        }


def get_readme_path():
    root_dir = os.path.dirname(os.path.dirname(ctc.__path__[0]))
    return os.path.join(root_dir, 'README.md')


readme_examples = get_readme_examples()


@pytest.mark.parametrize('example', readme_examples['python'])
async def test_readme_python_examples(example):
    example_lines = example.split('\n')
    code = 'async def f_example():\n' + '    ' + '\n    '.join(example_lines)
    exec(code)
    await locals()['f_example']()


@pytest.mark.parametrize('example', readme_examples['bash'])
async def test_readme_bash_examples(example):
    tempdir = tempfile.mkdtemp()
    os.chdir(tempdir)

    script = '#!/bin/bash\n\nset -e\n\n' + example
    with open('script.sh', 'w') as f:
        f.write(script)

    import subprocess
    subprocess.check_call('bash script.sh', shell=True)
