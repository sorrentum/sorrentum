#!/usr/bin/python3


import sys
# from framework import Mapper
import os
# import sys
import csv

from itertools import groupby
from operator import itemgetter


SEPERATOR = "\t"

class Streaming(object):

    @staticmethod
    def get_job_conf(name):
        name = name.replace(".", "_")
        return os.environ.get(name)

    
    def __init__(self, infile=sys.stdin, seperator=SEPERATOR):
        self.infile = infile
        self.sep = seperator

    def emit(self, key, value):
        sys.stdout.write("{}{}{}\n".format(key, self.sep, value))

    def read(self):
        for line in self.infile:
            yield line.rstrip()

    def __iter__(self):
        for line in self.read():
            yield line


    
class Mapper(Streaming):

    def map(self):
        raise NotImplementedError("Mappers must implement a map method")

    def __iter__(self):
        for line in self.read():
            yield line.split(",")




class Reducer(Streaming):

    def reduce(self):
        raise NotImplementedError("Reducers must implement a reduce method")

    def __iter__(self):
        generator = (line.split(self.sep, 1) for line in self.read())
        for key, val in groupby(generator, itemgetter(0)):
            yield key, val

    
class AggMapper(Mapper):

    def map(self):
        
        for row in self:
            try:
                self.emit(row[4], float(row[11]))
            except Exception as e:
                pass


if __name__ == '__main__':
    mapper = AggMapper(sys.stdin)
    mapper.map()
