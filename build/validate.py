#!/usr/bin/env python3

import xmlschema
import sys
import pathlib

script_dir = pathlib.PurePath(__file__).parent

component_schema = xmlschema.XMLSchema(str(script_dir.joinpath('schema/2009/component.xsd')))


def validate_component(filename):
    component_schema.validate(filename)


if __name__ == "__main__":
    validate_component(sys.argv[1])
