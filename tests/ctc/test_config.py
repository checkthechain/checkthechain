import os
import configparser


def test_tox_legacy_config():
    import toml

    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    path = os.path.join(repo_root, 'pyproject.toml')
    print(path)
    with open(path) as f:
        config = toml.load(f)

    # load current deps
    current_deps = {}
    for dep_str in config['project']['dependencies']:
        if '>=' not in dep_str:
            raise Exception('need min version for dependency: ' + str(dep_str))
        dep_name, version_tail = dep_str.split(' >=')
        min_version, max_version = version_tail.split(', <')
        current_deps[dep_name] = tuple(
            int(number) for number in min_version.split('.')
        )

    # load legacy deps
    legacy_parser = configparser.ConfigParser()
    legacy_parser.read_string(config['tool']['tox']['legacy_tox_ini'])
    legacy_deps_str = legacy_parser.get("testenv:py37-legacy", "deps")
    legacy_deps_strs = legacy_deps_str.split('\n')
    legacy_deps = {}
    for legacy_dep_str in legacy_deps_strs:
        if legacy_dep_str == '':
            continue

        if '==' not in legacy_dep_str:
            continue

        dep_name, version = legacy_dep_str.split('==')
        legacy_deps[dep_name] = tuple(
            int(number) for number in version.split('.')
        )

    # assert that legacy uses the min version number of each dependency
    for dep_name in legacy_deps.keys():
        if dep_name not in current_deps:
            raise Exception(
                dep_name
                + ' in legacy dependencies but not in current dependencies'
            )
        assert current_deps[dep_name] == legacy_deps[dep_name], (
            dep_name
            + ' has different versions in legacy vs current test environments'
        )
    for dep_name in current_deps:
        if dep_name not in legacy_deps:
            raise Exception(
                dep_name
                + ' in current dependencies but not in legacy dependencies'
            )
