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


def normalise_text(text):
    """
    Normalises text by stripping whitespace and converting to lowercase.

    Args:
        text (str): The text to be normalised.

    Returns:
        str: The normalised text.
    """
    return text.strip().lower()


def validate_scope(scope):
    """
    Validates the provided scope filters and ensures they are in the correct format.

    Entries are stripped and lower-cased; empty entries and duplicates are
    dropped while keeping the original order.

    Args:
        scope (str): The scope input as a comma-separated string.

    Returns:
        list: A list of validated scope filters.
    """
    if not scope:
        return []
    entries = []
    for entry in scope.split(","):
        entry = entry.strip().lower()
        if entry and entry not in entries:
            entries.append(entry)
    return entries


def log_verbose(message, verbose):
    """
    Prints a message to standard error if verbose mode is enabled.

    Diagnostics go to standard error so they never mix with the results on
    standard output.

    Args:
        message (str): The message to print.
        verbose (bool): Flag indicating if verbose mode is active.
    """
    if verbose:
        print(message, file=sys.stderr)
