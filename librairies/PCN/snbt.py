"""Parse Single Tag(return Tag):
> Tag.parse(TEXT)
----------------------------------------------------------
Parse Multiple Tags(no name):
> index = 0
> tags = []
> while index < len(TEXT) - 1
>     key, value, index = Tag.parse_key_value(TEXT, index)
>     tags.append(Tag.parse(value))
----------------------------------------------------------
Parse Multiple Tags(with name):
> index = 0
> tags = {}
> while index < len(TEXT) - 1
>     key, value, index = Tag.parse_key_value(TEXT, index)
>     tags[key] = Tag.parse(value)
----------------------------------------------------------
Get Item of Compound Tag(return Tag):
> compound['key']
----------------------------------------------------------
Get Item of List Tag(return Tag):
> list[index]
----------------------------------------------------------
Iterate over Items in Compound Tag:
> for key in compound.tags():
>     tag = compound[key]
----------------------------------------------------------
Iterate over Items in List Tag:
> for tag in list:
>     # do what ever here
>     pass
----------------------------------------------------------
Check Type(return Boolean):
> tag.type_match(type)

Example: tag.type_match(TagByte)

Usage: the type of the tag read may not be the type in
game, such as Count:1 is parsed as TagInt, but it should
be TagByte in game. This function can check if the tag
can be converted into the type in game.
---------------------------------------------------------
String representation of Tag(return string, no indent):
> str(tag)
----------------------------------------------------------
Pretty print(return string, with indent and line break)
> tag.tree(0)
----------------------------------------------------------
Error: NbtException
Sources of error:
+ Illegal black slash outside string, such as 'say \\nhi'
+ Imbalance bracket, such as '{[}]'
+ No ending bracket, such as '{'
+ No ending quote, such as '"abcd'"""

import re
import json

class NbtException(Exception):
    def __init__(self, message):
        self.message = message
class Tag:
    strict = False
    def __init__(self, value = None):
        self.value = value
    def __str__(self):
        return self.value
    def parse(text):
        success = False
        for i in (TagByte, TagCompound, TagDouble, TagFloat, TagInt, TagList, \
            TagLong, TagShort, TagString):
            try:
                success, tag = i.parse(text)
            except NbtException as error:
                raise error
            if success:
                return tag
    def parse_key_value(text, index):
        has_key = True
        value = ''
        key = ''
        temp = []
        brackets = []
        string = False
        escape = False
        for j in range(index, len(text)):
            i = text[j]
            if string:
                if escape:
                    escape = False
                elif i == '\\':
                    escape = True
                elif i == '"':
                    string = False
                temp.append(i)
            else:
                if escape:
                    if i == '"':
                        raise NbtException('Illegal \\" pattern at char %d.\n%s\n%s' % \
                                (j+1,'...' + text[j-50 if j>50 else 0:j+1],\
                                ' '*(j-(j-50 if j>50 else 0)+3) + '^'))
                    else:
                        escape = False
                elif i == ':':
                    if has_key:
                        key = ''.join(temp)
                        temp.clear()
                        has_key = False
                        continue
                elif i == '{' or i == '[':
                    has_key = False
                    brackets.append(i)
                elif i == '}':
                    if len(brackets) == 0 or brackets[-1] == '[':
                        raise NbtException('Imbalance bracket at char %d.\n%s\n%s' % \
                            (j+1,'...' + text[j-50 if j>50 else 0:j+1],\
                            ' '*(j-(j-50 if j>50 else 0)+3) + '^'))
                    brackets.pop()
                elif i == ']':
                    if len(brackets) == 0 or brackets[-1] == '{':
                        raise NbtException('Imbalance bracket at char %d.\n%s\n%s' % \
                            (j+1,'...' + text[j-50 if j>50 else 0:j+1],\
                            ' '*(j-(j-50 if j>50 else 0)+3) + '^'))
                    brackets.pop()
                elif i == '"':
                    string = True
                elif i == '\\':
                    escape = True
                elif i == ',':
                    if len(brackets) == 0:
                        value = ''.join(temp)
                        return key.strip(), value.strip(), j+1
                temp.append(i)
        if len(brackets) > 0:
            raise NbtException('No ending bracket.\n%s' % text[index:])
        if string:
            raise NbtException('No ending quote\n%s' % text[index:])
        value = ''.join(temp)
        return key.strip(), value.strip(), len(text)
    def tree(self, level):
        return str(self)
    def str_to_class_name(text):
        if text == 'byte':
            return TagByte
        elif text == 'double':
            return TagDouble
        elif text == 'float':
            return TagFloat
        elif text == 'int':
            return TagInt
        elif text == 'list':
            return TagList
        elif text == 'long':
            return TagLong
        elif text == 'short':
            return TagShort
        elif text == 'string':
            return TagString
        elif text == 'int array':
            return TagIntArray
        else:
            return TagCompound
class TagByte(Tag):
    pattern = re.compile(r'(-?\d+)b|(true|false)')
    MAX = 127
    MIN = -128
    def __str__(self):
        return str(self.value) + "b"
    def parse(text):
        match = TagByte.pattern.fullmatch(text.lower())
        if match is not None:
            value = 0
            if match.group(2) == 'true':
                value = 1
            elif match.group(2) == 'false':
                value = 0
            else:
                value = int(match.group(1))
                if value > TagByte.MAX or value < TagByte.MIN:
                    return False, None
            return True, TagByte(value)
        return False, None
    def type_match(self, nbt_type):
        if Tag.strict:
            return nbt_type is TagByte
        return nbt_type in [TagByte]
class TagCompound(Tag):
    def __contains__(self, item):
        return item in self.value
    def __getitem__(self, key):
        return self.value[key]
    def __setitem__(self, key, value):
        self.value[key] = value
    def __delitem__(self, key):
        del(self.value[key])
    def __init__(self, value = {}):
        self.value = value
    def __str__(self):
        temp = []
        for key, tag in self.value.items():
            temp.append(key + ":" + str(tag))
        return '{%s}' % ','.join(temp)
    def keys(self):
        return self.value.keys()
    def parse(text):
        if text[0] == '{' and text[-1] == '}':
            index = 0
            tags = {}
            while index < len(text[1:-1]):
                try:
                    key, value, index = Tag.parse_key_value(text[1:-1], index)
                except NbtException as error:
                    raise NbtException('%s\nTag stack:\n>    ' % error.message)
                if key == '':
                    raise NbtException('Should have key\nTag stack:\n>    ')
                try:
                    tags[key] = Tag.parse(value)
                except NbtException as error:
                    raise NbtException('%s\n>    %s'%(error.message, key))
            return True, TagCompound(tags)
        return False, None
    def tree(self, level):
        temp = []
        for key in self.value:
            temp.append('    ' * (level+1) + key + ":" + self.value[key].tree(level+1))
        if len(temp) > 0:
            return '{\n%s\n%s}' % (',\n'.join(temp), '    ' * level)
        else:
            return '{}'
    def type_match(self, nbt_type):
        if Tag.strict:
            return nbt_type is TagCompound
        return nbt_type in [TagCompound]
class TagDouble(Tag):
    pattern = re.compile(r'(-?\d+\.\d+[dD]?)|(-?\d+[dD])')
    def __str__(self):
        return "%.6fd" % self.value
    def parse(text):
        match = TagDouble.pattern.fullmatch(text)
        if match is not None:
            return True, \
                TagDouble(float(text if text[-1] not in ['d', 'D'] else text[:-1]))
        return False, None
    def type_match(self, nbt_type):
        if Tag.strict:
            return nbt_type is TagDouble
        return nbt_type in [TagDouble]
class TagFloat(Tag):
    pattern = re.compile(r'(-?\d+(\.\d+)?)[fF]')
    def __str__(self):
        return "%.5ff" % self.value
    def parse(text):
        match = TagFloat.pattern.fullmatch(text)
        if match is not None:
            return True, TagFloat(float(match.group(1)))
        return False, None
    def type_match(self, nbt_type):
        if Tag.strict:
            return nbt_type is TagFloat
        return nbt_type in [TagFloat]
class TagInt(Tag):
    pattern = re.compile(r'-?\d+')
    MAX = 2147483647
    MIN = -2147483648
    def __str__(self):
        return str(self.value)
    def parse(text):
        match = TagInt.pattern.fullmatch(text)
        if match is not None:
            value = int(text)
            if value > TagInt.MAX or value < TagInt.MIN:
                return False, None
            return True, TagInt(value)
        return False, None
    def type_match(self, nbt_type):
        if Tag.strict:
            return nbt_type is TagInt
        return nbt_type in [TagInt, TagByte, TagShort]
class TagIntArray(Tag):
    pass
class TagList(Tag):
    def __contains__(self, item):
        return item in self.value
    def __getitem__(self, key):
        return self.value[key]
    def __setitem__(self, key, value):
        self.value[key] = value
    def __delitem__(self, key):
        del(self.value[key])
    def __len__(self):
        return len(self.value)
    def __init__(self, value = []):
        self.value = value
    def __str__(self):
        temp = []
        for tag in self.value:
            temp.append(str(tag))
        return '[%s]' % ','.join(temp)
    def parse(text):
        if text[0] == '[' and text[-1] == ']':
            index = 0
            tags = []
            while index < len(text[1:-1]):
                try:
                    key, value, index = Tag.parse_key_value(text[1:-1], index)
                except NbtException as error:
                    raise NbtException('%s\nTag stack:\n>    ' % error.message)
                try:
                    tags.append(Tag.parse(value))
                except NbtException as error:
                    raise NbtException('%s\n>    [%d]'%(error.message, len(tags)))
            return True, TagList(tags)
        return False, None
    def tree(self, level):
        temp = []
        for tag in self.value:
            temp.append('    ' * (level+1) + tag.tree(level+1))
        if len(temp) > 0:
            return '[\n%s\n%s]' % (',\n'.join(temp), '    ' * level)
        else:
            return '[]'
    def type_match(self, nbt_type):
        if nbt_type == TagIntArray:
            for i in self:
                if not i.type_match(TagInt):
                    return False
            return True
        return nbt_type == TagList
class TagLong(Tag):
    pattern = re.compile(r'(-?\d+)[lL]')
    MAX = 9223372036854775807
    MIN = -9223372036854775808
    def __str__(self):
        return str(self.value) + "l"
    def parse(text):
        match = TagLong.pattern.fullmatch(text)
        if match is not None:
            value = int(match.group(1))
            if value > TagLong.MAX or value < TagLong.MIN:
                return False, None
            return True, TagLong(value)
        return False, None
    def type_match(self, nbt_type):
        if Tag.strict:
            return nbt_type is TagLong
        return nbt_type in [TagLong]
class TagShort(Tag):
    MAX = 32767
    MIN = -32768
    pattern = re.compile(r'(-?\d+)[sS]')
    def __str__(self):
        return str(self.value) + "s"
    def parse(text):
        match = TagShort.pattern.fullmatch(text)
        if match is not None:
            value = int(match.group(1))
            if value > TagShort.MAX or value < TagShort.MIN:
                return False, None
            return True, TagShort(value)
        return False, None
    def type_match(self, nbt_type):
        if Tag.strict:
            return nbt_type is TagShort
        return nbt_type in [TagShort]
class TagString(Tag):
    def __str__(self):
        if TagString.need_escape(self.value) or \
            re.fullmatch(r'\d+(\.\d+)?[bBdDfFlLsS]?', self.value) is not None or \
            (self.value[0] in ['{', '['] and self.value[-1] in ['}', ']']):
            return '"' + TagString.escape(self.value) + '"'
        else:
            return self.value
    def escape(text):
        return text.replace('\\', '\\\\').replace('"', '\\"')
    def need_escape(text):
        brackets = []
        in_string = False
        for char in text:
            if in_string:
                if char == '"':
                    in_string = False
                elif char == '\\':
                    return True
            else:
                if char == '{' or char == '[':
                    brackets.append(char)
                elif char == '}':
                    if len(brackets) == 0:
                        return True
                    if not brackets.pop() == '{':
                        return True
                elif char == ']':
                    if len(brackets) == 0:
                        return True
                    if not brackets.pop() == '[':
                        return True
                elif char == ',':
                    if len(brackets) == 0:
                        return True
                elif char == '"':
                    in_string = True
                elif char == '\\':
                    return True
        if len(brackets) > 0:
            return True
        if in_string:
            return True
        return False
    def parse(text):
        if text[0] == '"' and text[-1] == '"':
            return True, TagString(TagString.unescape(text[1:-1]))
        return True, TagString(TagString.unescape(text))
    def unescape(text):
        return text.replace('\\"', '"').replace('\\\\', '\\')
    def type_match(self, nbt_type):
        return nbt_type is TagString

def load_json(json_text):
    return json.loads(json_text)

def check_compound_items(rules, compound, base_tag):
    for key in compound.keys():
        if key not in rules[base_tag]:
            raise NbtException('Unknown tag name\nTag stack:\n>    %s' % key)

        if '|' in rules[base_tag][key]['type']:
            match = False
            for type_name in rules[base_tag][key]['type'].split('|'):
                if compound[key].type_match(Tag.str_to_class_name(type_name)):
                    match = True
                    break
            if not match:
                raise NbtException('Invalid tag type, should be %s\nTag stack:\n>    %s'\
                    % (rules[base_tag][key]['type'], key))
            return
        tag_type = Tag.str_to_class_name(rules[base_tag][key]['type'])
        if not compound[key].type_match(tag_type):
            raise NbtException('Invalid tag type, should be %s\nTag stack:\n>    %s'\
                % (rules[base_tag][key]['type'], key))

        if tag_type is TagList:
            if rules[base_tag][key]['count'] > 0 and \
                len(compound[key]) != rules[base_tag][key]['count']:
                raise NbtException('Invalid number of items\nTag stack:\n>    %s' % key)
            tag_type = Tag.str_to_class_name(rules[base_tag][key]['subtype'])
            check_value = 'values' in rules[base_tag][key]
            check_range = 'range' in rules[base_tag][key]

            index = 0
            for tag in compound[key]:
                if not tag.type_match(tag_type):
                    raise NbtException(\
                        'Invalid item type, should be %s\nTag stack:\n>    %s[%d]' %\
                        (rules[base_tag][key]['subtype'], key, index))
                if tag_type is TagCompound:
                    try:
                        check_compound_items(rules, tag, rules[base_tag][key]['subtype'])
                    except NbtException as error:
                        raise NbtException('%s\n>    %s[%d]'%(error.message, key, index))
                else:
                    if check_value:
                        if not tag.value in rules[base_tag][key]['values']:
                            raise NbtException('Invalid value\nTag stack:\n>    %s[%d]'\
                                % (key, index))
                    if check_range:
                        if not (tag.value >= rules[base_tag][key]['range']['min'] and \
                            tag.value <= rules[base_tag][key]['range']['max']):
                            raise NbtException('Invalid value\nTag stack:\n>    %s[%d]'\
                                % (key, index))
                index += 1
        elif tag_type is TagCompound:
            try:
                check_compound_items(rules, compound[key], rules[base_tag][key]['type'])
            except NbtException as error:
                raise NbtException('%s\n>    %s' % (error.message, key))
        elif tag_type is TagIntArray:
            check_value = 'values' in rules[base_tag][key]
            check_range = 'range' in rules[base_tag][key]
            for tag in compound[key]:
                if not tag.type_match(TagInt):
                    raise NbtException(\
                        'Invalid item type, should be int\nTag stack:\n>    %s' % key)
                if check_value:
                    if not tag.value in rules[base_tag][key]['values']:
                        raise NbtException('Invalid value\nTag stack:\n>    %s' % key)
                if check_range:
                    if not (tag.value >= rules[base_tag][key]['range']['min'] and \
                        tag.value <= rules[base_tag][key]['range']['max']):
                        raise NbtException('Invalid value\nTag stack:\n>    %s' % key)
        else:
            if 'values' in rules[base_tag][key]:
                if not compound[key].value in rules[base_tag][key]['values']:
                    raise NbtException('Invalid value\nTag stack:\n>    %s' % key)
            if 'range' in rules[base_tag][key]:
                if not (compound[key].value >= rules[base_tag][key]['range']['min'] and \
                    compound[key].value <= rules[base_tag][key]['range']['max']):
                    raise NbtException('Invalid value\nTag stack:\n>    %s' % key)

