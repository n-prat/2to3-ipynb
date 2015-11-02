#!/usr/bin/env python3

# based on IPython-2to3 by @vlad17 (https://github.com/vlad17)
# https://github.com/vlad17/IPython-2to3/blob/master/ipy2to3.py

import logging
import io
import json
import os
import subprocess
import tempfile
import sys
import inspect
import multiprocessing

# global variables
code_cell_name = "" # for compatibility
nb_version = 0 # Notebook version

def is_python_code_cell(cell):
    return cell['cell_type'] == "code"

def is_magic(line):
    line = line.strip()
    if len(line) == 0: return False
    return line[0] in ['%', '!', '?'] or line[-1] == '?'

# Empties magic lines and returns where they were and what they are
# necessery because 2to3 will cause ParseError : bad input on magic lines
def replace_magic_lines(lines):
    magic_lines = []
    for i, line in enumerate(lines):
        if is_magic(line):
            magic_lines.append((i, lines[i]))
            lines[i] = "\n"
    return magic_lines

# convert an ipynb json
def convert_ipynb_json(ipynb_json,path2to3,cmd2to3):
    code_cells = []
    cmd = []
    
    # we filter out everything except code cells
    if nb_version >= 4:
        code_cells = filter(is_python_code_cell, ipynb_json['cells'])
    else:
        for worksheet in ipynb_json['worksheets']: 
            code_cells_temp = filter(is_python_code_cell, worksheet['cells']) 
            for cell in code_cells_temp:
                #print(cell)
                code_cells.append(cell)

    # we loop on the code cells
    for c in code_cells:

        # remove the magic lines
        magic = replace_magic_lines(c[code_cell_name])

        file_name = None
        with tempfile.NamedTemporaryFile(
                    mode = "w", delete = False) as ostream:                    
                ostream.writelines(c[code_cell_name]) 
                file_name = ostream.name   

        # now we can add the filename argument
        # WARNING Python uses names ~ references
        #cmd = cmd2to3
        cmd = cmd2to3.copy()
        cmd.append(file_name)

        logging.debug("cmd ; %s",cmd)

        # we can now call 2to3 on the content
        # do not show the output
        # USE A BLOCKING CALL because already multithreaded above
        p = subprocess.check_call(cmd, stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

        # write back the converted content
        with io.open(file_name, mode = "r") as istream:
                c[code_cell_name] = istream.readlines()

        # put the magic lines back in place
        for i, line in magic:
            c[code_cell_name][i] = line

        # the work is done, remove the temp file
        ostream.close()

    return 0



# TODO refactor to use 1 if/else
def find_2to3():
    path2to3 = ""
    cmd2to3 = []
    found = None
    
    # check if 2to3 is in the PATH
    if sys.platform == "win32":
        try:
            subprocess.check_call("where 2to3.py", stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            found = True
        except subprocess.CalledProcessError as e:
            logging.info(e)
            found = False    
    else:
        # assume non-windows platform can use "which"
        # probably not true
        try:
            subprocess.check_call("which 2to3", stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            found = True
        except subprocess.CalledProcessError as e:
            print(e)
            found = False

    if not(found):
        # 2to3 is NOT in the path, we have to find it
        # start from the python executable directory
        # and assume that stucture : Python35\Tools\scripts

        logging.info("2to3 is not in the PATH")        

        script_path = os.path.dirname(sys.executable)
        script_path = script_path+os.sep+"Tools"+os.sep+"scripts"+os.sep+"2to3.py"
    else:
        # 2to3 is in the path, we just store it
        # 'we already know it won't throw an exception)
        if sys.platform == "win32":
            script_path = subprocess.check_output("where 2to3.py",shell=True)
        else:
            script_path = subprocess.check_output("which 2to3",shell=True)

    if os.path.exists(script_path):        
        path2to3 = script_path
        # now we can contruct the command we will use
        if sys.platform == "win32":
            # on windows, 2to3 is a python script : 2to3.py
            # so we call it from python
            cmd2to3.append("python")
        
        # we can now append the complete path of 2to3
        # we will add the others later
        cmd2to3.append(path2to3)

        # options
        cmd2to3.append("--nobackups")
        cmd2to3.append("--write")
    else:
        logging.error("can not find 2to3 in : %s",script_path)
            
    logging.info("path2to3: %s",path2to3)
    logging.info("cmd2to3: %s",cmd2to3)

    return path2to3,cmd2to3




def cell_name_compatibility(ipy_json):
    global code_cell_name
    global nb_version

    # compatibility between Notebooks v4+ and v3-
    nb_version = ipy_json['nbformat']
    if nb_version == 4:
        code_cell_name = 'source'
    elif nb_version <= 3:
         code_cell_name = 'input'
    else:
        # we can try and suppose it could work
        code_cell_name = 'source'
        logging.warning("WARNING Unsupported Notebook version: %s",nb_version)
        logging.warning("IT MAY NOT WORK")

    logging.info("Notebook version: %s cell: %s",nb_version,code_cell_name)

    return 0




def convert_ipynb_file(file_path,path2to3,cmd2to3):  
    logging.debug("convert_ipynb_file: %s %s %s",file_path,path2to3,cmd2to3)
    ipy_json = None
    #with io.open(argv[1], mode = "rU") as istream:
    with io.open(file_path, mode = "rU") as istream:
        ipy_json = json.load(istream,strict=False)     
               
    # we need to call it here because it is called from convert_all
    # and we could have multiple versions in a given directory
    cell_name_compatibility(ipy_json)

    # now we convert the json file with 2to3
    convert_ipynb_json(ipy_json,path2to3,cmd2to3)

    # and write it back to disk when it is done
    with io.open(file_path, mode = "w") as ostream:
        json.dump(ipy_json, ostream)

    return 0



def convert_py_file(file_path,path2to3,cmd2to3):      
    # simpler with basic py files :

    # Construct the command
    # WARNING : Python uses object names ~ references
    # Do NOT do : cmd = []; cmd = cmd2to3; cmd.append(file_path)
    # IT WOULD APPEND TO CMD2TO3    
    cmd = cmd2to3.copy()
    cmd.append(file_path)

    # Popen requires a string
    str = ' '.join(cmd) 

    # we can now call 2to3 on the content
    # do not show the output
    #subprocess.check_call(cmd, stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    #subprocess.Popen(str,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    # # USE A BLOCKING CALL because already multithreaded above
    subprocess.check_call(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

    return 0


def test_logging_one_arg(file_path):
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.INFO)

    logging.debug("logging test_logging_one_arg debug: %s",file_path)
    logging.info("logging test_logging_one_arg info: %s",file_path)

    print("PRINT test_logging_one_arg",file_path)

    logger.debug("multiprocessing.get_logger gdf")

    return 0