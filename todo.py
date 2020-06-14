#!/usr/bin/env python3

################################################################################
# Author: Mike Brown (m8r0wn), Darnell Martin (darneymartin)
# License: GPL-3.0
# Description: Search through files on the local machine and identify @TODO tags
#              to create a task list for developers.
################################################################################

import click
import os
import re
import threading
from sys import exit, argv, stdout
from time import sleep


################################################################################
#
# Class that inherits the threading.Thread class to create a thread that will be
# supplied a filename as an argument to scan and parse.
#
################################################################################
class ParserThread(threading.Thread):

    #-----------------------------------------------
    # Initializes the object
    #-----------------------------------------------
    def __init__(self, filename):
        threading.Thread.__init__(self)
        self.filename = filename
    #-----------------------------------------------
    # This method will be ran whenever the start
    # method is called.
    #-----------------------------------------------
    def run(self):
        self._running = True
        try:
            with open(self.filename) as f:
                content = f.readlines()
            content = [x.strip() for x in content]
            line_count = 1
            for line in content:
                if self.match(line):
                    comment = self.parse(line)
                    click.echo(click.style(self.filename +"  " + str(line_count) + "  "+ comment,fg='blue'))
                line_count += 1
        except UnicodeDecodeError as e:
            pass
        self._running = False

    #-----------------------------------------------
    # Forces the thread to stop by setting the
    # _running flag equal to False
    #-----------------------------------------------
    def stop(self):
        self._running = False

    #-----------------------------------------------
    # Returns the state of the thread
    # True for running and False for stopped
    #-----------------------------------------------
    def isRunning(self):
        return self._running

    #-----------------------------------------------
    # Returns whether the line contains a match
    #-----------------------------------------------
    def match(self,line):
        regex = re.compile('.*@TODO.*')
        if regex.match(line) is not None:
            return True
        else:
            return False

    #-----------------------------------------------
    # Returns the parsed comment when found
    #-----------------------------------------------
    def parse(self, line):
        regex = re.compile('.*@TODO(.+)')
        m = regex.match(line)
        if m is not None:
            comment = m.group(1)
            comment = comment.strip()
            comment = re.sub('^[/:/-]','',comment)
            comment = comment.strip()
            return comment
        else:
            return "No Comment"

################################################################################
#
# Called by single thread, used to get all files within the directory that was
# supplied by the user OR just the file that was supplied
#
################################################################################
class SearchThread(threading.Thread):

    #-----------------------------------------------
    # Initializes the object
    #-----------------------------------------------
    def __init__(self, path):
        threading.Thread.__init__(self)
        self.daemon = True
        self.path = path
        self.file_queue = []

    #-----------------------------------------------
    # This method will be ran whenever the start
    # method is called.
    #-----------------------------------------------

    @staticmethod
    def not_hidden_path(path):
        dirs=path.split(path)
        if len(dirs) > 1:
            return False
        return True

    def run(self):
        self._running = True
        if os.path.isfile(self.path):
            self.file_queue.append(self.path)
        else:
            if SearchThread.not_hidden_path(self.path):
                for root, dirs, files in os.walk(self.path):
                    for file in files:
                        self.file_queue.append(os.path.join(root, file))
        self._running = False

    #-----------------------------------------------
    # Returns the state of the thread
    # True for running and False for stopped
    #-----------------------------------------------
    def isRunning(self):
        return self._running

    #-----------------------------------------------
    # Returns the file_queue that is built by the
    # thread
    #-----------------------------------------------
    def getFileQueue(self):
        return self.file_queue

################################################################################
#
# The main function that gets ran whenever the program is ran
#
################################################################################


@click.command()
@click.option("--path", help='Target path')
@click.option("--maxthreads", default=6, help='Define maximmum no. of threads to be used(Default: 6)')
def main(info,path,maxthreads):
    """
    Tool to search through files on the local machine and identify @TODO tags to create a task list for developers.

    Usage:

        todo  --path=/dir

        todo --path=/root/project-one/
    """
    try:
        click.echo(click.style("File\tLine#\tComment",fg='green'))
        # Launch thread to search directory and place in file queue
        search_thread = SearchThread(path)
        search_thread.daemon = True
        search_thread.start()

        #Wait for the SearchThread to finish running
        while(search_thread.isRunning()):
            sleep(0.01)

        #Get the list of files
        file_queue = search_thread.getFileQueue()

        #Free up the memory
        del search_thread

        #Start file lookup
        active_threads = []
        while file_queue:
            thread = ParserThread(file_queue.pop(0))
            thread.start()
            active_threads.append(thread)
            while(threading.activeCount() == maxthreads):
                sleep(0.01)
                for thread in reversed(active_threads):
                    if thread.isRunning() == False:
                        active_threads.remove(thread)

        # Wait for threads to close
        while len(active_threads) > 0:
            sleep(0.01)
            for thread in reversed(active_threads):
                if thread.isRunning() == False:
                    active_threads.remove(thread)

    except Exception as e:
        click.echo("\n[!] An Unknown Event Occured, Closing...", err=True)
        exit(1)
    except KeyboardInterrupt:
        click.echo("\n[!] Key Event Detected, Closing...", err=True)
        exit(0)


################################################################################
if __name__ == '__main__':
    main()

