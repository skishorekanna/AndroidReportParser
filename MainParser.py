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
        self.stacktracestr = ""
        self.stacktracelist = []
        self.stacktraceflag = False
        self.pattern = "\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}  (\d{4})  \d{4} ([A-Z]) .*:(.*)"
        self.stack_pattern = "\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}  (\d{4})  \d{4} ([A-Z]) (\w*AndroidRuntime):.*at\w*.*"
        self.stack_header_pattern = "\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}  (\d{4})  \d{4} (E) (\w*AndroidRuntime\w*):(.*)"
        def read_file(path):
            with open(path,encoding='utf-8') as f:
                self.lines = f.readlines()
        read_file(filepath)

    def process_line(self, line, line_number):
        """ To process line and update the dictionaries
        # Note: There are three groups matched
        # group(1) is pid
        # group(2) is log level
        # group(3) is log message
        """
        # If exception header is found, we need to add to errors as well as stack trace
        if re.match(self.stack_header_pattern, line):
            self.stacktracestr += line
            self.stacktraceflag = True
        elif re.match(self.stack_pattern, line):
            self.stacktracestr += line
        else:
            if self.stacktraceflag:
                    self.stacktracelist.append(self.stacktracestr)
                    self.stacktracestr = ""
                    self.stacktraceflag = False                
            s = re.match(self.pattern, line)
            if s:
                if self.pid == s.group(1):
                    log_level = s.group(2)
                    msg = s.group(3)
                    if log_level == "E":
                        if self.errors.get(msg):
                            self.errors[msg].append(line_number)
                        else:
                            self.errors[msg]=[line_number]


    def process_lines(self):
        """ To process all lines """
        for lineno,line in enumerate(self.lines, start=1):
            self.process_line(line, lineno)

    def print_fatalexceptions(self):
        """ To print only the fatal exceptions """
        print("\nFATAL EXCEPTION")
        print("===============")
        for number, string in enumerate(self.stacktracelist,start=1):
            string_lines = string.split("\n")
            print("#{0}){1}".format(number,string_lines[2]))        


    def print_stacktraces(self):
        print("\nStacktrace")
        print("==========")
        for number, string in enumerate(self.stacktracelist,start=1):
            string_lines = string.split("\n")
            print("#{0}){1}".format(number,string))

    def print_errors(self):
        """ To print only the errors"""
        print("\nErrors")
        print("=======")
        for number, string in enumerate(self.stacktracelist,start=1):
            string_lines = string.split("\n")
            print("#{0}){1}".format(number,string_lines[2]))

    def print_matchingstrings(self):
        """ To print only the matching strings"""
        pass

    def print_all(self):
        """ To print the final output"""
        self.print_fatalexceptions()
        self.print_stacktraces()
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
