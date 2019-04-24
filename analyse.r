#!/usr/bin/Rscript
suppressPackageStartupMessages(library('tidyverse'))
suppressPackageStartupMessages(library('ggplot2'))
suppressPackageStartupMessages(library('tikzDevice'))
suppressPackageStartupMessages(library('xtable'))
suppressPackageStartupMessages(library('lemon'))
suppressPackageStartupMessages(library('knitr'))
suppressPackageStartupMessages(library('scales'))

cat("Reading results.csv\n")

# Read input data
# For timeouts, "States" field is set to -1
input <- read_delim('results.csv', delim=";", col_names=FALSE, trim_ws=TRUE, col_types="cccdiiiidi")
colnames(input) <- c("Model", "Dataset", "Solver", "Time", "Done", "Nodes", "Edges", "Priorities", "Solving", "Metric")

# Add "Id" column
input <- input %>% mutate(Id = paste(Model, Solver, sep = "-"))

# Drop anything with Nodes == 0
input <- input %>% filter(Nodes != 0)

# Report data on input set, per dataset (mc, ec, synt)
kable(input %>% filter(Nodes!=0) %>% group_by(Dataset,Priorities,Nodes,Edges) %>% distinct(Model) %>% group_by(Dataset) %>% summarize(n_distinct(Model), mean(Nodes), max(Nodes), mean(Edges), max(Edges), mean(Edges/Nodes), max(Edges/Nodes)))
# Report data on input set, but also split by Priorities
kable(input %>% filter(Nodes!=0) %>% group_by(Dataset,Priorities,Nodes,Edges) %>% distinct(Model) %>% group_by(Dataset, Priorities) %>% summarize(n_distinct(Model), mean(Nodes), max(Nodes), mean(Edges), max(Edges), mean(Edges/Nodes), max(Edges/Nodes)))

# Output as tikz
kable(input %>% filter(Nodes!=0) %>% group_by(Dataset,Priorities,Nodes,Edges) %>% distinct(Model) %>% group_by(Dataset) %>% summarize(n_distinct(Model), mean(Nodes), max(Nodes), mean(Edges), max(Edges), mean(Edges/Nodes), max(Edges/Nodes)) %>% gather("k","v",-Dataset) %>% spread(Dataset, v),format="latex",booktabs=TRUE,linesep="",digits=2)
kable(input %>% filter(Nodes!=0) %>% group_by(Dataset,Priorities,Nodes,Edges) %>% distinct(Model) %>% group_by(Dataset) %>% summarize(n_distinct(Model), mean(Nodes), max(Nodes), mean(Edges), max(Edges), mean(Edges/Nodes), max(Edges/Nodes)), format="latex", booktabs=TRUE, linesep="")
kable(input %>% filter(Nodes!=0) %>% group_by(Dataset,Priorities,Nodes,Edges) %>% distinct(Model) %>% group_by(Dataset, Priorities) %>% summarize(n_distinct(Model), mean(Nodes), max(Nodes), mean(Edges), max(Edges), mean(Edges/Nodes), max(Edges/Nodes)) %>% group_by(Dataset,Priorities) %>% gather("k","v",-Dataset,-Priorities) %>% ungroup %>% mutate(DP=paste(Dataset,Priorities)) %>% select(-Dataset,-Priorities) %>% spread(DP, v), digits=2, format="latex", linesep="")

modelinfo <- input %>% filter(Priorities!=0, Nodes!=0) %>% group_by(Dataset,Priorities,Nodes,Edges) %>% distinct(Model)


# Split into <times> and <timeouts> and remove timeouts for which we have any times
times <- input %>% filter(Done != 0) %>% select(-Done)
timeouts <- input %>% filter(!Id %in% (times %>% distinct(Id))$Id) %>% select(-Done)

# Compute median/mean/sd for times, and highest timeout for timeouts
times <- times %>% group_by(Id, Model, Dataset, Solver) %>% summarize(MedianTime = median(Time), MeanTime = mean(Time), sd = sd(Time)) %>% ungroup
timeouts <- timeouts %>% group_by(Id, Model, Dataset, Solver) %>% summarize(Timeout = max(Time)) %>% ungroup

# Compute Model-Order that are solved (or timeout) by all Method-Worker combinations
times_s <- times %>% select(Solver, Dataset, Model, Time=MedianTime)
times_s_s <- times_s %>% spread(Solver, Time)
timeouts_s <- timeouts %>% select(Solver, Dataset, Model, Time=Timeout)
MODone <- bind_rows(times_s, timeouts_s) %>% spread(Solver, Time) %>% drop_na() %>% pull(Model)
MOAll <- times_s %>% spread(Solver, Time) %>% drop_na() %>% pull(Model)
times %>% filter(Model %in% MOAll) %>% group_by(Dataset) %>% summarize(Count=n_distinct(Model))

MOAllmc <- times %>% filter(Model %in% MOAll, Dataset == "modelchecking") %>% pull(Model) %>% unique()
MOAlleq <- times %>% filter(Model %in% MOAll, Dataset == "equivchecking") %>% pull(Model) %>% unique()
MOAllsy <- times %>% filter(Model %in% MOAll, Dataset == "synt") %>% pull(Model) %>% unique()

# Compute Model-Order that are solved before timeout by all Method-Worker combinations
# MOLong1 <- times %>% filter(MedianTime>=1) %>% mutate(MW = paste(Method, Workers)) %>% select(MW, Model, Order, MedianTime) %>% spread(MW, MedianTime) %>% drop_na() %>% mutate(MO = paste(Model, Order)) %>% pull(MO)
# MOLong2 <- times %>% filter(MedianTime>=1 | Workers!=1) %>% mutate(MW = paste(Method, Workers)) %>% select(MW, Model, Order, MedianTime) %>% spread(MW, MedianTime) %>% drop_na() %>% mutate(MO = paste(Model, Order)) %>% pull(MO)
# MODoneByLDDandMDD <- bind_rows(times_s, timeouts_s) %>% filter(MW == "ldd-sat 1" | MW == "mdd-sat 1") %>% spread(MW, Time) %>% drop_na() %>% select(Model, Order) %>% mutate(MO = paste(Model, Order)) %>% pull(MO)
# MOAllByLDDandMDD <- times_s %>% filter(MW == "ldd-sat 1" | MW == "mdd-sat 1") %>% spread(MW, Time) %>% drop_na() %>% select(Model, Order) %>% mutate(MO = paste(Model, Order)) %>% pull(MO)

# MODone  are those MO where all solvers solve or timeout (no error)
# MOAll   are those MO where all solvers solve (no timeout/error)
# MOLong1 are those MO where all solvers solve and require more than 1 second
# MOLong2 are those MO where all solvers solve and require more than 1 second with 1 worker
# MODoneByLDDandMDD are those where ldd-sat 1 and mdd-sat 1 solve or timeout
# MOAllByLDDandMDD  are those where ldd-sat 1 and mdd-sat 1 solve (no timeout)

cat(sprintf("MODone (all solvers solve/timeout) contains %d Models.\n", length(MODone)))
cat(sprintf("MOAll (all solvers solve, no timeout) contains %d Models.\n", length(MOAll)))
cat(sprintf("MOAllmc contains %d Models.\n", length(MOAllmc)))
cat(sprintf("MOAlleq contains %d Models.\n", length(MOAlleq)))
cat(sprintf("MOAllsy contains %d Models.\n", length(MOAllsy)))




timesSummary <- times %>% filter(Model %in% MOAll) %>% group_by(Dataset, Solver) %>% summarize(SumMeanTime = sum(MeanTime)) %>% spread(Solver, SumMeanTime) %>% select("Dataset","fpi-n","fpj-n","zlk-n","npp-n","tl-n","rtl-n","ortl-n")
kable(timesSummary,digits=2)
kable(timesSummary,format="latex",linesep="",digits=2,format.args=list(big.mark=","),booktabs=TRUE)
