## What does it do?
It converts IPython Notebooks from Python2 to Python3. 
Basically, it is simply calling 2to3 on the code cells of a Notebook.


## How to use?
* 2to3_ipynb in.ipyn out.ipynb


## NOTES
* On windows, if you get errors related to tcl/tk
Copy ...Python35\tcl\tk8.6 and Python35\tcl\tcl8.6 to ...assignment1\.env\Lib

* If you get UnicodeDecodeError when loading with pickle
Replace the *pickle.load line* with *datadict = pickle.load(f, encoding='latin1')*

#### TODO
* test on Linux (and Mac)
* test with IPython 3 Notebooks -> seems to be mostly working
* errors with magic lines
