#!/usr/bin/env python
# -*- coding: utf8 -*-
import logging

import click

from .cmds.analyzer import Analyzer
from .cmds.extractor import Extractor
from .cmds.exporter import Exporter
from .cmds.indexer import Indexer
from .cmds.dump import Dumper

# logging.getLogger().addHandler(logging.StreamHandler())
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG)


def enableVerbose():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )


@click.group()
def cli1():
    pass


@cli1.command()
@click.argument("inputfile")
@click.option("--verbose",
              "-v",
              count=False,
              help="Verbose output. Print additional info")
@click.option(
    "--filetypes",
    "-t",
    default=None,
    help="File types (default: doc,xls,ppt,docx,xlsx,pptx",
)
@click.option("--fields", "-f", default=None, help="Fieldnames to extract")
@click.option("--output", "-o", default=None, help="Output file")
def metadata(inputfile, verbose, filetypes, fields, output):
    """Extracts metadata from files inside WARC file or another file container"""
    if verbose:
        enableVerbose()
    acmd = Extractor()
    acmd.metadata_by_ext(inputfile,
                         filetypes.split(",") if filetypes else None,
                         fields,
                         output=output)
    pass


@click.group()
def cli2():
    pass


@cli2.command()
@click.argument("inputfile")
@click.option("--mode",
              "-m",
              default="mimes",
              help="Analysis mode: mimes, exts. Default: mimes")
@click.option("--verbose",
              "-v",
              count=False,
              help="Verbose output. Print additional info")
def analyze(inputfile, mode, verbose):
    """Analysis of the WARC"""
    if verbose:
        enableVerbose()
    acmd = Analyzer()
    acmd.analyze(inputfile, mode=mode)
    pass

@click.group()
def cli3():
    pass


@cli3.command()
@click.argument("inputfile")
@click.option("--verbose",
              "-v",
              count=False,
              help="Verbose output. Print additional info")
@click.option("--type", "-t", "exporttype", default='headers', help="Type of export: headers, warcio, content")
@click.option(
    "--fields",
    "-f",
    default="offset,length,filename,http:status,http:content-type,warc-type,warc-target-uri",
    help="WARCIO export related field names to extract",
)
@click.option("--output", "-o", default="export.jsonl", help="Output file")
def export(inputfile, verbose, exporttype, fields, output):
    """Exports WARC file headers or warcio index"""
    if verbose:
        enableVerbose()
    acmd = Exporter()
    if exporttype == 'headers':
        acmd.headers_export(inputfile, output=output)
    elif exporttype == 'warcio':
        acmd.warcio_indexer_export(inputfile, fields.split(","), output=output)
    if exporttype == 'content':
        acmd.content_export(inputfile, output=output, content_types=['text/html'])
    pass

@click.group()
def cli4():
    pass

@cli4.command(name="index")
@click.argument("inputfile")
@click.option("--verbose",
              "-v",
              count=False,
              help="Verbose output. Print additional info")
def warcindex(inputfile, verbose):
    """Generates WARC file index"""
    if verbose:
        enableVerbose()
    acmd = Indexer()
    acmd.index_content(inputfile)
    pass

@click.group()
def cli5():
    pass

@cli5.command(name="stats")
@click.option("--mode",
              "-m",
              default="mimes",
              help="Analysis mode: mimes, exts. Default: mimes")
@click.option("--verbose",
              "-v",
              count=False,
              help="Verbose output. Print additional info")
def stats(mode, verbose):
    """Generates WARC file index"""
    if verbose:
        enableVerbose()
    acmd = Indexer()
    acmd.calc_stats(mode)
    pass


@click.group()
def cli6():
    pass

@cli6.command(name="list")
@click.option("--mimes",
              "-m",
              default=None,
              help="Mimes list, default None")
@click.option("--exts",
              "-e",
              default=None,
              help="File extensions, default: None")
@click.option("--query",
              "-q",
              default=None,
              help="Custom SQL query to select records")
@click.option("--verbose",
              "-v",
              count=False,
              help="Verbose output. Print additional info")
@click.option("--output",
              "-o",
              default=None,
              help="Output file (CSV)")
def listfiles(mimes, exts, query, verbose, output):
    """Lists urls inside WARC file"""
    if verbose:
        enableVerbose()
    acmd = Dumper()
    acmd.listfiles(mimes=mimes, exts=exts, query=query, output=output)
    pass

@click.group()
def cli7():
    pass

@cli7.command(name="dump")
@click.option("--mimes",
              "-m",
              default=None,
              help="Mimes list, default None")
@click.option("--exts",
              "-e",
              default=None,
              help="File extensions, default: None")
@click.option("--query",
              "-q",
              default=None,
              help="Custom SQL query to select records")
@click.option("--verbose",
              "-v",
              count=False,
              help="Verbose output. Print additional info")
@click.option("--output",
              "-o",
              default='dump',
              help="Output dir. Default: dump")
def dump(mimes, exts, query, verbose, output):
    """Dumps content by query"""
    if verbose:
        enableVerbose()
    acmd = Dumper()
    acmd.dump(mimes=mimes, exts=exts, query=query, output=output)
    pass

cli = click.CommandCollection(sources=[cli1, cli2, cli3, cli4, cli5, cli6, cli7])

# if __name__ == '__main__':
#    cli()
