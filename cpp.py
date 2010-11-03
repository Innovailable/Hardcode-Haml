class CppWriter:

    def __init__(self, name):
        self.out = open("%s.cpp" % name, 'w')
        self.write_buf = []

        self.name = name

    def start(self):
        self.out.write("#include <iostream>\n\n")
        self.out.write("void %s(std::ostream &out) {\n" % self.name)

        self.indent = 1

    def finish(self):
        self.flush()
        self.out.write("}\n")
        self.out.write("int main() { %s(std::cout); return 0; }\n" % self.name)

    def evaluate(self, cmd):
        self.execute("out << %s" % cmd)

    def execute(self, cmd):
        self.flush()
        self.out.write("\t" * self.indent + cmd + ";\n")

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

