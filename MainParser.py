"""
Utility for parsing the android logs.


Usage:
MainParser.py <filepath> <pid> <search strings>
filepath - path to the file - type(str)
pid - process id - type(str)
search_strings - strings to be searched as comma separated values- type( list of strings )

Note: search_strings are optional; Rest all the parameters are mandatory

***************************INPUT********************************************************
>python MainParser.py bugreport-N2G47H-2019-08-27-19-02-04.txt 4667 "WARNING","OOM"
***************************OUTPUT********************************************************
FATAL EXCEPTION
===============
#1)java.lang.IllegalStateException: Can not perform this action after onSaveInstanceState|2
#2)java.lang.OutOfMemoryError: OutOfMemoryError thrown while trying to throw OutOfMemoryError; no stack trace available|1

Stacktrace
==========
#1)java.lang.IllegalStateException: Can not perform this action after onSaveInstanceState
       at android.support.v4.app.FragmentManagerImpl.checkStateLoss(Unknown Source:10)
       at android.support.v4.app.FragmentManagerImpl.enqueueAction(Unknown Source:2)
       at android.support.v4.app.BackStackRecord.a(Unknown Source:78)
       at android.support.v4.app.BackStackRecord.commit(Unknown Source:1)
       at glance.ui.sdk.activity.GlanceHomeActivity.showBingeContainer(Unknown Source:19)
       at glance.ui.sdk.activity.GlanceHomeActivity.e(Unknown Source:0)
       at glance.ui.sdk.activity.GlanceHomeActivity$3.onTabSelected(Unknown Source:30)
       at android.support.design.widget.TabLayout.dispatchTabSelected(Unknown Source:19)
       at android.support.design.widget.TabLayout.a(Unknown Source:55)
       at android.support.design.widget.TabLayout.a(Unknown Source:1)
       at android.support.design.widget.TabLayout$Tab.select(Unknown Source:14)
       at android.support.design.widget.TabLayout$TabView.performClick(Unknown Source:16)
       at android.view.View.performClickInternal(View.java:6585)
       at android.view.View.access$3100(View.java:785)
       at android.view.View$PerformClick.run(View.java:25921)
       at android.os.Handler.handleCallback(Handler.java:873)
       at android.os.Handler.dispatchMessage(Handler.java:99)
       at android.os.Looper.loop(Looper.java:201)
       at android.app.ActivityThread.main(ActivityThread.java:6810)
       at java.lang.reflect.Method.invoke(Native Method)
       at com.android.internal.os.RuntimeInit$MethodAndArgsCaller.run(RuntimeInit.java:547)
       at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:873)


Errors
=======
#1)java.lang.IllegalStateException: Can not perform this action after onSaveInstanceState|2
#2)java.lang.OutOfMemoryError: OutOfMemoryError thrown while trying to throw OutOfMemoryError; no stack trace available|1

Matching Strings
==================
#1)Throwing OutOfMemoryError "Failed to allocate a 12 byte allocation with 0 free bytes and -2MB until OOM"|4
#2)Throwing OutOfMemoryError "Failed to allocate a 28 byte allocation with 0 free bytes and -2MB until OOM"|2
#3)Throwing OutOfMemoryError "Failed to allocate a 32 byte allocation with 0 free bytes and -2MB until OOM"|1
#4)Throwing OutOfMemoryError "Failed to allocate a 24 byte allocation with 0 free bytes and -2MB until OOM"|2
#5)Throwing OutOfMemoryError "Failed to allocate a 43 byte allocation with 0 free bytes and -2MB until OOM"|2
#6)Throwing OutOfMemoryError "Failed to allocate a 16 byte allocation with 0 free bytes and -2MB until OOM"|1
#7)Throwing OutOfMemoryError "Failed to allocate a 56 byte allocation with 0 free bytes and -2MB until OOM"|1
#8)Throwing OutOfMemoryError "Failed to allocate a 8204 byte allocation with 0 free bytes and -2MB until OOM"|2
#9)Throwing OutOfMemoryError "Failed to allocate a 128 byte allocation with 0 free bytes and -2MB until OOM"|1
#10)JNI WARNING: java.lang.OutOfMemoryError thrown while calling printStackTrace|3
#11)Throwing OutOfMemoryError "Failed to allocate a 28 byte allocation with 0 free bytes and -2MB until OOM" (recursive case)|16

"""
import sys
import os
import re
from collections import OrderedDict

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
        self.output = OrderedDict({})
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
        if header_match and self.pid==header_match.group(1):
            self.stacktracestr += (header_match.group(4) + self.newline)
            self.stacktraceflag = True
        elif content_match and self.pid==content_match.group(1):
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
        for index,(key, value) in enumerate(self.output.items(),start=1):
            print("#{0}){1}|{2}".format(index,key,value["count"]))

    def print_stacktraces(self):
        print("\nStacktrace")
        print("==========")
        for index, (key, value) in enumerate(self.output.items(),start=1):
            if value["content"]:
                print("#{0}){1}".format(index,key+self.newline+value["content"]))

    def print_errors(self):
        """ To print only the errors"""
        print("\nErrors")
        print("=======")
        for index, (key, value) in enumerate(self.output.items(),start=1):
            print("#{0}){1}|{2}".format(index,key,value["count"]))

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
    if len(sys.argv) < 3:
        print("Insufficient number of arguments.")
        print(__doc__)
        exit(-1)
    search_list = sys.argv[3]
    if sys.argv[3]:
        search_list = sys.argv[3].split(",")
    else:
        search_list = []
    lp = LogParser(sys.argv[1],sys.argv[2],search_list)
    if not os.path.exists(sys.argv[1]):
        print("Given log file does not exist")
        exit(-2)
    lp.process_lines()
    lp.print_all()


if __name__=="__main__":
    main()
