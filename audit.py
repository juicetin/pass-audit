from subprocess import check_output, CalledProcessError, run
import os
import pdb
import sys

PASS_PATH='/home/me/.password-store'
MIN_LENGTH=15
exclude=['.git', '.gitattrib', '.gpg-id', '.gp'] # TODO will need to be abstracted out more for custom excludes

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
    all_pass_files = []
    for root, dirs, files in os.walk(path, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude]
        all_pass_files += join_root_with_each_file(root, files)

    return all_pass_files

def extract_pass_from_output(output):
    # TODO this doesn't account for windows line endings
    pw = output.decode('UTF-8').split('\n')[0]
    return pw

def sufficient_length(pw, length):
    return len(pw) >= length

def pass_is_insecure(output):
    pw = extract_pass_from_output(output)
    # TODO run through list of check functions
    return not sufficient_length(pw, MIN_LENGTH)

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
            "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                    "(or 'y' or 'n').\n")

def execute_pass_for_file(cur_file):
    try:
        print('Checking {}...'.format(cur_file)) # 
        output = check_output(['pass', cur_file])
        if pass_is_insecure(output):
            print_insecure_file(cur_file)
            modify_current = query_yes_no('Ready to modify current password? Current one will copy to clipboard. No to skip.', default="no")
            if modify_current is True:
                # TODO only run if flag checked
                # TODO spawn browser with contained url as user has chosen to change pw
                run(['pass', 'update', '-c', '-l', '30', cur_file]) 
                query_yes_no('Ready to continue with file check?', default="no")
            return True
        else:
            return False
        del(output)
    except CalledProcessError:
        print('Calling pass on {} failed.'.format(cur_file))

def print_insecure_summary(insecure_passes):
    print(
        '''
        ############################################
        ######## LIST OF INSECURE PASSWORDS ########
        ############################################
        '''
    )
    for insecure_pass in insecure_passes:
        print(insecure_pass)

    print('############################################')

def print_insecure_file(filename):
    insecure_warning = '''
    #####################################################
    #### {} is insecure!! ####
    #####################################################
    '''.format(filename)
    print(insecure_warning) # TODO show password with flag

def execute_pass_per_file(files):
    insecure = []
    for cur_file in files:
        if execute_pass_for_file(cur_file):
            insecure.append(cur_file)

    f = lambda x: x if x[0] != '/' else x[1:]
    insecure_sorted = sorted(insecure)
    print_insecure_summary(insecure_sorted)
    pdb.set_trace()
    # TODO allow user to save output to file (for later use)


check_pass_exists();
all_pass_files = get_list_of_all_passwords(PASS_PATH)
execute_pass_per_file(all_pass_files)
