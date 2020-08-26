#!/usr/bin/env python3

import os
from argparse import ArgumentParser


FILE_SECTIONS = (b'VERS', b'GUID', b'INST', b'WAM ', b'IMG ')
FILE_SIGNATURES = (b'ATTM', b'SNGM')
FILE_EXTENSION = 'WSM'


def validate_sections(section_list):
    f"""Get requested sections from the given comma separated list. Ensure that any section specified exists in the
        {FILE_SECTIONS} and pad to 4 bytes for space suffixed FourCCs. Duplicates ignored thanks to set()."""

    sections = section_list.split(',')
    validated_sections = set()
    for section in sections:
        section = section.strip()
        section = section.ljust(4).encode()
        if section not in FILE_SECTIONS:
            print(f'"{section}" is not a valid {FILE_EXTENSION} FourCC/section')
            return False
        validated_sections.add(section)
    return tuple(validated_sections)


def get_filename(basename, fourCC):
    """Handle any changes that may be needed for a specific section. Such as LAND_*.DAT prefix and suffix and stripping
       extraneous whitespace. Return the file basename and decoded FourCC extension otherwise."""

    if fourCC == b'WAM ':
        return basename + '.WAM'
    if fourCC == b'IMG ':
        return 'LAND_' + basename + '.DAT'
    return basename + '.' + fourCC.decode().strip()


def process_file(file_path, output_dir_root, save_sections, overwrite):
    f"""Process a {FILE_EXTENSION} file. Skip it if signature doesnt match one in {FILE_SIGNATURES}. Process each FourCC
        section and save the indicated length to a file if it has been requested. Do not overwrite unless prompted.
        Print progress for each section saved."""

    print('Processing:', file_path)
    with open(file_path, 'rb') as in_file:
        if in_file.read(4) not in FILE_SIGNATURES:
            print('File signature invalid. Skipping.')
            return False
        else:
            in_file.seek(4, 1)  # skip size

        while True:
            fourCC = in_file.read(4)
            if not fourCC:
                return True  # no more data, done.

            if not fourCC in FILE_SECTIONS:
                print(f'{fourCC} is not a valid {FILE_EXTENSION} section. Skipping file')
                return False
            length = int.from_bytes(in_file.read(4), byteorder='little', signed=False)

            if fourCC in save_sections:
                output_basename = os.path.basename(file_path)[:-4]
                output_dir = os.path.join(output_dir_root, output_basename)
                output_filename = get_filename(output_basename, fourCC)
                output_path = os.path.join(output_dir, output_filename)
                if not os.path.isdir(output_dir):
                    os.mkdir(output_dir)

                if os.path.isfile(output_path) and not overwrite:
                    print('File exists but overwrite not set. Not saving:', output_filename)
                    in_file.seek(length, 1)
                    continue

                with open(output_path, 'wb') as out_file:
                    out_file.write(in_file.read(length))
                print('Saved:', output_filename)
            else:
                in_file.seek(length, 1)


def main():
    """Use argparse to get the launch arguments and carry out the requested actions. Validate user input, and check if
       passed paths exist and that they have the correct file extension. Print progress for each input.
       process_file deals with per file progress."""

    parser = ArgumentParser(description='WSM Extract (wsme). A tool to extract the various sections of a WSM file.')
    parser.add_argument('-e', '--extract', type=str.upper, nargs='?', default=None, metavar='SECTION[,SECTION ...]',
                        help='A comma separated list of sections (FourCC) to extract. Defaults to all sections.' +
                             ' Valid sections: ' + ','.join((s.decode().strip() for s in FILE_SECTIONS)) +
                             ' (NOTE: the "IMG " section is actually a land.dat file. Not an img file)')
    parser.add_argument('-o', '--output', type=str, nargs='?', default=None, metavar='OUTPUT_DIR',
                        help="Output directory for extracted parts' subfolders. Defaults to the same folder as the" +
                             ' input folder.')
    parser.add_argument('-f', '--force-overwrite', action='store_true', help='Allow overwriting files.')
    parser.add_argument('inputs', type=str, nargs='+', metavar='File_or_Folder',
                        help='One or more files or folders (non recursive) to process')
    args = parser.parse_args()

    if args.output is not None:
        if os.path.exists(args.output):
            if not os.path.isdir(args.output):
                parser.error(f'"{args.output}" is not a directory')
        else:
            parser.error(f'"{args.output}" does not exist')

    if args.extract is None:
        save_sections = FILE_SECTIONS
    else:
        save_sections = validate_sections(args.extract)
        if not save_sections:
            parser.error('Invalid extract section selection')

    print('Starting extraction process.')
    print('Saving sections:', ','.join((s.decode().strip() for s in save_sections)))
    if (count := len(args.inputs)) > 1:
        print(count, 'inputs to process')
    print()

    for input_idx, input in enumerate(args.inputs, start=1):
        if not os.path.exists(input):
            print('Skipping non existent input:', {input})
            continue

        if os.path.isdir(input):
            if len(args.inputs) > 1:
                print('Processing input:', input)
            output_dir = args.output if args.output else input
            file_paths = [os.path.join(input, f) for f in os.listdir(input) if f.upper().endswith(FILE_EXTENSION)]
            if (count := len(file_paths)) > 1:
                print(count, 'files to process')
        else:
            output_dir = args.output if args.output else os.path.dirname(input)
            file_paths = [input]

        for file_idx, file_path in enumerate(file_paths, start=1):
            if not file_path.upper().endswith(FILE_EXTENSION):
                print('Skipping non', FILE_EXTENSION, 'file extension for:', file_path)
                continue

            process_file(file_path, output_dir, save_sections, args.force_overwrite)
            if file_idx != len(file_paths):
                print()
        if input_idx != len(args.inputs):
            print()


if __name__ == '__main__':
    main()
