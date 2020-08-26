## WSM Extract (wsme). A tool to extract the various sections of a WSM file.

Will extract sections from a Worms World Party Aqua WSM file. Can be passed files or folders. Folders will have it process any WSM files in the immediate directory (non recursive).

usage: wsme.py [-h] [-e [SECTION[,SECTION ...]]] [-o [OUTPUT_DIR]] [-f] File_or_Folder [File_or_Folder ...]

positional arguments:  
One or more files or folders (non recursive) to process

optional arguments:
* `-h` or `--help`  
  show this help message and exit
* `-e [SECTION[,SECTION ...]]` or `--extract [SECTION[,SECTION ...]]`  
  A comma separated list of sections (FourCC) to extract. Defaults to all sections. Valid sections: VERS,GUID,INST,WAM,IMG (NOTE: the "IMG " section is actually a land.dat file. Not an img file)
* `-o [OUTPUT_DIR]` or `--output [OUTPUT_DIR]`  
  Output directory for extracted parts' subfolders. Defaults to the same folder as the input folder.
* `-f` or `--force-overwrite`  
  Allow overwriting files.
