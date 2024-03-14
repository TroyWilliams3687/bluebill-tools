#!/usr/bin/env python3
#-*- coding:utf-8 -*-

"""
Useful utilities

https://docs.sublimetext.io/guide/extensibility/plugins.html#conventions-for-command-names

# Conventions for Command Names

You may have noticed that our command is named ExampleCommand, but we
passed the string example to the API call instead. This is necessary
because Sublime Text standardizes command names by stripping the
Command suffix, splitting subwords of PhrasesLikeThis with underscores,
and lower-casing it, like so: phrases_like_this. New commands should
follow the same naming pattern.

# Reference
https://www.sublimetext.com/docs/3/api_reference.html

"""
import sublime
import sublime_plugin

import bisect
import re
import uuid
import os
import subprocess
import platform

from datetime import datetime
from random import randint
from string import Template

# NOTE: Need to install PackageDev to get access to the PathLib for
# Sublime v3.2.2 Build 3211 from pathlib import Path


# Suggested Key Bindings
# [
#     { "keys": ["ctrl+shift+t"], "command": "time_parsing" },
#     { "keys": ["ctrl+k","ctrl+d"], "command":"insert_date"},
#     { "keys": ["ctrl+k","ctrl+b"], "command":"insert_time"},
#     { "keys": ["ctrl+k","ctrl+j"], "command":"insert_uuid"},
#     { "keys": ["ctrl+k", "ctrl+t"], "command": "title_case" },
#     { "keys": ["ctrl+t", "ctrl+t"], "command": "create_todo" },
#     { "keys": ["ctrl+t", "ctrl+r"], "command": "open_links" },
# ]


# # ctrl+` -> view.run_command("bluebill_insert_text", {'start': start_point, 'text': new_text})
# class BluebillInsertTextCommand(sublime_plugin.TextCommand):
#     """
#     The Bluebill insert text command implementation.

#     This is basically a method used by other commands. This probably should have been a function call instead

#     """

#     def run(self, edit, start, text):
#         """

#         # Parameters

#             edit - Edit
#                 - The edit object to identify this operation.

#             start - int
#                 - The beginning of the Region to insert the text into.

#             text str
#                 - The text to insert.

#         # Usage

#         view.run_command("bluebill_insert_text", {'start': start_point, 'text': new_text})

#         """
#         print(start)
#         print(text)

#         self.view.insert(edit, start, text)
#         print('inserted...')


def _insert_text(view, edit, start, text):
    """
    This simple method is used to insert text into the view.
    """

    view.insert(edit, start, text)
    # print('inserted...')


# ctrl+` -> view.run_command("insert_date")
class InsertDateCommand(sublime_plugin.TextCommand):
    """
    Insert the current date in iso format (YYYY-MM-DD) at all the cursor
    locations.
    """

    def run(self, edit):

        print("Inserting Date...")

        current_date = datetime.now().date().isoformat()

        for s in self.view.sel():

            _insert_text(self.view, edit, s.a, current_date)




# ctrl+` -> view.run_command("insert_time")
class InsertTimeCommand(sublime_plugin.TextCommand):
    """
    Insert the current time in 24hr format with no separator, i.e. 1634
    instead of 16:34 at all the cursor locations (same time at each
    one).
    """

    def run(self, edit):

        print("Inserting Time...")

        current_time = datetime.now().time().strftime('%H%M')

        for s in self.view.sel():
            _insert_text(self.view, edit, s.a, current_time)

# ctrl+` -> view.run_command("insert_uuid")
class InsertUuidCommand(sublime_plugin.TextCommand):
    """
    Insert a UUID at all the cursor locations.
    """

    def run(self, edit):

        print("Inserting UUID...")
        generated_uuid = str(uuid.uuid1())

        for s in self.view.sel():
            _insert_text(self.view, edit, s.a, generated_uuid)


# ctrl+` -> view.run_command("create_todo")
class CreateTodoCommand(sublime_plugin.TextCommand):
    """
    Given the selected text, transform it into a Notes TODO item.

    - [] todo item

    Basically it will add the dash and square brackets.

    """

    def run(self, edit):

        print("Creating TODO entry...")

        for region in self.view.sel():

            # If the selection region is empty, select the line
            if region.empty():
                current_line = self.view.line(region)
                region = sublime.Region(current_line.a, current_line.b)

                s = self.view.substr(region)

            else:
                # use the selected text
                s = self.view.substr(region)

            match = re.match(r"^(\s*)-(.*)$", s)

            if match:
                todo_line = match.group(1) + '- []' + match.group(2)

            else:
                todo_line = '- [] {}'.format(s)

            self.view.replace(edit, region, todo_line)

# ----

# def print_region_info(region):
#     """
#     """
#     print("region.a: ", region.a)
#     print("region.b: ", region.b)
#     print("region.xpos: ", region.xpos)
#     print("region.size: ", region.size())
#     print("region.empty:", region.empty())

def find_whitespace_positions(input_string):
    """
    Given the string, return a list of index numbers for each location
    of whitespace
    """

    # Define the regex pattern for matching whitespace
    whitespace_pattern = re.compile(r'\s+')

    # Use finditer to find all matches in the input string
    matches = whitespace_pattern.finditer(input_string)

    # Extract and return the positions of each match
    positions = [match.start() for match in matches]

    return positions if len(positions) > 0 else None



def find_largest_quoted_substring(input_string):
    """
    Find the largest substring in single quotes, double quotes, or back
    ticks (matching pairs).

    Returns the start and end index of the substring if there is a match
    else it returns None.
    """

    match = re.search(r'([\'\"`])(.*?)\1', input_string)

    if match:

        return match.start(2), match.end(2)

    else:

        return None



def find_markdown_links(input_string):
    """
    """

    markdown_link_pattern = re.compile(r"\[(?P<text>[^\]]+)\]\((?P<url>[^)]+)\)")
    matches = markdown_link_pattern.finditer(input_string)

    result = []

    for match in matches:
        result.append(
            (
                match.group('text'),
                match.group('url'),
                match.start(),
                match.end(),
            )
        )

    return result or None



# def find_largest_quoted_substring(input_string, index):
#     """
#     Find the largest substring in single quotes, double quotes, or back
#     ticks (matching pairs)
#     """

#     match = re.search(r'([\'\"`])(.*?)\1', input_string)
#     largest_quoted_substring = match.group(2) if match else ''

#     # Get the substring around the provided index
#     start_index = max(0, index - len(largest_quoted_substring))
#     end_index = min(len(input_string), index + len(largest_quoted_substring))
#     substring_around_index = input_string[start_index:end_index]

#     return largest_quoted_substring, substring_around_index


def open_with_default_app(path):
    """
    given a path, attempt to open it using the default system
    application. Determine the appropriate command based on the
    operating system
    """

    if platform.system() == "Darwin":  # macOS
        command = ["open", path]

    elif platform.system() == "Windows":
        # command = ["start", "", path, "/B", "/WAIT"]
        os.startfile(path)
        return

    elif platform.system() == "Linux":
        command = ["xdg-open", path]

    else:
        print("Unsupported operating system :(")
        return

    try:

        subprocess.call(command)

    except subprocess.CalledProcessError as e:
        print("Error: {}".format(e))



# ctrl+` -> view.run_command("open_links")
class OpenLinksCommand(sublime_plugin.TextCommand):
    """
    If the selected text is a file path, folder path open it.

    behavior:
    - assumes cursor is placed in the path i.e. user clicks the path

    - assumes user selects the path

    - [x] We should be able to handle paths
    - [x] we should be able to handle paths that are in a selection
    - [x] We should be able to handle paths that are relative to the project
    - We should be able to handle paths defined in markdown links
    - We should be able to handle paths in back ticks or quotes (single and double)
    """

    def run(self, edit):

        print("Opening Link...")

        for region in self.view.sel():

            potential_path = None

            if region.empty():

                # assume that the cursor is placed in the middle of
                # path, we want to select all of the text towards the
                # beginning and end of the line until we hit a
                # whitespace

                # If the region is empty, region.a == region.b will be
                # the cursor position

                # select the current line
                current_line = self.view.line(region)
                # print_region_info(current_line)

                # translate the cursor position to the line coordinate
                # system. Essentially we are calculation the column
                # position
                cursor_position = region.a - current_line.a

                # the column is 1 based
                # print(cursor_position + 1)

                # get the string representing the entire line
                full_line_text = self.view.substr(current_line)

                # ---
                quoted_string = find_largest_quoted_substring(full_line_text)
                # print("quoted_string: ", full_line_text[slice(*quoted_string)])

                markdown_links = find_markdown_links(full_line_text)

                potential_path = None




                if quoted_string:
                    start_index, end_index = quoted_string
                    potential_path = full_line_text[start_index: end_index]

                if markdown_links:

                    for md_link in markdown_links:
                        link_text, link_url, start_index, end_index = md_link
                        if start_index <= cursor_position <= end_index:
                            potential_path = link_url
                            break

                if potential_path is None:
                    # ----
                    # Find white spaces by index

                    whitespaces = find_whitespace_positions(full_line_text)
                    # print(whitespaces)

                    if whitespaces is None:
                        potential_path = full_line_text

                    else:

                        left_items = [index for index in whitespaces if index <= cursor_position]
                        left_index = max(left_items) if left_items else 0


                        right_items = [index for index in whitespaces if index >= cursor_position]
                        right_index = min(right_items) if right_items else len(full_line_text)

                        # # figure out where in the list of whitespaces the cursor would fit
                        # insert_cursor = bisect.bisect_left(whitespaces, cursor_position)
                        # print(insert_cursor)

                        potential_path = full_line_text[left_index:right_index].lstrip()
                        # print(potential_path)

            else:
                # use the selected text
                potential_path = self.view.substr(region).strip()

            # the strings may have %20 sometimes that are the html for
            # spaces in markdown
            potential_path = potential_path.replace("%20", " ")

            if potential_path is not None:
                print(potential_path)

                if os.path.exists(potential_path):
                    open_with_default_app(potential_path)
                    print('Opening absolute path...')
                    return

                # Is the path a relative path of the project?

                project_properties = self.view.window().extract_variables()

                if "folder" in project_properties:

                    root = project_properties["folder"]
                    full_path = os.path.join(root, potential_path)

                    # normalize the path as we might have .. or . or ./
                    # in it...
                    full_path = os.path.normpath(full_path)

                    if os.path.exists(full_path):
                        open_with_default_app(full_path)
                        print('Opening relative path...')
                        return


# ----

# ctrl+` -> view.run_command("select_empty_lines")
class SelectEmptyLinesCommand(sublime_plugin.TextCommand):
    """
    Takes a view and selects all of the empty lines
    """
    def run(self, edit):

        print("Selecting empty lines...")

        # construct a region that encompasses the entire view
        r = sublime.Region(0, self.view.size())

        # split the view region up into a list of regions containing that
        # encapsulates lines within the buffer
        lines = self.view.split_by_newlines(r)

        # ----------------
        # Strip empty lines from the start and ends of the buffer
        empty_start_lines = True
        empty_end_lines = True
        while empty_start_lines or empty_end_lines:
            if len(lines[0]) == 0:
                lines.pop(0)
            else:
                empty_start_lines = False

            if len(lines[-1]) == 0:
                lines.pop(-1)
            else:
                empty_end_lines = False
        # ----------------

        # ----------------
        # Remove empty adjacent lines. That is, if we have an empty line
        # in the list and the next line is empty, remove that next line
        # from the list, we don't want to select it

        new_list = []

        previous_empty = False
        for l in lines:

            if len(l) > 0:
                new_list.append(l)
                previous_empty = False

            else:
                if not previous_empty:
                    new_list.append(l)
                    previous_empty = True

        lines = new_list
        # ----------------

        empty_lines = [l for l in lines if l.size() == 0]

        self.view.sel().clear()

        for el in empty_lines:
            self.view.sel().add(el)

        print('{} empty lines selected.'.format(len(empty_lines)))


def find_regions_by_selections(view):
    """
    Take the view and split it up into regions based on the cursor(s) location.
    If there is one cursor, two regions will be returned. If there are 2 cursors, 3
    regions will be returned.
    """

    # Determine where to split the document
    values = set()
    sel = view.sel();
    for s in sel:
        r,c = view.rowcol(s.a)
        values.add(r)

        r,c = view.rowcol(s.b)
        values.add(r)

    # the set isn't sorted
    values = sorted(values)

    # collect the areas into regions, starting at the beginning
    # of the document to the first
    regions = []
    a = 0
    for row in values:
        b = view.text_point(row, 0)

        # construct a region to capture the 'in-between' text
        r = sublime.Region(a, b)

        # Make sure there are enough characters. There has to be
        # more than 2 char (i.e. \n) for us to consider it a valid region
        if r.size() > 1:
            regions.append(r)

        a = b

    # capture the last part of the file
    r = sublime.Region(a, view.size())
    if r.size() > 1:
        regions.append(r)

    return regions

def random_4_digit_hex():
    """
    Generate a random 4 digit hex value between 4096 (0x1000) and 65535 (0xffff)

    # Return

    Random hex string between between 4096 (0x1000) and 65535 (0xffff)

    # Note

    >>> from random import randint
    >>> print(f'{randint(4096, 65535):x}')
    2ec7

    4 Digit:
    >>> int(0x1000)
    4096
    >>> int(0xffff)
    65535

    5 digit:
    >>> int(0xfffff)
    1048575
    >>> int(0x10000)
    65536

    """

    lower = 4096
    upper = 65535

    return "{:x}".format(randint(lower, upper))

def suggest_date_based_name(extension):
    """

    Generate a file string based on the current date and a random 4 digit
    hex number

    # Parameters

    extension - str
        - the file extension to use (.txt, .md)

    # Returns

    A new name based on the current date and a random hex number.

    """

    return '{} [{}]{}'.format(datetime.now().date().isoformat(), random_4_digit_hex(), extension)


# # NOTE: Need to install PackageDev to get access to the PathLib for Sublime v3.2.2 Build 3211
# def new_view_from_lines(window, lines, view_name):
#     """
#     Creates a new view in sublime text that isn't saved yet. The view will be populated
#     with the lines in the list.

#     # Parameters

#     edit

#     window - Window
#         - the sublime text window object

#     lines - str
#         - Represents the string to write to the view.

#     view_name - str
#         - the name of the buffer

#     """

#     new_view = window.new_file()
#     new_view.set_name(view_name)
#     new_view.run_command("bluebill_insert_text", {'start':0, 'text':lines})

#     return new_view


# # ctrl+` -> view.run_command("bluebill_new_note_view", {'text': new_text})
# class BluebillNewNoteViewCommand(sublime_plugin.TextCommand):
#     """
#     Create a new view for a note based and insert the text.
#     """

#     def run(self, edit, text):
#         """
#         Create a new view based and insert the text. The view will be named
#         using an iso date suitable for a note in the system.

#         # Parameters

#         edit - Edit
#             - The edit object to identify this operation.

#         text str
#             - The text to insert.

#         root str
#             - The path that we want to store the view in

#         # Usage

#         view.run_command("bluebill_new_note_view", {'text': new_text})
#         """

#         fn = suggest_date_based_name(".md")
#         nv = new_view_from_lines(self.view.window(), text, fn)

#         # This doesn't work the way I want it. It just saves it without prompting
#         # if root:
#         #     # retarget requires the complete path so when the user saves, it opens in a folder
#         #     # we are interested in.
#         #     nv.retarget(str(Path(root).joinpath(fn)))


# # ctrl+` -> view.run_command("clone_current_view")
# class CloneCurrentViewCommand(sublime_plugin.TextCommand):
#     """
#     Make a clone of the currently active view with different file name.

#     Useful when you need to make a new meeting note or other notes from an existing one.

#     It will create a new view, copy all of the text and insert it and name the file
#     based on the current date and hex code.

#     """

#     def run(self, edit):

#         active_view = self.view
#         r = sublime.Region(0, active_view.size())

#         self.view.run_command("bluebill_new_note_view", {'text': active_view.substr(r)})


# # ctrl+` -> view.run_command("new_note_menu")
# class NewNoteMenuCommand(sublime_plugin.TextCommand):
#     """
#     Display a menu to allow the user to select what kind of template to apply
#     when creating a new note.

#     """

#     def __init__(self, view):
#         super().__init__(view)

#         self.menu_options = [('Clone Active View', "clone_current_view")]

#         # Get the root project folder name
#         if self.view.window().project_file_name():
#             project = Path(self.view.window().project_file_name()).resolve()

#             # Does the template folder (.templates) exist?
#             template_folder = project.parent.joinpath('.templates')
#             if template_folder.exists():

#                 # Construct the menu:
#                 for f in template_folder.glob("*"):
#                     self.menu_options.append((f.stem, f))


#     def run(self, edit):

#         # find the .templates folder - it should be in the path of the project

#         # find the files in the .templates folder, the name of the file will be the menu name

#         # present the menu of choices to the user


#         #https://www.sublimetext.com/docs/3/api_reference.html#sublime.Window
#         self.view.window().show_quick_panel([m for m, c in self.menu_options], self.on_done)

#         # show_quick_panel(items, on_done, <flags>, <selected_index>, <on_highlighted>)
#         # self.view.show_popup_menu(['foo', 'bar'], self.done)


#     def on_done(self, selected_index):
#         """
#         This method is called when the menu is done showing and the user made a choice.

#         The selected_index will contain the index integer of the users choice. If they canceled
#         the value will be -1.

#         """

#         if selected_index < 0:
#             print('User canceled.')

#         # Did the user select the Clone option?
#         elif selected_index == 0:
#             m, c = self.menu_options[selected_index]
#             self.view.run_command(c)

#         else:
#             m, f = self.menu_options[selected_index]

#             note_template = Path(f)
#             with note_template.open("r", encoding="utf-8") as f:
#                 text = f.read()

#                 # The file text will be following the python Template library for syntax
#                 # https://docs.python.org/3/library/string.html
#                 t = Template(text)

#                 # We only recognize the $Date variable right now
#                 s = t.substitute(Date=datetime.now().date().isoformat())

#                 # root = None
#                 # if self.view.window().project_file_name():
#                 #     root = Path(self.view.window().project_file_name()).resolve().parent

#                 self.view.run_command("bluebill_new_note_view", {'text': s})

# ==============
# Older methods that may not be required any more

# def new_view_from_region(index, current_view, regions):
#     """
#     Takes the current view and a region within that view and constructs
#     a new view from it.
#     """

#     # at this point, the text is split up into regions based
#     # on the cursor positions within the document. Insert the
#     # region into a new documents
#     new_view = current_view.window().new_file()
#     # new_view.insert(edit, 0 , '\n'.join([current_view.substr(r) for r in regions]))
#     new_view.run_command("bluebill_insert_text", {'start':0, 'text':'\n'.join([current_view.substr(r) for r in regions])})

#     # print(current_view.name())
#     # print(current_view.file_name())

#     # capture the name of the current view as a default
#     view_name = current_view.name()

#     # if the view has a file name, use that to generate a view name.
#     if current_view.file_name():

#         # Capture the original path
#         original_path = Path(current_view.file_name()).resolve()

#         # Construct a new path based on the original
#         new_path = original_path.parent.joinpath('{} ({}){}'.format(original_path.stem,
#                                                                     index,
#                                                                     original_path.suffix))

#         # Link the new view to the new path
#         new_view.retarget(str(new_path))

#         # set the new views name - TBW 2020-06-20 - this isn't required
#         # view_name = new_path.name

#         # save the view
#         new_view.run_command('save')

#     # TBW 2020-06-20 - This isn't required
#     # new_view.set_name(str(view_name))


# # ctrl+` -> view.run_command("split_by_selection")
# class SplitBySelectionCommand(sublime_plugin.TextCommand):
#     """
#     The idea is that if the user places the cursor on a line in the
#     document we can generate two documents, one with the top portion and the
#     other with the bottom portion (including the selected line). If 3 lines are
#     selected, we are only interested in the row numbers, but 3 files will be generated.
#     """
#     def run(self, edit):
#         print('Splitting the view into regions based on the cursor position(s).')

#         regions = find_regions_by_selections(self.view)

#         for i, r in enumerate(regions):

#             # print('Region {} ->'.format(i))
#             # print()
#             # print(self.view.substr(r))
#             # print()
#             # print('<<<<<>>>>>>')

#             new_view_from_region(i, self.view, edit, [r])


# # ctrl+` -> view.run_command("split_by_selection_and_append")
# class SplitBySelectionAndAppendCommand(sublime_plugin.TextCommand):
#     """
#     The idea is that if the user places the cursor on a line in the
#     document we can generate two documents, one with the top portion and the
#     other with the bottom portion (including the selected line). If 3 lines are
#     selected, we are only interested in the row numbers, but 3 files will be generated.
#     """
#     def run(self, edit):

#         print('Splitting the view into regions based on the cursor position(s) and appending them to the first section.')
#         regions = find_regions_by_selections(self.view)

#         for i, r in enumerate(regions[1:]):

#             # print('Region {} ->'.format(i))
#             # print()
#             # print(self.view.substr(r))
#             # print()
#             # print('<<<<<>>>>>>')

#             new_view_from_region(i, self.view, edit, [regions[0], r])
