#!/usr/bin/env python3

import sys

import verible_verilog_syntax
import anytree

def process_file_data(path: str, data: verible_verilog_syntax.SyntaxData):
  """Print tree representation to the console.
  The function uses anytree module (which is a base of a tree implementation
  used in verible_verilog_syntax) method to print syntax tree representation
  to the console.
  Args:
    path: Path to source file (used only for informational purposes)
    data: Parsing results returned by one of VeribleVerilogSyntax' parse_*
          methods.
  """
  #print(f"\033[1;97;7m{path} \033[0m\n")
  if data.tree:
    for prefix, _, node in anytree.RenderTree(data.tree):
      #print(f"\033[90m{prefix}\033[0m{node.to_formatted_string()}")
      print(f"{prefix}{node}")
    print()


v = verible_verilog_syntax.VeribleVerilogSyntax()

process_file_data(sys.argv[1], v.parse_file(sys.argv[1], options= { 'gen_tree': True }))
