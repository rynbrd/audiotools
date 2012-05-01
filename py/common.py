
import re

class Atom:

    is_quoted_match = re.compile('^".*"$')
    should_quote_match = re.compile('[\s"]')
    escape_seqs = [
        ('\\', '\\\\'),
        ('"', '\\"')]

    def __init__(self, value='', force_quote=False, auto_quote=True):
        self.value = value
        self.auto_quote = auto_quote
        self.force_quote = force_quote

    @classmethod
    def is_quoted(cls, value):
        return cls.is_quoted_match.search(value) is not None

    @classmethod
    def should_quote(cls, value):
        return cls.should_quote_match.search(value) is not None

    @classmethod
    def escape(cls, value):
        for escape in cls.escape_seqs:
            value = value.replace(escape[0], escape[1])
        return value

    @classmethod
    def unescape(cls, value):
        seqs = cls.escape_seqs
        seqs.reverse()
        for escape in seqs:
            value = value.replace(escape[1], escape[0])
        return value

    @classmethod
    def parse(cls, value, force_unescape=False):
        if cls.is_quoted(value):
            return cls(cls.unescape(value[1:-1]), True)
        elif force_unescape:
            return cls(cls.unescape(value), True)
        else:
            return cls(value)

    def __str__(self):
        if self.force_quote or (self.auto_quote and self.should_quote(self.value)):
            return '"%s"' % self.escape(self.value)
        else:
            return self.value

class Line:

    tabval = '  '

    def __init__(self, level=0, atoms=[]):
        self.level = level
        self.atoms = atoms

    @classmethod
    def line_parse(self, line):
        atoms = []
        parts = re.split(' +"|^"', line, 1)
        if parts[0] == '':
            parts = parts[1:]
        items = re.split(' +', parts[0])
        if items[0] == '':
            items = items[1:]
        atoms = [CueAtom(i) for i in items]
        if len(parts) > 1:
            parts = re.split('" +|"$', parts[1], 1)
            atoms.append(CueAtom.parse(parts[0], True))
            if parts[1] != '':
                atoms.extend(self.line_parse(parts[1]))
        return atoms

    @classmethod
    def line_level(self, line):
        level = 0
        while line[:len(self.tabval)] == self.tabval:
            line = line[len(self.tabval):]
            level += 1
        return level

    @classmethod
    def parse(cls, line):
        return cls(cls.line_level(line), cls.line_parse(line))

    def __getitem__(self, item):
        return self.atoms.__getitem__(item)

    def __setitem__(self, item, value):
        return self.atoms.__setitem__(item, value)

    def __len__(self):
        return self.atoms.__len__()

    def __iter__(self):
        return self.atoms.__iter__()

    def __str__(self):
        return '%s%s' % (self.tabval * self.level, ' '.join([str(a) for a in self.atoms]))


