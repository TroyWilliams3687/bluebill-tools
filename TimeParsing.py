import sublime, sublime_plugin
from datetime import datetime, timedelta

"""
On linux this plugin goes here:
/home/troy/.config/sublime-text-2/Packages/TimeParser/

On windows this plugin goes:
C:\\Users\troy.williams\AppData\Roaming\Sublime Text 2\Packages\TimeParsing\

Add this key binding to Key-Bindings User:
{ "keys": ["ctrl+shift+t"], "command": "time_parsing" }


Copyright (c) 2015 Troy Williams

License: The MIT License (http://www.opensource.org/licenses/mit-license.php)

"""

def get_total_seconds(td): return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 1e6) / 1e6

class TimeParsingCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        # self.view.insert(edit, 0, "Hello, World!")
        view = self.view
        for region in view.sel():
            if not region.empty():
                # Get the selected text
                s = view.substr(region)
                # s = self.parse_time_ranges_standard(s)
                s = self.parse_time_ranges_military(s)

                # replace the original
                # view.replace(edit, region, s)

                # add a new line and put the orginal after that
                view.insert(edit, region.end(), '\n' + s)

    def parse_time_ranges_standard(self, time_ranges):
        """
        Takes  a range of time_ranges of the form:
        T: 645am - 730am, 815am - 12pm, 1230pm - 345pm. The method attempts to
        parse out the time ranges into proper datetime objects.

        It assumes that all of the times are on the same date.

        returns a properly formatted string with the total time attached:
        06:45AM - 07:30AM, 08:15AM - 12:00PM, 12:30PM - 15:45PM (7:45:00)

        """
        # parse the time_ranges
        if not time_ranges.startswith('T:'):
            raise ValueError("{} is not a valid time range".format(time_ranges))

        ranges = time_ranges[2:].strip().split(',')
        # print(tokens)
        # ['645am - 730am', ' 815am - 12pm', ' 1230pm - 345pm']

        processed_values = []
        for time_span in ranges:
            # time_span = '645am - 730am'
            tokens = time_span.partition('-')
            left = tokens[0].strip()
            right = tokens[2].strip()

            if len(right) == 0:
                raise ValueError("missing range in {}".format(time_span))

            # repair the numeric representation of the times so they are interpreted
            # correctly
            left_number_count = len(left[:-2])
            if left_number_count < 4:
                # we need to figure out where to pad
                # case 1, 1 digit - 1pm - need leading 0 and trailing minutes so
                #                  1pm becomes 0100pm
                # case 2, 2 digits - 11am - pad minutes, 11am -> 1100am
                # case 3, 3 digits - 111pm -> 1:11pm 111am <- doesn't make sense.
                #                           111pm -> 0111pm
                if left_number_count == 3:
                    left = '0' + left

                elif left_number_count == 2:
                    left = left[:-2] + '00' + left[-2:]

                elif left_number_count == 1:
                    left = '0' + left[:-2] + '00' + left[-2:]

            right_number_count = len(right[:-2])
            if right_number_count < 4:
                if right_number_count == 3:
                    right = '0' + right

                elif right_number_count == 2:
                    right = right[:-2] + '00' + right[-2:]

                elif right_number_count == 1:
                    right = '0' + right[:-2] + '00' + right[-2:]

            start_time = datetime.strptime(left, '%I%M%p')
            end_time = datetime.strptime(right, '%I%M%p')

            # see if the times need to be swapped
            if start_time > end_time:
                start_time, end_time = end_time, start_time

            processed_values.append((start_time,
                                     end_time,
                                     end_time - start_time))

        formatted_values = []
        for value in processed_values:
            formatted_values.append('{0:%I:%M%p} - {1:%I:%M%p}'.format(*value))

        total_time = sum([p[-1] for p in processed_values], timedelta())

        formatted_times = ', '.join(formatted_values)
        # return '{0} ({1} -> {2}s)'.format(formatted_times,
        #                                   total_time,
        #                                   int(get_total_seconds(total_time)))



        total_seconds = get_total_seconds(total_time)
        days, seconds = total_time.days, total_time.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        # seconds = seconds % 60

        decimal_hours = hours + minutes/60.0
        return '{0} ({1}h{2}m -> {3:.2f}h -> {4}s)'.format(formatted_times,
                                                           hours,
                                                           minutes,
                                                           decimal_hours,
                                                           int(total_seconds))

    def parse_time_ranges_military(self, time_ranges):
        """
        Takes  a range of time_ranges of the form:
        T: 0645 - 0730, 0815 - 1200, 1230 - 1545. The method attempts to
        parse out the time ranges into proper datetime objects.

        It assumes that all of the times are on the same date.

        returns a properly formatted string with the total time attached:
        0645 - 0730, 0815 - 1200, 1230 - 1545 (7:45:00)

        """
        # parse the time_ranges
        if not time_ranges.startswith('T:'):
            raise ValueError("{} is not a valid time range".format(time_ranges))

        ranges = time_ranges[2:].strip().split(',')
        # print(tokens)
        # ['0645 - 0730', ' 0815 - 1200', ' 1230 - 1545']

        processed_values = []
        for time_span in ranges:
            # time_span = '0645 - 0730'
            tokens = time_span.partition('-')
            left = tokens[0].strip()
            right = tokens[2].strip()

            if len(right) == 0:
                raise ValueError("missing range in {}".format(time_span))

            # Make sure that the times have 4 charactors and is a number
            if len(left) != 4:
                raise ValueError("Not enough digits in {}".format(left))

            if len(right) != 4:
                raise ValueError("Not enough digits in {}".format(right))

            start_time = datetime.strptime(left, '%H%M')
            end_time = datetime.strptime(right, '%H%M')

            # see if the times need to be swapped
            if start_time > end_time:
                start_time, end_time = end_time, start_time

            processed_values.append((start_time,
                                     end_time,
                                     end_time - start_time))

        formatted_values = []
        for value in processed_values:
            formatted_values.append('{0:%H%M} - {1:%H%M}'.format(*value))

        total_time = sum([p[-1] for p in processed_values], timedelta())

        formatted_times = ', '.join(formatted_values)
        # return '{0} ({1} -> {2}s)'.format(formatted_times,
        #                                   total_time,
        #                                   int(get_total_seconds(total_time)))



        total_seconds = get_total_seconds(total_time)
        days, seconds = total_time.days, total_time.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        # seconds = seconds % 60

        decimal_hours = hours + minutes/60.0
        return '{0} ({1}h{2}m -> {3:.2f}h -> {4}s)'.format(formatted_times,
                                                           hours,
                                                           minutes,
                                                           decimal_hours,
                                                           int(total_seconds))


