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

    Args:
        scope (str): The scope input as a comma-separated string.

    Returns:
        list: A list of validated scope filters.
    """
    if not scope:
        return []
    return [s.strip().lower() for s in scope.split(",") if s.strip()]

def log_verbose(message, verbose):
    """
    Prints a message if verbose mode is enabled.

    Args:
        message (str): The message to print.
        verbose (bool): Flag indicating if verbose mode is active.
    """
    if verbose:
        print(message)

