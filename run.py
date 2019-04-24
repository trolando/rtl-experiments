#!/usr/bin/env python3
from framework import ExperimentEngine, Experiment
from experiments import OinkExperiments
import os
import sys

ITERATIONS = 5
TIMEOUT = 300
LOGDIR = "logs"
CACHEFILE = "cache.json"

dirs = []
dirs += ["synt"]
# dirs += ["random2"]
dirs += ["modelchecking"]
dirs += ["equivchecking"]
# dirs += ["tc"]
# dirs += ["random1"]
# dirs += ["pgsolver"]
# dirs += ["mlsolver"]
# dirs += ["langincl"]


engine = ExperimentEngine(logdir=LOGDIR, cachefile=CACHEFILE, timeout=TIMEOUT)
for d in dirs:
    # exps = OinkExperiments("inputs/"+d, [["fpi-n","fpi","zlk","zlk-n","pp","pp-n","tl","tl-n","psi","psi-n","fpi-1","fpi-2","fpi-4","fpi-8","fpi-16"])
    exps = OinkExperiments("inputs/"+d)
    for group in exps:
        for exp in group:
            exp.dataset = d
    engine += exps


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def usage():
    cmd = os.path.realpath(__file__)
    eprint(f"Valid calls:")
    eprint(f"{cmd} todo <IT>      List all groups to do")
    eprint(f"{cmd} report         Report all experiments")
    eprint(f"{cmd} report <GROUP> Report all experiments in a group")
    eprint(f"{cmd} run <GROUP>    Run a group")
    eprint(f"{cmd} cache          Update the cache")
    eprint(f"{cmd} csv            Write the CSV of the results to stdout")
    eprint(f"{cmd} clean          Delete cache and delete error experiments")


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == 'todo':
            if len(sys.argv) > 2:
                todo(int(sys.argv[2]))
            else:
                todo()
        elif sys.argv[1] == 'report':
            report()
        elif sys.argv[1] == 'run' and len(sys.argv) == 2:
            run()
        elif sys.argv[1] == 'run' and len(sys.argv) > 2:
            run_group(sys.argv[2])
        elif sys.argv[1] == 'cache':
            cache()
        elif sys.argv[1] == 'csv':
            csv()
        elif sys.argv[1] == 'clean':
            clean()
        else:
            usage()
    else:
        usage()


def clean():
    engine.initialize(ITERATIONS, False)
    engine.clean(iterations=ITERATIONS)


def csv():
    engine.initialize(ITERATIONS, False)
    expmap = {e.name: e for e in engine}
    for i, it in enumerate(engine.results):
        if i > ITERATIONS:
            break
        for ename, res in it.items():
            e = expmap[ename]
            csv_print_experiment(e, res)


def csv_print_experiment(e, res):
    status, value = res
    if status == Experiment.TIMEOUT:
        print("{}; {}; {}; {:.6f}; 0; 0; 0; 0; 0; 0".format(e.group, e.dataset, e.solver, TIMEOUT))
        return
    if status != Experiment.DONE:
        return

    nodes = value.get("nodes", 0)
    edges = value.get("edges", 0)
    priorities = value.get("priorities", 0)
    time = value['time']
    solving = value.get("solving",value["time"])
    metric = value.get("iterations", value.get("promotions", value.get("tangles", -1)))
    print("{}; {}; {}; {:.6f}; 1; {}; {}; {}; {:.6f}; {}".format(e.group, e.dataset, e.solver, value['time'], nodes, edges, priorities, solving, metric))


def run_group(group_to_run):
    # run the given group with given number of iterations
    engine.initialize(ITERATIONS, False)
    engine.run(group=group_to_run, iterations=ITERATIONS)


def run():
    engine.initialize(ITERATIONS, False)
    engine.run(iterations=ITERATIONS)


def cache():
    engine.initialize(ITERATIONS, True)
    engine.save_cache(True)
    count_tot = ITERATIONS * sum([1 for i, x in enumerate(engine) if x.repeat]) + sum([1 for i, x in enumerate(engine) if not x.repeat])
    count_done = sum([len(x) for i, x in enumerate(engine.results) if i < ITERATIONS])
    count_to = sum([1 for i, x in enumerate(engine.results)
                    for a, b in x.items() if b[0] == Experiment.TIMEOUT and b[1] < TIMEOUT])
    print("Remaining: {} experiments not done + {} experiments rerun for higher timeout."
          .format(count_tot - count_done, count_to))
    for j in range(ITERATIONS):
        count_tot = sum([1 for i, x in enumerate(engine) if j == 0 or x.repeat])
        count_done = sum([len(x) for i, x in enumerate(engine.results) if i == j])
        count_to = sum([1 for i, x in enumerate(engine.results)
                for a, b in x.items() if b[0] == Experiment.TIMEOUT and b[1] < TIMEOUT and i == j])
        print("Iteration {}: {} experiments not done + {} experiments rerun for higher timeout."
                .format(j, count_tot - count_done, count_to))


def report():
    engine.initialize(ITERATIONS, False)
    if len(sys.argv) > 2:
        engine.report(group=sys.argv[2], iterations=ITERATIONS)
    else:
        engine.report(iterations=ITERATIONS)


def todo(it=None):
    if it is None:
        engine.initialize(ITERATIONS, False)
        for x in engine.todo(iterations=ITERATIONS):
            print(x)
    else:
        engine.initialize(it, False)
        for x in engine.todo(iterations=it):
            print(x)


if __name__ == "__main__":
    main()
