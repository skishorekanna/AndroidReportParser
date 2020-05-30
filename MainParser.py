"""
This is the utility for parsing the android logs
"""

import re

class LogParser:
    def __init__(self, filepath, process_id, search_strings):
        self.filepath = filepath
        self.search_strings = search_strings
        self.pid = process_id
        self.lines = []
        self.fatalexceptions = {}
        self.errors = {}
        self.matching_strings = {}
        self.stacktraces = {}
        self.pattern = "\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}  (\d{4})  \d{4} ([A-Z]) .*:(.*)"
        def read_file(path):
            with open(path,encoding='utf-8') as f:
                self.lines = f.readlines()
        read_file(filepath)

    def process_line(self, line):
        """ To process line and update the dictionaries """
        if "FATAL EXCEPTION" in line:
            print(line)
        else:
            s = re.match(self.pattern, line)
            # There are three groups matched
            # group(1) is pid
            # group(2) is log level
            # group(3) is log message
            if s:
                if self.pid == s.group(1):
                    log_level = s.group(2)
                    msg = s.group(3)
                    if log_level == "E":
                        if self.errors.get(msg):
                            self.errors[msg]+=1
                        else:
                            self.errors[msg]=1


    def process_lines(self):
        """ To process all lines """
        for line in self.lines:
            self.process_line(line)

    def print_fatalexceptions(self):
        """ To print only the fatal exceptions """
        pass

    def print_errors(self):
        """ To print only the errors"""
        if self.errors:
            for value, count in self.errors.items():
                print("{}|{}".format(value,count))

    def print_matchingstrings(self):
        """ To print only the matching strings"""
        pass

    def print_all(self):
        """ To print the final output"""
        self.print_fatalexceptions()
        self.print_errors()
        self.print_matchingstrings()


def main():
    import sys
    input_file = "bugreport-N2G47H-2019-08-27-19-02-04.txt"
    sys.argv.append(input_file)
    if len(sys.argv) < 2:
        print("Please provide file as the input")
        exit(-1)
    lp = LogParser(input_file,"4667",[])
    lp.process_lines()
    lp.print_all()


if __name__=="__main__":
    main()
