# This source code is part of the Biotite package and is distributed
# under the 3-Clause BSD License. Please see 'LICENSE.rst' for further
# information.

__name__ = "biotite.sequence"
__author__ = "Patrick Kunzmann"
__all__ = ["encode_chars", "decode_to_chars"]

cimport cython
cimport numpy as np

import numpy as np


ctypedef np.uint8_t uint8


@cython.boundscheck(False)
@cython.wraparound(False)
def encode_chars(const unsigned char[:] alphabet,
                 const unsigned char[:] symbols):
    """
    Encode an array of symbols into an array of symbol codes.

    Only works for letters.
    """
    cdef int i
    # The last symbol code of the alphabet + 1 is always illegal
    # Since this code cannot occur from symbol encoding
    # it can be later used to check for illegal symbols
    cdef uint8 illegal_code = alphabet.shape[0]
    # An array based map that maps from symbol to code
    # Since the maximum value of a char is 256
    # the size of the map is known at compile time
    cdef uint8 sym_to_code[256]
    # Initially fill the map with the illegal symbol
    # Consequently, the map will later return the illegal symbol
    # when indexed with a character that is not part of the alphabet
    sym_to_code[:] = [illegal_code] * 256
    # Then fill in entries for the symbols of the alphabet
    cdef unsigned char symbol
    for i, symbol in enumerate(alphabet):
        sym_to_code[symbol] = i
    
    # Encode the symbols
    code = np.empty(symbols.shape[0], dtype=np.uint8)
    cdef uint8[:] code_view = code
    cdef uint8 symbol_code
    for i in range(symbols.shape[0]):
        symbol_code = sym_to_code[symbols[i]]
        # Check if the symbols is valid
        if symbol_code == illegal_code:
            illegal_symbol = chr(symbols[i])
            # Local import to avoid circular imports
            from .alphabet import AlphabetError
            raise AlphabetError(f"'{illegal_symbol}' is not in the alphabet")
        code_view[i] = symbol_code

    return code


@cython.boundscheck(False)
@cython.wraparound(False)
def decode_to_chars(const unsigned char[:] alphabet, const uint8[:] code):
    """
    Encode an array of symbol codes into an array of symbols.

    Only works for letters.
    """
    cdef int i
    cdef int alphabet_length = alphabet.shape[0]
    
    symbols = np.empty(code.shape[0], dtype=np.ubyte)
    cdef uint8[:] symbols_view = symbols
    cdef uint8 symbol_code
    for i in range(code.shape[0]):
        symbol_code = code[i]
        if symbol_code >= alphabet_length:
            # Local import to avoid circular imports
            from .alphabet import AlphabetError
            raise AlphabetError(f"'{symbol_code:d}' is not a valid code")
        symbols_view[i] = alphabet[symbol_code]
    return symbols
