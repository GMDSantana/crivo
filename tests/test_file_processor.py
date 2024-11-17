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

import pytest
from crivo.file_processor import process_file

def test_process_file_valid():
    # Create a temporary file for testing
    with open("temp_test_file.txt", "w", encoding="utf-8") as f:
        f.write("Sample content for testing.")

    content = process_file("temp_test_file.txt")
    assert content == "Sample content for testing."

    # Clean up the temporary file
    import os
    os.remove("temp_test_file.txt")

def test_process_file_not_found():
    with pytest.raises(FileNotFoundError):
        process_file("non_existent_file.txt")

def test_process_file_io_error(mocker):
    mocker.patch("builtins.open", side_effect=IOError("Mocked IO error"))
    with pytest.raises(IOError):
        process_file("mocked_file.txt")

