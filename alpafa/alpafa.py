'''Core classes associated with ALPAFA. Defines Head, Category, and Lexicon objects. Lexicons are
created using a set of heads and a prominence order, and the Lexicon._learn method builds categories
based on these, following the alogrithm in AAFP. Categories and heads use a ternary d list to define
their categorial features, which is populated by Lexicon.category_properties. C-selectional features
are represented as actual Category objects assigned to Head.c_feat and Category.c_feat. Most of the
heavy algorithmic lifitng is done methods of Lexcion, but Category.assign and Category.divide are
also fairly key.
'''

class FeatureBearer():
    '''Defines some display methods common to Head and Category'''

    def __init__(self):
        self.d = []
        self.feats = []
        self.c_feat = None
        self.category_properties = [] # properties that are used to define categories

    def dstring(self, c_select=False):
        '''Returns a string of self's categorial feature bundle.

        :param c_select: c-selectional feature bundle.
        '''

        def catfeats():
            '''Converts d to a readable +/- feature string.'''

            for i, digit in enumerate(self.d):
                if digit == 2:
                    yield '+' + self.category_properties[i]
                elif digit == 1:
                    yield '-' + self.category_properties[i]

        if c_select:
            return '(' + ','.join(catfeats()) + ')'
        return '[' + ','.join(catfeats()) + ']'

    def c_select(self):
        '''Returns a str of self's c-selectional feature.'''

        if self.c_feat is None:
            return ''
        return self.c_feat.dstring(c_select=True)

    def featstring(self):
        '''Returns a str of self's non-categorial feature bundle'''

        if self.feats:
            return '[' + ','.join(self.feats) + ']'
        return ''

class Head(FeatureBearer):
    '''Instances of this class correspond to linguistic heads, and recieve their name and properties
    from the input. During the course of the algorithm they are divided into categories, and
    assigned categorial, non-categorial, and c-selectional features.
    '''

    def __init__(self, name, properties):
        FeatureBearer.__init__(self)
        self.name = name
        self.properties = properties

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def spec(self, c_select_choice=False):
        '''Returns a full (tabbed) specifcation str for self.

        :param c_select_choice: include c-selectional features
        '''

        if c_select_choice is True:
            spec = (self.name, self.dstring(), self.c_select(), self.featstring())
        else:
            spec = (self.name, self.dstring(), self.featstring())
        return '\t'.join(spec).rstrip('\t')

class Category(FeatureBearer):
    '''Instances of this class correspond to categories of linguistic heads, defined by a bundle of
    categorial features (d). Initially the only category is the category of all heads, but in during
    the course of the algorithm this is divided into smaller categories (by Category.divide), each
    of which can be assigned non-categorial and c-selectional features (by Category.assign).
    '''

    def __init__(self, container, d, contents):
        FeatureBearer.__init__(self)
        self.container = container # lexicon containing the category
        self.log = container.log # log of operations carried out by the algorithm
        self.category_properties = container.category_properties # overriding base class
        self.d = d # overriding base class
        self.contents = contents

    def __repr__(self):
        return self.dstring()

    def __str__(self):
        return self.dstring()

    def __iter__(self):
        return iter(self.contents)

    def __len__(self):
        '''len(X) returns the number of categorial features that X bears.'''

        return sum(1 for i in self.d if i != 0)

    def __ge__(self, other):
        '''X >= Y iff Y is a subcategory of X: i.e. Y has a superset of X's categorial features.'''

        for i, j in zip(self.d, other.d):
            if i != 0 and i != j:
                return False
        return True

    def lhd(self):
        '''Returns a display string of the values of l, h, and d.'''

        l = len(self)
        h = len(self.contents)
        d = ''.join(str(i) for i in self.d)
        return 'l = {}, h = {}, d = {}'.format(l, h, d)

    def spec(self, cats_dep_choice=False):
        '''Returns a full (tabbed) specifcation str for self, including non-categorial and
        c-selectional features if specified by the user.

        :param cats_dep_choice: show dependent features beneath categories
        '''

        spec = (self.dstring(), self.lhd(), ','.join(str(head) for head in self.contents))
        if cats_dep_choice and (self.c_feat or self.feats):
            return '\t'.join(spec) + '\n' + self.c_select() + self.featstring()
        return '\t'.join(spec)

    def assign(self, feat):
        '''Assigns a non-categorial or c-selectional feature to self and all the heads it contains.
        '''

        if isinstance(feat, Category):
            self.c_feat = feat
            for head in self:
                head.c_feat = feat
            self.log.append('Assign {} to {}'.format(self.c_select(), self.dstring()))
        else:
            self.feats.append(feat)
            for head in self:
                head.feats.append(feat)
            self.log.append('Assign [{}] to {}'.format(feat, self.dstring()))

    def divide(self, headswithp):
        '''Divide any subcategories of self that have at least one head in headswithp and at least
        one not in headswithp new [+P] and [-P] variants. Returns a list of newly created
        categories.
        '''

        new_cats = []
        minus_p = {head for head in self.contents if head not in headswithp}

        # Extend head features.
        for head in self.container.heads:
            if head in headswithp:
                head.d = head.d[:-1] + [2]
            elif head in minus_p:
                head.d = head.d[:-1] + [1]

        for cat in list(self.container):
            if (self >= cat and
                    headswithp.intersection(set(cat.contents)) != set() and
                    set(cat.contents) - headswithp != set()):
            # i.e. cat is a subcat of self, and contains all heads with p and at least one head
            # without p
                cat_ps = [head for head in cat if head in headswithp]
                cat_others = [head for head in cat if head in minus_p]
                cat_plus_p = Category(self.container, cat.d[:-1] + [2], cat_ps)
                cat_minus_p = Category(self.container, cat.d[:-1] + [1], cat_others)
                self.container.categories.extend([cat_plus_p, cat_minus_p])
                new_cats.extend(self.container.categories[-2:])
        self.log.append('Divide {} into [{}]'
                        .format(self.dstring(), self.category_properties[-1]))
        return new_cats

class Lexicon():
    '''Defines a "container" for all the Heads, which are then divided up into categories by the
    assignment of features to these heads via a specified prominence order. Lexicon._learn starts
    the main algorithm, which also uses Lexicon._add_dependent_feature and
    Lexicon._divide_categories, with the help of Lexicon.headswith. The remaining methods are
    largely for display purposes.
    '''

    def __init__(self, prominence, heads, uf_choice=True, c_select_choice=True):
        ''':param uf_choice: implement unvalued features
           :param c_select_choice: implement c-selection
        '''

        # parameters
        self.uf_choice = uf_choice
        self.c_select_choice = c_select_choice

        # core setup
        self.prominence = prominence
        self.heads = heads
        self.initial_prominence = list(prominence)
        self._invis_index = None # position of the special "invis" cateorial feature
        self.category_properties = [] # properties that are used to define categories
        self.log = []  # log of operations carried out by the algorithm
        self.categories = [Category(self, [], self.heads)]
        for head in self.heads:
            head.container = self
            head.category_properties = self.category_properties
        if self.c_select_choice:
            self.prominence.append(self.categories[0])

        self._learn()

    def __iter__(self):
        return iter(self.categories)

    def __repr__(self):
        return '\n'.join(cat.spec() for cat in self)

    def headswith(self, p):
        '''Helper function for the main algorithm. Returns a set of the heads bearing the current
        property p, and a bool stating whether or not that property triggers movement.
        '''

        move = False
        if isinstance(p, Category):
            headswithp = {head for head in self.heads if
                          set([h.name for h in p.contents]) in head.properties}
            return headswithp, move
        else:
            headswithp = {head for head in self.heads if p in head.properties}
        if headswithp == set():
        # no singleton sets, so must be a movement feature
            headswithp = {head for head in self.heads if (list(p)[0], 'm') in head.properties}
            move = True

        return headswithp, move

#---------------------------------------------------------------------------------------------------
# Main body of the algorithm, annotated with the step numbers from (103) of AAFP chapter 1:
#---------------------------------------------------------------------------------------------------

    def _learn(self):
        '''Loops over the prominence order, first attempting to assign p as a dependent feature of
        the "largest" possible category, and if this fails, dividing the "smallest" possible
        category (and its relevant subcategories) into +P and -P variants.
        '''

        # (i, xv) identify next undescribed property p
        for p in self.prominence:
            non_cat = False
            headswithp, move = self.headswith(p)

            # (ii) search for "largest" category coextensive with p
            for cat in self:
                if set(cat.contents) == headswithp:
                    non_cat = True
                    # go to (iii)
                    self._add_dependent_feature(p, cat, move)
                    break

            if non_cat is False and isinstance(p, str) and headswithp != set():
            # (x) is p a bare property?
                # go to (xi)
                self._divide_categories(p, headswithp)

        self.acquired = True

    def _add_dependent_feature(self, prop, category, move):
        '''Adds the appropriate dependent feature, depending on the nature of prop. Equivalent to
        the schema in (102) of AAFP chapter 2. Note that move is a bool.
        '''

        if isinstance(prop, str):
        # (iii) is p a bare property?
            if self.uf_choice:
                # (iv) assign [vp], add {p} to prominence
                category.assign('v' + prop)
                self.prominence.append({prop})
            else:
                # (iv) assign [vp]
                category.assign(prop)

        elif isinstance(prop, Category):
        # (v) is p a category?
            # (vi) assign corresponding c-selectional feature
            if category.c_feat is None:
                category.assign(prop)

        elif move:
        # (vii) does p trigger movement?
            # (viii) assign [up^]
            category.assign('u' + list(prop)[0] + '^') # (viii)

        else:
            # (ix) assign [up]
            category.assign('u' + list(prop)[0]) # (ix)

    def _divide_categories(self, prop, headswithprop):
        '''Divides the chosen category and all relevant subcategories into +PROP and -PROP variants.
        '''

        if prop == 'invis':
            self._invis_index = len(self.category_properties)

        # add new categorial feature to lexicon
        self.category_properties.append(prop.upper())
        for cat in self:
            cat.d = cat.d + [0]
        for head in self.heads:
            head.d = head.d + [0]

        # (xi) search for "smallest" category
        for category in reversed(self.categories):
            if headswithprop < set(category.contents):
                # (xii, xiii) assign categorial features to the appropriate heads and categories
                new_cats = category.divide(headswithprop)
                break

        # (xiv) reorder categories and append new visible categories to prominence
        self.categories.sort(key=lambda k: (-len(k), len(k.contents), k.d), reverse=True)
        if self.c_select_choice:
            if self._invis_index is not None:
                new_cats = [cat for cat in new_cats if cat.d[self._invis_index] != 2]
            self.prominence.extend([cat for cat in self if cat in new_cats])

#---------------------------------------------------------------------------------------------------

    def display(self, divlog_choice=True, cats_choice=True, cats_dep_choice=False):
        '''Takes a number of optional parameters, and returns a tabbed specification of the lexicon.

        :param divlog_choice: display self.log
        :param cats_choice: display categories
        :param cats_dep_choice: display dependent features below categories
        '''

        output = ''
        if divlog_choice:
            output += '\n'.join(self.log) + '\n\n'
        if cats_choice:
            output += '\n'.join(cat.spec(cats_dep_choice=cats_dep_choice) for cat in self) + '\n\n'
        output += '\n'.join(head.spec(self.c_select_choice) for head in self.heads)
        output += '\n\n' + self.stats()
        return output

    def stats(self):
        '''Returns a string containing some information on the algorithm's behaviour.'''

        def agree(number, y=False):
            '''Returns a tuple of number and its agreement inflection.

            :param y: for irregular "y/ies" plurals
            '''

            agree = [number]
            if y:
                if number == 1:
                    agree += ['y']
                else:
                    agree += ['ies']
            else:
                if number == 1:
                    agree += ['']
                else:
                    agree += ['s']
            return tuple(agree)

        loops = agree(len(self.prominence))
        nonvacs = len(self.log)
        cats = agree(len(self.categories), y=True)
        catfeats = agree(len(self.category_properties))
        noncatfeats = agree(len(self.log) - len(self.category_properties))
        stats = 'Over {} loop{}, '.format(*loops)
        if loops == 1:
            stats += 'which was non-vacuous, '
        elif loops == nonvacs:
            stats += 'all of which were non-vacuous, '
        elif loops != 0:
            stats += '{} of which were non-vacuous, '.format(nonvacs)
        stats += 'ALPAFA created {} categor{} '.format(*cats)
        stats += 'using {} pair{} of categorial features, '.format(*catfeats)
        stats += 'and assigned {} non-categorial feature{}.'.format(*noncatfeats)
        return stats
