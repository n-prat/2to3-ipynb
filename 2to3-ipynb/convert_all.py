#!/usr/bin/env python3

import os
import lib_convert as convert
import logging
import argparse

def main(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument("directory")
    parser.add_argument("--log", dest="logLevel", 
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logging level")

    args = parser.parse_args()
    dir = args.directory

    if( args.logLevel ):
        logging.basicConfig(level=getattr(logging, args.logLevel))

    if not(os.path.exists(dir)):
        logging.error("DIRECTORY %s does not exist",dir)
        exit(1)

    path2to3,cmd2to3 = convert.find_2to3()

    for subdir, dirs, files in os.walk(dir):
        for file in files:
            filename, file_extension = os.path.splitext(file)
            if file_extension == ".py":
                full_path = os.path.join(subdir, file)
                logging.info("found python file: %s",full_path)
                # TODO multithread / Popen
                convert.convert_py_file(full_path,path2to3,cmd2to3)
            elif file_extension == ".ipynb":
                full_path = os.path.join(subdir, file)
                logging.info("found IPython notebook: %s",full_path)
                convert.convert_ipynb_file(full_path,path2to3,cmd2to3)
            else:
                logging.info("ignoring: %s%s",filename,file_extension)

    print("\n *************************** \n")
    print(" Manual conversions could still be needed")
    print(" Check notes in README.md")    
    print("\n *************************** \n")

    return 0

if __name__ == "__main__":
    import sys
    main(sys.argv)

# TODO magic lines(notebook v3 issue?)
# TODO multithread convert_ipynb_json
## - can't use Popen there because we have to wait 2to3 to complete