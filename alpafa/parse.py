'''Utlities for parsing correctly formatted UTF-8 input files, and return them as a prominence list
and a list of alpafa.Head objects.
'''

from .alpafa import Head

class ParserError(Exception):
    '''For parser-specific errors.'''
    pass

class ParseHead():
    '''Parser for input file lines which represent a head. Designed to be created once per line,
    with self.parse immediately being called, which returns a parsed frozenset of properties.'''

    def __init__(self, linenum, line):

        self._linenum = linenum # for more informative errors
        self._name, separator, properties = line.partition(':')
        if not (self._name and separator):
            raise ParserError("Invalid syntax on line {} of input".format(self._linenum))
        self._properties = properties.split(',') # split but unparsed properties list

        # set during self.parse
        self._index = None # current position in parsing this list
        self._item = None # current object in list
        self._setstart = None
        self._tupstart = None

        # always have the same initial values
        self._prevobjend = 0 # position of last set or tuple
        self._final_properties = []

    def _open_bracket(self, tup=False):
        '''Called when the parser comes across an open bracket - checks for illicit embeddings,
        and updates instance attributes appropriately.

        :param tup: < rather than {
        '''

        if self._tupstart is not None or self._setstart is not None:
            raise ParserError("Set inside set on line {} of input".format(self._linenum))
        # we're done with the chunk of properties up to here
        self._final_properties += self._properties[self._prevobjend:self._index]
        if tup:
            self._tupstart = int(self._index)
        else:
            self._setstart = int(self._index)

    def _close_bracket(self, tup=False):
        '''Called when the parser comes across a closed bracket - checks for invalid closings (and
        makes sure ordered pairs are well-formed), then adds the new subobject to
        self.final_properties and updates instance attributes appropriately.

        :param tup: > rather than }
        '''
        if tup and (self._tupstart is None or self._setstart is not None or
                    self._index - self._tupstart != 1 or self._item != 'm>'):
            raise ParserError("Invalid ordered set on line {} of input".format(self._linenum))
        if not tup and (self._setstart is None or self._tupstart is not None):
            raise ParserError("Invalid set on line {} of input".format(self._linenum))
        if tup:
            newtup = self._properties[self._tupstart:self._index+1]
            newtup[0] = newtup[0].lstrip('<')
            newtup[-1] = newtup[-1].rstrip('>')
            self._final_properties.append(tuple(newtup))
            self._tupstart = None
        else:
            newset = self._properties[self._setstart:self._index+1]
            newset[0] = newset[0].lstrip('{')
            newset[-1] = newset[-1].rstrip('}')
            self._final_properties.append(frozenset(newset))
            self._setstart = None

        self._prevobjend = self._index+1

    def parse(self):
        '''Parses self._properties into frozenset of properties, which is combined with self.Name to
        return a Head object.
        '''

        for i, item in enumerate(self._properties):
            self._index = i
            self._item = item

            if item.startswith('{'):
                self._open_bracket()
            elif item.startswith('<'):
                self._open_bracket(tup=True)

            if item.endswith('}'):
                self._close_bracket()
            elif item.endswith('>'):
                self._close_bracket(tup=True)

        if self._setstart is not None or self._tupstart is not None:
            raise ParserError("Unclosed bracket on line {} of input".format(linenum))

        self._final_properties += self._properties[self._prevobjend:]

        return Head(self._name, frozenset(self._final_properties))

def parse_file(input_file):
    '''Takes a correctly formatted input file and returns a parsed prominence order and list of
    Head objects.
    '''

    prominence = []
    heads = []
    with open(input_file, encoding='utf-8') as f:
        for i, line in enumerate(f):
            line = line.replace(' ', '').strip()
            if line.startswith("prominence="):
                prominence = line[11:].split(',')
            elif line != '':
                heads.append(ParseHead(i+1, line).parse())
    if not heads:
        raise ParserError("No heads found")
    if not prominence:
        raise ParserError("No prominence order found")
    if '' in prominence:
        raise ParserError("Zero length feature in prominence order")
    return prominence, heads
