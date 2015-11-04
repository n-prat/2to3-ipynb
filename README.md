## What does it do?
Recursively converts every Python and IPython Notebook in a directory to Python 3.  
The conversion is done with *2to3*


## How to use?
**MAKE SURE YOU HAVE A BACKUP**   
**The files will be overridden** 

**convert_all** ***directory***  
(not tested on Linux)  

Will convert every *.py* and *.ipynb* files in *directory* to Python 3   
*directory* can also be a single file   

It should use all your CPU cores.

## NOTES
* If you get *UnicodeDecodeError* when loading with pickle :   
Replace *pickle.load* with *pickle.load(f,encoding='latin1')*  
This is because Python 3 is using unicode.

#### TODO
* test on Linux/Unix
