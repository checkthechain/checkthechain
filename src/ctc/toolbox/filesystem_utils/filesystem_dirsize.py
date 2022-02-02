import subprocess


def get_directory_nbytes(dirpath: str) -> int:
    cmd = 'du -sb ' + dirpath
    cmd_pieces = cmd.split(' ')
    output_bytes = subprocess.check_output(cmd_pieces)
    output = output_bytes.split(b'\t')[0].decode()
    return int(output)


def get_directory_nbytes_human(dirpath: str) -> str:
    cmd = 'du -h ' + dirpath
    cmd_pieces = cmd.split(' ')
    output = subprocess.check_output(cmd_pieces)
    return output.split(b'\t')[0].decode()

