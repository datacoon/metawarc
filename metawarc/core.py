#!/usr/bin/env python
# -*- coding: utf8 -*-
import logging

import click

from .cmds.analyzer import Analyzer
from .cmds.extractor import Extractor

# logging.getLogger().addHandler(logging.StreamHandler())
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)


def enableVerbose():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)


@click.group()
def cli1():
    pass


@cli1.command()
@click.argument('inputfile')
@click.option('--verbose', '-v', count=False, help='Verbose output. Print additional info')
@click.option('--filetypes', '-t', default=None, help="File types (default: doc,xls,ppt,docx,xlsx,pptx")
@click.option('--fields', '-f', default=None, help="Fieldnames to extract")
@click.option('--output', '-o', default=None, help="Output file")
def metadata(inputfile, verbose, filetypes, fields, output):
    """Extracts metadata from files inside WARC file or another file container"""
    if verbose:
        enableVerbose()
    acmd = Extractor()
    acmd.metadata_by_ext(inputfile, filetypes.split(',') if filetypes else None, fields, output=output)
    pass


@click.group()
def cli2():
    pass


@cli2.command()
@click.argument('inputfile')
@click.option('--mode', '-m', default='mimes', help='Analysis mode: mimes, exts. Default: mimes')
@click.option('--verbose', '-v', count=False, help='Verbose output. Print additional info')
def analyze(inputfile, mode, verbose):
    """Analysis of the WARC"""
    if verbose:
        enableVerbose()
    acmd = Analyzer()
    acmd.analyze(inputfile, mode=mode)
    pass


cli = click.CommandCollection(sources=[cli1, cli2])

# if __name__ == '__main__':
#    cli()
