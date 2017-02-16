# text-exercise

List of files is specified in table format with header (BOM).
* File format - txt;
* Separator of fields - Tab.

Header format:
* Location - File location;
* Destination - Where to place file;
* Md5 - File checksum;
* Patching - Contains string which is appended at the end of file. Optional.

Example: bomA.txt
```
Location	Destination	Md5	Patching
C:/aaa.so	C:/target/SO/aaa.so	2175372653213
C:/bbb.txt	C:/target/TXT/bbb.txt	5309398678165	ENDOFTEXTFILE
C:/ccc.dll	C:/target/DLL/ccc.dll	8974398732625
C:/ddd.so	C:/target/SO/ddd.so	9873955636487
```

Multiple BOMs can be placed in BOM list
Example: master_BOM_list.txt
```
bomA.txt
bomB.txt
bomC.txt
```

## Goal

Write script that is able to read BOMs from BOM lists and parse their content.
Script should then:
* Validate BOM:
    1. Check that files exists. If file is invalid report it and stop.
    2. Validate checksums.
    3. Check that **Location** is unique for all files in BOM.
    4. The same as  above for **Destination**.
* Copy files according to it;
* Patch files, if necessary.

Logging should be possible through CLI option `--logging <path_to_log_file>`

## Result

1. Script;
2. Prepare test BOM files alongside with content.
3. Run script with following scenarios:
    * Good input;
    * Fail validation 1;
    * Fail validation 2;
    * Fail validation 3 & 4;

