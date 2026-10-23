# Drafting a profile with the configured LLM: design

Status: not built. This document describes how Consta could draft an ecosystem profile
with the LLM that is already configured for summaries, and what can go wrong.

## 1. The problem

A profile (`profiles/*.yaml`) holds what a person learned by hand about one project:
synonyms, label names, alternative projects with URLs, files worth reading. It does three
jobs in a run:

- The planner expands the question with its synonyms and label searches.
- The validator drops off-topic issues and pull requests. `validate_evidence` only does
  this when a profile is loaded; without one, every search result is kept.
- The adjacent-projects retriever fetches the alternatives it lists.

So a question about a project with no profile gets a report with no filtering and no
alternatives. The pandas `SparseArray` example shows the result: the top issues are
about import time, plot error bars and Excel export, with "dropped as off-topic: 0".

Today the fix is to write a profile. People already do that with their own LLM: give it
`profiles/_template.yaml` and the project's labels and docs, then review the YAML. This
design moves that step into Consta when an LLM provider is configured, and adds the checks
a person would otherwise have to remember.

## 2. What stays the same

- Retrieval, validation and the citation check stay plain Python. The model drafts a
  profile once; it does not take part in searching or filtering.
- A reviewed profile in `profiles/` always wins. Consta never drafts over it or changes it.
- With no LLM configured, nothing changes: no profile, no filter, same report as today.
- The drafted profile is an ordinary `EcosystemProfile`, so the planner, validator and
  retrievers need no new code paths.

## 3. Two entry points

### 3.1 `consta profile draft`

```bash
consta profile draft --repo pandas-dev/pandas --path pandas/core/arrays/sparse \
    --id pandas -o profiles/pandas.yaml
```

Explicit and reviewable. It writes a YAML file with a header that lists what was dropped
and why (section 5), and a `provenance` block (section 4). It refuses to overwrite an
existing file. The person reads it, edits it, sets `reviewed: true`, and commits it.

### 3.2 Automatic draft inside `assess`

When `assess` runs with no `--ecosystem`, Consta first looks for a profile whose
`default_repos` contains the requested repository. That lookup is new; today a profile is
only chosen by name. If none matches and an LLM is configured, Consta drafts one, uses it
for this run, and caches it (section 6).

The report then says, above the evidence: "Profile drafted by `<model>` on `<date>`, not
reviewed", with the terms it added and the ones that were dropped. A reader can tell
which evidence came in only because of drafted terms.

Switches:

- `--no-draft-profile` turns the automatic draft off.
- `--no-synthesis` also turns it off. People use that flag to mean "no model in this
  run", and a silent extra LLM call would break that promise. A new `--no-llm` flag would
  say this more plainly; `--no-synthesis` stays as it is for compatibility.
- `--ecosystem NAME` with a name that does not exist stays an error. A typo must not turn
  into a silent draft.

## 4. What the model may write

The model returns JSON for a subset of the profile:

| Field | Drafted? | Why |
|-------|----------|-----|
| `synonyms` | yes | The main gain: names the question does not use |
| `issue_search_queries` (label searches) | yes, only for labels that exist | Labels get renamed; this is the PyTorch `module: masked` case |
| `adjacent_projects` | yes, checked | Alternatives are often outside the repository |
| `scope_files`, `path_hints` | yes, only for files that exist | Cheap to verify |
| `pinned_issue_numbers`, `path_pinned_issue_numbers` | no | Pinned issues bypass the off-topic filter |
| `label_boosts` | no | Changes ranking without any visible reason |
| `discourse`, `huggingface`, `rfc` | no | Need a person to choose the venue |
| `assignment_precision` | no | It is a measurement, not a guess |

Consta fills `id`, `display_name`, `default_repos` and `last_verified` itself, and adds:

```yaml
provenance:
  drafted_by: huggingface/openai/gpt-oss-120b
  drafted_at: 2026-10-23
  inputs_sha256: 3f1c...
  reviewed: false
max_age_days: 30
```

`provenance` is a new optional field on `EcosystemProfile`. Hand-written profiles do not
have it. A drafted profile expires after 30 days instead of 90.

## 5. Checks before a draft is used

The model's output is treated like the summary: nothing is used until code has checked it
against what Consta fetched. Each failed item is dropped with a reason, as the validator
does for evidence, and the reasons go into the YAML header and the report.

| Drafted item | Check | On failure |
|--------------|-------|------------|
| Label in a search query | Exists in the repository's label list, exact match | Drop the query |
| Synonym | Appears in the grounding material (section 7): file or symbol names, README, docs, recent issue titles | Drop the synonym |
| Synonym | Matches at most 20% of a sample of 100 recent issue titles in the repository | Drop it as too broad |
| Synonym | At least 4 characters and not on the filler-word list the validator already uses | Drop it |
| Scope file or path hint | The file exists in the repository | Drop it |
| Alternative project | URL is `https`, the host is public, the page answers, and its text contains the project's name | Drop it |
| Whole draft | Valid against `EcosystemProfile` | Retry once with the errors listed, then give up |

If nothing survives, Consta says so and runs without a profile, as today. A draft that
keeps one weak synonym is not better than no draft; the report shows how many terms
survived.

The 20% rule is the important one. A term like "array" or "tensor" turns the filter on in
name only: everything matches, so nothing is dropped, and the report looks filtered when
it is not. That is worse than an honest "no profile".

## 6. Caching and repeatability

The same request must give the same plan, as it does today. A model asked twice will not
write the same YAML twice. So:

- The draft is cached under the user cache directory, keyed by repository, path, provider,
  model and a hash of the grounding material. The question is not part of the key; see section 9.
- A cached draft is reused until it expires or `--redraft-profile` is passed.
- The report records the profile's hash, so two reports can be compared.
- Cached drafts are never written to `profiles/`. Only `consta profile draft -o` writes
  a file a person is meant to review.

## 7. Grounding material

The model gets what Consta fetched, not only what it remembers:

- The repository's labels. Large projects have hundreds; GitHub returns 100 per page.
  Send only labels whose names share a token with the path or question, plus the 50 most
  used, and say in the prompt that the list is cut.
- File and directory names under the path, and top-level class and function names from
  those files.
- README, CONTRIBUTING and the module's docs page, if one is found, cut to a fixed size.
- Titles of up to 50 recent issues that mention the path or its last directory name.

All of this is untrusted text written by other people. The prompt says so, and section 5
is the real defence: a model can be steered into writing anything, but only verified items get
used.

## 8. Pitfalls

1. Invented labels, files and links. The model fills gaps from memory, and its memory is
   out of date. Labels get renamed. Checks in section 5 catch these; the report lists them.
2. Terms that are too broad. The filter then keeps everything while looking active. The
   20% rule catches the common case, not every case.
3. Terms that are too narrow. Relevant issues get dropped. They still appear under
   "Retrieved but excluded" with a reason, so a reader can see it, but most readers will
   not look.
4. The model shapes its own evidence. With an LLM configured, the same model may draft the
   profile and then write the summary. If it believes "FlexAttention replaces this", it
   adds FlexAttention as an alternative, Consta fetches the page, and the summary cites it.
   The citation check still holds, because the quote is real, but the selection was the
   model's prior. Mitigations: the banner, the list of drafted terms, and an option to draft
   with a different model (`CONSTA_PROFILE_LLM_MODEL`).
5. Prompt injection. A README or an issue title can carry instructions. The worst
   realistic outcome is a planted alternative URL that Consta then fetches. Mitigations:
   only `https`, no private or link-local addresses, no redirects to them, and the existing
   rule that curator notes are never quotable. In the web UI, an automatic draft fetches
   URLs from the server, so it is off there by default.
6. Cost and rate limits. One extra LLM call per new repository and path, plus a few GitHub
   calls for labels, files and the issue sample. The cache keeps it to once per 30 days.
   The GitHub Action must not draft on every new issue: it uses a committed profile or none.
7. Private repositories. Drafting sends more of the repository to the provider than a
   summary does: file names, symbols, docs. The summary already sends snippets, so the
   consent is the same in kind, but the docs must say it, and `--no-draft-profile` must be
   easy to find.
8. Provider differences. Some providers return empty content (seen with `gpt-oss` on the
   Hugging Face router), `claude-code` has no JSON mode, and models wrap JSON in prose.
   Reuse the synthesizer's JSON parsing and its single retry.
9. Questions that span modules. A profile drafted for one path may be wrong for another
   path in the same repository. The cache key includes the path for that reason.
10. A draft that hides a missing profile. If drafting fails, the report must still say
    "no profile", not quietly run without one.
11. Forecasts. A drafted profile has no measured assignment precision, so the topic
    forecast keeps refusing. That is correct and needs no change.
12. Drift between a reviewed profile and the draft. If someone commits a reviewed
    profile later, the cached draft must stop being used. Lookup order: `--ecosystem`,
    then reviewed profiles by `default_repos`, then the cache, then a new draft.

## 9. Open questions

- Should the question be part of the draft? It gives better synonyms for that question,
  as the `pytorch` profile shows, but then the cache holds one draft per question and two
  questions about the same module see different filters. Current choice: path only, and
  the question's own words are added at run time as they are today.
- Should a reviewed profile be allowed to include drafted fields, marked per field? That
  would let people accept a draft partly. It adds a field-level provenance format.

## 10. Implementation steps

1. `provenance` field on `EcosystemProfile`; loader accepts it; `max_age_days` default 30
   when `reviewed` is false. Tests in `test_profiles.py`.
2. Profile lookup by `default_repos` in `assess`, before any drafting. Tests with two
   profiles that list the same repository (refuse as ambiguous).
3. Grounding fetch: labels (paginated, cut as in section 7), file list under the path,
   symbol names, issue-title sample. GitHub client methods with cache, and fixtures.
4. Draft prompt and JSON schema; parse with the synthesizer's helpers; one retry.
5. Checks from section 5, each with its own drop reason. Unit tests with a fake LLM that
   returns invented labels, a broad synonym, a private-IP URL and a missing file.
6. `consta profile draft` command, writing YAML with the header of dropped items.
7. Automatic draft in `assess`, the cache, the report banner, and the flags
   `--no-draft-profile`, `--redraft-profile`, `--no-llm`.
8. Evaluation. Draft profiles for `pytorch`, `numpy`, `sklearn` and `apertus` with the
   reviewed files hidden, and compare: share of reviewed labels, synonyms and alternatives
   recovered, and the off-topic share in the sample cases. Then the pandas `SparseArray`
   case: the share of top-10 issues that mention sparse arrays, without and with a draft.
   Ship the automatic draft only if that share goes up and no sample case gets worse.
9. Docs: `ARCHITECTURE.md` (profiles), `README.md` (flags, what is sent to the provider),
   `STATUS.md`.
