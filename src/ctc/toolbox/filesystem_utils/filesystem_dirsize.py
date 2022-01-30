import subprocess


def get_directory_nbytes(dirpath: str) -> int:
    cmd = 'du -sb ' + dirpath
    cmd = cmd.split(' ')
    output = subprocess.check_output(cmd)
    output = output.split(b'\t')[0].decode()
    return int(output)


def get_directory_nbytes_human(dirpath: str) -> str:
    cmd = 'du -h ' + dirpath
    cmd = cmd.split(' ')
    output = subprocess.check_output(cmd)
    return output.split(b'\t')[0].decode()

