"""

╔██████╗██████╗ ██╗██╗     ██╗╔██████╗
██╔════╝██╔══██╗██║╚██╗   ██╔╝██╔═══██╗
██║     ██████╔╝██║ ╚██╗ ██╔╝ ██║   ██║
██║     ██╔██═╝ ██║  ╚████╔╝  ██║   ██╝
╚██████╗██║ ██╗ ██║   ╚██╔╝   ╚██████╝
© Guilherme Santana
https://gmdsantana.com
https://github.com/GMDSantana/crivo

"""

import sys


def process_file(file_path):
    """
    Reads the content of a text file and returns it as a string.

    The file is decoded as UTF-8 (a BOM is accepted). Bytes that are not
    valid UTF-8 are replaced rather than aborting, so binary data or files in
    other encodings can still be filtered. A path of "-" reads standard input.

    Args:
        file_path (str): The path to the input file, or "-" for standard input.

    Returns:
        str: The content of the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        IsADirectoryError: If the path is a directory.
        PermissionError: If the file cannot be opened.
        OSError: For other read errors.
    """
    if file_path == "-":
        return read_stdin()
    try:
        with open(file_path, "r", encoding="utf-8-sig", errors="replace") as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' was not found.") from None
    except IsADirectoryError:
        raise IsADirectoryError(f"'{file_path}' is a directory, not a file.") from None
    except PermissionError:
        raise PermissionError(f"Permission denied when reading '{file_path}'.") from None
    except OSError as e:
        raise OSError(f"Error reading the file '{file_path}': {e}") from e


def read_stdin():
    """
    Reads all of standard input as text, replacing invalid UTF-8 bytes.

    Returns:
        str: The text read, or an empty string if there is no standard input.
    """
    stream = sys.stdin
    if stream is None:
        return ""
    buffer = getattr(stream, "buffer", None)
    if buffer is not None:
        return buffer.read().decode("utf-8-sig", errors="replace")
    return stream.read()


def read_url_list(file_path):
    """
    Reads a list of URLs, one per line.

    Blank lines and lines starting with '#' are ignored, surrounding
    whitespace is stripped and duplicates are removed (first occurrence kept).

    Args:
        file_path (str): The path to the list, or "-" for standard input.

    Returns:
        list: The URLs, in file order.
    """
    urls = []
    seen = set()
    for line in process_file(file_path).splitlines():
        url = line.strip()
        if not url or url.startswith("#") or url in seen:
            continue
        seen.add(url)
        urls.append(url)
    return urls
