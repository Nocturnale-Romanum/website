#!venv/bin/python

import os, shutil, sys
from pdf2image import convert_from_path

template_file = "build_template.tex"
gabc_file_pattern = "THE_SCORE_HERE"
build_dir = "tex_build"

def build(filepath, img_path):
  """takes a file path to a .gabc file, and an output folder img_path, 
  and outputs a cropped borderless .png file of the same base name as the .gabc file, into folder img_path."""
  filename = os.path.basename(filepath)
  basename = os.path.splitext(filename)[0]
  texfile = basename+".tex"
  imgfilepath = os.path.join(img_path, basename+".png")
  try:
    os.remove(imgfilepath)
  except:
    pass
  shutil.copyfile(filepath, os.path.join(build_dir, filename))
  fin = open(os.path.join(build_dir, template_file), "rt")
  fout = open(os.path.join(build_dir, texfile), "wt")
  for line in fin:
    fout.write(line.replace(gabc_file_pattern, filename))
  fin.close()
  fout.close()
  os.system("cd {} && lualatex --interaction=nonstopmode {}".format(build_dir, texfile))
  os.system("cd {} && lualatex --interaction=nonstopmode {}".format(build_dir, texfile))
  os.system("cd {} && pdfcrop {}.pdf {}_cropped.pdf".format(build_dir, basename, basename))
  images = convert_from_path(os.path.join(build_dir, basename+'_cropped.pdf'), dpi=600)
  image = images[0]
  image.save(imgfilepath, "PNG")
  os.system("cd {} && rm *.pdf *.glog *.gtex *.aux *.gaux *.gabc".format(build_dir))

build(sys.argv[1], sys.argv[2])
