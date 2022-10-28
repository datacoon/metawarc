import logging
import json
import io
from warcio import ArchiveIterator
from warcio.indexer import Indexer
from warcio.utils import BUFF_SIZE

READ_SIZE = BUFF_SIZE * 4

def get_content(record):
    out = io.BytesIO()
    stream = record.content_stream()
    buf = stream.read()
    while buf:
        out.write(buf)
        buf = stream.read(READ_SIZE)    
    return out.getvalue()


class Exporter:
    """Export data from WARC files"""

    def __init__(self):
        pass

    def headers_export(self, fromfile, output="headers.jsonl"):
        """Reads and exports all record headers"""
        if output is None:
            output = "headers.jsonl"
        logging.debug("Preparing %s" % fromfile)
        resp = open(fromfile, "rb")
        out = open(output, "w", encoding="utf8")
        iterator = ArchiveIterator(resp, arc2warc=True)
        for record in iterator:
            if record.rec_type != "response":
                continue
            if record.http_headers is not None:
                r = {
                    "content-type":
                    record.http_headers.get_header("content-type"),
                    "offset" : iterator.get_record_offset(),
                    "length" : iterator.get_record_length(),
                    "url": record.rec_headers.get_header("WARC-Target-URI"),
                    "status" : record.http_headers.get_statuscode()
                }
                headers = dict(record.http_headers.headers)
                r["http_headers"] = headers
                out.write(json.dumps(r, ensure_ascii=False) + "\n")
        out.close()
        resp.close()

    def warcio_indexer_export(self, fromfile, fields=None, output="index.jsonl"):
        """Exports WarcIO index"""
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


    def content_export(self, fromfile, output="content.jsonl", content_types = ['text/html']):
        """Exports HTML content"""
        logging.debug("Re %s" % fromfile)
        if output is None:
            output = "content.jsonl"
        logging.debug("Preparing %s" % fromfile)
        resp = open(fromfile, "rb")
        out = open(output, "w", encoding="utf8")
        iterator = ArchiveIterator(resp, arc2warc=True)
        n = 0
        for record in iterator:
            if record.rec_type != "response":
                continue
            if record.http_headers is not None:
                content_type = record.http_headers.get_header("content-type")
                if content_type is not None:
                    content_type = content_type.split(';', 1)[0]
                if content_type not in content_types:
                    continue
                n += 1
                content = get_content(record).decode('utf8')
                r = {
                    "id" : n,
                    "url": record.rec_headers.get_header("WARC-Target-URI"),
                    "content" : content
                }
                    
                out.write(json.dumps(r, ensure_ascii=False) + "\n")
        out.close()
        resp.close()
        logging.debug("Finished processing %s" % fromfile)


