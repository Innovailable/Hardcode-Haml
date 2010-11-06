#!/usr/bin/env python
###############################################################################
##
##  hardcode_haml - Haml for hardcore coders
##  Copyright (C) 2010  Thammi
## 
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU Affero General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
## 
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU Affero General Public License for more details.
## 
##  You should have received a copy of the GNU Affero General Public License
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
###############################################################################

from parser import Parser
from optparse import OptionParser
from os.path import split

import c, cpp, python

def main(argv):
    out_modules = {
            'cpp': cpp.CppWriter,
            'c': c.CWriter,
            'python': python.PythonWriter
            }

    optp = OptionParser(usage="usage: %prog [options] file [...]")

    optp.add_option("-o", "--output", help="Determine Output module (language)", metavar="MODULE", default="cpp")
    optp.add_option("-d", "--directory", help="Set the output directory", metavar="DIR", default=".")
    optp.add_option("-r", "--readable", help="Make output more readable for debugging", action="store_true")
    
    (options, args) = optp.parse_args()

    if len(args) == 0:
        print "Please specify at least one file!"
        return 1
    else:
        out_module = out_modules[options.output]
        for in_file in args:
            name = split(in_file)[1].split('.')[0]

            writer = out_module(name, options.directory)

            Parser(file(in_file), writer, readable=options.readable).parse()

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])

