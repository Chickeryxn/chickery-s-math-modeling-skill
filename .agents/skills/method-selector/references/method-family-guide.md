# Method-Family Routing Guide

Use this guide to form a shortlist, not as a menu that must be exhausted.

## Evaluation and ranking

- Credible baselines: equal-weight normalized score or an existing operational rule, when they complete the real task.
- Main families: entropy/TOPSIS, PCA-assisted evaluation, grey/fuzzy evaluation when their assumptions fit.
- Key risks: redundant indicators, unjustified directions or weights, weight dominance, concentrated scores, unstable top-k ranks.

## Prediction

- Credible baselines: seasonal naive, last value, moving average, or simple regression selected to match the time structure.
- Main families: exponential smoothing, ARIMA/SARIMA, regression, tree boosting, small-data grey models.
- Key risks: leakage, invalid split, short series, nonstationarity, over-capacity, poor interval coverage.

## Optimization

- Credible baselines: current policy, a feasible greedy rule, or a relaxed exact formulation.
- Main families: LP/MILP, network flow, dynamic or nonlinear programming, justified metaheuristics.
- Key risks: missing constraints, infeasibility, meaningless objectives, nonimplementable solutions, excessive runtime.

## Classification and clustering

- Credible baselines: rule-based or majority/stratified reference when meaningful.
- Main families: logistic/tree models, SVM, random forest, k-means or other clustering with validation.
- Key risks: label absence, class imbalance, arbitrary cluster count, instability, accuracy-only evaluation.

## Mechanism and simulation

- Credible baselines: simplified algebraic or deterministic scenario model that preserves the core mechanism.
- Main families: differential/difference equations, compartment models, Monte Carlo, discrete-event or agent-based simulation.
- Key risks: unidentified parameters, unit errors, invalid boundary conditions, hidden distribution assumptions, too few replications.

## Graph and routing

- Credible baselines: feasible direct rule or nearest-neighbor heuristic.
- Main families: shortest path, flow, matching, spanning tree, TSP/VRP formulations.
- Key risks: unrealistic edges or weights, omitted operational constraints, mathematically valid but unusable routes.

## Descriptive and inferential statistics

(Completes the routing table for problem-classifier's descriptive /
inference types — these families previously had no entry here.)

- Descriptive (summarize/characterize, no causal claim): summary statistics,
  distributions, indices; credible baselines are simple aggregations (mean /
  median / rate) that answer the same descriptive question.
- Inferential (estimate/compare with uncertainty): hypothesis tests, CI
  construction, regression with uncertainty, bootstrap; credible baselines are
  the null or simplest estimator.
- Key risks: p-value misuse, multiple-comparison inflation, ignoring sampling
  design, overclaiming causation from correlation, small effective sample size.

## Mixed-type routing

When a subquestion mixes types (e.g. prediction + optimization), build the
shortlist from the dominant output family and treat the secondary family as a
constraint or evaluation layer; do not silently keep only one paradigm when
the problem admits several.
