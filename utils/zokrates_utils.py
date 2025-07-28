ZOKRATES_DIRECTORY_PATH = 'zokrates'
SOURCE_DIRECTORY_PATH = 'src'
TEMP_DIRECTORY_PATH = 'temp'
BUILD_DIRECTORY_PATH = 'builds'
KEY_DIRECTORY_PATH = 'keys'
PROOF_DIRECTORY_PATH = 'proofs'
CONTRACT_DIRECTORY_PATH = 'contracts'
ZOKRATES_STDLIB_DIRECTORY_PATH = '/opt/zokrates/stdlib/'

import subprocess
import shlex
import os

def subprocess_run_wrapper(command, byte_input=None, print_stdout=False):
    process = subprocess.run(shlex.split(command), input=byte_input, stdout=subprocess.PIPE)
    stdout_string = process.stdout.decode('UTF-8')
    if print_stdout:
        print(stdout_string)
    # Make sure the returncode is accepted
    assert(process.returncode == 0)
    return stdout_string

def compile_zokrates_script(zokrates_file_name):
    path = {}
    path['zokrates_directory'] = ZOKRATES_DIRECTORY_PATH
    path['source_directory'] = SOURCE_DIRECTORY_PATH
    path['temp_directory'] = TEMP_DIRECTORY_PATH
    path['build_directory'] = BUILD_DIRECTORY_PATH
    path['file_name'] = zokrates_file_name

    zokrates_path_string = '{zokrates_directory}/{source_directory}/{file_name}.zok'.format(**path)
    build_path_string = '{zokrates_directory}/{temp_directory}/{build_directory}/{file_name}/'.format(**path)
    
    os.system('mkdir -p ' + build_path_string)
    zokrates_compile_command = ('zokrates compile '+
        '-s '+ build_path_string +'abi.json '+
        '-o '+ build_path_string +'out '+
        '-r '+ build_path_string +'out.r1cs '+
        '--stdlib-path '+ ZOKRATES_STDLIB_DIRECTORY_PATH + ' '+
        '-i '+ zokrates_path_string)
    stdout_string = subprocess_run_wrapper(zokrates_compile_command)
    circuit_size = int(stdout_string.split(' ')[-1].replace('\n',''))
    return circuit_size