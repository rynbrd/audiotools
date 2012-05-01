
import re

class CueTrack:

    def __init__(self):
        self.track = None
        self.title = None
        self.performer = None
        self.indices = {}
        self.extra = []


class CueCollection:

    def __init__(self, lines=[]):
        self.lines = list(lines)

    def __getitem__(self, item):
        return self.lines.__getitem__(item)

    def __setitem__(self, item, value):
        return self.lines.__setitem__(item, value)

    def __len__(self):
        return self.lines.__len__()

    def __iter__(self):
        return self.lines.__iter__()

    def append(self, line):
        self.lines.append(line)

    def find(self, name, subname=None):
        if subname is not None:
            return [ lines for lines in self.lines if lines[0].value == name and lines[1].value == subname ]
        else:
            return [ lines for lines in self.lines if lines[0].value == name ]

    def find_first(self, name, subname=None):
        lines = self.lines(name, subname)
        return None if len(lines) == 0 else lines[0]

    def get_value(self, name, subname=None):
        line = self.find_first(name, subname)
        if line is None:
            return None
        return line[1] if subname is None else line[2]

    def set_value(self, name, value, subname=None):
        line = self.find_first(name, subname)
        if line is None:
            if subname is None:
                line = CueLine([CueAtom(name), CueAtom(value, True)])
            else:
                line = CueLine([CueAtom(name), CueAtom(subname), CueAtom(value, True)])
            self.append(line)
        elif subname is None:
            line[1].value = value
        else:
            line[2].value = value

class CueSection(CueLine):

    def __init__(self, line, children=[]):
        CueLine.__init__(self, line.level, line.atoms)
        self.children = CueCollection(children)

    def __str__(self):
        buf = "%s\n" % str(CueLine.__str__(self))
        for child in self.children:
            child.level = self.level + 1
            buf += "%s\n" % str(child).rstrip('\n')
        return buf.rstrip('\n')

    @classmethod
    def factory(self, line, children=[]):
        if line[0].value == 'TRACK':
            return CueTrack(line, children)
        elif line[0].value == 'FILE':
            return CueFile(line, children)
        else:
            return CueSection(line, children)

class CueTrack(CueSection):

    def __init__(self, line, children=[]):
        CueSection.__init__(self, line, children)

    @property
    def number(self):
        return int(self.__getitem__(1).value)

    @number.setter
    def number(self, value):
        self.line[1].value = '%02d' % int(value)

    @property
    def type(self):
        return self.line[2].value

    @type.setter
    def type(self, value):
        self.line[2].value = value

    @property
    def performer(self):
        return self.children.get_value('PERFORMER')

    @performer.setter
    def performer(self, value):
        self.children.set_value('PERFORMER', value)

class CueFile(CueSection):

    def __init__(self, line, children=[]):
        CueSection.__init__(self, line, children)

    @property
    def file(self):
        return self.line[1].value

    @file.setter
    def file(self, value):
        self.line[1].value = value

    @property
    def type(self):
        return self.line[2].value

    @file.setter
    def type(self, value):
        self.line[2].value = value

    @property
    def tracks(self):
        return self.children.find('TRACK')

class CueParser(CueCollection):

    def __init__(self):
        CueCollection.__init__(self)

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
                self.lines.append(line)
            elif line.level > 0:
                if len(sections) == 0:
                    assert(line.level == 1)
                    self.lines[-1] = CueSection.factory(self.lines[-1], [line])
                    sections.append(self.lines[-1])
                elif line.level == sections[-1].level + 1:
                    sections[-1].children.append(line)
                elif line.level == sections[-1].level + 2:
                    sections[-1].children[-1] = CueSection.factory(sections[-1].children[-1], [line])
                    sections.append(sections[-1].children[-1])
                else:
                    raise Exception("Improperly formatted CUE.")
            else:
                raise Exception("Improperly formatted CUE.")

    def parse(self, data):
        self.parse_lines(data.split('\n'))

    def load(self, file):
        f = open(file, 'r')
        self.parse_lines(f)
        f.close()

    def save(self, file):
        f = open(file, 'w')
        f.write(self.__str__().rstrip())
        f.close()

    @property
    def rem(self):
        return self.find('REM')

    @property
    def performer(self):
        return self.get_value('PERFORMER')

    @performer.setter
    def performer(self, value):
        self.set_value('PERFORMER', value)

    def __str__(self):
        buf = ''
        for line in self.lines:
            buf += "%s\n" % str(line)
        return buf

