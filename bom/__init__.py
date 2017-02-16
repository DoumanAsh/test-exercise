from os import path as os_path
from hashlib import md5 as hash_md5
import logging


def _md5(path):
    md5_algo = hash_md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_algo.update(chunk)
    return md5_algo.hexdigest()


""" Represents BOM's entry """
class Entry(object):
    def __init__(self, location, dest, md5, patch=None):
        self.location = location
        self.dest = dest
        self.md5 = md5
        self.patch = patch

    def __repr__(self):
        return "BOM(location={}, dest={}, md5={}, patch={})".format(
                self.location,
                self.dest,
                self.md5,
                self.patch)

    def __str__(self):
        return self.__repr__()

    def __bool__(self):
        return self.is_valid()

    def __nonzero__(self):
        return self.is_valid()

    def is_valid(self):
        return os_path.isfile(self.location) and _md5(self.location) == self.md5


def parse_list(path):
    bom_header = ["Location", "Destination", "Md5", "Patching"]
    root_path = os_path.dirname(path)
    with open(path) as bom:
        header = bom.readline().rstrip().split('\t')

        if not header == bom_header:
            raise ValueError("Invalid BOM header in file='{}'".format(path))

        for num, line in enumerate(bom):
            line.strip()

            if not line:
                continue

            entry = line.split('\t')
            entry_len = len(entry)

            if entry_len < 3 and entry_len > 4:
                raise ValueError("Invalid number of fields in BOM entry. Line {}".format(num + 1))

            location = entry[0] if os_path.isabs(entry[0]) else os_path.join(root_path, entry[0])
            dest = entry[1] if os_path.isabs(entry[1]) else os_path.join(root_path, entry[1])
            yield Entry(os_path.normpath(location.strip()),
                        os_path.normpath(dest.strip()),
                        entry[2].strip(),
                        entry[3].strip() if entry_len == 4 else None)
