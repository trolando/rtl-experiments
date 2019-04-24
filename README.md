ORTL/RTL experiments
====================

This repository hosts the experimental scripts and log files for evaluating the performance of the ORTL and RTL algorithms.

You can contact the main author of this work at <t.vandijk@utwente.nl>

Information on the experiments is found in the submitted paper.

Files
-----
| Filename               | Description |
| ---------------------- | ----------- |
| `framework.py`         | Framework for running experiments |
| `experiments.py`       | Definitions of Oink experiments |
| `run.py`               | Main entry point for running experiments |
| `cache.json`           | Cache of log files (after parsing) |
| `results.csv`          | CSV of results of experiments |
| `analyse.r`            | Script in R to run analysis for the paper |
| `LICENSE`              | Apache 2.0 license |
| `README.md`            | This file |

Compiling the sources
-----
- Compile Oink from https://www.github.com/trolando/oink, using the ISOLA24 tag.
- Use CMAKE_BUILD_TYPE Release and enable compiling extra tools.
- Copy "oink" from Oink's build directory to the tools/ directory

Obtaining benchmark input files
-----
- Copy the files from Oink's "examples" directory to inputs/synt
- Download modelchecking.zip, equivchecking.zip, equivchecking-hesselink.zip from https://figshare.com/articles/dataset/Parity_games/6004130
- Unpack the games from modelchecking.zip into inputs/modelchecking
- Unpack the games from the two equivchecking zip files into inputs/equivchecking

Running the experiments
-----
- The `run.py` file runs the experiments. Just run it without a parameter and it gives usage info.
- Use `run.py run` to run the experiments one by one and store the log files in the logs directory.
- Use `run.py cache` to populate cache.json. Not strictly required but can improve repeated parsing.
- Use `run.py csv` to generate the CSV file with results

Experimental results
-----
- All log files are stored in the `logs` directory.
- The results of experiments are stored in `results.csv`.

Analysing the results
-----
- Use `analyse.r`; the file `results.csv` must be present.
- This file generates all tables and figures of the paper.
