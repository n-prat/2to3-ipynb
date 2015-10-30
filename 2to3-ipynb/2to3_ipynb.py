#!/usr/bin/env python3

# based on IPython-2to3 by @vlad17 (https://github.com/vlad17)
# https://github.com/vlad17/IPython-2to3/blob/master/ipy2to3.py

import io
import json
import os
import subprocess
import tempfile
import sys
import inspect

# global variable to store the path of 2to3
path2to3 = ""
cmd2to3 = []
code_cell_name = ""

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

def convert_ipynb(ipynb_file):

    # we filter out everything except code cells := cell_type : "code" 
    code_cells = filter(is_python_code_cell, ipynb_file['cells'])

    # we loop on the code cells
    for c in code_cells:
        #print(cell) #DEBUG
       #code = c['source'] #CHECK        

        # remove the magic lines
        magic = replace_magic_lines(c[code_cell_name])

        #print(code) #DEBUG
        file_name = None
        with tempfile.NamedTemporaryFile(
                    mode = "w", delete = False) as ostream:                    
                ostream.writelines(c[code_cell_name]) 
                file_name = ostream.name   
                #print(file_name) #DEBUG

        # now we can add all the necessary arguments
        # as we work on temp files, no need to backup
        cmd2to3.append("--nobackups")
        cmd2to3.append("--write")
        cmd2to3.append(file_name)

        # we can now call 2to3 on the content
        subprocess.check_call(cmd2to3, stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

        # write back the converted content
        with io.open(file_name, mode = "r") as istream:
                c[code_cell_name] = istream.readlines()

        # put the magic lines back in place
        for i, line in magic:
            c[i] = line

        # the work is done, remove the temp file
        ostream.close()

    return 0

def find_2to3():
    global path2to3
    global cmd2to3
    found = None

    # check if 2to3 is in the PATH
    if sys.platform == "win32":
        try:
            subprocess.check_call("where 2to3",shell=True)
            found = True
        except subprocess.CalledProcessError as e:
            print(e)
            found = False    
    else:
        # assume non-windows platform can use "which"
        # probably not true
        try:
            subprocess.check_call("which 2to3",shell=True)
            found = True
        except subprocess.CalledProcessError as e:
            print(e)
            found = False

    if not(found):
        # 2to3 is NOT in the path, we have to find it
        # start from the python executable directory
        # and assume that stucture : Python35\Tools\scripts

        print("2to3 is not in the PATH...")        

        script_path = os.path.dirname(sys.executable)
        script_path = script_path+os.sep+"Tools"+os.sep+"scripts"+os.sep+"2to3.py"

        # other way to do this
        #script_path = str.split(sys.path[1],"\\")
        #script_path = script_path[:-1]
        #script_path.insert(1,os.sep)
        #script_path.append("Tools")
        #script_path.append("scripts")
        #script_path.append("2to3.py")
        #print("script_path",script_path)
        #print(os.sep)
        #print(os.path.join('',*script_path))
    else:
        # 2to3 is in the path, we just store it
        # 'we already know it won't throw an exception)
        if sys.platform == "win32":
            script_path = subprocess.check_output("where 2to3",shell=True)
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

    else:
        print("can not find 2to3 :",script_path)

    return 0

# TODO take care of line endings (win vs linux)
def main(argv):
    global code_cell_name

    if len(argv) != 3:        
        print("Usage: {} fromfile.ipynb tofile.ipynb".format(argv[0]))        
        return 1

    # we search the path of 2to3 and write it in a global variable
    find_2to3()

    # checks
    print("path2to3:",path2to3)
    print("cmd2to3:",cmd2to3)
    
    ipy_json = None
    with io.open(argv[1], mode = "r") as istream:
        ipy_json = json.load(istream)
        
    # compatibility between Notebooks v4+ and v3-
    nb_version = ipy_json['nbformat']
    if nb_version == 4:
        code_cell_name = 'source'
    elif nb_version <= 3:
         code_cell_name = 'input'
    else:
        # we can try and suppose it could work
        code_cell_name = 'source'
        print("WARNING Unsupported Notebook version:",nb_version)
        print("IT MAY NOT WORK")

    print("Notebook version:",nb_version)

    # now we convert the json file with 2to3
    convert_ipynb(ipy_json)

    # and write it back to disk when it is done
    with io.open(argv[2], mode = "w") as ostream:
        json.dump(ipy_json, ostream)
    return 0

if __name__ == "__main__":
    import sys
    main(sys.argv)