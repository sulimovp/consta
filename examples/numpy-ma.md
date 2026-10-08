# Assessment: Is improving numpy.ma worth an upstream contribution, given __array_function__?

Generated: 2026-10-08T19:07:42.895293+00:00 | Repo: `numpy/numpy` | Profile: numpy | Evidence freshness: 2026-08-30T00:00:00+00:00

## Summary (model synthesis — verify citations below)

The numpy/ma module shows declining commit activity with 30 commits in the last 3 months and 125 open issues, though recent commits continue with top contributors like jorenham and mattip. "commits 3/6/12mo = 30/57/197 (falling)" [3] "open\_issues\_total=125" [3] "Latest: 01d9da3 on 2026-10-07T23:48:37Z" [4] "Top committers: jorenham, mattip, Aniketsy." [4]

Long-standing bugs include mask loss in functions like np.append and incorrect fill_value handling, but __array_function__ support could address some gaps. "Masked array `__array_function__` could "fix" e.g. \`np.append\` MA usage" [1] "indirect source of several bugs" [2] "fix stale fill\_value after ufuncs change MaskedArray dtype" [7]

Adjacent projects pandas and xarray already provide robust missing-data and labelled-array alternatives, potentially reducing the need for extensive numpy.ma improvements. "pandas uses different sentinel values to represent a missing" [5] "coerced to np.float64 or object" [5] "Xarray makes working with labelled multi-dimensional arrays in Python simple" [6]

## Topic trajectory

_Topic rollup refused:_ item→topic assignment precision unmeasured for this profile

_Hazard score refused:_ item→topic assignment precision unmeasured for this profile; trained topic-hazard artifact not shipped (topic-hazard-v0-refuse); observation window unknown — need ≥360d (2× the 180d horizon)

_Demand×supply rollup is descriptive, from realized outcomes. Resolution-hazard score is a forecast over ~180 days — not a recommendation._

## Evidence

### Issues and discussions

[1] ENH: Masked array `__array_function__` could "fix" e.g. `np.append` MA usage — https://github.com/numpy/numpy/issues/22338 — ### Describe the issue: if I append a masked array and something else using np.append, it returns a masked array but wit
[2] Why/when does np.something remove the mask of a np.ma array ? — https://github.com/numpy/numpy/issues/18675 — This is obviously more a feature than a bug, otherwise it would have been corrected (I'm using numpy 1.20.1). But it has
[13] DISCUSS: About issue of masked array — https://github.com/numpy/numpy/issues/27588 — While reading the code and addressing some bugs related to `numpy/ma`, I encountered a few questions: 1. **Filling Value
[14] BUG: Masked division considers large float64 values as inf  — https://github.com/numpy/numpy/issues/22347 — ### Describe the issue: I am testing my data pipeline that uses `SimpleImputer` from sklearn. Their code uses masked arr
[15] masked arrays do not operate commutatively with numpy scalars — https://github.com/numpy/numpy/issues/3543 — When performing an operation with a masked array and a numpy scalar the order of the operands will change the results. E
[16] ENH: support `where=` in MaskedArray reductions — https://github.com/numpy/numpy/issues/32126 — ### Proposed new feature or change: ndarray reductions accept a where= keyword to select which elements participate in t
[17] BUG of 1.19.2, numpy.ma.MaskedArray: unexpected overflow of fill_value — https://github.com/numpy/numpy/issues/17697 — If User accessed `MaskedArray`'s default `fill_value` before assignment of it, an overflow might occur. ### Reproducing 
[18] MaskedArray recarray, multi-dimensional field + set_fill_value = exception — https://github.com/numpy/numpy/issues/9748 — A bug was introduced in fix for #6723, ``` x = np.array([([0, 0], 0.0), ([2, 2], 3.0)], dtype=[('field1', 'i4', (2,)), (
[19] BUG: MaskedArray.astype('uint8') with certain fill_value raises warning on ARM (Mac M3) inside Docker (Ubuntu 24.04/25.04) and leads inconsistent output — https://github.com/numpy/numpy/issues/28403 — ### Describe the issue: I encountered a warning when converting a MaskedArray to uint8 inside a Docker container running
[20] Masked array mean reports spurious floating point error (underflow) — https://github.com/numpy/numpy/issues/4895 — When numpy is set to raise exception on floating point errors, taking the mean of masked arrays sometimes raises spuriou
[21] BUG: ma.corrcoef produces wrong results and takes very long. — https://github.com/numpy/numpy/issues/15601 — In the following code, I calculate the correlation coefficients of an array with missing data in three ways: * Using Num
[22] BUG: Stack overflow on double inheritance from numpy.flexible and numpy.ma.core.MaskedArray — https://github.com/numpy/numpy/issues/23737 — ### Describe the issue: ``` >>> import numpy >>> numpy.__version__ '1.24.3' >>> class X(numpy.flexible, numpy.ma.core.Ma
[23] Current stance on NA implementation — https://github.com/numpy/numpy/issues/15858 — Some time ago, I actually got my statistics professor to try out python, and he came back claiming that python would nev
[24] BUG: `MaskedArray.fill_value` not consistently preserved in structured voids with array-valued fields — https://github.com/numpy/numpy/issues/28450 — ### Describe the issue: If a masked array of a structured void type with an array-valued field is built, the `.fill_valu
[25] Wrong results of ma.isin() and ma.in1d() for masked arrays — https://github.com/numpy/numpy/issues/19877 — For masked arrays, `isin()` and `in1d()` produce wrong results. In particular, the result is masked at wrong places. The
[26] np.pad applied to the MaskedArray subclass silently unmasks the array, and returns output as ndarray — https://github.com/numpy/numpy/issues/8881 — It seems to me this should be resolved so that the `MaskedArray` subclass is preserved and the `mask` attribute is likew
[27] BUG: np.ones_like behaves differently depending on whether the fill_value of the input array has been accessed — https://github.com/numpy/numpy/issues/28255 — ### Describe the issue: Hello, For some cases of fill value casting, `np.ones_like` for a masked array behaves different
[28] Masked array view fails if structured dtype has datetime component — https://github.com/numpy/numpy/issues/4476 — A view as `numpy.ma.MaskedArray` fails if the array has a structured dtype, including at least one part that is `datetim
[29] BUG: MaskedArray.__array_wrap__ propagates a stale, dtype-invalid fill_value across dtype-changing ufuncs — https://github.com/numpy/numpy/issues/32401 — ### Describe the issue: When a ufunc changes the dtype of a MaskedArray's output relative to its input (e.g. `np.strings
[30] BUG: masked std and median on unmasked array result in invalid masked array — https://github.com/numpy/numpy/issues/24525 — ### Describe the issue: Since version 1.24, the code example below results in a masked array where the data array and th
[31] Markup errors in trunk/numpy/ma/API_CHANGES.txt (Trac #783) — https://github.com/numpy/numpy/issues/1381 — _Original ticket http://projects.scipy.org/numpy/ticket/783 on 2008-05-08 by @vnoel, assigned to unknown._ There are two
[32] Markup errors in trunk/numpy/ma/API_CHANGES.txt (Trac #778) — https://github.com/numpy/numpy/issues/1376 — _Original ticket http://projects.scipy.org/numpy/ticket/778 on 2008-05-08 by @vnoel, assigned to @jarrodmillman._ There 
[33] BUG: `numpy.ma.MaskedArray` arithmetic with Python scalars differs from `ndarray` — https://github.com/numpy/numpy/issues/31868 — ### Describe the issue: When you use binary arithmetic with Python scalars, `numpy.ma.MaskedArray` gives different resul
[34] Markup errors in trunk/numpy/ma/API_CHANGES.txt (Trac #782) — https://github.com/numpy/numpy/issues/1380 — _Original ticket http://projects.scipy.org/numpy/ticket/782 on 2008-05-08 by @vnoel, assigned to unknown._ There are two
[35] np.ma.arrray(['string', np.ma.masked]) gives FutureWarning after #18116 (breaks astropy) — https://github.com/numpy/numpy/issues/18425 — <!-- Please describe the issue in detail here, and fill in the fields below --> #18116 caused the `astropy` regression t
[37] ENH: add type annotations to `numpy.ma` — https://github.com/numpy/numpy/issues/26404 — ### Describe the issue: Running Mypy on some functions within `numpy.ma` lead to type checking errors due to missing ann
[38] Markup errors in trunk/numpy/ma/API_CHANGES.txt (Trac #781) — https://github.com/numpy/numpy/issues/1379 — _Original ticket http://projects.scipy.org/numpy/ticket/781 on 2008-05-08 by @vnoel, assigned to unknown._ There are two
[39] BUG: filled MaskedArray becomes object dtype if given a fill_value of None — https://github.com/numpy/numpy/issues/27269 — ### Describe the issue: Passing `fill_value=None` results in the `MaskedArray` dtype changing to `object`. Is this behav
[40] TST: [Tracking] Improving code coverage (Python) — https://github.com/numpy/numpy/issues/32275 — ## Current Status <details><summary>Python Coverage (current)</summary> <p> ```md | Name | Stmts | Miss | Branch | BrPar
[41] Inconsistent results from numpy divide for masked arrays when using the out parameter — https://github.com/numpy/numpy/issues/10382 — I am using Red Hat 7.4, python 2.7 and numpy version 1.13, 1.14.0 and 1.7. For numpy version 1.7 I have no problem. But 
[42] Markup errors in trunk/numpy/ma/API_CHANGES.txt (Trac #780) — https://github.com/numpy/numpy/issues/1378 — _Original ticket http://projects.scipy.org/numpy/ticket/780 on 2008-05-08 by @vnoel, assigned to unknown._ There are two
[43] BUG: MaskedArray.mean (and sum) do not propagate subclass metadata via _update_from, unlike var/std — https://github.com/numpy/numpy/issues/30037 — ### Describe the issue: When subclassing numpy.ma.MaskedArray, user-defined metadata stored in `_optinfo` (or propagated
[44] MaskedArray.copy Shares Fill Value — https://github.com/numpy/numpy/issues/7329 — Copying a Masked Array does not create a new MA with it's own fill value. Modifying the fill_value attribute on the dest
[45] Odd behavior of ma.add.reduce on boolean arrays  — https://github.com/numpy/numpy/issues/7623 — Consider two masked arrays: ``` In [40]: a = np.ma.array([True] * 3, mask=[False] * 3) In [41]: b = np.ma.array([True] *
[46] Markup errors in trunk/numpy/ma/API_CHANGES.txt (Trac #779) — https://github.com/numpy/numpy/issues/1377 — _Original ticket http://projects.scipy.org/numpy/ticket/779 on 2008-05-08 by @vnoel, assigned to unknown._ There are two
[47] BUG: Error in `MaskedArray` with `StringDType` when setting `fill_value` — https://github.com/numpy/numpy/issues/29421 — ### Describe the issue: #### Description of the Error I encountered an error when having a `MaskedArray` with `dtype` se
[48] Log and MaskedArray — https://github.com/numpy/numpy/issues/12183 — Masked array do not work with numpy.log, and numpy.log10 ```python >>> A = np.ma.MaskedArray([1, 0, 2], mask =[False, Tr
[49] MaskedArray ufuncs don't return `out` parameter — https://github.com/numpy/numpy/issues/7394 — The ufuncs defined for `MaskedArrays` don't return `out` if it is supplied as a keyword, unlike normal ufuncs. ``` pytho
[50] TYP:  mypy reports `error: "TypeAliasType" not callable` when creating arrays with `numpy.ma.masked_array` since numpy v2.5 — https://github.com/numpy/numpy/issues/31737 — ### Describe the issue: Running the code example below through mypy with the command `pixi x --with numpy=2.5 mypy --ver
[51] BUG: test_maskedarray_tofile_raises_notimplementederror leaves a leftover `xm.np.npy` in cwd — https://github.com/numpy/numpy/issues/27942 — ### Describe the issue: The test `numpy.ma.tests.test_core::TestMaskedArray::test_maskedarray_tofile_raises_notimplement
[52] ma.power should not take masked values into account — https://github.com/numpy/numpy/issues/5108 — Method numpy.ma.power computes the result taking into account the masked values: Example: ``` a = np.ma.array([1.8446744
[54] Bug: mask of non-writable MaskedArray are writeable — https://github.com/numpy/numpy/issues/16976 — Setting a `MaskedArray` `a` as non-writable (i.e., `a.setflags(write=False)`) does not prevent writing to `a.mask`. I be
[55] BUG: The mask value may be removed in numpy.ma.core.MaskedArray — https://github.com/numpy/numpy/issues/27726 — ### Describe the issue: If you overwrite an array defined with numpy.ma.core.MaskedArray with numpy.ndarray, the mask wi
[56] BUG: inconsistency between `MaskedArray` and `ndarray` for dtype array — https://github.com/numpy/numpy/issues/27258 — ### Describe the issue: Hi all, I am using data stored inside netCDF4. Depending on how you create this kind of data, if
[57] DOC: clarify if astype is meant to be called on numpy.ma.MaskedArray — https://github.com/numpy/numpy/issues/24392 — ### Issue with current documentation: Seems like there is no mention of `astype` in the documentation (https://numpy.org
[58] DOC: numpy.ma.allequal — https://github.com/numpy/numpy/issues/32400 — ### Issue with current documentation: The documentation mentions a `given tolerance`, but there is no option for a toler

### Merged work

[7] BUG: fix stale fill_value after ufuncs change MaskedArray dtype — https://github.com/numpy/numpy/pull/32423
[12] TYP: Annotate remaining ``ma.MaskedArray`` methods — https://github.com/numpy/numpy/pull/30221

### Module activity

[4] Recent activity on numpy/ma — https://github.com/numpy/numpy/commit/01d9da3d7f250af1c3e075368b7c14a35e0a8fa7 — Path `numpy/ma`: 150 commits fetched (truncated). Latest: 01d9da3 on 2026-10-07T23:48:37Z. Top committers: jorenham, mat

### Repository files

[10] README.md — https://github.com/numpy/numpy/blob/HEAD/README.md — <h1 align="center"> <img src="https://raw.githubusercontent.com/numpy/numpy/main/branding/logo/primary/numpylogo.svg" wi
[11] doc/neps/nep-0012-missing-data.rst — https://github.com/numpy/numpy/blob/HEAD/doc/neps/nep-0012-missing-data.rst — .. _NEP12: ============================================ NEP 12 — Missing data functionality in NumPy ===================
[53] numpy/ma/README.rst — https://github.com/numpy/numpy/blob/HEAD/numpy/ma/README.rst — ================================== A guide to masked arrays in NumPy ================================== .. Contents:: Se

### Adjacent projects (validated)

[5] pandas — https://pandas.pydata.org/docs/user_guide/missing_data.html — Working with missing data # Values considered “missing” # pandas uses different sentinel values to represent a missing (
  _Curator note, not source text:_ Primary missing-data UX for many data scientists; often preferred over np.ma for new code.
[6] xarray — https://docs.xarray.dev/ — Xarray makes working with labelled multi-dimensional arrays in Python simple, efficient, and fun! Version: 2026.9.0- Wha
  _Curator note, not source text:_ Labeled N-D arrays with NA semantics; common in geoscience / climate stacks.
[36] JAX — https://jax.readthedocs.io/ — .rst .pdf JAX: High performance array computing Contents JAX: High performance array computing # High performance array 
  _Curator note, not source text:_ Alternative array stack with different autograd and masking patterns.

### Maintainer / process

[8] NEP 12 — missing data (historical) — https://github.com/numpy/numpy/blob/main/doc/neps/nep-0012-missing-data.rst — Design / RFC index: NEP 12 — missing data (historical)
[9] NEP 50 — scalar promotion — https://numpy.org/neps/nep-0050-scalar-promotion.html — Design / RFC index: NEP 50 — scalar promotion

### Module vital signs

[3] Module vital signs: numpy/ma — https://github.com/numpy/numpy/commits/numpy/ma — `numpy/ma`: commits 3/6/12mo = 30/57/197 (falling); committers=29; open_issues_total=125; closure_rate=0.782; CODEOWNERS

- Commits 3 / 6 / 12 months: 30 / 57 / 197 (trend: falling) — https://github.com/numpy/numpy/commits/numpy/ma
- Distinct committers (12mo sample): 29; top=jorenham; active on this path in 6mo=True
- Open issues (API total_count): 125; closed total=448; median open age days=674.0; closure_rate=0.782 — https://github.com/numpy/numpy/issues?q=%22numpy/ma%22
- CODEOWNERS present=False; mentions path=None
- Prototype/stale label hits in open sample: 0

## Retrieved but excluded

- numpy.ma.masked_equal seems to leak — https://github.com/numpy/numpy/issues/6010 — _off-topic: title/snippet matched none of the profile/question tokens_
- DOC: signature of `__array__` — https://github.com/numpy/numpy/issues/30907 — _off-topic: title/snippet matched none of the profile/question tokens_
- Typing support for shapes — https://github.com/numpy/numpy/issues/16544 — _off-topic: title/snippet matched none of the profile/question tokens_
- What should be the calling convention for ufunc inner loop signatures? — https://github.com/numpy/numpy/issues/12518 — _off-topic: title/snippet matched none of the profile/question tokens_
- DOC: build of numpy-user.pdf reports Missing Chinese characters with font FreeSerif — https://github.com/numpy/numpy/issues/22930 — _off-topic: title/snippet matched none of the profile/question tokens_
- DEP: Disallow setting `arr.dtype` (or limit it?) — https://github.com/numpy/numpy/issues/20715 — _off-topic: title/snippet matched none of the profile/question tokens_
- BUG: crashes found by fuzzing with fusil — https://github.com/numpy/numpy/issues/28829 — _off-topic: title/snippet matched none of the profile/question tokens_
- nanquantile is hundreds of times slower than quantile for certain cases — https://github.com/numpy/numpy/issues/16575 — _off-topic: title/snippet matched none of the profile/question tokens_
- diag returns ndarray (Trac #1417) — https://github.com/numpy/numpy/issues/2015 — _off-topic: title/snippet matched none of the profile/question tokens_
- BUG: numpy.histogram should raise an error for string arrays — https://github.com/numpy/numpy/issues/24032 — _off-topic: title/snippet matched none of the profile/question tokens_
- BUG: numpy.ma.put(a, indices, values, mode='wrap') runs for a very long time even when a, values are invalid — https://github.com/numpy/numpy/issues/28630 — _off-topic: title/snippet matched none of the profile/question tokens_
- ENH: Reduce the scope of imports when running the mypy plugin — https://github.com/numpy/numpy/issues/25967 — _off-topic: title/snippet matched none of the profile/question tokens_
- BUG/DOC: `numpy.ma.median` return dtype does not match documented behavior — https://github.com/numpy/numpy/issues/31486 — _off-topic: title/snippet matched none of the profile/question tokens_
- BUG: `ma.flatten_structured_array` crashes on string fields due to infinite recursion in `flatten_sequence` — https://github.com/numpy/numpy/issues/30269 — _off-topic: title/snippet matched none of the profile/question tokens_
- ENH,DOC: Better implementation and documentation for `numpy.trapezoid` — https://github.com/numpy/numpy/issues/30337 — _off-topic: title/snippet matched none of the profile/question tokens_
- BUG: Segmentation fault when misusing `masked_object` — https://github.com/numpy/numpy/issues/29299 — _off-topic: title/snippet matched none of the profile/question tokens_
- Consider populating `optional-dependencies` in pyproject.toml — https://github.com/numpy/numpy/issues/24670 — _off-topic: title/snippet matched none of the profile/question tokens_
- DOC: any class decorated with `@set_module` does not show its source on automatically generated documentation — https://github.com/numpy/numpy/issues/28629 — _off-topic: title/snippet matched none of the profile/question tokens_
- BUG: Rounding floats which are already equal to an integer changes the value — https://github.com/numpy/numpy/issues/20514 — _off-topic: title/snippet matched none of the profile/question tokens_
- PERF: optimize field accesses in abi3t builds — https://github.com/numpy/numpy/issues/32865 — _off-topic: title/snippet matched none of the profile/question tokens_
- BUG: `vdot` of object arrays along zero-length is `None` — https://github.com/numpy/numpy/issues/31735 — _off-topic: title/snippet matched none of the profile/question tokens_
- BUG: np.compress casting fails from narrower to wider type — https://github.com/numpy/numpy/issues/21676 — _off-topic: title/snippet matched none of the profile/question tokens_
- BUG: Silent int32 overflow in lapack work size computation leads to wrong exception — https://github.com/numpy/numpy/issues/25564 — _off-topic: title/snippet matched none of the profile/question tokens_
- Making the numpy test suite separately installable — https://github.com/numpy/numpy/issues/26289 — _off-topic: title/snippet matched none of the profile/question tokens_
- BUG: On Windows, np.finfo(np.float64).eps is a longdouble once np.finfo(np.longdouble) has been requested (regression in 2.4.0) — https://github.com/numpy/numpy/issues/32947 — _off-topic: title/snippet matched none of the profile/question tokens_
- ENH: Static typing support for custom array containers — https://github.com/numpy/numpy/issues/21737 — _off-topic: title/snippet matched none of the profile/question tokens_
- DOC: Remove versionadded/versionchanged directives referencing unsupported NumPy releases — https://github.com/numpy/numpy/issues/32868 — _off-topic: title/snippet matched none of the profile/question tokens_
- DOC: List API reference for numpy.random — https://github.com/numpy/numpy/issues/20121 — _off-topic: title/snippet matched none of the profile/question tokens_
- BUG: ndarray.__reduce__ converts shape errors to SystemError — https://github.com/numpy/numpy/issues/32786 — _off-topic: title/snippet matched none of the profile/question tokens_
- BUG: `nanquantile` along an axis returns the input dtype when the first slice is all-NaN — https://github.com/numpy/numpy/issues/32832 — _off-topic: title/snippet matched none of the profile/question tokens_
- DOC: Links to latest numpy docs on old scipy.org doc builds redirect to scipy docs — https://github.com/numpy/numpy/issues/23156 — _off-topic: title/snippet matched none of the profile/question tokens_
- BUG: Possible regression in string  trim_zeros — https://github.com/numpy/numpy/issues/28150 — _off-topic: title/snippet matched none of the profile/question tokens_
- BUG: np.choose results in rule 'safe' cast error in 32-bit Python — https://github.com/numpy/numpy/issues/21305 — _off-topic: title/snippet matched none of the profile/question tokens_
- Support of multiple axes in max operator for c-api — https://github.com/numpy/numpy/issues/6296 — _off-topic: title/snippet matched none of the profile/question tokens_
- BUG: Platform dependent test failures of `tanh`, `atanh` and `sqrt` function. — https://github.com/numpy/numpy/issues/32234 — _off-topic: title/snippet matched none of the profile/question tokens_
- BUG: same_kind casting between strings and bytes is inconsistent — https://github.com/numpy/numpy/issues/32880 — _off-topic: title/snippet matched none of the profile/question tokens_
- TYP: ``ma``: accept integer array-likes as mask — https://github.com/numpy/numpy/pull/32909 — _off-topic: title/snippet matched none of the profile/question tokens_
- TYP/DOC: release notes for the main ``numpy`` namespace shape-typing improvements — https://github.com/numpy/numpy/pull/32835 — _off-topic: title/snippet matched none of the profile/question tokens_
- BUG: Reset an unrepresentable fill_value on a dtype change  (#32508) — https://github.com/numpy/numpy/pull/32557 — _off-topic: title/snippet matched none of the profile/question tokens_
- BUG: Reset an unrepresentable fill_value on a dtype change — https://github.com/numpy/numpy/pull/32508 — _off-topic: title/snippet matched none of the profile/question tokens_
- TYP: ``ma.extras`` stubs — https://github.com/numpy/numpy/pull/30563 — _off-topic: title/snippet matched none of the profile/question tokens_
- DOC: relnotes for the ``numpy.ma`` typing improvements — https://github.com/numpy/numpy/pull/30566 — _off-topic: title/snippet matched none of the profile/question tokens_
- DOC: update typing roadmap — https://github.com/numpy/numpy/pull/30565 — _off-topic: title/snippet matched none of the profile/question tokens_
- TYP: ``ma.core.mvoid`` annotations — https://github.com/numpy/numpy/pull/30558 — _off-topic: title/snippet matched none of the profile/question tokens_

## Open questions

- Whether adjacent libraries or APIs already cover this use case better than extending the target feature (see evidence: pandas, xarray, JAX). Confirm with maintainers before investing.
- What is the maintainer roadmap for __array_function__ in numpy.ma?
- Is there a prototype or design doc for extending __array_function__ coverage?
- Would improvements duplicate pandas/xarray missing-data functionality?
- Is NEP 12 still relevant to current missing-data strategy?

## Diagnostics

_Pipeline notes; useful when reporting a problem._

- topic_history: maintainer set empty — R1-by-answer disabled

## Sources index

[1] issue-22338 — https://github.com/numpy/numpy/issues/22338
[2] issue-18675 — https://github.com/numpy/numpy/issues/18675
[3] vitals-numpy-ma — https://github.com/numpy/numpy/commits/numpy/ma
[4] activity-numpy-ma — https://github.com/numpy/numpy/commit/01d9da3d7f250af1c3e075368b7c14a35e0a8fa7
[5] adjacent-pandas — https://pandas.pydata.org/docs/user_guide/missing_data.html
[6] adjacent-xarray — https://docs.xarray.dev/
[7] pr-32423 — https://github.com/numpy/numpy/pull/32423
[8] process-doc-0 — https://github.com/numpy/numpy/blob/main/doc/neps/nep-0012-missing-data.rst
[9] process-doc-1 — https://numpy.org/neps/nep-0050-scalar-promotion.html
[10] file-README-md — https://github.com/numpy/numpy/blob/HEAD/README.md
[11] file-doc-neps-nep-0012-missing-data-rst — https://github.com/numpy/numpy/blob/HEAD/doc/neps/nep-0012-missing-data.rst
[12] pr-30221 — https://github.com/numpy/numpy/pull/30221
[13] issue-27588 — https://github.com/numpy/numpy/issues/27588
[14] issue-22347 — https://github.com/numpy/numpy/issues/22347
[15] issue-3543 — https://github.com/numpy/numpy/issues/3543
[16] issue-32126 — https://github.com/numpy/numpy/issues/32126
[17] issue-17697 — https://github.com/numpy/numpy/issues/17697
[18] issue-9748 — https://github.com/numpy/numpy/issues/9748
[19] issue-28403 — https://github.com/numpy/numpy/issues/28403
[20] issue-4895 — https://github.com/numpy/numpy/issues/4895
[21] issue-15601 — https://github.com/numpy/numpy/issues/15601
[22] issue-23737 — https://github.com/numpy/numpy/issues/23737
[23] issue-15858 — https://github.com/numpy/numpy/issues/15858
[24] issue-28450 — https://github.com/numpy/numpy/issues/28450
[25] issue-19877 — https://github.com/numpy/numpy/issues/19877
[26] issue-8881 — https://github.com/numpy/numpy/issues/8881
[27] issue-28255 — https://github.com/numpy/numpy/issues/28255
[28] issue-4476 — https://github.com/numpy/numpy/issues/4476
[29] issue-32401 — https://github.com/numpy/numpy/issues/32401
[30] issue-24525 — https://github.com/numpy/numpy/issues/24525
[31] issue-1381 — https://github.com/numpy/numpy/issues/1381
[32] issue-1376 — https://github.com/numpy/numpy/issues/1376
[33] issue-31868 — https://github.com/numpy/numpy/issues/31868
[34] issue-1380 — https://github.com/numpy/numpy/issues/1380
[35] issue-18425 — https://github.com/numpy/numpy/issues/18425
[36] adjacent-jax — https://jax.readthedocs.io/
[37] issue-26404 — https://github.com/numpy/numpy/issues/26404
[38] issue-1379 — https://github.com/numpy/numpy/issues/1379
[39] issue-27269 — https://github.com/numpy/numpy/issues/27269
[40] issue-32275 — https://github.com/numpy/numpy/issues/32275
[41] issue-10382 — https://github.com/numpy/numpy/issues/10382
[42] issue-1378 — https://github.com/numpy/numpy/issues/1378
[43] issue-30037 — https://github.com/numpy/numpy/issues/30037
[44] issue-7329 — https://github.com/numpy/numpy/issues/7329
[45] issue-7623 — https://github.com/numpy/numpy/issues/7623
[46] issue-1377 — https://github.com/numpy/numpy/issues/1377
[47] issue-29421 — https://github.com/numpy/numpy/issues/29421
[48] issue-12183 — https://github.com/numpy/numpy/issues/12183
[49] issue-7394 — https://github.com/numpy/numpy/issues/7394
[50] issue-31737 — https://github.com/numpy/numpy/issues/31737
[51] issue-27942 — https://github.com/numpy/numpy/issues/27942
[52] issue-5108 — https://github.com/numpy/numpy/issues/5108
[53] file-numpy-ma-README-rst — https://github.com/numpy/numpy/blob/HEAD/numpy/ma/README.rst
[54] issue-16976 — https://github.com/numpy/numpy/issues/16976
[55] issue-27726 — https://github.com/numpy/numpy/issues/27726
[56] issue-27258 — https://github.com/numpy/numpy/issues/27258
[57] issue-24392 — https://github.com/numpy/numpy/issues/24392
[58] issue-32400 — https://github.com/numpy/numpy/issues/32400
