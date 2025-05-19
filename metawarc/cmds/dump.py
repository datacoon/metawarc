import os
import csv
from datetime import datetime
import logging
import json
import io
from warcio import ArchiveIterator
from warcio.utils import BUFF_SIZE
from ..base import models
from ..constants import MIME_EXT_MAP

READ_SIZE = BUFF_SIZE * 4

import duckdb



def get_ext_from_content_type(content_type):
    """Returns base extension for content types"""
    if content_type is not None:
        content_type = content_type.split(';', 1)[0]
        if content_type in MIME_EXT_MAP.keys():
            return MIME_EXT_MAP[content_type]
    return 'unknown'

class Dumper:
    """Dumps data files from WARC file"""

    def __init__(self):
        pass

    def listfiles(self, dbfile='warcindex.db', mimes=None, exts=None, query=None, output=None):
        """Lists files in WARC file"""
        from rich.table import Table
        from rich import print
        if not os.path.exists(dbfile):
            print('Plese generate %s database with "metawarc index <filename.warc> command"' % dbfile)
            return

        headers = ['offset', 'url', 'length', 'content_type', 'ext', 'warc_id']
        prep_headers = ','.join(['"' + sub + '"' for sub in headers]) 

        con = duckdb.connect(dbfile)  
        results = None

        if mimes is not None:
            prep_mimes = ','.join(["'" + sub + "'" for sub in mimes.split(',')])
            s = "select %s from records where c_type in (%s)" % (prep_headers, prep_mimes)
            print('Query', s)
            results = con.sql(s).fetchall()
        elif exts is not None:
            prep_exts = ','.join(["'" + sub + "'" for sub in exts.split(',')])
            s = "select %s from records where ext in (%s)" % (prep_headers, prep_exts)
            print('Query', s)
            results = con.sql(s).fetchall()
        elif query is not None:
            s = "select %s from records where %s" % (prep_headers, query)
            results = con.sql(s).fetchall()
        if results is None:
            print('At least one parameter: query, exts or mimes should be provided')
            return 
        outdata = []
        for record in results:
            outdata.append(record)
        if output is None:
            title = 'URL/file list'
            reptable = Table(title=title)
#            reptable.add_column(headers[0], justify="left", style="magenta")
            for key in headers:#[1:-1]:
                reptable.add_column(key, justify="left", style="cyan", no_wrap=False)
#            reptable.add_column(headers[-1], justify="right", style="cyan")
            for row in outdata:
                reptable.add_row(*map(str, row))
            print(reptable)
        else:
            writer = csv.writer(open(output, 'w', encoding='utf8'))
            writer.writerow(headers)
            writer.writerows(outdata)

    def dump(self, dbfile='warcindex.db', mimes=None, exts=None, query=None, output=None):
        """Dump WARC file contents"""
        from rich.table import Table
        from rich import print
        if not os.path.exists(dbfile):
            print('Plese generate %s database with "metawarc index <filename.warc> command"' % dbfile)
            return

        headers = ['offset', 'filename', 'url', 'length', 'content_type', 'ext', 'status_code', 'warc_id', 'source']

        prep_headers = ','.join(['"' + sub + '"' for sub in headers]) 

        con = duckdb.connect(dbfile)  
        results = None
        if mimes is not None:
            prep_mimes = ','.join(["'" + sub + "'" for sub in mimes.split(',')])
            s = "select %s from records where c_type in (%s)" % (prep_headers, prep_mimes)
            print('Query', s)
            results = con.sql(s).fetchall()        
        elif exts is not None:
            prep_exts = ','.join(["'" + sub + "'" for sub in exts.split(',')])
            s = "select %s from records where ext in (%s)" % (prep_headers, prep_exts)
            print('Query', s)
            results = con.sql(s).fetchall()        
        elif query is not None:
            s = "select %s from records where %s" % (prep_headers, query)
            results = con.sql(s).fetchall()
        if results is None:
            print('At least one parameter: query, exts or mimes should be provided')
            return 
        outdata = []
        os.makedirs(output, exist_ok=True)
        opened_files = {}
        for record in results:            
            if record[8] in opened_files.keys():
                fileobj = opened_files[record[8]]
            else:
                fileobj = open(record[8], "rb")
                opened_files[record[8]] = fileobj
            fileobj.seek(record[0])
            it = iter(ArchiveIterator(fileobj))
            warcrec = next(it)
            filename = record[7] + '.' + get_ext_from_content_type(record[4])
            outdata.append(record)            
            out_raw = open(os.path.join(output, filename), 'wb')
            stream = warcrec.content_stream()
            buf = stream.read(READ_SIZE)
            while buf:
                out_raw.write(buf)
                buf = stream.read(READ_SIZE)
            out_raw.close()
            print('Wrote %s, url %s' % (filename, record[2]))
        output_file = os.path.join(output, 'records.csv')
        writer = csv.writer(open(output_file, 'w', encoding='utf8'))
        writer.writerow(headers)
        writer.writerows(outdata)
