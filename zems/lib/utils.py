import os


def find_files(path, extension):
    if not extension.startswith("."):
        extension = "." + extension

    files = [
        os.path.join(root, filename)
        for root, dirs, files in os.walk(path)
        for filename in files if filename.endswith(extension)
    ]

    if len(files) < 1:
        raise IOError("No files found with extension %s" % extension)

    return files
