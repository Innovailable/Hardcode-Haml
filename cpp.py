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

from os.path import join

import primitives

class AbstractCppWriter:

    def __init__(self, name, directory):
        self.write_buf = []
        self.name = name
        self.directory = directory

    def start(self):
        directory = self.directory
        name = self.name

        self.out = open(join(directory, "%s.cpp" % name), 'w')
        self.header = open(join(directory, "%s.h" % name), 'w')

        self.out.write('#include <iostream>\n#include "test.h"\n\n')

        gate = "%s_H" % self.name.upper()

        self.header.write("#ifndef %s\n" % gate)
        self.header.write("#define %s\n\n" % gate)
        self.header.write("#include <iostream>\n\n")

        self.indent = 0

    def evaluate(self, cmd):
        prim = primitives.find_primitive(cmd)

        if prim:
            self.write_buf.append(prim)
        else:
            self.execute("out << (%s)" % cmd)

    def execute(self, cmd):
        self.flush()

        cmd = cmd.strip()

        if cmd.startswith('#'):
            out_str = cmd + "\n"
        else:
            out_str = "\t" * self.indent + cmd + ";\n"

        self.out.write(out_str)

        if self.header:
            self.header.write(out_str)

    def write(self, data):
        # escape!
        replacements = [
                ('\\', '\\\\'),
                ('\n', '\\n'),
                ('"', '\\"'),
                ]
        
        for old, new in replacements:
            data = data.replace(old, new)

        self.write_buf.append(data)

    def flush(self):
        if self.write_buf:
            data = ''.join(self.write_buf)
            self.write_buf = []
            self.execute('out << "%s"' % data)

    def block_exec(self, cmd):
        self.flush()
        self.out.write("\t" * self.indent + cmd + " {\n")
        self.indent += 1

    def close_block(self):
        self.flush()
        self.indent -= 1
        self.out.write("\t" * self.indent + "}\n")

    def comment(self, data):
        self.flush()
        self.out.write("\t" * self.indent + "// " + data + "\n")

class FunCppWriter(AbstractCppWriter):

    def declare(self, paras):
        para_str = ', '.join(['std::ostream &out'] + paras)
        declaration = "void %s(%s)" % (self.name, para_str)

        self.out.write("\n%s {\n" % declaration)

        self.header.write("\n%s;\n\n#endif\n" % declaration)

        self.header.close()
        self.header = None

        self.indent += 1

    def finish(self):
        self.flush()
        self.out.write("}\n")

class ClassCppWriter(AbstractCppWriter):

    def declare(self, paras):
        class_name = self.name.capitalize()
        para_str = ', '.join(paras)
        cp_str = ', '.join("{0}({0})".format(para.split()[-1]) for para in paras)
        friend_str = "std::ostream& operator<<(std::ostream& out, %s &templ)" % class_name

        # writing into the .cpp
        self.out.write("%s {\n\ttempl.run(out);\n\treturn out;\n}\n\n" % friend_str)
        self.out.write("void %s::run(std::ostream &out) {\n" % class_name)

        # writing into the header
        self.header.write("class %s {\npublic:\n" % class_name)
        self.header.write("\t%s(%s) : %s {}\n" % (class_name, para_str, cp_str))
        self.header.write("\tvoid run(std::ostream &out);\n")
        self.header.write("\tfriend %s;" % friend_str)
        self.header.write("\nprivate:\n")

        for para in paras:
            self.header.write("\t%s;\n" % para)

        self.header.write("};\n\n#endif\n")

        self.header.close()
        self.header = None

        self.indent += 2

    def finish(self):
        self.flush()
        self.out.write("}\n")

