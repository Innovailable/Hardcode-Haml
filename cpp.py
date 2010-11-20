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

from os.path import join, exists

import primitives

class AbstractCppWriter:

    def __init__(self, name, directory):
        self.write_buf = []
        self.name = name
        self.directory = directory

    def start(self):
        directory = self.directory
        name = self.name

        self.out = open(join(directory, "{name}.cpp".format(name=name)), 'w')
        self.header = open(join(directory, "{name}.h".format(name=name)), 'w')

        inc_f = '#include <iostream>\n#include "{name}.h"\n\n'
        self.out.write(inc_f.format(name=name))

        gate = self.name.upper() + "_H"

        self.header.write("#ifndef {gate}\n".format(gate=gate))
        self.header.write("#define {gate}\n\n".format(gate=gate))
        self.header.write("#include <iostream>\n\n")

        self.indent = 0

    def evaluate(self, cmd):
        prim = primitives.find_primitive(cmd)

        if prim:
            self.write_buf.append(prim)
        else:
            self.execute("out << ({cmd})".format(cmd=cmd))

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
            self.execute('out << "{data}"'.format(data=data))

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
        decl = "void {name}({para})".format(name=self.name, para=para_str)

        self.out.write("\n{decl} {{\n".format(decl=decl))

        self.header.write("\n{decl};\n\n#endif\n".format(decl))

        self.header.close()
        self.header = None

        self.indent += 1

    def finish(self):
        self.flush()
        self.out.write("}}\n")

template_header = '''\
#ifndef HAMLTEMPLATE_H
#define HAMLTEMPLATE_H

#include <ostream>

class HamlTemplate {
public:
    virtual void run(std::ostream& out) = 0;
    friend std::ostream& operator<<(std::ostream& out, HamlTemplate& templ) { templ.run(out); }
    friend std::ostream& operator<<(std::ostream& out, HamlTemplate* templ) { templ->run(out); }
};

#endif /* HAMLTEMPLATE_H */
'''

class ClassCppWriter(AbstractCppWriter):

    def declare(self, paras):
        th_file = join(self.directory, "hamltemplate.h")
        if not exists(th_file):
            th_out = open(th_file, 'w')
            th_out.write(template_header)
            th_out.close()

        h_write = self.header.write
        o_write = self.out.write

        class_name = self.name.capitalize()
        para_str = ', '.join(paras)

        # writing into the .cpp
        o_write("void %s::run(std::ostream &out) {\n" % class_name)

        # writing into the header
        h_write('#include "hamltemplate.h"\n\n')
        h_write("class {name} : public HamlTemplate {{\npublic:\n".format(name=class_name))
        h_write("\t{name}({para}) ".format(name=class_name, para=para_str))

        if paras:
            cp_str = ', '.join("{0}({0})".format(para.split()[-1])
                    for para in paras)

            h_write(": " + cp_str)

        h_write("{}\n")
        h_write("\tvirtual void run(std::ostream &out);\n")
        h_write("\nprivate:\n")

        for para in paras:
            h_write("\t{para};\n".format(para=para))

        h_write("};\n\n#endif\n")

        self.header.close()
        self.header = None

        self.indent += 1

    def finish(self):
        self.flush()
        self.out.write("}\n")

