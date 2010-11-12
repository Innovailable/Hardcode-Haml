# Hardcode Haml - Haml for Hardcore Coders (and Embedded devices)

Compiling Haml markup/templates to program code.

*Warning:* The code isn't ready for production use, yet. The TODO section is an
imcomplete documentation of the missing parts.

## Concept

Most template engines for compiled and statically typed languages (like C and
C++) are only able to do simple search and replace jobs for given values. Having
used template engines in script languages like Ruby, Python or Java Script makes
returning to those template engines hard. This is where Hardcode Haml comes into
play.

Haml was first implemented in ruby and got ported to multiple other languages.
It compines the ability to replace parts of your markup with values calculated
at runtime (even allowing evaluation of code directly from the markup) and
additionally replaces XML with more writeable and readable markup.

This project turns Haml markup into program code. Therefore the markup gets
parsed and processed before runtime and maybe even optimized by your compiler.
Therefore execution time, memory footprint and file size on the target device
should be superior to other approaches. The drawback is, that your templates are
compiled in your binary and you can't edit them on the target system.

The language modules will generate a function which, when executed, will output
the generated XML markup into a stream. The parameters of the function can be
referenced directly from within the template. Haml contains syntax elements
which let you print out evaluated code and even pass code directly to the
generated code. Loops and other control flow elements can be used to repeat
blocks or conditionally display them.

To fullfill the needs of the target languages, Haml syntax has to be extended.
We need a way to specify the name and type of the parameters given to the
template. Additionally most languages need a way to execute code before the
function declaration (e.g. to include headers).

## Supported Languages

Output can currently be generated in several languages

* C++ _(using ostream)_
* C _(using fputs())_
* python _(using Pythons file objects)_

Other languages can be implemented with ease. All language implementations are
currently smaller than 100 lines (including whitespaces).

Haml passes code directly to the underlying language, so the language modules
won't be interchangable without replacing some code in your templates.

## Hardcode Haml Dialect

Some syntax changes were neccessary to adopt Haml to the target languages.

TODO

### Subtle changes

TODO

## TODOs

### Tasks

* implement most common syntax/language elements (see below)
* ...
* document implemented functionality and introduced syntax extensions of Haml
* clean up the code (especially in the parser)
* target language side helper
* ...

### Syntax/Language Elements

#### Must have

* direct HTML tags (status unknown)
* tag parsing (check some behaviour)
* entity escape (static and dynamic)
* self closing tags
* filters (infrastructure, some filters)
* multiline

### May have

* haml comments -#
* whitespace removal (&lt; and >)
* conditional comments /\[] (only needed to support IE afaik)
* whitespace preservation
* escaping/unescaping html in evaluations

### Won't implement (in the near future)

* object reference \[] (too close to the target language)
* boolean attributes?

## Links

* [Official Haml Homepage](http://haml-lang.com/)
* [Haml "Reference"](http://haml-lang.com/docs/yardoc/file.HAML_REFERENCE.html)

