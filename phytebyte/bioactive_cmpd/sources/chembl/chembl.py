import functools
from typing import Callable, Iterator, List

from phytebyte.bioactive_cmpd.sources import BioactiveCompoundSource
from phytebyte.bioactive_cmpd import BioactiveCompound
from .queries import (
    ChemblBioactiveCompoundQuery, ChemblRandomCompoundSmilesQuery)


class ChemblBioactiveCompoundSource(BioactiveCompoundSource):
    def fetch_with_gene_tgts(self,
                             gene_tgts: List[str]) ->\
                                 Iterator[Callable[[], BioactiveCompound]]:
        """
        Fetch `BioactiveCompounds`, with assayed bioactivity,
        that target specific genes.

        `gene_tgts`: List of strings representing genes. Each
        `BioactiveCompound` returned should target one of the genes in the list
        """
        query = ChemblBioactiveCompoundQuery(gene_tgts=gene_tgts)
        return self._fetch_bioactive_compounds(query)

    def fetch_with_compound_names(self, compound_names: List[str]) -> \
            Iterator[Callable[[], BioactiveCompound]]:
        """
        Fetch `BioactiveCompounds` that have names given by `compound_names`.

        `compound_names`: A list of str's representing the `pref_name` of the
        drugs that should be queried.

        Returns: An iterator of partials, each of which, when called, will
        return a BioactiveCompound. This allows multiple processes to
        deserialize in parallel, rather than a single process deserializing.
        """
        query = ChemblBioactiveCompoundQuery(compound_names=compound_names)
        return self._fetch_bioactive_compounds(query)

    def _fetch_bioactive_compounds(self, query) -> \
            Iterator[Callable[[], BioactiveCompound]]:
        executable_query = query.build()
        # Return generator of curried functions, which when called, will
        # deserialize each row into namedtuple (allows caller to multi-process)
        with self.engine.connect() as conn:
            conn.execution_options(stream_results=True)
            iterator = conn.execute(executable_query)
            cnt = 0
            while True:
                chunk = iterator.fetchmany(1000)
                cnt += 1
                if not chunk:
                    break
                for row in chunk:
                    yield functools.partial(query.row_to_bioactive_compound,
                                            row)

    def fetch_random_compounds_exc_smiles(self,
                                          excluded_smiles: List[str],
                                          limit: int) -> Iterator[str]:
        """ Fetch Iterator of SMiLES strs of random compounds, where each
        compound does NOT have its SMiLE string in the `excluded_smiles`
        parameter.

        `excluded_smiles`: List of strings represneting compounds which should
        be excluded from the query.
        `limit`: Number of random `smiles` to fetch.

        Returns: An `Iterator` of str's representing each random compounds'
        SMiLES representation.
        """
        query = ChemblRandomCompoundSmilesQuery(
            limit=limit, excluded_smiles=excluded_smiles)
        executable_query = query.build()
        with self.engine.connect() as conn:
            conn.execution_options(stream_results=True)
            iterator = conn.execute(executable_query)
            cnt = 0
            while True:
                chunk = iterator.fetchmany(1000)
                cnt += 1
                if not chunk:
                    break
                for row in chunk:
                    yield row[0]
