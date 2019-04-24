#!/usr/bin/env python3
import os
import sys
import re
from itertools import chain

# import framework
from framework import Experiment, ExperimentEngine


OINK = "tools/oink"


###
# We have some classes implementing Experiment:
# - <parse_log> to parse a log file into a result dictionary (or None)
# - <get_text> to obtain a textual description from a result dictionary
###


class ExpOink(Experiment):
    def __init__(self, name, model):
        super().__init__(name=name, call=[], group=name)
        self.group = name
        self.solver = ""
        self.name = f"{name}"
        self.call = [OINK, model, "-v"]
        self.model = model

    def parse_log(self, contents):
        s = re.search(r'solution verified', contents)
        if not s:
            return None
        res = {}
        s = re.search(r'solving took ([\d\.,]+)', contents)
        if s:
            res['solving'] = float(s.group(1))
        else:
            res['solving'] = float(0)
        s = re.search(r'preprocessing took ([\d\.,]+)', contents)
        if s:
            res['preprocessing'] = float(s.group(1))
        else:
            res['preprocessing'] = float(0)
        s = re.search(r'total solving time: ([\d\.,]+)', contents)
        if s:
            res['time'] = float(s.group(1))
        s = re.search(r'with ([\d]+) nodes and ([\d]+) edges', contents)
        if s:
            res['nodes'] = int(s.group(1))
            res['edges'] = int(s.group(2))
        else:
            res['nodes'] = res['edges'] = 0
        s = re.search(r'([\d]+) priorities', contents)
        if s:
            res['priorities'] = int(s.group(1))
        else:
            res['priorities'] = 0
        s = re.search(r'solved with ([\d\.,]+) major iterations, ([\d\.,]+) minor iterations', contents)
        if s:
            res['iterations'] = int(s.group(1)+s.group(2)) # major + minor
        s = re.search(r'solved with ([\d\.,]+) iterations', contents)
        if s:
            res['iterations'] = int(s.group(1))
        s = re.search(r'solved with ([\d\.,]+) promotions', contents)
        if s:
            res['promotions'] = int(s.group(1))
        s = re.search(r'solved with ([\d]+) tangles', contents)
        if s:
            res['tangles'] = int(s.group(1))
        s = re.search(r'solved with ([\d\.,]+) tangles and ([\d\.,]+) iterations', contents)
        if s:
            res['tangles'] = int(s.group(2))
            res['iterations'] = int(s.group(2))
        return res

    def get_text(self, res):
        if 'error' in res:
            return res['error']
        return "{:0.6f} sec".format(res['time'])

    def compress(self):
        self.name = "{}-c".format(self.name)
        self.solver = "{}-c".format(self.solver)
        self.call += ["--compress"]
        return self

    def inflate(self):
        self.name = "{}-i".format(self.name)
        self.solver = "{}-i".format(self.solver)
        self.call += ["--inflate"]
        return self

    def scc(self):
        self.name = "{}-s".format(self.name)
        self.solver = "{}-s".format(self.solver)
        self.call += ["--scc"]
        return self

    def nosp(self):
        self.name = "{}-n".format(self.name)
        self.solver = "{}-n".format(self.solver)
        self.call += ["--no-loops", "--no-single", "--no-wcwc"]
        return self

    def fpi(self):
        self.name = f"{self.name}-fpi"
        self.solver = "fpi"
        self.call += ["--fpi", "-w", "1"]
        return self

    def fpj(self):
        self.name = f"{self.name}-fpj"
        self.solver = "fpj"
        self.call += ["--fpj", "-w", "1"]
        return self

    def tl(self):
        self.name = f"{self.name}-tl"
        self.solver = "tl"
        self.call += ["--tl"]
        return self

    def rtl(self):
        self.name = f"{self.name}-rtl"
        self.solver = "rtl"
        self.call += ["--rtl"]
        return self

    def ortl(self):
        self.name = f"{self.name}-ortl"
        self.solver = "ortl"
        self.call += ["--ortl"]
        return self

    def npp(self):
        self.name = f"{self.name}-npp"
        self.solver = "npp"
        self.call += ["--npp"]
        return self

    def zlk(self):
        self.name = f"{self.name}-zlk"
        self.solver = "zlk"
        self.call += ["--zlk", "-w", "1"]
        return self


###
# Now that we have defined our experiments, we define the collections
###


class FileFinder(object):
    def __init__(self, directory, extensions):
        self.directory = directory
        self.extensions = extensions

    def __iter__(self):
        if not hasattr(self, 'files'):
            self.files = []
            for ext in self.extensions:
                dotext = "." + ext
                # get all files in directory ending with the extension
                files = [f[:-len(dotext)] for f in filter(lambda f: f.endswith(dotext) and os.path.isfile(self.directory+"/"+f), os.listdir(self.directory))]
                self.files.extend([(x, "{}/{}{}".format(self.directory, x, dotext)) for x in files])
        return self.files.__iter__()


class OinkExperiments(object):
    def __init__(self, directory, solvers=None):
        if solvers is None:
            solvers = []
        self.files = FileFinder(directory, ["pg","pg.bz2","pg.gz","gm","gm.bz2","gm.gz"])
        self.solvers = solvers

    def get_solvers(self):
        return {
            'fpi': lambda name, filename: ExpOink(name, filename).fpi().nosp(),
            'fpj': lambda name, filename: ExpOink(name, filename).fpj().nosp(),
            'tl': lambda name, filename: ExpOink(name, filename).tl().nosp(),
            'rtl': lambda name, filename: ExpOink(name, filename).rtl().nosp(),
            'ortl': lambda name, filename: ExpOink(name, filename).ortl().nosp(),
            'npp': lambda name, filename: ExpOink(name, filename).npp().nosp(),
            'zlk': lambda name, filename: ExpOink(name, filename).zlk().nosp(),
            }

    def __iter__(self):
        if not hasattr(self, 'grouped'):
            # define
            slvrs = self.get_solvers()
            if len(self.solvers) != 0:
                slvrs = {k:v for k,v in slvrs.items() if k in self.solvers}
            for slvr in slvrs:
                setattr(self, slvr, {})
            self.grouped = {}
            for name, filename in self.files:
                self.grouped[name] = []
                for slvr, fn in slvrs.items():
                    exp = fn(name, filename)
                    getattr(self, slvr)[name] = exp
                    self.grouped[name].append(exp)
        return self.grouped.values().__iter__()
