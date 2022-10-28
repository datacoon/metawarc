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


MIME_EXT_MAP = {'application/javascript' : 'js',
'application/json' : 'json',
'application/octet-stream' : 'bin',
'application/pdf' : 'pdf',
'application/rar' : 'rar',
'application/vnd.android.package-archive' : 'apk',
'application/msword' : 'doc',
'application/vnd.ms-excel' : 'xls',
'application/vnd.ms-fontobject' : 'eot',
'application/x-font-woff' : 'woff',
'text/html' : 'html',
'video/mp4' : 'mp4',
'application/vnd.ms-word.document.macroEnabled.12' : 'docm',
'application/vnd.openxmlformats-officedocument.wordprocessingml.document' : 'docx',
'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' : 'xlsx',
'application/vnd.openxmlformats-officedocument.presentationml.presentation' : 'pptx',
'application/zip' : 'zip',
'application/x-zip-compressed' : 'zip',
'application/x-x509-ca-cert' : 'crt',
'audio/x-wav' : 'wav',
'text/plain' : 'txt',
'image/svg+xml' : 'svg',
'application/rtf' : 'rtf',
'image/png' : 'png',
'text/css' : 'css',
'image/x-icon' : 'ico',
'image/jpeg' : 'jpg',
'image/gif' : 'gif',
'audio/mpeg' : 'mp3',
'application/x-javascript' : 'js',
'video/quicktime' : 'mov',
'video/x-ms-wmv' : 'wmv',
'application/x-7z-compressed' : '7z',
'application/x-font-ttf' : 'ttf',
'image/tiff' : 'tif',
'text/xml' : 'xml',
'images/webp' : 'webp'
}

def get_ext_from_content_type(content_type):
    """Returns base extension for content types"""
    content_type = content_type.split(';', 1)[0]
    if content_type in MIME_EXT_MAP.keys():
        return MIME_EXT_MAP[content_type]
    return unknown

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
        headers = ['offset', 'url', 'length', 'content-type', 'ext', 'status', 'warc_id']
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
