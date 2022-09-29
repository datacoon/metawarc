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
Returns list of mime mimetypes with stats as number of files and total files size for each mime type

Analyzes 'digital.gov.ru.warc.gz' and output results of list of mime types as table to console

.. code-block:: bash

    $ metawarc analyze digital.gov.ru.warc.gz



Other commands
--------------

* headers - dumps HTTP headers of WARC records
* index - writes WARC file index (similar to warcio index)