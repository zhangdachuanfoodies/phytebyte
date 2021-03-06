from bitarray import bitarray
import numpy as np
from .base import Fingerprinter


class BitstringCacheFingerprinter(Fingerprinter):
    _bitstring_cache = None

    @classmethod
    def set_cache(cls, bitstring_cache):
        cls._bitstring_cache = bitstring_cache

    def fingerprint_and_encode(self, smiles: str, encoding: str):
        cached_bitstring = self._bitstring_cache.get(
            smiles) if self._bitstring_cache else None
        if encoding == 'numpy':
            if cached_bitstring is not None:
                return self.bitstring_to_nparray(cached_bitstring)
            else:
                return self.smiles_to_nparray(smiles)
        elif encoding == 'bitarray':
            if cached_bitstring is not None:
                return self.bitstring_to_bitarray(cached_bitstring)
            else:
                return self.smiles_to_bitarray(smiles)
        else:
            raise NotImplementedError(encoding)

    def smiles_to_bitstring(self, smiles: str):
        return self.nparray_to_bitstring(
            self.smiles_to_nparray(
                smiles))

    @staticmethod
    def nparray_to_bitstring(nparray: np.ndarray):
        if nparray is not None:
            return "".join([str(bit) for bit in list(nparray)])

    @staticmethod
    def bitarray_to_bitstring(bitarr: bitarray):
        if bitarr:
            return bitarr.to01()

    @staticmethod
    def bitstring_to_nparray(bitstring: str):
        if bitstring:
            return np.fromstring(bitstring, dtype='u1') - 48

    @staticmethod
    def bitstring_to_bitarray(bitstring: str):
        if bitstring:
            return bitarray(bitstring)
