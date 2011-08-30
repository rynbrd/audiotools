#!/bin/python

import re

class CueTrack:

    def __init__(self):
        self.track = None
        self.title = None
        self.performer = None
        self.indices = {}
        self.extra = []

class CueAtom:

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

class CueLine:

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

class CueSection:

    def __init__(self, line=None, children=[]):
        self.line = line
        self.children = children

    @property
    def level(self):
        return None if self.line is None else self.line.level

    @level.setter
    def level(self, value):
        if self.line is not None:
            self.line.level = value

    def append(self, item):
        return self.children.append(item)

    def __getitem__(self, item):
        return self.children.__getitem__(item)

    def __setitem__(self, item, value):
        return self.children.__setitem__(item, value)

    def __len__(self):
        return self.children.__len__()

    def __iter__(self):
        return self.children.__iter__()

    def __str__(self):
        buf = "%s\n" % str(self.line)
        for child in self.children:
            child.level = self.level + 1
            buf += "%s\n" % str(child).rstrip('\n')
        return buf.rstrip('\n')

class CueReader:

    def __init__(self):
        self.items = []

    def parse_lines(self, lines):
        sections = []
        for line in lines:
            if line.strip() == '':
                continue
            line = CueLine.parse(line.rstrip('\n'))

            while line.level < len(sections):
                pop = sections.pop()

            if line.level == 0:
                sections = []
                self.items.append(line)
            elif line.level > 0:
                if len(sections) == 0:
                    assert(line.level == 1)
                    self.items[-1] = CueSection(self.items[-1], [line])
                    sections.append(self.items[-1])
                elif line.level == sections[-1].level + 1:
                    sections[-1].append(line)
                elif line.level == sections[-1].level + 2:
                    sections[-1].children[-1] = CueSection(sections[-1].children[-1], [line])
                    sections.append(sections[-1].children[-1])
                else:
                    raise Exception("Improperly formatted CUE.")

    def parse(self, data):
        self.parse_lines(data.split('\n'))

    def load(self, file):
        f = open(file, 'r')
        self.parse_lines(f)
        f.close()

    def save(self, file):
        pass

    def __getitem__(self, item):
        return self.items.__getitem__(item)

    def __setitem__(self, item, value):
        return self.items.__setitem__(item, value)

    def __len__(self):
        return self.items.__len__()

    def __iter__(self):
        return self.items.__iter__()

    def __str__(self):
        buf = ''
        for item in self.items:
            buf += "%s\n" % str(item)
        return buf

if __name__ == '__main__':
    cf = CueReader()
    cf.load_file('test/archive/Alestorm/Back Through Time.cue')
    print str(cf).rstrip('\n')

