import logging

from tabulate import tabulate
from warcio.indexer import Indexer


class WARCIndexer:
    """WARC files indexer"""

    def __init__(self):
        pass

    def doindex(self, fromfile, fields=None, output="index.jsonl"):
        """Indexes WARC file"""
        logging.debug("Reading %s" % fromfile)
        indexer = Indexer(
            fields,
            [
                fromfile,
            ],
            output,
        )
        indexer.process_all()
        logging.debug("Finished processing %s" % fromfile)
