import string
from collections import namedtuple

__all__ = ["Formatter"]

Section = namedtuple("Section", "name tokens data scopes conversion format")
Token = namedtuple("Token", "text field fieldname marker spec conversion")

class Formatter(string.Formatter):
    converters = {}
    markers = {
        '#': "startsection",
        '/': "endsection",
        '%': "comment",
    }
    markerlen = 1

    def vformat(self, string, args, kwargs):
        return self._vformat(string, args, kwargs)

    def _vformat(self, string, args, kwargs):
        tokens = self.tokenize(string)
        return self.formatsection(tokens, kwargs)

    def tokenize(self, string):
        for text, field, spec, conversion in self.parse(string):
            fieldname = field
            marker = None
            if field and len(field) >= self.markerlen:
                indicator = field[:self.markerlen]
                if indicator in self.markers:
                    marker = self.markers[indicator]
                    field = field[self.markerlen:]
                
            yield Token(text, field, fieldname, marker, spec, conversion)

    def formatsection(self, tokens, data, scopes=[]):
        sections = []
        result = []
        depth = 0

        for token in tokens:
            section = sections and sections[-1] or Section(None, [], {}, [], None, None)
            text = token.text

            # Short circuit parsing if...
            if depth == 0 and section.name == token.field and token.marker == "endsection":
                # ...we're closing the topmost section (depth=0); render the
                # subsection and continue.
                section.tokens.append(Token(text, None, None, None, None, None))
                _data, _ = self.get_field(token.field, (), [data] + scopes)
                for d in _data:
                    content = self.formatsection(section.tokens, d, [data] + scopes)
                    if section.conversion:
                        content = self.convert_field(content, section.conversion)
                    if section.format:
                        content = self.format_field(content, section.format)
                    result.append(content)
                sections.pop()
                continue
            elif section.name is not None:
                # ...we're in a section; add our token to the section's list and
                # continue.
                section.tokens.append(token)

                # Track depth (but not the subsections themselves).
                if token.marker == "startsection": depth += 1
                elif token.marker == "endsection": depth -= 1
                continue

            # Always add the token's text to the result. Since the parser produces
            # tokens with preceding text, this has to happen early.
            if text:    
                result.append(text)

            if token.marker == "startsection":
                section = Section(name=token.field, tokens=[], data=data,
                    scopes=scopes, conversion=token.conversion, format=token.spec)
                sections.append(section)
            elif token.marker == "endsection":
                # Already handled.
                pass
            elif token.field is not None:
                # Perform the usual string formatting on the field.
                obj, _ = self.get_field(token.field, (), [data] + scopes)
                obj = self.convert_field(obj, token.conversion)
                spec = super(Formatter, self)._vformat(token.spec, (), data, (), 2)
                result.append(self.format_field(obj, spec))

        return ''.join(result)

    def get_value(self, field, args, scopes):
        _scopes = list(scopes)
        value = ''
        while _scopes and value == '':
            scope = _scopes.pop(0)
            value = scope.get(field, '')

        return value

    def convert_field(self, value, conversion):
        converter = self.converters.get(conversion, None)
        if callable(converter):
            value = converter(value)
        else:
            value = super(Formatter, self).convert_field(value, conversion)
        return value
