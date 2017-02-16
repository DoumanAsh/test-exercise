from argparse import ArgumentParser
from sys import argv, exit
from os import path as os_path
from os import makedirs
from shutil import copy2 as copy
import logging

from bom import parse_list


def gen_bom_master_entries(path):
    """
        Generates list of BOM lists paths.

        Args:
            path: Valid path to file with BOM lists.

        Yields:
            Path to BOM list.
    """
    root_path = os_path.dirname(path)
    with open(path) as bom_master:
        for line in bom_master:
            line = line.strip()

            if line:
                yield line if os_path.isabs(line) else os_path.join(root_path, line)


def copy_file(location, dest, patch=None):
    """
        Performs copy of file by applying optional patch.

        Args:
            location: Valid path to file
            dest: Valid path to copy file into.
            patch: Optional patch to append.
    """
    logging.debug("Copy file from %s to %s", location, dest)
    dest_dir = os_path.dirname(dest)

    if not os_path.isdir(dest_dir):
        try:
            makedirs(dest_dir)
        except OSError as error:
            logging.error("Cannot create directory %s. Error: %s",
                          dest_dir, error)
            raise error

    try:
        copy(location, dest)
    except OSError as error:
        logging.error("Cannot copy file to %s. Error: %s",
                      dest, error)
        raise error

    if patch:
        logging.debug("Append patch to %s", dest)
        with open(dest, "a") as dest_fd:
            dest_fd.write(patch)


def process_list(path, is_strict):
    """
        Processes BOM list.

        Performs validation:
        * File should be valid and exist.
        * Checks checksums
        * Location & Destination cannot be repeated.

        Args:
            path: Valid path to BOM list.
            is_strict: Flag whether to stop on first error.

        Raises:
            ValueError: on invalid entry.
    """
    locations = set()
    dests = set()

    def raise_if(error=None):
        if is_strict:
            raise error if error else ValueError

    for entry in parse_list(path):
        if entry:
            if entry.location in locations:
                logging.error("location='%s' is repeated", entry.location)
                raise_if()
                continue
            elif entry.dest in dests:
                logging.error("destination='%s' is repeated", entry.dest)
                raise_if()
                continue

            locations.add(entry.location)
            dests.add(entry.dest)

            try:
                copy_file(entry.location, entry.dest, entry.patch)
            except OSError as error:
                raise_if(error)

        else:
            logging.error("BOM entry='%s' isn't valid!", entry)
            raise_if()

def main(args):
    parser = ArgumentParser(description='Process BOM lists')
    parser.add_argument('bom', metavar='BOM', help="Text file with list of BOM files")
    parser.add_argument('--strict',
                        action="store_true",
                        help="Stop on first error")
    parser.add_argument('--logging',
                        help="Enable logging to specified file",
                        metavar='FILE')
    parser.add_argument('--log-level',
                        help="Specifies logging level. Default is WARNING",
                        metavar='LEVEL',
                        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"],
                        default="WARNING")

    if not args:
        parser.print_help()
        return 0

    args = parser.parse_args(args)

    logging.basicConfig(format='%(asctime)-15s - %(filename)s:%(lineno)d - [%(levelname)s] - %(message)s',
                        level=getattr(logging, args.log_level),
                        filename=args.logging)

    logging.info("Start script with arguments {}".format(args))

    if not os_path.isfile(args.bom):
        logging.critical("{}: no such file".format(args.bom))
        return 1

    for bom_list in gen_bom_master_entries(args.bom):
        logging.info("Parse BOM list='{}'".format(bom_list))

        if os_path.isfile(bom_list):
            try:
                process_list(bom_list, args.strict)
            except:
                exit(1)
        else:
            logging.warning("BOM list='{}' doesn't exist".format(bom_list))

    return 0

if __name__ == "__main__":
    exit(main(argv[1:]))
