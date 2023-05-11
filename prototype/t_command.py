
def list_command(command: str):
    liste = ['']

    no_stop_until = None
    for index, text in enumerate(command):
        # check begin
        if index == 0 and text in ['/', '#']:
            liste = [text, '']
        # make string, struct and list
        elif no_stop_until is not None:
            liste[-1] += text
            if text == no_stop_until:
                no_stop_until = None
        # detect string, struct and list
        elif text == '"':
            liste[-1] += text
            no_stop_until = '"'
        elif text == '{':
            liste[-1] += text
            no_stop_until = '}'
        elif text == '[':
            liste[-1] += text
            no_stop_until = ']'
        # add arg if space
        elif text == ' ':
            if index == 1 and liste[-1] == '':
                pass
            else:
                liste.append('')
        # add to last
        else:
            liste[-1] += text

    return liste


from strenum import StrEnum

class e_type(StrEnum):
    BEGIN_COMMAND = 'begin_command'     # '/' in first position
    BEGIN_COMMENT = 'begin_comment'     # '#' in first position
    COMMAND = 'command'                 # in command.json
    EXECUTE_COMMAND = 'execute_command'     # in execute_command.json
    POSITIONNED_COMMAND = 'positionned_command'     # in positionned_command.json
    MOB = 'mob'                             # in mob.json
    NULL = 'null'                           # if fit in any type

data = {
    'command': ['execute', 'say', 'summon'],
    'execute_command': ['as', 'run'],
    'positionned_command': ['as'],
    'mob': ['chicken', 'dolphin'],
}

def type_list(liste: list[str]):
    types = [[e_type.NULL] for _ in liste]

    for index, argument in enumerate(liste):
        if index == 0:
            if argument == '/':
                types[index].append(e_type.BEGIN_COMMAND)
            elif argument == '#':
                types[index].append(e_type.BEGIN_COMMENT)

        if argument in data['command']:
            types[index].append(e_type.COMMAND)
        if argument in data['execute_command']:
            types[index].append(e_type.EXECUTE_COMMAND)
        if argument in data['positionned_command']:
            types[index].append(e_type.POSITIONNED_COMMAND)
        if argument in data['mob']:
            types[index].append(e_type.MOB)

    return types

def clean_types(types: list(e_type)):
    clean = []

    for index, t in enumerate(types):
        if e_type.BEGIN_COMMAND in t and index == 0:
            clean.append(e_type.BEGIN_COMMAND)
        elif e_type.BEGIN_COMMENT in t and index == 0:
            clean.append(e_type.BEGIN_COMMENT)
        elif e_type.NULL in t and len(t) == 1:
            clean.append(e_type.NULL)
        elif e_type.COMMAND in t and (index == 0 or clean[index - 1] in [e_type.BEGIN_COMMAND, e_type.EXECUTE_COMMAND]):
            clean.append(e_type.COMMAND)
        elif e_type.EXECUTE_COMMAND in t and clean[index - 1] == e_type.COMMAND:
            clean.append(e_type.EXECUTE_COMMAND)
        elif e_type.POSITIONNED_COMMAND in t and clean[index - 1] == e_type.EXECUTE_COMMAND:
            clean.append(e_type.POSITIONNED_COMMAND)
        elif e_type.MOB in t and clean[index - 1] == e_type.COMMAND:
            clean.append(e_type.MOB)
        else:
            clean.append(None)

    return clean

commands = [
        "/execute run say hello world !",
        "execute as",
        "i am an error test",
        "#i am a comment",
        "# i  am a comment",
        "summon chicken"
    ]

for i in commands:
    liste = list_command(i)
    types = type_list(liste)
    print(f"{liste}\n{types}\n{clean_types(types)}\n")