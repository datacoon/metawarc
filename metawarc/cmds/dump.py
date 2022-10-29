import os
import csv
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


# Common mime types to extension mappings
# Source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types

MIME_EXT_MAP = {
'application/atom+xml' : 'xml',
'application/epub+zip' : 'epub',
'application/gzip' : 'gz',
'application/java-archive' : 'jar',
'application/javascript' : 'js',
'application/json' : 'json',
'application/ld+json' : 'jsonld',
'application/msword' : 'doc',
'application/octet-stream' : 'bin',
'application/pdf' : 'pdf',
'application/rar' : 'rar',
'application/rss+xml' : 'xml',
'application/rtf' : 'rtf',
'application/vnd.android.package-archive' : 'apk',
'application/vnd.ms-excel' : 'xls',
'application/vnd.ms-fontobject' : 'eot',
'application/vnd.oasis.opendocument.presentation' : 'ogp',
'application/vnd.oasis.opendocument.spreadsheet' : 'ods',
'application/vnd.oasis.opendocument.text' : 'odt',
'application/vnd.rar' : 'rar',
'application/vnd.visio' : 'vsd',
'application/x-font-woff' : 'woff',
'application/x-7z-compressed' : '7z',
'application/x-bzip' : 'bz',
'application/x-bzip2' : 'bz2',
'application/x-font-ttf' : 'ttf',
'application/x-javascript' : 'js',
'application/x-tar' : 'tar',
'application/x-x509-ca-cert' : 'crt',
'application/x-zip-compressed' : 'zip',
'application/xml' : 'xml',
'application/zip' : 'zip',

'audio/mp3' : 'mp3',
'audio/mpeg' : 'mp3',
'audio/ogg' : 'ogg',
'audio/x-wav' : 'wav',
'audio/wav' : 'wav',
'audio/webm' : 'weba',

'font/otf' : 'otf',
'font/ttf' : 'ttf',
'font/woff' : 'woff',
'font/woff2' : 'woff2',

'image/bmp' : 'bmp',
'image/gif' : 'gif',
'image/jpeg' : 'jpg',
'image/png' : 'png',
'image/svg+xml' : 'svg',
'image/tiff' : 'tif',
'image/webp' : 'webp',
'image/x-icon' : 'ico',

'text/calendar' : 'ics',
'text/css' : 'css',
'text/csv' : 'csv',
'text/html' : 'html',
'text/plain' : 'txt',
'text/xml' : 'xml',

'video/mp2t' : 'ts',
'video/mp4' : 'mp4',
'video/ogg' : 'ogv',
'video/quicktime' : 'mov',
'video/webm' : 'webm',
'video/x-ms-wmv' : 'wmv',
'video/x-msvideo' : 'avi'
}

def get_ext_from_content_type(content_type):
    """Returns base extension for content types"""
    content_type = content_type.split(';', 1)[0]
    if content_type in MIME_EXT_MAP.keys():
        return MIME_EXT_MAP[content_type]
    return 'unknown'

class Dumper:
    """Dumps data files from WARC file"""

    def __init__(self):
        pass

    def listfiles(self, mimes=None, exts=None, query=None, output=None):
        """Lists files in WARC file"""
        from rich.table import Table
        from rich import print
        if not os.path.exists('metawarc.db'):
            print('Plese generate metawarc.db database with "metawarc index <filename.warc> command"')
            return
        engine = create_engine("sqlite:///metawarc.db", echo=False)
        session = Session(engine)
        results = None
        if mimes is not None:
            results = session.query(models.Record).filter(models.Record.content_type.in_(mimes.split(','))).all()
        elif exts is not None:
            results = session.query(models.Record).filter(models.Record.ext.in_(exts.split(','))).all()
        elif query is not None:
            results = session.execute("select * from record where %s" % (query))
        if results is None:
            print('At least one parameter: query, exts or mimes should be provided')
            return 
        outdata = []
        for record in results:
            outdata.append([record.offset, record.url, record.length, record.content_type, record.ext, record.warc_id])
        headers = ['offset', 'url', 'length', 'content-type', 'ext', 'warc_id']
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

    def dump(self, mimes=None, exts=None, query=None, output=None):
        """Dump WARC file contents"""
        from rich.table import Table
        from rich import print
        if not os.path.exists('metawarc.db'):
            print('Plese generate metawarc.db database with "metawarc index <filename.warc> command"')
            return
        engine = create_engine("sqlite:///metawarc.db", echo=False)
        session = Session(engine)
        results = None
        if mimes is not None:
            results = session.query(models.Record).filter(models.Record.content_type.in_(mimes.split(','))).all()
        elif exts is not None:
            results = session.query(models.Record).filter(models.Record.ext.in_(exts.split(','))).all()
        elif query is not None:
            results = session.execute("select * from record where %s" % (query))
        if results is None:
            print('At least one parameter: query, exts or mimes should be provided')
            return 
        outdata = []
        headers = ['offset', 'filename', 'url', 'length', 'content-type', 'ext', 'status', 'warc_id']
        os.makedirs(output, exist_ok=True)
        opened_files = {}
        for record in results:            
            if record.source in opened_files.keys():
                fileobj = opened_files[record.source]
            else:
                fileobj = open(record.source, "rb")
                opened_files[record.source] = fileobj
            fileobj.seek(record.offset)
            it = iter(ArchiveIterator(fileobj))
            warcrec = next(it)
            filename = record.warc_id + '.' + get_ext_from_content_type(record.content_type)
            outdata.append([record.offset, filename, record.url, record.length, record.content_type, record.ext, record.status_code, record.warc_id])            
            out_raw = open(os.path.join(output, filename), 'wb')
            stream = warcrec.content_stream()
            buf = stream.read(READ_SIZE)
            while buf:
                out_raw.write(buf)
                buf = stream.read(READ_SIZE)
            out_raw.close()
            print('Wrote %s, url %s' % (filename, record.url))
        output_file = os.path.join(output, 'records.csv')
        writer = csv.writer(open(output_file, 'w', encoding='utf8'))
        writer.writerow(headers)
        writer.writerows(outdata)
