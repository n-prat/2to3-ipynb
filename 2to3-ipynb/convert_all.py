#!/usr/bin/env python3

import os
import convert_ipynb as ipy
import logging

def main(argv):
    if len(argv) != 2:        
        print("Usage: {} directory".format(argv[0]))                
        return 1

    path2to3,cmd2to3 = ipy.find_2to3()

    for subdir, dirs, files in os.walk(argv[1]):
        for file in files:
            filename, file_extension = os.path.splitext(file)
            if file_extension == ".py":
                full_path = os.path.join(subdir, file)
                print("found python file:",full_path)
                # TODO multithread / Popen
                ipy.convert_py_file(full_path,path2to3,cmd2to3)
            elif file_extension == ".ipynb":
                full_path = os.path.join(subdir, file)
                print("found IPython notebook:",full_path)
                ipy.convert_ipynb_file(full_path,path2to3,cmd2to3)
            else:
                logging.info("ignoring:",filename,file_extension)

    print("\n *************************** \n")
    print("Manual conversions could still be needed")
    print("Check notes README.md")    
    print("\n *************************** \n")

    return 0

if __name__ == "__main__":
    import sys
    main(sys.argv)

# TODO magic lines(notebook v3 issue?)
# TODO check if directory exists