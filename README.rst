metawarc: a command-line tool for metadata extraction from files from WARC (Web ARChive)
########################################################################################

metawarc (pronounced *me-ta-warc*) is a command line WARC files processing tools.
Its goal is to make CLI interaction with files inside WARC archives so easy as possible.
It provides a simple ``metawarc`` command that allows to extract metadata from images, documents and other files inside
WARC archives.


.. contents::

.. section-numbering::



Main features
=============

* Built-in WARC support
* Metadata extraction for a lot of file formats
* Low memory footprint
* Documentation
* Test coverage


File formats supported
======================

* MS Office OLE: .doc, .xls, .ppt
* MS Office XML: .docx, .xlsx, .pptx
* Adobe PDF: .pdf
* Images: .png, .jpg, .tiff, .jpeg, .jp2


Installation
============


Any OS
-------------

A universal installation method (that works on Windows, Mac OS X, Linux, …,
and always provides the latest version) is to use pip:


.. code-block:: bash

    # Make sure we have an up-to-date version of pip and setuptools:
    $ pip install --upgrade pip setuptools

    $ pip install --upgrade metawarc


(If ``pip`` installation fails for some reason, you can try
``easy_install metawarc`` as a fallback.)


Python version
--------------

Python version 3.6 or greater is required.

Usage
=====


Synopsis:

.. code-block:: bash

    $ metawarc [command] [flags]  inputfile


See also ``metawarc --help`` and ``metawarc [command] --help`` for help for each command.


Examples
--------

Extract metadata of all supported file types from 'digital.gov.ru.warc.gz' and output results to default filename 'metadata.jsonl':

.. code-block:: bash

    $ metawarc metadata digital.gov.ru.warc.gz


Extract metadata for .doc and .docx file types from 'digital.gov.ru.warc.gz' and output results to default filename 'metadata.jsonl':

.. code-block:: bash

    $ metawarc metadata --filetypes doc,docx digital.gov.ru.warc.gz

Extract metadata for .doc and .docx file types from 'digital.gov.ru.warc.gz' and output results to filename 'digital_meta.jsonl':

.. code-block:: bash

    $ metawarc metadata --filetypes doc,docx --output digital_meta.jsonl digital.gov.ru.warc.gz


Commands
========

Metadata command
----------------
Extracts metadata from files inside .warc files. Returns JSON lines output for each file found.

Extract metadata for .doc and .docx file types from 'digital.gov.ru.warc.gz' and output results to filename 'digital_meta.jsonl':

.. code-block:: bash

    $ metawarc metadata --filetypes doc,docx --output digital_meta.jsonl digital.gov.ru.warc.gz



Analyze command
----------------
Returns list of mime mimetypes with stats as number of files and total files size for each mime type.
Will be merged or replaced by 'stats' command that uses sqlite db to speed up data processing

Analyzes 'digital.gov.ru.warc.gz' and output results of list of mime types as table to console

.. code-block:: bash

    $ metawarc analyze digital.gov.ru.warc.gz



Index command
-------------
Generates 'metawarc.db' SQLite database with records HTTP metadata. Requred for 'stats' command to calculate stats quickly

Analyzes 'digital.gov.ru.warc.gz' and writes 'metawarc.db' with HTTP metadata.

.. code-block:: bash

    $ metawarc index digital.gov.ru.warc.gz

Index command
-------------
Same as 'analyze' command but uses 'metawarc.db' to speed up data processing. Returns total length and count of records by each mime or file extension.

Processes data in 'metawarc.db' and prints total length and count for each mime

.. code-block:: bash

    $ metawarc stats -m mimes

Processes data in 'metawarc.db' and prints total length and count for each file extension

.. code-block:: bash

    $ metawarc stats -m exts


Export command
--------------
Extracts HTTP headers, WARC headers or text content from WARC file and saves as NDJSON (JSON lines) data file.

Exports http headers from 'digital.gov.ru.warc.gz' and writes as 'headers.jsonl'

.. code-block:: bash

    $ metawarc export -t headers -o headers.jsonl digital.gov.ru.warc.gz

Exports WarcIO index from 'digital.gov.ru.warc.gz' and writes as 'data.jsonl' with fields listed in '-f' option. 

.. code-block:: bash

    $ metawarc export -t warcio -f offset,length,filename,http:status,http:content-type,warc-type,warc-target-uri -o data.jsonl digital.gov.ru.warc.gz

Exports text (HTML) content from 'digital.gov.ru.warc.gz' and writes as 'content.jsonl'

.. code-block:: bash

    $ metawarc export -t content -o content.jsonl digital.gov.ru.warc.gz

