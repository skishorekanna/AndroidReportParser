"""
This is the utility for parsing the android logs
"""
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

    def read_file(self, path):
        with open(path,encoding='utf-8') as f:
            self.lines = f.readlines()

    def process_line(self, line):
        """ To process line and update the dictionaries """
        pass

    def process_lines(self):
        """ To process all lines """
        for line in self.lines:
            self.processline(line)

    def print_fatalexceptions(self):
        """ To print only the fatal exceptions """
        pass

    def print_errors(self):
        """ To print only the errors"""
        pass

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


if __name__=="__main__":
    main()
