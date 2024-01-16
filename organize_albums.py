#!/usr/bin/python3
import os

FILE = os.path.abspath("README.md")
KNOWN_HEADERS = {}
HEADER_STARTER = '### '
ALBUM_STARTER = ' - '
UNDEF_SYMBOL = '~'


def remove_tail_chars(phrase: str, *chars) -> str:
    while phrase.startswith(chars):
        phrase = phrase[1:]
    while phrase.endswith(chars):
        phrase = phrase[:-1]

    return phrase


def split_line(line: str, reverse=False) -> list:
    line = line.split(':')
    if reverse:
        line = line[::-1]

    line = [remove_tail_chars(i, ' ', '\n') for i in line]

    return line


class Header:

    def __init__(self, l: chr):
        # Headers are built like a list with albums that start with the Header letter
        self.letter = l
        self.albums = []

    def add_album(self, album):
        self.albums.append(album)

    @staticmethod
    def get_album_repr(album: list):
        album[0] = f"**{album[0]}**"

        final = ALBUM_STARTER
        final += ': '.join(album)

        return final

    def parse_upcoming_headers(self, lines: list):
        i = 0
        while lines[i].startswith(ALBUM_STARTER):
            album = split_line(lines[i])
            self.add_album(album)
            i += 1

    def __repr__(self):
        ret = f"{HEADER_STARTER}{self.letter}\n"
        self.albums.sort()

        for a in self.albums:
            ret += f"{self.get_album_repr(a)}\n"

        return ret

    def __str__(self):
        return self.__repr__()


def custom_sort_key(c):
    if c.isalpha():
        return 0, c
    elif c.isdigit():
        return 1, int(c)
    else:
        return 2, c


def validate_header(h: chr):
    v = ord(h)
    return (0x29 < v < 0x3A) or (0x40 < v < 0x5B) or (0x60 < v < 0x7B)


def needs_reversing(lines: list):
    example_name = 'Pink Floyd'
    for line in lines:
        if example_name in line:
            s = line.split(':')
            return example_name in s[0]

    return


def add_to_header(line):
    if line == ['']:
        return

    header = line[0][0].upper()
    if not validate_header(header):
        header = UNDEF_SYMBOL

    if header in list(KNOWN_HEADERS.keys()):
        h = KNOWN_HEADERS[header]
        h.add_album(line)
    else:
        h = Header(header)
        h.add_album(line)
        KNOWN_HEADERS[header] = h


def parse_raw_albums(lines):
    to_rev = needs_reversing(lines)

    for line in lines:
        _tmp = line
        if line.startswith((HEADER_STARTER, ALBUM_STARTER, '#')):
            continue

        line = split_line(line, to_rev)

        if line:
            add_to_header(line)


def parse_existing_headers(lines):
    for i in range(len(lines)):
        line = lines[i]

        if line.startswith(HEADER_STARTER):
            header = line.split()[1][0]

            if validate_header(header):
                if header.islower():
                    header = header.upper()
            else:
                header = UNDEF_SYMBOL

            if header in list(KNOWN_HEADERS.keys()):
                header_obj = KNOWN_HEADERS[header]
            else:
                header_obj = Header(header)
                KNOWN_HEADERS[header] = header_obj

            header_obj.parse_upcoming_headers(lines[i:])


def write_lines_to_file(f, lines):
    with open(f, 'w') as file:
        file.writelines(lines)


def main():
    final = "# Albums\n" \
            "## Note: \n" \
            "If you want to add any album, " \
            "just add it in the folowing syntax:" \
            "**\\<ALBUM_NAME\\>: \\<ARTIST\\>** " \
            "and run `organize_albums.py`\n\n"

    with open(FILE, 'r') as file:
        lines = file.readlines()

        parse_raw_albums(lines)
        parse_existing_headers(lines)

        headers = list(KNOWN_HEADERS.keys())
        headers.sort(key=custom_sort_key)

        for h in headers:
            final += str(KNOWN_HEADERS[h])

    write_lines_to_file(FILE, final)


if __name__ == "__main__":
    main()

