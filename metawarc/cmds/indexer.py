import os
import sys
from datetime import datetime
import logging
import json
import io
from fastwarc.warc import ArchiveIterator, WarcRecordType
#from warcio import ArchiveIterator
#C:\workspace\public\ruarxive\metawarc\metawarc\cmds\indexer.pyfrom warcio.utils import BUFF_SIZE
import duckdb
import pyarrow as pa
from io import BytesIO
import glob

#from lxml import etree, html
from bs4 import BeautifulSoup

from ..constants import SUPPORTED_FILE_TYPES, IMAGE_FILES, MS_XML_FILES, MIME_SHORT_MAP, ADOBE_FILES, MS_OLE_FILES

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pdfminer.pdfdocument import PDFDocument

# from hachoir.core.i18n import initLocale
from pdfminer.pdfparser import PDFParser

from .extractor import processWarcRecord

BUFF_SIZE = 16384
READ_SIZE = BUFF_SIZE * 4

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


DEFAULT_LINK_ATTRS = ['class', 'id', 'href']


ALL_TABLES = ['records', 'headers','links', 'oledocs', 'ooxmldocs', 'images', 'pdfs']

class Indexer:
    """Indexes WARC file metadata"""

    def __init__(self):
        pass

    def index_content(self, fromfiles, tofile='warcindex.db', tables=['records',]):
        """Generates DuckDB database as WARC index"""
        from rich.progress import track
        from rich import print

#        parser = etree.HTMLParser()  

        
        real_tables = ALL_TABLES.copy() if tables is None or 'all' in tables else tables
        
        for fromfile in fromfiles:
            con = duckdb.connect(tofile)
            tables = [x[0] for x in con.sql('show tables').fetchall()]
            logging.debug("Indexing %s" % fromfile)
            resp = open(fromfile, "rb")  
            iterator = ArchiveIterator(resp, record_types=WarcRecordType.response)
                            
            cdx_filename = fromfile.rsplit('.', 2)[0] + '.cdx'
            records_num = None
            if os.path.exists(cdx_filename):
                records_num = cdx_size_counter(cdx_filename)
                print('CDX file found. Estimated number of WARC records %d' % (records_num))
            else:
                print("No CDX file. Cant measure progress")
            n = 0 
            list_records = []
            list_headers = []
            list_links = []
            list_oledocs = []
            list_ooxmldocs = []        
            list_pdfs = []
            list_images = []

            for record in iterator:
    #            print(dir(record))
#                print(record.record_type)
#                print(record)
#                if record.record_type != "response":
#                    continue

                n += 1      
                if records_num is not None:
                    if n % THRESHOLD == 0: print('Processed %d (%0.2f%%) records' % (n, n*100.0 / records_num))            
                else:
                    if n % THRESHOLD == 0: print('Processed %d records' % (n))
                if record.http_headers is not None:
                    dbrec = {}
                    dbrec['warc_id'] = record.headers["WARC-Record-ID"].rsplit(':', 1)[-1].strip('>')
                    dbrec['url'] = record.headers["WARC-Target-URI"]
                    content_type = record.http_headers["content-type"] if 'content-type' in record.http_headers else None
                    dbrec['content_type'] = content_type
                    charset = None
                    content_type_no_ch = content_type
                    if content_type is not None and content_type.find(';') > -1:
                        content_type_no_ch, charset = content_type.split(';', 1)
                        content_type_no_ch = content_type_no_ch.strip().lower()
                        if charset.find('=') > -1:
                            charset = charset.split('=', 1)[-1].lower().strip()

                    if 'links' in real_tables and content_type_no_ch == 'text/html':
#                        stream = record.content_stream()                                        
                        out_raw = BytesIO()
                        buf = record.reader.read(READ_SIZE)
                        while buf:
                            out_raw.write(buf)
                            buf = record.reader.read(READ_SIZE)
                        try:
                            root = BeautifulSoup(out_raw.getvalue())
#                            root = etree.fromstring(out_raw.getvalue(), parser)  
                            if root is not None:
                                links = root.find_all('a')
                                if links is not None:
                                    for l in links:
                                        lrec = {'warc_id' : dbrec['warc_id'], 'source' : fromfile, 'url' : dbrec['url'], '_text' : l.text}
                                        for att in DEFAULT_LINK_ATTRS:
                                            if att in l.attrs.keys(): lrec[att] = l.attrs[att]
                                        list_links.append(lrec)
                        except KeyboardInterrupt:
                            pass
                        except ValueError:
                            logging.info('Error parsing links from %s' % (dbrec['url']))                    
                            pass


                    filename = dbrec['url'].rsplit("?", 1)[0].rsplit("/", 1)[-1].lower()
                    ext = filename.rsplit(".", 1)[-1]
                    if content_type_no_ch is not None and content_type_no_ch in MIME_SHORT_MAP.keys():
                        if MIME_SHORT_MAP[content_type_no_ch] in MS_OLE_FILES and 'oledocs' in real_tables:
                            list_oledocs.append(processWarcRecord(record, dbrec['url'], filename, mime=content_type_no_ch, source=fromfile))
                        if MIME_SHORT_MAP[content_type_no_ch] in MS_XML_FILES and 'ooxmldocs' in real_tables:
                            list_ooxmldocs.append(processWarcRecord(record, dbrec['url'], filename, mime=content_type_no_ch, source=fromfile))
                        if MIME_SHORT_MAP[content_type_no_ch] in ADOBE_FILES and 'pdfs' in real_tables:
                            list_pdfs.append(processWarcRecord(record, dbrec['url'], filename, mime=content_type_no_ch, source=fromfile))
                        if MIME_SHORT_MAP[content_type_no_ch] in IMAGE_FILES and 'images' in real_tables:
                            list_images.append(processWarcRecord(record, dbrec['url'], filename, mime=content_type_no_ch, source=fromfile))



                    dbrec['c_type'] = content_type_no_ch
                    dbrec['c_type_charset'] = charset
                    dbrec['offset'] = record.stream_pos
                    dbrec['length'] = record.content_length
                    warc_date  = record.headers["WARC-Date"]
                    dbrec['rec_date'] = datetime.strptime(warc_date, "%Y-%m-%dT%H:%M:%S%z")
                    dbrec['content_length'] = int(record.headers["Content-Length"])
                    dbrec['status_code'] = int(record.http_headers.status_code)                
                    dbrec['source'] = fromfile
                    dbrec['filename'] = dbrec['url'].rsplit("?", 1)[0].rsplit("/", 1)[-1].lower() 
                    dbrec['ext'] = dbrec['filename'].rsplit(".", 1)[-1] if dbrec['filename'].find(".") > -1 else ""
                    properties = []
                    if 'records' in real_tables:
                        list_records.append(dbrec)
                    if 'headers' in real_tables:
                        for key, value in dict(record.http_headers).items():
                            properties.append({'key' : key, 'value' : value, 'warc_id' : dbrec['warc_id'], 'source': fromfile})
                        list_headers.extend(properties)        

            resp.close()

            if 'records' in real_tables:
                pa_records = pa.Table.from_pylist(list_records)
                if 'records' not in tables:
                    con.sql("CREATE TABLE records AS SELECT * FROM pa_records")
                else:
                    con.sql("DELETE FROM records where source = '%s'" % (fromfile))
                    con.sql("INSERT INTO records SELECT * FROM pa_records")
            if 'headers' in real_tables:
                pa_headers = pa.Table.from_pylist(list_headers)

                if 'headers' not in tables:
                    con.sql("CREATE TABLE headers AS SELECT * FROM pa_headers")
                else:
                    con.sql("DELETE FROM headers where source = '%s'" % (fromfile))
                    con.sql("INSERT INTO headers SELECT * FROM pa_headers")
            if 'links' in real_tables:
                pa_links = pa.Table.from_pylist(list_links)                    
                if 'links' not in tables:
                    con.sql("CREATE TABLE links AS SELECT * FROM pa_links")
                else:
                    con.sql("DELETE FROM links where source = '%s'" % (fromfile))
                    con.sql("INSERT INTO links SELECT * FROM pa_links")
            if 'ooxmldocs' in real_tables:
                pa_ooxmldocs = pa.Table.from_pylist(list_ooxmldocs)
                if 'ooxmldocs' not in tables:
                    con.sql("CREATE TABLE ooxmldocs AS SELECT * FROM pa_ooxmldocs")
                else:
                    con.sql("DELETE FROM ooxmldocs where source = '%s'" % (fromfile))
                    con.sql("INSERT INTO ooxmldocs SELECT * FROM pa_ooxmldocs")
            if 'oledocs' in real_tables:
                pa_oledocs = pa.Table.from_pylist(list_oledocs)
                if 'oledocs' not in tables:
                    con.sql("CREATE TABLE oledocs AS SELECT * FROM pa_oledocs")
                else:
                    con.sql("DELETE FROM oledocs where source = '%s'" % (fromfile))
                    con.sql("INSERT INTO oledocs SELECT * FROM pa_oledocs")
            if 'pdfs' in real_tables:
                pa_pdfs = pa.Table.from_pylist(list_pdfs)
                if 'pdfs' not in tables:
                    try:
                        con.sql("CREATE TABLE pdfs AS SELECT * FROM pa_pdfs")
                    except: 
                        pass
                else:
                    con.sql("DELETE FROM pdfs where source = '%s'" % (fromfile))
                    con.sql("INSERT INTO pdfs SELECT * FROM pa_pdfs")
            if 'images' in real_tables:
                pa_images = pa.Table.from_pylist(list_images)
                if 'images' not in tables:
                    try:
                        con.sql("CREATE TABLE images AS SELECT * FROM pa_images")
                    except: 
                        pass
                else:
                    con.sql("DELETE FROM images where source = '%s'" % (fromfile))
                    con.sql("INSERT INTO images SELECT * FROM pa_images")


    def calc_stats(self, dbfile='warcindex.db', mode='mime'):
        from rich.table import Table
        from rich import print
        if not os.path.exists(dbfile):
            print(f'Plese generate {dbfile} database with "metawarc index <filename.warc> command"')
            return
        con = duckdb.connect(dbfile)  
       
        if mode == 'mimes':
             results = con.sql("select c_type, SUM(content_length), COUNT(warc_Id) from records group by c_type ")
             title = 'Group by mime type'
             headers = ('mime', 'size', 'size share', 'count')
        elif mode == 'exts':
             results = con.sql("select ext, SUM(content_length), COUNT(warc_Id) from records group by ext ")
             title = 'Group by file extension'
             headers = ('extension', 'size', 'size share', 'count')
  
        reptable = Table(title=title)
        reptable.add_column(headers[0], justify="left", style="magenta")
        for key in headers[1:-1]:
            reptable.add_column(key, justify="left", style="cyan", no_wrap=True)
        reptable.add_column(headers[-1], justify="right", style="cyan")
        total_size = 0
        for row in results.fetchall():
            total_size += row[1]
        for row in results.fetchall():
            result = [row[0], row[1], '%0.2f%%' % (row[1] *100.0 / total_size), row[2]]
            reptable.add_row(*map(str, result))
        print(reptable)

if __name__ == "__main__":
    indexer = Indexer()
    indexer.index_content(sys.argv[1], tables=['records', 'headers', 'links', 'ooxmldocs', 'oledocs', 'pdfs', 'images'])

