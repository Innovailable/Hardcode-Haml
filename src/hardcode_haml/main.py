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

from optparse import OptionParser
from os.path import split

from hardcode_haml.parser import HamlFile

from hardcode_haml.lang import c, cpp, python

def main():
    out_modules = [
            cpp.ClassCppWriter,
            cpp.FunCppWriter,
            c.CWriter,
            python.PythonWriter,
            ]

    optp = OptionParser(usage="usage: %prog [options] file [...]")

    optp.add_option("-o", "--output",
            help="Determine output module (language)",
            metavar="MODULE",
            default="cpp")

    optp.add_option("-d", "--directory",
            help="Set the output directory",
            metavar="DIR",
            default=".")

    optp.add_option("-r", "--readable",
            help="Make output more readable for debugging",
            action="store_true")

    optp.add_option("-l", "--list",
            help="List available output modules",
            action="store_true")
    
    (options, args) = optp.parse_args()

    if options.list:
        print "Available language IDs:"

        for lang in sorted(out_modules, key=lambda lang: lang.IDS[0]):
            ids = ', '.join("'%s'" % i for i in lang.IDS)
            print "- %s -> %s" % (ids, lang.NAME)

        return 0

    if len(args) == 0:
        print "Please specify at least one file!"
        return 1
    else:
        out_module = None

        for cur in out_modules:
            if options.output in cur.IDS:
                out_module = cur
                break
        else:
            print "Output module '%s' not found" % options.output
            return 2

        opts = {
                'indent': True,
                'debug': options.readable,
                'auto_indent': True,
                }

        for in_file in args:
            file_name = split(in_file)[1]

            # determine template name
            if file_name.lower().endswith(".haml"):
                # the sane way
                name = file_name[:-5]
            else:
                # backup solution
                name = file_name.split('.')[0]

            parser = HamlFile(file(in_file), opts)
            writer = out_module(name, options.directory)

            parser.execute(writer)

if __name__ == '__main__':
    main()

