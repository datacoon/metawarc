import tempfile
import zipfile
import sys
import os
import json
import logging

from warcio import ArchiveIterator
from lxml import etree
from hachoir.parser import createParser
#from hachoir.core.tools import makePrintable
from hachoir.metadata import extractMetadata
#from hachoir.core.i18n import initLocale
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

from ..constants import SUPPORTED_FILE_TYPES, MS_XML_FILES, MIME_MAP, MIME_PATTERNS, ADOBE_FILES


def extractPDF(filename):
    """Extracts metadata from Adobe PDF files"""
    fp = open(filename, 'rb')
    parser = PDFParser(fp)
    try:
        doc = PDFDocument(parser)
    except:
        return None
    if len(doc.info) > 0:
        result = {}
        for k, v in doc.info[0].items():
            try:
                result[k] = v.decode('utf8', 'ignore')
            except:
                result[k] = str(v)
        return result
    return None

def extractXmeta(filename):
    """Extracts metadata from MS Office XML files like docx, xlsx, e.t.c."""
    try:
        zf = zipfile.ZipFile(filename, 'r')
    except zipfile.BadZipFile:
        return None
    meta = {}
    try:
        try:
            s = zf.open('docProps/core.xml', 'r').read()
            root = etree.fromstring(s)
            meta = {}
            namespaces = {'w': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties'}
            for t in root:
                meta[t.tag.rsplit('}', 1)[-1]] = t.text
        except KeyError:
            pass
        try:
            s = zf.open('docProps/app.xml', 'r').read()
            root = etree.fromstring(s)
            namespaces = {'w': 'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties'}
            for t in root:
                meta[t.tag.rsplit('}', 1)[-1]] = t.text
        except KeyError:
            pass
    except KeyboardInterrupt:
        meta = None
    if len(meta.keys()) == 0:
        meta = None
    return meta

def processWarcRecord(record, url, filename, mime=None, fields=None):
    """Processes single WARC record"""
    if mime and mime in MIME_MAP.keys():
        ext = MIME_MAP[mime]
    else:
        ext = filename.rsplit('.', 1)[-1]
    temp = tempfile.NamedTemporaryFile(suffix=ext, dir=tempfile.gettempdir(), mode='wb', delete=False)
    temp.write(record.raw_stream.read())
    temp.close()
    result = {'filename': filename, 'ext': ext, 'url': url, 'mime': mime, 'metadata': None}
    if ext in MS_XML_FILES or (mime in MIME_MAP.keys() and MIME_MAP[mime] in MS_XML_FILES):
        meta = extractXmeta(temp.name)
        result['metadata'] = meta
    elif ext in ADOBE_FILES or (mime in MIME_MAP.keys() and MIME_MAP[mime] in ADOBE_FILES):
        meta = extractPDF(temp.name)
        result['metadata'] = meta
    else:
        try:
            parser = createParser(temp.name)
        except KeyboardInterrupt:
            logging.info("Unable to parse file")
            return result
        if not parser:
            logging.info("Unable to parse file")
            return result
        else:
            try:
                metadata = extractMetadata(parser)
            except KeyboardInterrupt as err:
                logging.info("Metadata extraction error: %s" % str(err))
            if not metadata:
                logging.info("Unable to extract metadata from: %s" % filename)
            else:
                result['metadata'] = metadata.exportDictionary()
    return result


class Extractor:
    """Metadata extraction class"""
    def __init__(self):
        pass

    def metadata(self, fromfile, file_types=SUPPORTED_FILE_TYPES, fields=None, output='metadata.jsonl'):
        """Reads and returns all metadata from list of file types inside selected file container"""
        if file_types is None:
            file_types = SUPPORTED_FILE_TYPES
        if output is None:
            output = 'metadata.jsonl'
        logging.debug('Preparing %s' % fromfile)
        file_mimes = {}
        for mime, ext in MIME_MAP.items():
            if ext in file_types:
                file_mimes[mime] = ext
        resp = open(fromfile, 'rb')
        out = open(output, 'w', encoding='utf8')
        for record in ArchiveIterator(resp, arc2warc=True):
            matched = False
            if record.rec_type == 'response':
                h = record.http_headers.get_header('content-type')
                url = record.rec_headers.get_header('WARC-Target-URI')
                filename = url.rsplit('?', 1)[0].rsplit('/', 1)[-1].lower()
                ext = filename.rsplit('.', 1)[-1]
                if h and h in file_mimes:
                    matched = True
                else:
                    if len(ext) in [3, 4] and ext in file_types:
                        matched = True
                if matched:
                    result = processWarcRecord(record, url, filename, mime=h)
                    result['source'] = os.path.basename(fromfile)
                    out.write(json.dumps(result) + '\n')
        out.close()




if __name__ == "__main__":
    ex = Extractor()
    ex.metadata(sys.argv[1])


