#!/usr/bin/env python3

import argparse
import struct
import typing
import binascii


def assert_same(a, b):
  assert a == b


def hex_dump(f):
  """
  :param typing.BinaryIO f:
  """
  # Code adapted from https://bitbucket.org/techtonik/hexdump/src/default/
  addr = f.tell()
  while True:
    # 00000000:
    line = '%08X:  ' % addr
    # 00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00
    d = f.read(16)
    for i in range(16):
      if i < len(d):
        line += binascii.hexlify(d[i:i + 1]).decode('ascii')
      else:
        line += "  "
      line += " "
      if i == 8:
        line += " "

    line += ' |'
    # ................
    for i in range(16):
      if i >= len(d):
        line += " "
        continue
      b = d[i]
      # printable ASCII range 0x20 to 0x7E
      if 0x20 <= b <= 0x7E:
        line += chr(b)
      else:
        line += '.'
    line += '|'
    print(line)

    addr += 16


def debug_print_str(s):
  """
  :param str|bytes s:
  """
  if isinstance(s, bytes):
    s = s.decode("utf8")  # ok?
  if len(s) >= 100:
    print(repr(s[:40] + "..." + s[-40:]))
    return
  print(repr(s))


class Reader:
  def __init__(self, filename):
    """
    :param str filename:
    """
    self.filename = filename
    self.file = open(filename, "rb")

    f = self.file

    assert_same(f.read(2), b"\xec\xce")
    x = self.read_uint16()
    x = self.read_uint32()
    x = self.read_uint32()
    x = self.read_uint32()
    s = self.read_pascal_str()
    assert_same(s, b"cmd.log")
    s = self.read_pascal_str()
    debug_print_str(s)
    hex_dump(f)

  def read_uint16(self):
    """
    :rtype: int
    """
    return struct.unpack(">H", self.file.read(2))[0]

  def read_uint32(self):
    """
    :rtype: int
    """
    return struct.unpack(">I", self.file.read(4))[0]

  def read_pascal_str(self):
    """
    :rtype: bytes
    """
    size = self.read_uint32()
    assert size > 0
    res = self.file.read(size)
    assert len(res) == size
    if res[-1] == 0:
      res = res[:-1]
    return res


def main():
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument("file")
  args = arg_parser.parse_args()
  reader = Reader(filename=args.file)


if __name__ == '__main__':
  import better_exchook
  better_exchook.install()
  main()
