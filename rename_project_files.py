#!/usr/bin/env python3
"""Utility for renaming images and jsons inside a labeled project folder.

Usage
-----
    python rename_project_files.py /path/to/project_folder

Given a project folder name (for example "antigravity") the script will
perform the following steps:

1. Descend into ``input-images`` and rename every file found there to
   ``{project}_image_{n:03d}{ext}`` where ``n`` is the 1-based index of the
   file when the directory listing is sorted lexicographically.
2. After renaming the files the directory itself is renamed from
   ``input-images`` to ``images``.
3. Descend into ``output-jsons`` and rename every file to
   ``{project}_annotation_{n:03d}.json`` (extension is forced to ``.json``).
4. Rename ``output-jsons`` to ``annotation``.

This mirrors the pattern described in earlier chats.  If any of the
intermediate directories are missing the script will emit a warning and
continue with whatever it can.

"""

import os
import sys


def _zero_padded(name_format: str, index: int) -> str:
    return name_format.format(index)


def rename_directory_files(src_dir: str, template: str, force_ext: str | None = None) -> None:
    """Rename files in ``src_dir`` according to ``template``.

    ``template`` should be a format string accepting a single integer, for
    example "antigravity_image_{:03d}.jpg".  ``force_ext`` allows the caller
    to override the original extension (useful for JSONs).
    """
    entries = sorted(os.listdir(src_dir))
    for idx, entry in enumerate(entries, start=1):
        old_path = os.path.join(src_dir, entry)
        if not os.path.isfile(old_path):
            # skip subdirectories or non-files
            continue
        name, ext = os.path.splitext(entry)
        ext = force_ext if force_ext is not None else ext
        new_name = template.format(idx) + ext
        new_path = os.path.join(src_dir, new_name)
        if old_path == new_path:
            continue
        os.rename(old_path, new_path)
        print(f"Renamed: {old_path} -> {new_path}")


def process_project(root: str) -> None:
    project = os.path.basename(os.path.normpath(root))

    # input-images -> images
    in_images = os.path.join(root, "input-images")
    if os.path.isdir(in_images):
        rename_directory_files(
            in_images, f"{project}_image_{{:03d}}", None
        )
        to_images = os.path.join(root, "images")
        if os.path.exists(to_images):
            print(f"Target directory {to_images!r} already exists, skipping rename of input-images.")
        else:
            os.rename(in_images, to_images)
            print(f"Renamed directory {in_images!r} -> {to_images!r}")
    else:
        print(f"Warning: {in_images!r} does not exist, nothing to rename there.")

    # output-jsons -> annotation
    out_jsons = os.path.join(root, "output-jsons")
    if os.path.isdir(out_jsons):
        rename_directory_files(
            out_jsons, f"{project}_annotation_{{:03d}}", ".json"
        )
        to_annotation = os.path.join(root, "annotation")
        if os.path.exists(to_annotation):
            print(f"Target directory {to_annotation!r} already exists, skipping rename of output-jsons.")
        else:
            os.rename(out_jsons, to_annotation)
            print(f"Renamed directory {out_jsons!r} -> {to_annotation!r}")
    else:
        print(f"Warning: {out_jsons!r} does not exist, nothing to rename there.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python rename_project_files.py /path/to/project_folder")
        sys.exit(1)
    project_folder = sys.argv[1]
    if not os.path.isdir(project_folder):
        print(f"Error: {project_folder!r} is not a directory.")
        sys.exit(1)
    process_project(project_folder)
