#!/usr/bin/env python3

import os
import convert_ipynb as ipy

def main(argv):
    print(len(argv),argv) # DEBUG

    if len(argv) != 2:        
        print("Usage: {} directory".format(argv[0]))                
        return 1
    else:
        print("args ok") #DEBUG

    for subdir, dirs, files in os.walk(argv[1]):
        for file in files:
            filename, file_extension = os.path.splitext(file)
            if file_extension == ".py":
                full_path = os.path.join(subdir, file)
                print("found python file:",full_path)
                ipy.convert_py_file(full_path)
            elif file_extension == ".ipynb":
                full_path = os.path.join(subdir, file)
                print("found IPython notebook:",full_path)
                ipy.convert_ipynb_file(full_path)
            else:
                print("ignoring:",filename,file_extension)

    return 0

if __name__ == "__main__":
    import sys
    main(sys.argv)