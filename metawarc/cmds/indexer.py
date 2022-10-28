import os
from datetime import datetime
import logging
import json
import io
from warcio import ArchiveIterator
from warcio.utils import BUFF_SIZE
from ..base import models


READ_SIZE = BUFF_SIZE * 4

from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session

THRESHOLD = 250

def bufcount(filename):
    """Count number of lines"""
    f = open(filename)                  
    lines = 0
    buf_size = 1024 * 1024
    read_f = f.read # loop optimization

    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)
    f.close() 
    return lines

def cdx_size_counter(filename):
    return bufcount(filename) - 1


class Indexer:
    """Indexes WARC file metadata"""

    def __init__(self):
        pass

    def index_content(self, fromfile):
        """Generates SQLite database as WARC index"""
        from rich.progress import track
        from rich import print

        engine = create_engine("sqlite:///metawarc.db", echo=False)
        models.Base.metadata.create_all(engine)
        logging.debug("Indexing %s" % fromfile)
        resp = open(fromfile, "rb")
        iterator = ArchiveIterator(resp, arc2warc=True)
        session = Session(engine)
        cdx_filename = fromfile.rsplit('.', 2)[0] + '.cdx'
        records_num = None
        if os.path.exists(cdx_filename):
            records_num = cdx_size_counter(cdx_filename)
            print('CDX file found. Estimated number of WARC records %d' % (records_num))
        else:
            print("No CDX file. Cant measure progress")
        n = 0 
        for record in iterator:
            if record.rec_type != "response":
                continue
            n += 1      
            if records_num is not None:
                if n % THRESHOLD == 0: print('Processed %d (%0.2f%%) records' % (n, n*100.0 / records_num))            
            else:
                if n % THRESHOLD == 0: print('Processed %d records' % (n))
            if record.http_headers is not None:
                dbrec = models.Record()
                dbrec.warc_id = record.rec_headers.get_header("WARC-Record-ID").rsplit(':', 1)[-1].strip('>')
                content_type = record.http_headers.get_header("content-type")                
                dbrec.content_type = content_type
                dbrec.offset = iterator.get_record_offset()
                dbrec.length = iterator.get_record_length()
                dbrec.url = record.rec_headers.get_header("WARC-Target-URI")
                warc_date  = record.rec_headers.get_header("WARC-Date")
                dbrec.rec_date = datetime.strptime(warc_date, "%Y-%m-%dT%H:%M:%S%z")
                dbrec.content_length = int(record.rec_headers.get_header("Content-Length"))
                dbrec.status_code = int(record.http_headers.get_statuscode())
                dbrec.headers = json.dumps(dict(record.http_headers.headers))
                dbrec.source = fromfile
                dbrec.filename = dbrec.url.rsplit("?", 1)[0].rsplit("/", 1)[-1].lower() 
                dbrec.ext = dbrec.filename.rsplit(".", 1)[-1] if dbrec.filename.find(".") > -1 else ""
                session.add(dbrec)
                session.commit()
        resp.close()

    def calc_stats(self, mode='mime'):
        from rich.table import Table
        from rich import print
        if not os.path.exists('metawarc.db'):
            print('Plese generate metawarc.db database with "metawarc index <filename.warc> command"')
            return
        engine = create_engine("sqlite:///metawarc.db", echo=False)
        session = Session(engine)
        if mode == 'mimes':
             results = session.query(models.Record.content_type, func.sum(models.Record.content_length), func.count(models.Record.warc_id)).group_by(models.Record.content_type).all()        
             title = 'Group by mime type'
             headers = ('mime', 'size', 'count')
        elif mode == 'exts':
             results = session.query(models.Record.ext, func.sum(models.Record.content_length), func.count(models.Record.warc_id)).group_by(models.Record.ext).all()        
             title = 'Group by file extension'
             headers = ('extension', 'size', 'count')
  
        reptable = Table(title=title)
        reptable.add_column(headers[0], justify="left", style="magenta")
        for key in headers[1:-1]:
            reptable.add_column(key, justify="left", style="cyan", no_wrap=True)
        reptable.add_column(headers[-1], justify="right", style="cyan")
        for row in results:
            reptable.add_row(*map(str, row))
        print(reptable)
