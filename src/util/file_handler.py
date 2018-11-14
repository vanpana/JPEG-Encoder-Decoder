import os


def read_lines_from_file(filename: str):
    """
    Yields all lines from a file. Lines are stripped from line breaks and empty spaces.
    :param filename: Path to the file
    :return None if file was not found
    """
    if not os.path.isfile(filename):
        return None
    with open(filename, 'r') as file:
        for line in file:
            yield line.strip('\n').strip(' ')


def write_lines_to_file(data, filename: str, file_format: str = None):
    """
    Writes data to a file.
    :param data: Data object to be written to the file.
    :param filename: The file where data should be written
    :param file_format: The file format
    :return: None
    """
    # Add extension to the filename if needed
    if file_format is not None and not filename.lower().endswith(file_format):
        if not file_format.startswith('.'):
            file_format = "." + file_format

        filename = filename.rstrip('.') + file_format

    with open(filename, 'w') as file:
        file.write(data)
