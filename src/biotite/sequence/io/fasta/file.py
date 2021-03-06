# This source code is part of the Biotite package and is distributed
# under the 3-Clause BSD License. Please see 'LICENSE.rst' for further
# information.

__name__ = "biotite.sequence.io.fasta"
__author__ = "Patrick Kunzmann"

from ....file import TextFile, InvalidFileError
import textwrap
from collections import OrderedDict
from collections.abc import MutableMapping

__all__ = ["FastaFile"]


class FastaFile(TextFile, MutableMapping):
    """
    This class represents a file in FASTA format.
    
    A FASTA file contains so called *header* lines, beginning with
    ``>``, that describe following sequence.
    The corresponding sequence starts at the line after the header line
    and ends at the next header line or at the end of file.
    The header along with its sequence forms an entry.
    
    This class is used in a dictionary like manner, implementing the
    :class:`MutableMapping` interface:
    Headers (without the leading ``>``) are used as keys,
    and strings containing the sequences are the corresponding values.
    Entries can be accessed using indexing,
    ``del`` deletes the entry at the given index.

    Parameters
    ----------
    chars_per_line : int, optional
        The number characters in a line containing sequence data
        after which a line break is inserted.
        Only relevant, when adding sequences to a file.
        Default is 80.
    
    Examples
    --------
    
    >>> import os.path
    >>> file = FastaFile()
    >>> file["seq1"] = "ATACT"
    >>> print(file["seq1"])
    ATACT
    >>> file["seq2"] = "AAAATT"
    >>> print(file)
    >seq1
    ATACT
    >seq2
    AAAATT
    >>> print(dict(file.items()))
    {'seq1': 'ATACT', 'seq2': 'AAAATT'}
    >>> for header, seq in file.items():
    ...     print(header, seq)
    seq1 ATACT
    seq2 AAAATT
    >>> del file["seq1"]
    >>> print(dict(file.items()))
    {'seq2': 'AAAATT'}
    >>> file.write(os.path.join(path_to_directory, "test.fasta"))
    """
    
    def __init__(self, chars_per_line=80):
        super().__init__()
        self._chars_per_line = chars_per_line
        self._entries = OrderedDict()
    
    def read(self, file):
        super().read(file)
        # Filter out empty and comment lines
        self.lines = [line for line in self.lines
                      if len(line.strip()) != 0 and line[0] != ";"]
        if len(self.lines) == 0:
            raise InvalidFileError("File is empty or contains only comments")
        self._find_entries()
        
    def __setitem__(self, header, seq_str):
        if not isinstance(header, str):
            raise IndexError(
                "'FastaFile' only supports header strings as keys"
            )
        if not isinstance(seq_str, str):
            raise TypeError("'FastaFile' only supports sequence strings "
                             "as values")
        # Delete lines of entry corresponding to the header,
        # if existing
        if header in self:
            del self[header]
        # Append header line
        self.lines += [">" + header.replace("\n","").strip()]
        # Append new lines with sequence string (with line breaks)
        self.lines += textwrap.wrap(seq_str, width=self._chars_per_line)
        self._find_entries()
    
    def __getitem__(self, header):
        if not isinstance(header, str):
            raise IndexError(
                "'FastaFile' only supports header strings as keys"
            )
        start, stop = self._entries[header]
        # Concatenate sequence string from following lines
        seq_string = "".join(
            [line.strip() for line in self.lines[start+1 : stop]]
        )
        return seq_string
    
    def __delitem__(self, header):
        start, stop = self._entries[header]
        del self.lines[start:stop]
        del self._entries[header]
        self._find_entries()
    
    def __len__(self):
        return len(self._entries)
    
    def __iter__(self):
        return self._entries.__iter__()
    
    def __contains__(self, identifer):
        return identifer in self._entries
    
    def _find_entries(self):
        if len(self.lines) > 0 and self.lines[0][0] != ">":
            raise InvalidFileError(
                f"File starts with '{self.lines[0][0]}' instead of '>'"
            )
        
        header_i = []
        for i, line in enumerate(self.lines):
            if line[0] == ">":
                header_i.append(i)
        
        self._entries = OrderedDict()
        for j in range(len(header_i)):
            # Remove leading '>' from header
            header = self.lines[header_i[j]].strip()[1:]
            start = header_i[j]
            if j < len(header_i) -1:
                # Header in mid or start of file
                # -> stop is start of next header
                stop = header_i[j+1]
            else:
                # Last header -> entry stops at end of file
                stop = len(self.lines)
            self._entries[header] = (start, stop)
    