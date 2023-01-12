#!/usr/bin/env python3

from build import create_project

import click

@click.command()
@click.argument('name')
def cli(name):
    create_project(name)


if __name__ == '__main__':
    cli()
