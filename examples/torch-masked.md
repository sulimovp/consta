# Assessment: Is reviving torch.masked worth an upstream contribution?

Generated: 2026-10-08T18:56:06.670306+00:00 | Repo: `pytorch/pytorch` | Profile: pytorch | Evidence freshness: 2026-08-30T00:00:00+00:00

## Summary (model synthesis — verify citations below)

The torch/masked module shows declining vital signs with zero commits in the last three months and only seven in six months, though it retains nine committers and a 76 % issue closure rate across ~100 open issues "commits 3/6/12mo = 0/7/23 (falling); committers=9; open\_issues\_total=100; closure\_rate=0.761" [3]. Recent activity is dominated by merge-bot traffic rather than substantive development "Latest: 80ef8b5 on 2026-07-02T15:36:56Z. Top committers: pytorchmergebot, Skylion007, aorenste" [7], and documentation remains incomplete "Masked Tensor documentation is missing" [1] despite a recent doc update PR "Update masked.rst (#89758)" [8].

Open issues reveal fundamental correctness and usability gaps: masks not moving to CUDA "Mask in MaskedTensor does not change device" [24], 10× slowdown versus regular tensors for softmax "\`MaskedTensor\` 10x slower than \`Tensor\` compared with \`nn.functional.softmax\`" [23], CPU/CUDA divergence for argmax "torch.masked.argmax returns different results on CPU vs CUDA" [22], crashes in `_masked_softmax` on empty dims "\`torch.\_masked\_softmax\` on an empty softmax dim crashes the process" [16], and lack of `torch.compile` support "[torch.compile] torch.masked.median fails on integer inputs under fullgraph=True" [19]. Meanwhile, the adjacent NestedTensor project carries an explicit warning "Nested tensors are not currently under active development. Use at your own risk" [9], and FlexAttention provides a high-performance alternative for masked attention workloads "optimized attention implementations like FlashAttention" [10], suggesting some use cases may already be served elsewhere.

## Topic trajectory

_Topic rollup refused:_ realized R1 rates unknown — cannot place topic on the supply axis

_Hazard score refused:_ trained topic-hazard artifact not shipped (topic-hazard-v0-refuse); observation window unknown — need ≥360d (2× the 180d horizon)

_Demand×supply rollup is descriptive, from realized outcomes. Resolution-hazard score is a forecast over ~180 days — not a recommendation._

## Evidence

### Issues and discussions

[1] Masked Tensor documentation is missing — https://github.com/pytorch/pytorch/issues/89734 — ### 📚 The doc issue In the docs for masked tensors (https://pytorch.org/docs/stable/masked.html?highlight=masked_tensor)
[2] `masked_fill` with `FloatTensor` mask will never mask but fails silently. — https://github.com/pytorch/pytorch/issues/89320 — ### 🐛 Describe the bug Passing `bool` or `int` tensors as a mask input to `masked_fill` returns the excepted result, but
[15] Give the possibly to get back normal `Tensor`s as `MaskedTensor` gradients — https://github.com/pytorch/pytorch/issues/124964 — ### 🚀 The feature, motivation and pitch I am working on a project that requires to manipulate a lot of masks and some ma
[16] `torch._masked_softmax` on an empty softmax dim crashes the process (SIGSEGV / integer division by zero), no Python exception — https://github.com/pytorch/pytorch/issues/199937 — ### 🐛 Describe the bug `F.softmax` on a tensor with softmax dim size 0 is fine. `torch._masked_softmax` on the same shap
[17] [CPU] _masked_softmax_backward reads past a smaller output tensor — https://github.com/pytorch/pytorch/issues/194801 — # Title `[CPU] _masked_softmax_backward reads past a smaller output tensor` ### Describe the bug `aten::_masked_softmax_
[18] masked.softmax/masked.softmin OpInfo samples can be fully masked-out, making test_vmapvjpvjp compare undefined values — https://github.com/pytorch/pytorch/issues/196289 — ### 🐛 Describe the bug `test/functorch/test_ops.py::TestOperatorsDevice::test_vmapvjpvjp_masked_softmax_*_float32` and `
[19] [torch.compile] torch.masked.median fails on integer inputs under fullgraph=True — https://github.com/pytorch/pytorch/issues/194766 — ### 🐛 Describe the bug `torch.masked.median` cannot be captured with `torch.compile(fullgraph=True)` for a valid integer
[20] DISABLED test_comprehensive_masked_cumprod_xpu_float16 (__main__.TestInductorOpInfoXPU) — https://github.com/pytorch/pytorch/issues/177483 — Platforms: xpu This test was disabled because it is failing on main branch ([recent examples](https://torch-ci.com/failu
[21] dim broadcast in masked tensor between mask and data. — https://github.com/pytorch/pytorch/issues/169191 — ### 🚀 The feature, motivation and pitch ``` mask = torch.randint(size=(3,),low=0, high=2, dtype=torch.bool, device = dev
[22] torch.masked.argmax returns different results on CPU vs CUDA when multiple maximum values exist — https://github.com/pytorch/pytorch/issues/166401 — ### 🐛 Describe the bug ### code ```python DEVICE = 'cpu' device = DEVICE import torch import torch.nn.functional as F to
[23] `MaskedTensor` 10x slower than `Tensor` compared with `nn.functional.softmax` — https://github.com/pytorch/pytorch/issues/150186 — ## Context I was reading the docs on the new `MasedTensor` feature and wanted to get some insight if it might be useful 
[24] Mask in MaskedTensor does not change device — https://github.com/pytorch/pytorch/issues/147140 — ### 🐛 Describe the bug When you create a MaskedTensor and change it to cuda, the data is the only one that change to cud
[25] Error computing the norm of MaskedTensor — https://github.com/pytorch/pytorch/issues/117287 — ### 🐛 Describe the bug According to the [documentation](https://pytorch.org/docs/2.1/masked.html#reductions), the `norm`
[26] nn.InstanceNorm and nn.GroupNorm are affected by padding, so they need to masking — https://github.com/pytorch/pytorch/issues/81985 — ### 🐛 Describe the bug For batch_size > 1, variable-length inputs (e.g. speech, text) are padded in order to construct o
[27] MaskedTensor do not support _is_any_true` — https://github.com/pytorch/pytorch/issues/128557 — ### 🐛 Describe the bug Hi, The op `_is_any_true` is not implemented for `MaskedTensor` which seems to be a problem in th
[28] topk with mask - efficent — https://github.com/pytorch/pytorch/issues/132608 — ### 🚀 The feature, motivation and pitch topk operation is important for many domains, but still suffer from high complex
[29] Poor scaling of `torch.masked.mean` — https://github.com/pytorch/pytorch/issues/131292 — ### 🐛 Describe the bug Consider this equivalent formulation (for strided tensors, at least): ```python def masked_mean( 
[30] RecursionError for MaskedTensor.where — https://github.com/pytorch/pytorch/issues/129272 — ### 🐛 Describe the bug ```pycon >>> import torch >>> from torch.masked import MaskedTensor >>> a = MaskedTensor(torch.te
[31] Backward is not supported by `MaskedTensor`'s `torch.maximum` — https://github.com/pytorch/pytorch/issues/128641 — ### 🐛 Describe the bug Running the following code: ```python torch.maximum( MaskedTensor( torch.tensor(5.), torch.tensor
[32] torch.masked_select passes in the same parameters, but gives different results on CPU and GPU. — https://github.com/pytorch/pytorch/issues/89415 — ### 🐛 Describe the bug Test on the CPU: import torch input = torch.rand([8], dtype=torch.float32) mask = torch.randint(0
[33] Numpy like Masked/where operations — https://github.com/pytorch/pytorch/issues/116461 — ### 🚀 The feature, motivation and pitch Numpy allows me to do masked operations such as mean/variance using `where` argu
[34] `amax` fails on `masked_tensor` with multiple negative dims — https://github.com/pytorch/pytorch/issues/115624 — ### 🐛 Describe the bug `amax` fails on `masked_tensor` with multiple negative dims, error message: "data.size() must equ
[35] Links on MaskedTensors are broken — https://github.com/pytorch/pytorch/issues/165134 — ### 📚 The doc issue The links provided on https://docs.pytorch.org/docs/stable/masked.html are broken. For example: http
[36] TypeError: no implementation found for 'torch._ops.aten.max.default' on types that implement __torch_dispatch__: [<class 'torch.masked.maskedtensor.core.MaskedTensor'>] — https://github.com/pytorch/pytorch/issues/92350 — ### 🐛 Describe the bug My problem with MaskedTensor is that the stacktrace is extremely incorrect and vague, I am unable
[37] Broken link to user guide for masked tensors — https://github.com/pytorch/pytorch/issues/173055 — ### 📚 The doc issue Tried to navigate to new user guide on the [torch.masked](https://docs.pytorch.org/docs/stable/maske
[39] [fx] A `forward` parameter named `nan` or `inf` shadows the float constant that the generated code prints as the bare name `nan` / `inf`: `GraphModule.forward` silently uses the tensor instead of the constant (`Interpreter` is correct) — https://github.com/pytorch/pytorch/issues/198072 — [fx] A `forward` parameter named `nan` or `inf` shadows the float constant that the generated code prints as the bare na
[40] string representation method for empty masked tensors fails — https://github.com/pytorch/pytorch/issues/115422 — ### 🐛 Describe the bug ``` import torch from torch.masked import masked_tensor empty_tensor = torch.empty(size=[0], dtyp
[41] nn.TransformerEncoder fastpath returns NaN for fully-masked rows; propagates as silent wrong predictions downstream — https://github.com/pytorch/pytorch/issues/199054 — Fastpath in `nn.TransformerEncoder`/`nn.MultiheadAttention` returns NaN for any row where `src_key_padding_mask` masks e
[45] Clarify dependency on NumPy (related to maskedtensor?) — https://github.com/pytorch/pytorch/issues/76656 — ### 🐛 Describe the bug I installed torch cpu version on a new python3.8 ubuntu 20.04 system via pip. From what I underst
[46] DISABLED test_index_put_as_masked_fill_mask_reads_target_by_extern_kernel_cuda (__main__.GPUTests) — https://github.com/pytorch/pytorch/issues/199672 — Platforms: rocm I approve of this message. > **What fails.** `GPUTests::test_index_put_as_masked_fill_mask_reads_target_
[47] [MPS][Inductor] Silent wrong result: a recomputed x² + y² read through F.pad becomes x² + x² — https://github.com/pytorch/pytorch/issues/199642 — ### 🐛 Describe the bug On MPS, `torch.compile` (Inductor) silently returns wrong values for the function below. Eager MP
[48] Backpropagating on some losses produces NaN where it should not — https://github.com/pytorch/pytorch/issues/121416 — ### 🐛 Describe the bug I run into `nan` in gradients where there should not be, when using the `SmoothL1Loss`, the `MSEL
[49] torch.to_dense backward ignores unspecified elements in sparse inputs — https://github.com/pytorch/pytorch/issues/95550 — ## Issue description For historical reasons, torch.to_dense backward on sparse inputs implements masked semantics that c
[51] Feedback about torch.masked_fill — https://github.com/pytorch/pytorch/issues/196659 — There is the following page about masked_fill is blank: https://docs.pytorch.org/docs/2.14/generated/torch.masked_fill.h
[52] Assertion error in Flex Attention backward pass when indexing a parameter — https://github.com/pytorch/pytorch/issues/146896 — ### 🐛 Describe the bug Flex Attention raises an assertion error during the backward pass if the `score_mod` implementati

### Merged work

[6] Implement masked_select op for NestedTensors — https://github.com/pytorch/pytorch/pull/131069
[8] Update masked.rst (#89758) — https://github.com/pytorch/pytorch/pull/89923
[43] Fix invalid read in masked softmax (#82272) (#82272) — https://github.com/pytorch/pytorch/pull/82405
[44] Add masked_fill_.Scalar, masked_fill_.Tensor — https://github.com/pytorch/pytorch/pull/68119

### Module activity

[7] Recent activity on torch/masked — https://github.com/pytorch/pytorch/commit/80ef8b58594034889b49bba33a6074d187b58a58 — Path `torch/masked`: 124 commits fetched. Latest: 80ef8b5 on 2026-07-02T15:36:56Z. Top committers: pytorchmergebot, Skyl

### Repository files

[13] README.md — https://github.com/pytorch/pytorch/blob/HEAD/README.md — <picture> <source media="(prefers-color-scheme: dark)" srcset="https://github.com/pytorch/pytorch/raw/main/docs/source/_
[14] docs/source/masked.md — https://github.com/pytorch/pytorch/blob/HEAD/docs/source/masked.md — ```{eval-rst} .. automodule:: torch.masked .. automodule:: torch.masked.maskedtensor ``` ```{eval-rst} .. currentmodule:
[50] torch/masked/__init__.py — https://github.com/pytorch/pytorch/blob/HEAD/torch/masked/__init__.py — from torch.masked._ops import ( _canonical_dim, _combine_input_and_mask, _generate_docstring, _input_mask, _output_mask,

### Dev-discuss and forums

[4] State of PyTorch core: September 2021 edition - frontend API - PyTorch Developer Mailing List — https://dev-discuss.pytorch.org/t/state-of-pytorch-core-september-2021-edition/332 — State of PyTorch core: September 2021 edition There are a lot of projects currently going on in PyTorch core and it can 
[5] What (and Why) is __torch_dispatch__? - frontend API - PyTorch Developer Mailing List — https://dev-discuss.pytorch.org/t/what-and-why-is-torch-dispatch/557 — With Alban Desmaison, Edward Yang, and Richard Zou. You may have seen us mention __torch_dispatch__ in various places re
[38] Torch.nn H2 2021 Lookback and H1 2022 Lookahead - frontend API - PyTorch Developer Mailing List — https://dev-discuss.pytorch.org/t/torch-nn-h2-2021-lookback-and-h1-2022-lookahead/477 — Hey everyone! I wanted to post some quick highlights from the torch.nn work during H2 2021 and the upcoming projects we 

### Adjacent projects (validated)

[9] NestedTensor — https://pytorch.org/docs/stable/nested.html — Rate this Page ★ ★ ★ ★ ★ torch.nested # Created On: Mar 02, 2022 | Last Updated On: Jan 16, 2026 Introduction # Warning 
  _Curator note, not source text:_ Core team's structured approach to ragged/masked batch data; often preferred over MaskedTensor for sequence models.
[10] FlexAttention — https://pytorch.org/blog/flexattention/ — In theory, Attention is All You Need. In practice, however, we also need optimized attention implementations like FlashA
  _Curator note, not source text:_ Masked attention patterns without a dedicated MaskedTensor type in hot paths.
[42] torch.nested — https://github.com/pytorch/pytorch/tree/main/torch/nested — Tensors and Dynamic neural networks in Python with strong GPU acceleration - pytorch/torch/nested at main · pytorch/pyto
  _Curator note, not source text:_ Active investment area adjacent to masked/ragged use cases.

### Maintainer / process

[11] CONTRIBUTING.md — https://github.com/pytorch/pytorch/blob/HEAD/CONTRIBUTING.md — Thank you for your interest in contributing to PyTorch! If you're a new contributor, please first read the [Issue and PR
[12] PyTorch RFC repo — https://github.com/pytorch/rfcs — Design / RFC index: PyTorch RFC repo

### Module vital signs

[3] Module vital signs: torch/masked — https://github.com/pytorch/pytorch/commits/torch/masked — `torch/masked`: commits 3/6/12mo = 0/7/23 (falling); committers=9; open_issues_total=100; closure_rate=0.761; CODEOWNERS

- Commits 3 / 6 / 12 months: 0 / 7 / 23 (trend: falling) — https://github.com/pytorch/pytorch/commits/torch/masked
- Distinct committers (12mo sample): 9; top=cyyever; active on this path in 6mo=False
- Open issues (API total_count): 100; closed total=318; median open age days=146.0; closure_rate=0.761 — https://github.com/pytorch/pytorch/issues?q=%22torch/masked%22
- CODEOWNERS present=True; mentions path=False — https://github.com/pytorch/pytorch/blob/HEAD/CODEOWNERS
- Prototype/stale label hits in open sample: 0

## Retrieved but excluded

- [MPS] Tracking issue: sparse compressed (CSR/CSC/BSR/BSC) tensor support — https://github.com/pytorch/pytorch/issues/196192 — _off-topic: title/snippet matched none of the profile/question tokens_
- `[Inductor][CPU] torch.var returns NaN for large-magnitude constant float64 inputs while eager returns 0` — https://github.com/pytorch/pytorch/issues/200229 — _off-topic: title/snippet matched none of the profile/question tokens_
- [FX][Performance] Expensive repeated cycle checks in CapabilityBasedPartitioner.propose_partitions() — https://github.com/pytorch/pytorch/issues/200262 — _off-topic: title/snippet matched none of the profile/question tokens_
- MPS: torch.mm crashes process (uncaught NSException) on non-contiguous/transposed input — regression between nightly 2026-08-31 and 2026-09-01 — https://github.com/pytorch/pytorch/issues/199882 — _off-topic: title/snippet matched none of the profile/question tokens_
- [Feature Request] Make torch.solve output NaN for singular matrix — https://github.com/pytorch/pytorch/issues/31546 — _off-topic: title/snippet matched none of the profile/question tokens_
- Tensor __getitem__ not documented, sparse grad? — https://github.com/pytorch/pytorch/issues/101068 — _off-topic: title/snippet matched none of the profile/question tokens_
- Most requested ops for the MPS backend — https://github.com/pytorch/pytorch/issues/154052 — _off-topic: title/snippet matched none of the profile/question tokens_
- [XPU] boolean-mask indexing silently returns empty on Intel Arc B580 — https://github.com/pytorch/pytorch/issues/199163 — _off-topic: title/snippet matched none of the profile/question tokens_
- Semantics of sparse operations clarification - Sparsity of the gradient with respect to a sparse tensor input — https://github.com/pytorch/pytorch/issues/87448 — _off-topic: title/snippet matched none of the profile/question tokens_
- [ROCm][gfx1201/RDNA4] expandable_segments silently produces NaN in bf16 training when a depthwise F.conv1d runs across the optimizer step — https://github.com/pytorch/pytorch/issues/195202 — _off-topic: title/snippet matched none of the profile/question tokens_
- torch.cond / while_loop / map / switch backward redraws random ops, so gradients use a different dropout mask than the forward — https://github.com/pytorch/pytorch/issues/199257 — _off-topic: title/snippet matched none of the profile/question tokens_
- ☂️ Missing shape checks result in out-of-bounds access of Tensor data — https://github.com/pytorch/pytorch/issues/195547 — _off-topic: title/snippet matched none of the profile/question tokens_
- Incorrect gradients in NaN-ignoring MSE — https://github.com/pytorch/pytorch/issues/89543 — _off-topic: title/snippet matched none of the profile/question tokens_
- [inductor] y.index_put_((mask,), v) with a mask that reads y through a transposed view reads the update's own output (regression) — https://github.com/pytorch/pytorch/issues/198533 — _off-topic: title/snippet matched none of the profile/question tokens_
- DISABLED test_serialization_array_with_empty (__main__.TestCuda) — https://github.com/pytorch/pytorch/issues/134966 — _off-topic: title/snippet matched none of the profile/question tokens_
- [inductor] 134 operators run under `torch.compile` on dtypes their eager kernels reject with `NotImplementedError` (bool conv, int softmax/losses, float bitwise ops, half special functions, complex norms): full list — https://github.com/pytorch/pytorch/issues/198155 — _off-topic: title/snippet matched none of the profile/question tokens_
- [inductor][cpu] Vectorized `torch.remainder` / `%` returns NaN for an infinite divisor and 0 for large quotients; elements handled by the scalar tail are correct, so the result depends on the tensor length and on the CPU — https://github.com/pytorch/pytorch/issues/198057 — _off-topic: title/snippet matched none of the profile/question tokens_
- DISABLED test_rerun_then_pass (test.junit_xml_testdata.pytest_suite.TestJunitOutcomes) — https://github.com/pytorch/pytorch/issues/198596 — _off-topic: title/snippet matched none of the profile/question tokens_
- [torch.compile] `expand` + `fill_` produces incorrect results — https://github.com/pytorch/pytorch/issues/197448 — _off-topic: title/snippet matched none of the profile/question tokens_
- DISABLED test_del_subscr_multi_stream_sync_dealloc_cuda (__main__.TestStreamsCUDA) — https://github.com/pytorch/pytorch/issues/195166 — _off-topic: title/snippet matched none of the profile/question tokens_
- [MPS] torch.remainder returns incorrect results for large quotients and infinite divisors — https://github.com/pytorch/pytorch/issues/200266 — _off-topic: title/snippet matched none of the profile/question tokens_
- DISABLED test_rerun_then_pass (__main__.TestJunitOutcomes) — https://github.com/pytorch/pytorch/issues/198595 — _off-topic: title/snippet matched none of the profile/question tokens_
- DISABLED test_torchvision_models_efficientnet_v2_l (__main__.TestVisionTracing) — https://github.com/pytorch/pytorch/issues/152632 — _off-topic: title/snippet matched none of the profile/question tokens_
- DISABLED test_opcheck_customopdef (__main__.TestGenerateOpcheckTests) — https://github.com/pytorch/pytorch/issues/200213 — _off-topic: title/snippet matched none of the profile/question tokens_
- [dynamo] torch.compile: StreamContextVariable.python_type() hardcoded to torch.cuda.StreamContext, returns wrong type for XPU/NPU — https://github.com/pytorch/pytorch/issues/200260 — _off-topic: title/snippet matched none of the profile/question tokens_
- [Inductor] torch.mvlgamma silently returns zeros for p=0 instead of raising the eager p>=1 check — https://github.com/pytorch/pytorch/issues/200228 — _off-topic: title/snippet matched none of the profile/question tokens_
- `[Inductor][CUDA] FTZ on subnormal inputs causes O(1) errors in ceil(float32) and atan2(bfloat16)` — https://github.com/pytorch/pytorch/issues/200239 — _off-topic: title/snippet matched none of the profile/question tokens_
- `[Inductor] nll_loss silently computes a loss for a shape-mismatched target that eager and aot_eager reject` — https://github.com/pytorch/pytorch/issues/200244 — _off-topic: title/snippet matched none of the profile/question tokens_
- [inductor] Integer floor division of the dtype's minimum by a negative divisor has the wrong sign on CUDA — https://github.com/pytorch/pytorch/issues/198545 — _off-topic: title/snippet matched none of the profile/question tokens_
- Support `bytearray` in Dynamo — https://github.com/pytorch/pytorch/issues/192126 — _off-topic: title/snippet matched none of the profile/question tokens_
- [DO NOT CLOSE] Autorevert actions shadow mode stream — https://github.com/pytorch/pytorch/issues/163650 — _off-topic: title/snippet matched none of the profile/question tokens_
- Python 3.15 support for PyTorch — https://github.com/pytorch/pytorch/issues/184352 — _off-topic: title/snippet matched none of the profile/question tokens_
- [v.2.15.0] Release Tracker — https://github.com/pytorch/pytorch/issues/199813 — _off-topic: title/snippet matched none of the profile/question tokens_
- DISABLED test_eager_equivalence_nn_functional_gelu_backend_inductor_default_cuda_float32 (__main__.TestOpInfoPropertiesCUDA) — https://github.com/pytorch/pytorch/issues/188840 — _off-topic: title/snippet matched none of the profile/question tokens_
- [Inductor] soft_margin_loss returns wrong dtype for mixed-dtype input and target — https://github.com/pytorch/pytorch/issues/198994 — _off-topic: title/snippet matched none of the profile/question tokens_
- Torch Elastic Wait timeout increase — https://github.com/pytorch/pytorch/issues/157318 — _off-topic: title/snippet matched none of the profile/question tokens_
- [Inductor][MPS] Fix half-precision type mismatches in Metal shader codegen (#176436) — https://github.com/pytorch/pytorch/pull/177193 — _off-topic: title/snippet matched none of the profile/question tokens_
- Dont exclude constant_pad_nd in prologue fusion — https://github.com/pytorch/pytorch/pull/150145 — _off-topic: title/snippet matched none of the profile/question tokens_
- [LTC] Add support for non-structured in-place operator variants — https://github.com/pytorch/pytorch/pull/67126 — _off-topic: title/snippet matched none of the profile/question tokens_
- Small cleanups for LoweringContext and BackendImplInterface — https://github.com/pytorch/pytorch/pull/67791 — _off-topic: title/snippet matched none of the profile/question tokens_
- Clean up Backend interface and lowering context related things — https://github.com/pytorch/pytorch/pull/67580 — _off-topic: title/snippet matched none of the profile/question tokens_
- [ONNX] fix export of embedding with padding_idx — https://github.com/pytorch/pytorch/pull/53053 — _off-topic: title/snippet matched none of the profile/question tokens_

## Open questions

- Whether adjacent libraries or APIs already cover this use case better than extending the target feature (see evidence: NestedTensor, FlexAttention, torch.nested). Confirm with maintainers before investing.
- Is there a maintainer-approved roadmap or RFC for reviving torch.masked, or is it intentionally deprecated?
- Are the open correctness bugs (device handling, CPU/CUDA parity, compile support) prioritized for fixes, or will they remain unresolved?
- Does the performance gap (10× slowdown) have a known optimization path, or is it architectural?
- Would contributions overlap with FlexAttention or other masked-kernel efforts already in progress?

## Diagnostics

_Pipeline notes; useful when reporting a problem._

- Discourse search on https://dev-discuss.pytorch.org/ returned no extra threads — review search terms or add pinned_threads.
- topic_history: maintainer set empty — R1-by-answer disabled
- topic_history: R1 sample truncated: 75 closed issues in 2024-10-08..2026-04-10, cap 50

## Sources index

[1] issue-89734 — https://github.com/pytorch/pytorch/issues/89734
[2] issue-89320 — https://github.com/pytorch/pytorch/issues/89320
[3] vitals-torch-masked — https://github.com/pytorch/pytorch/commits/torch/masked
[4] discourse-332 — https://dev-discuss.pytorch.org/t/state-of-pytorch-core-september-2021-edition/332
[5] discourse-557 — https://dev-discuss.pytorch.org/t/what-and-why-is-torch-dispatch/557
[6] pr-131069 — https://github.com/pytorch/pytorch/pull/131069
[7] activity-torch-masked — https://github.com/pytorch/pytorch/commit/80ef8b58594034889b49bba33a6074d187b58a58
[8] pr-89923 — https://github.com/pytorch/pytorch/pull/89923
[9] adjacent-nestedtensor — https://pytorch.org/docs/stable/nested.html
[10] adjacent-flexattention — https://pytorch.org/blog/flexattention/
[11] file-CONTRIBUTING-md — https://github.com/pytorch/pytorch/blob/HEAD/CONTRIBUTING.md
[12] process-doc-0 — https://github.com/pytorch/rfcs
[13] file-README-md — https://github.com/pytorch/pytorch/blob/HEAD/README.md
[14] file-docs-source-masked-md — https://github.com/pytorch/pytorch/blob/HEAD/docs/source/masked.md
[15] issue-124964 — https://github.com/pytorch/pytorch/issues/124964
[16] issue-199937 — https://github.com/pytorch/pytorch/issues/199937
[17] issue-194801 — https://github.com/pytorch/pytorch/issues/194801
[18] issue-196289 — https://github.com/pytorch/pytorch/issues/196289
[19] issue-194766 — https://github.com/pytorch/pytorch/issues/194766
[20] issue-177483 — https://github.com/pytorch/pytorch/issues/177483
[21] issue-169191 — https://github.com/pytorch/pytorch/issues/169191
[22] issue-166401 — https://github.com/pytorch/pytorch/issues/166401
[23] issue-150186 — https://github.com/pytorch/pytorch/issues/150186
[24] issue-147140 — https://github.com/pytorch/pytorch/issues/147140
[25] issue-117287 — https://github.com/pytorch/pytorch/issues/117287
[26] issue-81985 — https://github.com/pytorch/pytorch/issues/81985
[27] issue-128557 — https://github.com/pytorch/pytorch/issues/128557
[28] issue-132608 — https://github.com/pytorch/pytorch/issues/132608
[29] issue-131292 — https://github.com/pytorch/pytorch/issues/131292
[30] issue-129272 — https://github.com/pytorch/pytorch/issues/129272
[31] issue-128641 — https://github.com/pytorch/pytorch/issues/128641
[32] issue-89415 — https://github.com/pytorch/pytorch/issues/89415
[33] issue-116461 — https://github.com/pytorch/pytorch/issues/116461
[34] issue-115624 — https://github.com/pytorch/pytorch/issues/115624
[35] issue-165134 — https://github.com/pytorch/pytorch/issues/165134
[36] issue-92350 — https://github.com/pytorch/pytorch/issues/92350
[37] issue-173055 — https://github.com/pytorch/pytorch/issues/173055
[38] discourse-477 — https://dev-discuss.pytorch.org/t/torch-nn-h2-2021-lookback-and-h1-2022-lookahead/477
[39] issue-198072 — https://github.com/pytorch/pytorch/issues/198072
[40] issue-115422 — https://github.com/pytorch/pytorch/issues/115422
[41] issue-199054 — https://github.com/pytorch/pytorch/issues/199054
[42] adjacent-torch.nested — https://github.com/pytorch/pytorch/tree/main/torch/nested
[43] pr-82405 — https://github.com/pytorch/pytorch/pull/82405
[44] pr-68119 — https://github.com/pytorch/pytorch/pull/68119
[45] issue-76656 — https://github.com/pytorch/pytorch/issues/76656
[46] issue-199672 — https://github.com/pytorch/pytorch/issues/199672
[47] issue-199642 — https://github.com/pytorch/pytorch/issues/199642
[48] issue-121416 — https://github.com/pytorch/pytorch/issues/121416
[49] issue-95550 — https://github.com/pytorch/pytorch/issues/95550
[50] file-torch-masked-__init__-py — https://github.com/pytorch/pytorch/blob/HEAD/torch/masked/__init__.py
[51] issue-196659 — https://github.com/pytorch/pytorch/issues/196659
[52] issue-146896 — https://github.com/pytorch/pytorch/issues/146896
