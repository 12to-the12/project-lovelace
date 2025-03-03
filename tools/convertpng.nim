# Copyright (c) 2025 by Alfred Morgan <alfred@54.org>
# License https://opensource.org/license/isc-license-txt
import std/[cmdline, os, strutils, strformat]

# to install nimPNG use:
# nimble install nimPNG
import nimPNG

const EX_USAGE = 64

let args = commandLineParams()
if args.len == 0:
    quit(&"usage:\n\t{getAppFilename()} <filename.png> [...]", EX_USAGE)

for fname in args:
    let png = loadPNG24 fname
    if png == nil:
      echo &"Skipping: \"{fname}\" not found"
      continue
    echo &"{fname}: {png.width = }, {png.height = }"
    let f = open(fname.changeFileExt("rgb"), fmWrite)
    f.write png.data
    close f
