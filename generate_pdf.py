#!/usr/bin/env python3

import os
from fpdf import FPDF
import argparse
from xml.etree import ElementTree


class CustomBuffer:
  """
  Instead of using FPDF.buffer, which is just a string, where FPDF uses `buffer += s` in the code,
  we provide this faster implementation, which directly writes into the file.
  """

  def __init__(self, filename):
    """
    :param str filename:
    """
    self.f = open(filename, "w", encoding="latin1")

  def __iadd__(self, other):
    """
    :param str other:
    :rtype: CustomBuffer
    """
    self.f.write(other)
    return self

  def __len__(self):
    return self.f.tell()


def main():
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument("dir")
  arg_parser.add_argument("--output", help="pdf")
  args = arg_parser.parse_args()

  pdf = FPDF(unit="pt", orientation="l", format="a4")
  tree = ElementTree.parse('%s/layout.xml' % args.dir)
  root = tree.getroot()

  img_count = 0
  for page in root.iter('pagegroup'):
    assert isinstance(page, ElementTree.Element)
    pdf.add_page()
    #print(page, page.attrib)
    width = float(page.attrib["width"])
    height = float(page.attrib["height"])
    factor_x = pdf.w_pt / width
    factor_y = pdf.h_pt / height
    for elem in page:
      assert isinstance(elem, ElementTree.Element)
      if elem.tag == "frame":
        img_kwargs = dict(
          x=float(elem.attrib["x"]) * factor_x, y=float(elem.attrib["y"]) * factor_y,
          w=float(elem.attrib["width"]) * factor_x, h=float(elem.attrib["height"]) * factor_y)
        for sub in elem:
          assert isinstance(sub, ElementTree.Element)
          if sub.tag == "img":
            print("img:", sub, sub.attrib)
            img_filename = "%s/%s/original" % (args.dir, sub.attrib["src"])
            if os.path.exists(img_filename + ".jpg"):
              img_filename += ".jpg"
            elif os.path.exists(img_filename + ".png"):
              img_filename += ".png"
            else:
              raise Exception("No image found: %r.{png|jpg}" % img_filename)
            print("img file:", img_filename)
            print(img_kwargs)
            pdf.image(img_filename, **img_kwargs)
            img_count += 1

  #pdf.set_font('Arial', 'B', 16)
  #pdf.cell(40, 10, 'Hello World!')

  if args.output:
    print("Finished, saving...")
    assert pdf.buffer == ""
    pdf.buffer = CustomBuffer(filename=args.output)
    pdf.close()  # instead of pdf.output()
  else:
    print("Not saving.")

  print("Done.")


if __name__ == '__main__':
  import better_exchook
  better_exchook.install()
  main()
