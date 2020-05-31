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
        self.matching_strings = {}
        self.stacktracestr = ""
        self.stacktracelist = []
        self.stacktraceflag = False
        self.pattern = "\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}  (\d{4})  \d{4} ([A-Z] \w*\s*:\s*) (.*)"
        self.stack_header_pattern = "\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}  (\d{4})  \d{4} (E) (\w*AndroidRuntime\w*): (.*)"
        self.stack_pattern = "\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}  (\d{4})  \d{4} (E) (\w*AndroidRuntime\w*):.*at (.*)"
        self.output = {}
        self.newline = "\n"
        def read_file(path):
            with open(path,encoding='utf-8') as f:
                self.lines = f.readlines()
        read_file(filepath)

    def process_line(self, line, line_number):
        """ To process line and update the dictionaries
        # Note: There are three groups matched
        # group(1) is pid
        # group(2) is log level
        # group(4) is log message
        """
        # If exception header is found, we need to add to errors as well as stack trace
        header_match = re.match(self.stack_header_pattern, line)
        content_match = re.match(self.stack_pattern, line)
        if header_match:
            self.stacktracestr += (header_match.group(4) + self.newline)
            self.stacktraceflag = True
        elif content_match:
            self.stacktracestr += (content_match.group(4) + self.newline)
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
                    for search_str in self.search_strings:
                        if search_str in msg:
                            if self.matching_strings.get(msg):
                                self.matching_strings[msg].append(line_number)
                            else:
                                self.matching_strings[msg]=[line_number]


    def process_lines(self):
        """ To process all lines """
        for lineno,line in enumerate(self.lines, start=1):
            self.process_line(line, lineno)
        self.parse_output()

    def parse_output(self):
        """
        This is the process the output and convert it to dict.
        rtype: dict key-> number value-> content, count
        """
        for number, string in enumerate(self.stacktracelist,start=1):
            lines = string.split(self.newline)
            already_added = []
            header = lines[2]
            content = "\n".join(lines[3:])
            if self.output.get(header):
                self.output[header]["count"]+=1
            else:
                self.output[header]={"count":0,"content":"","number":-1}
                self.output[header]["count"]=1
                self.output[header]["content"]=content
                self.output[header]["number"]=number

    def print_fatalexceptions(self):
        """ To print only the fatal exceptions """
        print("\nFATAL EXCEPTION")
        print("===============")
        for key, value in self.output.items():
            print("#{0}){1}|{2}".format(value["number"],key,value["count"]))

    def print_stacktraces(self):
        print("\nStacktrace")
        print("==========")
        for key, value in self.output.items():
            if value["content"]:
                print("#{0}){1}".format(value["number"],key+self.newline+value["content"]))

    def print_errors(self):
        """ To print only the errors"""
        print("\nErrors")
        print("=======")
        for key, value in self.output.items():
            print("#{0}){1}|{2}".format(value["number"],key,value["count"]))

    def print_matchingstrings(self):
        """ To print only the matching strings"""
        print("\nMatching Strings")
        print("==================")
        for index, (key, values) in enumerate(self.matching_strings.items(), start=1):
            print("#{0}){1}|{2}".format(index, key,len(values)))        
    
    def print_all(self):
        """ To print the cummulative output"""
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
    lp = LogParser(input_file,"4667",["WARNING","OOM","OutOfMemoryError"])
    lp.process_lines()
    lp.print_all()


if __name__=="__main__":
    main()
