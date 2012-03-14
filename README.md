# Hardcode Haml - Haml for Hardcore Coders (and Embedded devices)

Compiling Haml markup/templates to program code.

*Warning:* There are still some language features missing. The TODO section is
an imcomplete documentation of the the parts I am aware of.

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

## State

Hardcode Haml is used in at least one production environment (in which I am
involved). The development is driven by this project as we find bugs and
important missing features. I am confident that Hardcode Haml in its current
state is stable and comprehensive enough to be useful in other projects.

If you are missing a useful feature or find a bug please file an issue on
[Github](https://github.com/thammi/Hardcode-Haml/issues). Also feel free to
contact me there if you have any questions.

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

### Declaration

As languages like C and C++ do not have tightly built-in dictionary types using
those does not come natural in these languages. I therefore decided to use a
more native approach to pass the data into the template: Function parameters. To
declare those the Haml syntax has to be extended:

    ? int a, std::string b

The `?` declares the parameters passed to the templates and starts the actual
template. An implicit `?` at the start of the document is assumed if there is
none explicit declaration.

Introducing this operator has another advantage: It is possible to introduce
code which will be placed outside the actual function processing the template.
Simply write this code before the `?` declaration. The way this code behaves
depends on the language you are using. In C/C++ this code will be added to the
header which enables you to include files and declare types used in your
template.

### Boolean attributes

Boolean attributes are implicit in ruby and detected at runtime. Hardcode Haml
tries to do as much as possible in the parser and avoids complexity in the
language modules. Another problem is that not all target languages are able to
determine whether an expression evaluates to a boolean.  Hardcode Haml therefore
extends the syntax with the '?=' and '?=&gt;' operators for attributes.

Boolean attributes are useful for radiobuttons, checkboxes and select elements.
Simply write:

    %input(type="radio" checked?=foo)

... or ...

    %input(type="radio"){checked ?=> foo}

This code evaluates to the following (X)HTML when `foo` is true:

    <input type="radio" checked="checked">

... and when `foo` is false to:

    <input type="radio">

## Example

There is an example in the [Wiki](https://github.com/thammi/Hardcode-Haml/wiki/Example-Workflow-%28C++%29).

## Todos

### Tasks

* correct scoping according to indent
* implement most common syntax/language elements (see below)
* ...
* document implemented functionality and introduced syntax extensions of Haml
* clean up the code (especially in the parser)
* target language site helper
* ...

### Syntax/Language Elements

#### Must have

* entity escape (static, dynamic?)
* filters (infrastructure, some filters)

### May have

* whitespace removal (&lt; and &gt;)
* conditional comments /\[] (only needed to support IE afaik)
* whitespace preservation
* escaping/unescaping html in evaluations

### Won't implement (in the near future)

* object reference \[] (too close to the target language)

## Links

* [Official Haml Homepage](http://haml-lang.com/)
* [Haml "Reference"](http://haml-lang.com/docs/yardoc/file.HAML_REFERENCE.html)

