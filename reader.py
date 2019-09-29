#!/usr/bin/env python3

import argparse


class Reader:
  def __init__(self, filename):
    """
    :param str filename:
    """
    self.filename = filename


def main():
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument("file")
  args = arg_parser.parse_args()
  reader = Reader(filename=args.file)


if __name__ == '__main__':
  main()
