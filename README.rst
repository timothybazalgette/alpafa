ALPAFA
======

ALPAFA (/ˌælˈpæfə/, Algorithm for Lexicocentric Parameter Acquisition by Feature Assignment) is a
Python implementation of the algorithm described in chapter 2 of my 2015 PhD thesis, `Algorithmic
Acquisition of Focus Parameters <http://ling.auf.net/lingbuzz/003006>`_ (AAFP), which grew out of
an attempt to formalise certain proposals of the `Rethinking Comparative Syntax
<http://recos-dtal.mml.cam.ac.uk/>`_ (ReCoS) project. The algorithm takes a set of heads, each of
which is specified for a number of discoverable properties, and uses a "prominence" order of
properties to construct a minimal categorial system. This is achieved by attempting to assign each
new feature to all heads of the "largest" existing category, and, if this fails, making the
"smallest" categorial division possible. This algorithm is a putative component of domain-general
categorisation processes that is designed to capture the structured typological and historical
syntactic variation seen crosslinguistically through third factor principles. The motivation for
and behaviour of this algorithm is described in detail in chapters 1 and 2 of AAFP, including
extensions for unvalued features, movement triggers, and c-selection. Chapter 10 presents and
compares worked examples of inputs to the algorithm for toy fragment grammars of 6 varieties.

Links
=====

* AAFP: http://ling.auf.net/lingbuzz/003006
* ReCoS project: http://recos-dtal.mml.cam.ac.uk/
* Github: https://www.github.com/timothybazalgette/alpafa
* PyPI: https://pypi.python.org/pypi/alpafa

Installation
============

Install with pip:

``$ pip install alpafa`` or ``$ pip3 install alpafa``

Input file format
=================

Input files are closely based on the set notation used for input specifications in AAFP, but are
somewhat simplified for ease of creation and reading. They should be plain text files with UTF-8
compatible encodings. Place each head name on a separate line, followed by a colon and a
comma-separated list of properties. The prominence order should be placed on another line, starting
``prominence=``, followed by a comma-separated list of property names. Properties that are sets or
ordered pairs remain the same as in AAFP, though all sets must be given in full (i.e. no set-builder
notation). All spaces and blank lines will be ignored. An example specification for a toy fragment
of English is as follows::

    Cmat: comp, {T}}
    Cwh: comp, int, <whq, m>, {T}
    Crel: n, comp, nom, {T}
    Csub: comp, arg, {T}
    T: <phi, m>, {V, Copadj}
    V: v, cat, {Csub, D, Dwh}
    Copadj: v, {A}
    D: n, arg, {Crel, φ}
    Dwh: n, arg, wh, whq, {Crel, φ}
    only: invis, excl, {D}
    OpCR: invis, {φ, N}
    φ: n, nom, phi, low, {noun}, {N}
    ind: n
    N: n, cat, noun, low
    A: cat
    Focfeat: invis, foc, feat, {Cmat, Cwh, Crel, Csub, T, V, Copadj, D, Dwh, only, OpCR, φ, ind, N, A, Focfeat}

    prominence = n, v, cat, noun, comp, arg, wh, whq, nom, phi, int, invis, excl, feat, foc, low

Included with the source code are example input files for the 6 toy fragment grammars in AAFP
chapter 10.

Ouput
=====

ALPAFA defaults to outputting a list of the heads with their categorial and dependent features,
along with a brief description of the algorithm's operation. Feature bundles are separated by tabs
for easy formatting when pasted into word processors - I may incorporate prettier printing in later
versions. There are a number of options for more detailed output of the algorithm's operation and
the categories created by it, discussed in the following section. ::

    Cmat	[-N,-V,-CAT,+COMP,-ARG,-INT]	(-N,-V,-CAT,-COMP,-INVIS)
    Cwh	[-N,-V,-CAT,+COMP,-ARG,+INT]	(-N,-V,-CAT,-COMP,-INVIS)	[uwhq^]
    Crel	[+N,-CAT,+COMP,-ARG,+NOM,-LOW]	(-N,-V,-CAT,-COMP,-INVIS)
    Csub	[-N,-V,-CAT,+COMP,+ARG]	(-N,-V,-CAT,-COMP,-INVIS)
    T	[-N,-V,-CAT,-COMP,-ARG,-INVIS]	(-N,+V)	[uphi^]
    V	[-N,+V,+CAT]	(-CAT,+ARG)
    Copadj	[-N,+V,-CAT,-COMP,-ARG]	(-N,-V,+CAT)
    D	[+N,-CAT,-COMP,+ARG,-WH,-LOW]	(+N,-CAT,-ARG,+NOM)
    Dwh	[+N,-CAT,-COMP,+ARG,+WH,-LOW]	(+N,-CAT,-ARG,+NOM)	[vwhq]
    only	[-N,-V,-CAT,-COMP,-ARG,+INVIS,+EXCL]	(+N,-CAT,-COMP,+ARG,-WH)
    OpCR	[-N,-V,-CAT,-COMP,-ARG,+INVIS,-EXCL,-FEAT]	(+N,+LOW)
    φ	[+N,-CAT,-COMP,-ARG,+NOM,+LOW]	(+N,+CAT)	[vphi,unoun]
    ind	[+N,-CAT,-COMP,-ARG,-NOM,-LOW]
    N	[+N,+CAT,+LOW]		[vnoun]
    A	[-N,-V,+CAT]
    Focfeat	[-N,-V,-CAT,-COMP,-ARG,+INVIS,-EXCL,+FEAT]	()	[vfoc]

    Over 82 loops, 28 of which were non-vacuous, ALPAFA created 67 categories using 12 pairs of categorial features, and assigned 16 non-categorial features.

Usage
=====

ALPAFA is implemented as a command line utility. Use the following syntax to read from an input file
and write the output of ALPAFA to a file (note that this will overwrite existing files of the same
name as the output):

``$ alpafa input_file output_file``

More complex options can be seen with ``$ alpafa -h`` or ``$ alpafa --help``::

    usage: alpafa [-h] [--no_uf] [--no_cselect] [--log] [--categories]
                  [--dependents]
                  input_file output_file

    Applies the algorithm from AAFP to a correctly formatted input file.

    positional arguments:
      input_file    correctly formatted UTF-8 input file
      output_file   name of file to output

    optional arguments:
      -h, --help    show this help message and exit
      --no_uf       do not implement unvalued features
      --no_cselect  do not implement c-selection
      --log         include a log of algorithm operations
      --categories  list all categories before heads
      --dependents  list all dependent features below their relevant categories
                    (implies --categories)
