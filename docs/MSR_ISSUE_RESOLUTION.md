# Prior work: predicting issue resolution time

Written 2026-09-03. A short survey of issue-level resolution-time prediction, to place
the topic forecast in [PREDICT.md](PREDICT.md). Repository-level abandonment prediction
is a separate body of work and is not covered here.

## Existing work

| Work | Predicts | Does not cover |
|------|----------|----------------|
| Giger et al., "Predicting the Fix Time of Bugs" (Eclipse, Mozilla, Gnome) | Fast or slow fix from bug report attributes, with decision trees | Module or topic level; fix versus administrative close; displacement by another module |
| Later bug-fix-time studies (Eclipse, Mozilla, Jira) | Hours or days to FIXED, as regression or classification | Same; often use features recorded after the issue was opened, which leak |
| "Predicting Issue Resolution Time of OSS Using Multiple Features", J. Softw. Evol. Process, doi:10.1002/smr.2746 | Resolution time of GitHub issues from project, issue and developer features | Topic level; fix versus close; demand and supply per path |
| Process mining of GitHub issue workflows | Patterns and duration of maintenance work | Whether to contribute to a module; alternative APIs |
| Leakage-aware studies (creation-time features, temporal splits) | Early estimates without post-open data | Rise or fall of neighbouring modules |

Findings this work takes as given:

1. Metadata available when an issue is opened predicts something. Later activity
   (comments, status changes) improves accuracy and is the main source of leakage.
2. Tree ensembles are the usual baseline. Random train/test splits overstate accuracy
   compared with temporal splits.
3. Resolution times have long tails. Studies usually report mean absolute error in hours,
   not cumulative incidence over competing outcomes.

## What the topic forecast adds

- It works at module or path level (`torch/masked`), not per issue.
- It separates outcomes: resolved by a merged change on the path (R1), closed without
  one (R2), or still open (censored).
- It looks for displacement: a neighbouring module gaining activity while this one loses
  it, as with NestedTensor and MaskedTensor.
- It refuses to score when the observation window or the issue-to-topic assignment
  precision is too weak, as for Apertus.

Issue-level resolution-time prediction is well studied. The untested part is the
topic-level version with competing outcomes, displacement and refusal.

## Consequence for evaluation

The baselines must include a simple issue-level or person-period model without the LLM
features and without displacement, so that an improvement is measured against a real
model and not against a mean. The model is kept only if it beats the vital-signs
baseline on Brier score at 90 days, with folds grouped by repository.
