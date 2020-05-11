import logging
from tabulate import tabulate
from warcio import ArchiveIterator


class Analyzer:
    """WARC files analysis"""
    def __init__(self):
        pass

    def analyze(self, fromfile, mode='mime'):
        """Reads data from WARC file and provides analysis"""
        logging.debug('Preparing %s' % fromfile)
        resp = open(fromfile, 'rb')
        total = 0
        mimes = {}
        for record in ArchiveIterator(resp, arc2warc=True):
            if record.rec_type == 'response':
                h = record.http_headers.get_header('content-type')
                url = record.rec_headers.get_header('WARC-Target-URI')
                filename = url.rsplit('?', 1)[0].rsplit('/', 1)[-1].lower()
                total += 1
                if h is not None:
                    h = h.split(';', 1)[0]

                v = mimes.get(h, {'total' : 0, 'size' : 0})
                v['total'] += 1
                v['size'] += record.length
                mimes[h] = v


        table = []
        for fd in mimes.items():
            record = [fd[0], fd[1]['total'], fd[1]['size']]
            table.append(record)
        headers = ['mime', 'files', 'files size']
        print(tabulate(table, headers=headers))








