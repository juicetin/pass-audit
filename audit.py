from subprocess import check_output, CalledProcessError
import os
import pdb

PASS_PATH='/home/me/.password-store'

def check_pass_exists():
    try:
        check_output(['pass'])
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            print('It appears pass is not available on your system. You need to install it for this tool to be of any use. Visit https://passwordstore.org for further instructions.')
        raise

def join_root_with_each_file(root, files):
    pass_path_len = len(PASS_PATH) + 1
    return ['{}/{}'.format(root[pass_path_len:], cur_file)[:-4] for cur_file in files]

def get_list_of_all_passwords(path):
    exclude=['.git', '.gitattrib', '.gpg-id'] # TODO will need to be abstracted out more for custom excludes
    all_pass_files = []
    for root, dirs, files in os.walk(path, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude]
        all_pass_files += join_root_with_each_file(root, files)

    return all_pass_files

def extract_pass_from_output(output):
    # TODO this doesn't account for windows line endings
    pw = output.decode('UTF-8').split('\n')[0]
    return pw

def check_for_insecure_pass(output):
    pw = extract_pass_from_output(output)
    return False # TODO

def execute_pass_for_file(cur_file):
    try:
        output = check_output(['pass', cur_file])
        if pass_is_insecure(output):
            pass # TODO 
    except CalledProcessError:
        print('Calling pass on ${} failed.'.format(cur_file))

def execute_pass_per_file(files):
    for cur_file in files:
        execute_pass_for_file(cur_file)


check_pass_exists();
all_pass_files = get_list_of_all_passwords(PASS_PATH)
execute_pass_per_file(all_pass_files)
