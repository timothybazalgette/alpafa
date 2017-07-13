'''Defines the command line interface for ALPALFA.'''

import argparse
from .alpafa import Lexicon
from .parse import parse_file, ParserError

def set_args():
    '''Sets command line parameters, and runs ALPAFA.'''

    parser = argparse.ArgumentParser(prog='alpafa',
                                     description='Applies the algorithm from AAFP to a correctly \
                                     formatted input file.')
    parser.add_argument('input_file', help='correctly formatted UTF-8 input file')
    parser.add_argument('output_file', help='name of file to output')

    parser.add_argument('--no_uf', dest='uf', action='store_false',
                        help='do not implement unvalued features')
    parser.add_argument('--no_cselect', dest='cselect', action='store_false',
                        help='do not implement c-selection')
    parser.add_argument('--log', dest='log', action='store_true',
                        help='include a log of algorithm operations')
    parser.add_argument('--categories', dest='cats', action='store_true',
                        help='list all categories before heads')
    parser.add_argument('--dependents', dest='dependents', action='store_true',
                        help='list all dependent features below their relevant categories (implies \
                        --categories)')

    args = parser.parse_args()
    if args.dependents:
        args.cats = True

    return(args.input_file, args.output_file, args.uf, args.cselect, args.log, args.cats,
           args.dependents)

def run_alpafa(input_file, output_file, uf, cselect, log, cats, dependents):
    '''Parse an input file, and apply ALPAFA to its contents, printing the output to a specified
    file.
    '''

    try:
        prominence, heads = parse_file(input_file)
    except FileNotFoundError as e:
        print('alpafa: input failure: ' + str(e)[10:])
        return
    except ParserError as e:
        print('alpafa: parsing failure: {}'.format(e))
        return
    lex = Lexicon(prominence, heads, uf, cselect)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(lex.display(log, cats, dependents))
    print(lex.stats())

def main():
    run_alpafa(*set_args())
