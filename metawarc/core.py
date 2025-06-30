#!/usr/bin/env python
# -*- coding: utf8 -*-
import logging

import click
import os
import glob

from .cmds.analyzer import Analyzer
from .cmds.extractor import Extractor
from .cmds.exporter import Exporter
from .cmds.indexer import Indexer
from .cmds.dump import Dumper

# Required to suppress Hachoir warnings
from hachoir.core import config as HachoirConfig
HachoirConfig.quiet = True

# logging.getLogger().addHandler(logging.StreamHandler())
#logging.basicConfig(
#    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#    level=logging.INFO)


def enableVerbose():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )



@click.group()
def cli4():
    pass

@cli4.command(name="index")
@click.argument("inputfile")
@click.option("--tofile",
              "-o",
              default="warcindex.db",
              help="Name of the output db file. Default: warcindex.db")     
@click.option("--tables",
              "-t",
              default="",
              help="Comma separated list of tables. Default: links. Possible values: links, pdfs, images, ooxmldocs, oledocs")                          
@click.option("--update",
              "-u",
              is_flag=True,
              default=True,
              help="Update database index if it exists")          
@click.option("--silent",
              "-s",
              is_flag=True,
              help="Do everything silent")          
@click.option("--verbose",
              "-v",
              is_flag=True,
              help="Verbose output. Print additional info")          
def warcindex(inputfile:str, tofile:str, tables:str, update:bool=True, silent:bool=False, verbose:bool=True):
    """Builds WARC file index as DuckDB database file and accompanied Parquet files"""
    if verbose:
        enableVerbose()
    if os.path.exists(tofile) and not update:
        print(f'Output database {tofile} already exists. Please choose another file name or use update option')
        return
    acmd = Indexer()
    all_tables = ['records', 'headers']
    files = glob.glob(inputfile.strip("'"))    
    print(inputfile, files)
    acmd.index_records(files, tofile, all_tables, silent=silent)
    pass


@click.group()
def cli9():
    pass

@cli9.command(name="index-content")
@click.option("--inputfiles",
              "-i",
              default=None,
              help="List of input files (globbed)")     
@click.option("--tofile",
              "-o",
              default="warcindex.db",
              help="Name of the output db file. Default: warcindex.db")     
@click.option("--tables",
              "-t",
              default="links",
              help="Comma separated list of tables. Default: links. Possible values: links, pdfs, images, ooxmldocs, oledocs")                               
@click.option("--silent",
              "-s",
              is_flag=True,
              help="Do everything silent")          
@click.option("--verbose",
              "-v",
              is_flag=True,
              help="Verbose output. Print additional info")          
def index_content(inputfiles:str, tofile:str, tables:str, update:bool=True, silent:bool=False, verbose:bool=True):
    """Builds WARC file index as DuckDB database file"""
    if verbose:
        enableVerbose()
    if os.path.exists(tofile) and not update:
        print(f'Output database {tofile} already exists. Please choose another file name or use update option')
        return
    acmd = Indexer()
    if inputfiles is not None and len(inputfiles) == 0:
        files = glob.glob(inputfiles)
    else:
        files = None
    for table in tables.split(','):
        acmd.index_by_table_type(files, tofile, table_type=table, silent=silent)
    pass

@click.group()
def cli5():
    pass

@cli5.command(name="stats")
@click.option("--mode",
              "-m",
              default="mimes",
              help="Analysis mode: mimes, exts. Default: mimes")
@click.option("--dbfile",
              "-i",
              default="warcindex.db",
              help="Name of the db file. Default: warcindex.db")               
@click.option("--verbose",
              "-v",
              is_flag=True,
              help="Verbose output. Print additional info")
def stats(mode, dbfile, verbose):
    """Generates mime or exts statistics"""
    if verbose:
        enableVerbose()
    acmd = Indexer()
    acmd.calc_stats(dbfile, mode)
    pass


@click.group()
def cli6():
    pass

@cli6.command(name="list-files")
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
              is_flag=True,
              default=False,
              help="Verbose output. Print additional info")
@click.option("--output",
              "-o",
              default=None,
              help="Output file (CSV)")
def listfiles(warcfiles:str=None, mimes:str=None, exts:str=None, query:str=None, verbose:bool=False, output:str=None):
    """Lists urls inside WARC file"""
    if verbose:
        enableVerbose()
    acmd = Dumper()
    acmd.listfiles(warcfiles=warcfiles, mimes=mimes, exts=exts, query=query, output=output)
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
              is_flag=True,
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


@click.group()
def cli1():
    pass

@cli1.command(name="dump-metadata")
@click.option("--inputfiles",
              "-i",
              default=None,
              help="List of input files (globbed)")     
@click.option("--dbfile",
              "-d",
              default="warcindex.db",
              help="Name of the  db file.")     
@click.option("--metadata-type",
              "-t",
              default="ooxmldocs",
              help="Metadata type: pdfs, images, ooxmldocs, oledocs")                               
@click.option("--output",
              "-o",
              default="None",
              help="Name of the output  file. Default: std out")                   
@click.option("--silent",
              "-s",
              is_flag=True,
              help="Do everything silent")          
@click.option("--verbose",
              "-v",
              is_flag=True,
              help="Verbose output. Print additional info")          
def dump_metadata(inputfiles:str, dbfile:str, metadata_type:str, output:str=None, silent:bool=False, verbose:bool=True):
    """Dumps indexed metadata"""
    if verbose:
        enableVerbose()
    if not os.path.exists(dbfile):
        print(f'Database {db} not found. Please index WARC files before dumping')
        return
    acmd = Indexer()
    if inputfiles is not None and len(inputfiles) == 0:
        files = glob.glob(inputfiles)
    else:
        files = None
    acmd.dump_metadata(files, dbfile, metadata_type=metadata_type, output=output, silent=silent)
    pass


cli = click.CommandCollection(sources=[cli1,  cli4, cli5, cli6, cli7, cli9])

# if __name__ == '__main__':
#    cli()
