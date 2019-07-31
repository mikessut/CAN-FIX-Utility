==================================
Firmware File Format Specification
==================================

This chapter describes the file format that the CFUtil firmware loading
utilities use for describing the information and the mechanism for downloading
a particular file to a node.

Overall Description
-------------------

The firmware file is simply an archive of at least two files.  The archive
should be a compressed tarball file.  The compression algorithm should be
Gzip.  The file can easily be made with the following command.


``tar zcvf firmware.tar.gz dirname``

This archive should contain at least two files.  The first is a file named
*index.json* which is a JSON file that contains all of the information as to
which files are contained in the archive and how they are to be loaded.  At
least one file should be included that represents the firmware data to be
downloaded into the node.

A typical *index.json* might look like this.

::

  {
    "name": "Johnny's EFIS Firmware",
    "vcode": "0x1234",                 # Verification Code
    "files": [                         # List of files
      {
        "name": "firmware.bin",        # File's Name
        "type": "binhex4",             # Type of Encoding
        "offset": "0x00000000",        # First block address represented
        "block type": 0,               # Corresponds to basic protocol block type
        "subsystem": 0,                # Corresponds to basic protocol subsystem
        "blocksize": 64                # Corresponds to basic protocol blocksize
      },
      {
        "name": "firmware.hex",
        "type": "intelhex",
        "offset": 0,
        "block type": 1,
        "subsystem": 0,
        "blocksize": 64
      }
    ]
  }


The *index.json* file contains overall information such as a descriptive name
for the firmware archive and the Verification Code that should be used when the
CAN-FiX host initiates the transfer with the individual node.  The Verification
Code is used to make sure that we don't try to download firmware to a device for
which it was not intended.

The index also contains the information about each firmware file in the archive.  At a minimum
each object in the files list should contain the name of the file within the archive
and the encoding type.  Possible encodings are...

  *  intelhex
  *  uuencode
  *  binhex4
  *  binary
  *  hex

*intelhex*, *uuencode* and *binhex4* are simply files of the given type.  The
*binary* type file is simply a file that contains the bytes directly with no
formatting at all.  The *hex* encoding is an unformatted file that contains an
ASCII hex representation of each byte.  A *hex* file would be exactly twice the
size of the same *binary* file since each byte would be converted into two
characters.

The only file encoding that contains addressing information is the *intelhex*
format. For all the other encodings it is assumed that the first byte in the
file corresponds to address 0x00000000 in the target node.  If *offset* is
given then it will be added to the address contained in the file.

The remainder of the information contained in each file object is protocol
specific. The example shows information that is needed for the Basic CAN-FiX
Firmware Protocol. Other protocols may have different information.  See the
individual protocol definitions for information that is required for each.
