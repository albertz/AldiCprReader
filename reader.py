#!/usr/bin/env python3

import os
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
      if i == 8:
        line += " "
      if i < len(d):
        line += binascii.hexlify(d[i:i + 1]).decode('ascii')
      else:
        line += "  "
      line += " "

    line += ' |'
    # ................
    for i in range(16):
      if i == 8:
        line += " "
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

    addr += len(d)
    if len(d) < 16:
      break


def debug_print_str(s):
  """
  :param str|bytes s:
  """
  if isinstance(s, bytes):
    try:
      s = s.decode("utf8")
    except UnicodeDecodeError:
      pass
  if len(s) >= 100:
    print(repr(s[:40]) + "..." + repr(s[-40:]))
    return
  print(repr(s))


class CprReader:
  def __init__(self, filename, output_dir):
    """
    :param str filename:
    :param str|None output_dir:
    """
    self.filename = filename
    self.output_dir = output_dir
    self.file = open(filename, "rb")

    f = self.file

    assert_same(f.read(2), b"\xec\xce")
    x1 = self.read_uint16()
    x2 = self.read_uint32()
    print(x1, x2)

    num_files = self.read_uint32()
    for i in range(num_files):
      self.read_file_entry()

    assert_same(f.read(1), b"")  # EOS!
    #hex_dump(f)

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
    if size == 0:
      return b""
    res = self.file.read(size)
    assert len(res) == size
    return res

  def read_file_entry(self):
    idx = self.read_uint32()
    print(idx)
    filename = self.read_pascal_str()
    if filename[-1] == 0:
      filename = filename[:-1]
    filename = filename.decode("utf8")
    debug_print_str(filename)
    data = self.read_pascal_str()
    #debug_print_str(data)
    if self.output_dir:
      assert not filename.startswith("/") and ".." not in filename
      output_filename = "%s/%s" % (self.output_dir, filename)
      os.makedirs(os.path.dirname(output_filename), exist_ok=True)
      with open(output_filename, "wb") as f:
        f.write(data)


def main():
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument("file")
  arg_parser.add_argument("--output", help="directory")
  args = arg_parser.parse_args()
  reader = CprReader(filename=args.file, output_dir=args.output)


if __name__ == '__main__':
  import better_exchook
  better_exchook.install()
  main()
