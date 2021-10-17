import subprocess


def get_directory_nbytes(dirpath):
    cmd = 'du -sh ' + dirpath
    cmd = cmd.split(' ')
    output = subprocess.check_output(cmd)
    return output.split(b'\t')[0].decode()

