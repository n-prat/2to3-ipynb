#!/usr/bin/env python3

import logging
import os
import argparse
import time
import multiprocessing as mp
from multiprocessing import Pool,cpu_count
#import multiprocessing as mp
from functools import partial

import libs.lib_convert as convert

def main(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument("directory")
    parser.add_argument("--log", dest="logLevel", 
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logging level")

    args = parser.parse_args()
    dir = args.directory

    if( args.logLevel ):
        print("Starting logging with level",args.logLevel)
        logging.basicConfig(level=args.logLevel)
        logger = mp.get_logger()
        logger.setLevel(logging.INFO)
        logger.warning('LOGGING WITH MULTIPROCESSING')

    if not(os.path.exists(dir)):
        logging.error("DIRECTORY %s does not exist",dir)
        exit(1)

    path_2to3,cmd_2to3 = convert.find_2to3()

    ipynb_files = []
    py_files = []

    for subdir, dirs, files in os.walk(dir):
        for file in files:
            filename, file_extension = os.path.splitext(file)
            if file_extension == ".py":
                full_path = os.path.join(subdir, file)
                logging.info("found python file: %s",full_path)

                # The underlying call to 2to3 is made with Popen
                # so it is basically multithreaded
                py_files.append(full_path)
            elif file_extension == ".ipynb":
                full_path = os.path.join(subdir, file)
                logging.info("found IPython notebook: %s",full_path)

                # Instead with store all files for later
                ipynb_files.append(full_path)
            else:
                logging.info("ignoring: %s%s",filename,file_extension)

    # Let's work
    cpu = cpu_count()    
    #cpu = mp.cpu_count()
    logging.info("CPU count : %s",cpu)

    # We have the list of all py files
    # Create a partial to hold the required arguments for convert_py_file
    partial_py = partial(convert.convert_py_file,path2to3=path_2to3,cmd2to3=cmd_2to3)
    logging.debug("pynb files : %s",py_files)

    # We have the list of all ipynb files
    # Create a partial to hold the required arguments for convert_ipynb_file
    partial_ipynb = partial(convert.convert_ipynb_file,path2to3=path_2to3,cmd2to3=cmd_2to3)
    logging.debug("ipynb files : %s",ipynb_files)

    # And then call map
    p = Pool(cpu)     
    p.map(partial_py,py_files)
    p.map(partial_ipynb, ipynb_files)

    # test logging in module
    #convert.test_logging_one_arg("DIRECT CALL")
    #print("MAP :")
    #p.map(convert.test_logging_one_arg,ipynb_files)


    # Benchmark multithread
    '''
    tic = time.clock()
    p.map(convert.convert_ipynb_helper, ipynb_files)
    toc = time.clock()
    t1 = toc-tic

    tic = time.clock()
    for ipy in ipynb_files:
        convert.convert_ipynb_helper(ipy)
    toc = time.clock()
    t2 = toc-tic

    print("SPEED-UP :",t2/t1)
    '''

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
# TODO use a Pool for py files too
# TODO do not convert ipynb checkpoints?
# TODO multiprocessing logging(windows-only issue?)