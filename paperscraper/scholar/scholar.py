import logging
import sys
from typing import List

import pandas as pd
from scholarly import scholarly

from ..citations.citations import get_citations_from_title  # noqa
from ..utils import dump_papers

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


scholar_field_mapper = {
    "venue": "journal",
    "author": "authors",
    "cites": "citations",
    "pub_year": "year",
}
process_fields = {"year": lambda x: int(x) if x.isdigit() else -1, "citations": int}


def get_scholar_papers(
    title: str,
    fields: List = ["title", "authors", "year", "abstract", "journal", "citations"],
    *args,
    **kwargs,
) -> pd.DataFrame:
    """
    Performs Google Scholar API request of a given query and returns list of papers with
    fields as desired.

    Args:
        query (str): Query to arxiv API. Needs to match the arxiv API notation.
        fields (list[str]): List of strings with fields to keep in output.

    Returns:
        pd.DataFrame. One paper per row.

    """
    logger.info(
        "NOTE: Scholar API cannot be used with Boolean logic in keywords."
        "Query should be a single string to be entered in the Scholar search field."
    )
    if not isinstance(title, str):
        raise TypeError(f"Pass str not {type(title)}")

    matches = scholarly.search_pubs(title)

    processed = []
    for paper in matches:
        # Extracts title, author, year, journal, abstract
        entry = {
            scholar_field_mapper.get(key, key): process_fields.get(
                scholar_field_mapper.get(key, key), lambda x: x
            )(value)
            for key, value in paper["bib"].items()
            if scholar_field_mapper.get(key, key) in fields
        }

        entry["citations"] = paper["num_citations"]
        processed.append(entry)

    return pd.DataFrame(processed)


def get_and_dump_scholar_papers(
    title: str,
    output_filepath: str,
    fields: List = ["title", "authors", "year", "abstract", "journal", "citations"],
) -> None:
    """
    Combines get_scholar_papers and dump_papers.

    Args:
        keywords (List[str, List[str]]): List of keywords to request arxiv API.
            The outer list level will be considered as AND separated keys, the
            inner level as OR separated.
        filepath (str): Path where the dump will be saved.
        fields (List, optional): List of strings with fields to keep in output.
            Defaults to ['title', 'authors', 'date', 'abstract',
            'journal', 'doi'].
    """
    papers = get_scholar_papers(title, fields)
    dump_papers(papers, output_filepath)
