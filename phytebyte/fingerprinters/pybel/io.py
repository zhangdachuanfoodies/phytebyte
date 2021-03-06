import logging
import pybel


class SmilesDeserializationError(Exception):
    pass


class PybelDeserializer():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    def smiles_to_molecule(self, smiles: str):
        try:
            mol = pybel.readstring("smi", smiles)
        except Exception as e:
            self.logger.error(e)
            return None
        return mol
