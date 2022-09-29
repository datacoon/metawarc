import logging

from tabulate import tabulate
from warcio import ArchiveIterator


class Analyzer:
    """WARC files analysis"""

    def __init__(self):
        pass

    def analyze(self, fromfile, mode="mime"):
        """Reads data from WARC file and provides analysis"""
        logging.debug("Preparing %s" % fromfile)
        resp = open(fromfile, "rb")
        total = 0
        mimes = {}
        exts = {}
        n = 0
        for record in ArchiveIterator(resp, arc2warc=False):
            #            logging.debug('Processing record %d' % (n))
            if record.rec_type == "response":
                n += 1
                if n % 10000 == 0:
                    logging.info("Processed %d records" % (n))
                h = record.http_headers.get_header("content-type")
                url = record.rec_headers.get_header("WARC-Target-URI")
                filename = url.rsplit("?", 1)[0].rsplit("/", 1)[-1].lower()
                total += 1
                if mode == "mimes":
                    if h is not None:
                        h = h.split(";", 1)[0]

                    v = mimes.get(h, {"total": 0, "size": 0})
                    v["total"] += 1
                    v["size"] += record.length
                    mimes[h] = v
                elif mode == "exts":
                    if filename.find(".") > -1:
                        ext = filename.rsplit(".", 1)[-1]
                    else:
                        ext = ""
                    v = exts.get(ext, {"total": 0, "size": 0})
                    v["total"] += 1
                    v["size"] += record.length
                    exts[ext] = v

        table = []
        total = ["#total", 0, 0, 100]
        records = mimes if mode == "mimes" else exts
        for fd in sorted(records.items(),
                         key=lambda item: item[1]["size"],
                         reverse=True):
            total[1] += fd[1]["total"]
            total[2] += fd[1]["size"]
        total[3] = 100
        for fd in sorted(records.items(),
                         key=lambda item: item[1]["size"],
                         reverse=True):
            record = [
                fd[0],
                fd[1]["total"],
                fd[1]["size"],
                fd[1]["size"] * 100.0 / total[2],
            ]
            table.append(record)
        table.append(total)

        headers = [mode, "files", "size", "share"]
        print(tabulate(table, headers=headers))
