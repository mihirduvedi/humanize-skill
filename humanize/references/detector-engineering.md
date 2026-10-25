# Building a detector: what its decisions actually depend on

Checked October 25, 2026. Use for method research, experimental design and interpretation
of local tests. Read [detector-methods.md](detector-methods.md) for commercial systems and
[detector-research.md](detector-research.md) for earlier reliability and vocabulary evidence.

## A detector learns a distinction inside a data-generating process

A text classifier estimates a relationship between text and labels under the examples,
generators, prompts, genres and editing policies used to build it. That relationship is
not a direct observation of who typed the document. Source provenance labels and
reader judgments of writing quality answer different questions.

Start with matched human and generated examples, separating topic from provenance.
Preserve generator, prompt, domain, date, source-document and revision lineage. Group
all variants from the same source into one split; fit features and parameters on training
data, select thresholds on a separate calibration set, and evaluate once on untouched
test groups. Keep a further domain or generator outside all development decisions.

## Inspectable method families

| Family | How it produces evidence | Main dependency |
| --- | --- | --- |
| Supervised text classification | Learn a boundary from source-labeled examples; a transformer head or a simpler linear model can do this | Training coverage, provenance and contamination control |
| Likelihood and rank | Measure token probabilities, ranks or distribution entropy under a scoring language model | Scoring model, tokenizer and generation settings |
| Perturbation | Compare an original passage's likelihood with generated nearby alternatives | Perturbation quality, source/surrogate access and computational cost |
| Conditional curvature | Standardize observed token log scores against alternative-token expectations | Reference/scoring distributions and token alignment |
| Paired-model ratios | Normalize one language model's loss using disagreement with another | The specified model pair and calibration |
| Probability-feature classifier | Combine probability summaries from weaker language models and train a classifier | Feature search and separation of selection from evaluation |
| Watermark testing | Test for an intentionally introduced generation signal | A compatible watermark scheme and its detection configuration |
| Mixed-authorship segmentation | Predict token/window labels, then align and aggregate them into segments | Boundary resolution, editing labels and aggregation rules |

These are alternatives and combinations, not stages every detector must use.

### What the sources and code show

- [GLTR, Gehrmann et al., ACL 2019](https://aclanthology.org/P19-3019/) uses token likelihood,
  rank and entropy to support inspection. A colored token is relative to its scoring model;
  it is not an intrinsic "AI word."
- [DetectGPT, Mitchell et al., ICML 2023](https://proceedings.mlr.press/v202/mitchell23a.html)
  compares a passage's log probability with perturbed alternatives. Surrogate-model
  performance must be evaluated rather than assumed to match source-model access.
- [Fast-DetectGPT, Bao et al., ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/file/6b8c6f846c3575e1d1ad496abea28826-Paper-Conference.pdf)
  uses conditional token alternatives. Its [analytic implementation](https://github.com/baoguangsheng/fast-detect-gpt/blob/971b05202bac2bb504d60c0ac0812fea7a8f7c82/scripts/fast_detect_gpt.py)
  divides the summed observed-minus-expected log score by the square root of summed
  reference variances. This is not sentence-length variance.
- [Binoculars, Hans et al., ICML 2024](https://proceedings.mlr.press/v235/hans24a.html)
  uses a paired-model ratio; its released implementation and model-specific thresholds
  are discussed in [detector-methods.md](detector-methods.md).
- [Ghostbuster, Verma et al., NAACL 2024](https://aclanthology.org/2024.naacl-long.95/)
  searches combinations of weaker-model probability features and fits regularized logistic
  regression. Its [released classification path](https://github.com/vivek3141/ghostbuster/blob/f60068d006b7dc617af90e7148118837e85d0555/classify.py)
  uses particular model API calls, saved normalization statistics and a classifier.
  Inspecting that path is not evidence of having run its end-to-end system.
- [Kirchenbauer et al., ICML 2023](https://proceedings.mlr.press/v202/kirchenbauer23a.html)
  introduces a generation-time watermark. The [released implementation](https://github.com/jwkirchenbauer/lm-watermarking/blob/82922516930c02f8aa322765defdb5863d07a00e/extended_watermark_processor.py)
  tests green-token counts against their expected proportion. Ordinary editorial advice
  cannot establish whether an unknown generator used that watermark.

[SynthID-Text, Nature 2024](https://www.nature.com/articles/s41586-024-08025-4)
describes a different generation-time approach using tournament sampling and watermark
scores. Its detectable signal depends on length and the generator distribution's entropy.
Do not collapse all watermarks into the original green-list method or imply that a text
classifier's score reveals a watermark. A provider's [August 2026 explanation](https://www.anthropic.com/news/claude-text-watermark)
also illustrates why natural-sounding prose and detectable generation provenance can coexist.

The [2025 Computational Linguistics survey](https://aclanthology.org/2025.cl-1.8/)
provides the broader taxonomy. Prefer each original paper and implementation when
explaining an exact algorithm; a survey's shorthand can hide assumptions and versions.

## Evidence that changes the evaluation design

[M4GT-Bench, ACL 2024](https://aclanthology.org/2024.acl-long.218/) separates binary
detection, generator attribution and mixed-text boundary detection. [DetectRL, NeurIPS
2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/b61bdf7e9f64c04ec75a26e781e2ad51-Paper-Datasets_and_Benchmarks_Track.pdf)
tests domains, generators, editing conditions and lengths. These distinctions mean that
strong full-document accuracy cannot substitute for segment localization or transfer tests.

[ARB, a July 2026 preprint](https://arxiv.org/html/2607.29539v1), matches human originals,
direct AI generations, AI rewrites of human originals and second-pass AI rewrites of AI
generations. Its results differ by rewriting regime, so testing only AI-to-AI rewrites
does not characterize human-origin assistance. The design does not establish a pure
causal effect of origin; preserve the distinction between matched comparisons and causal
identification. This benchmark was read, not rerun locally.

[Sadasivan et al., January 2025 version](https://arxiv.org/html/2303.11156v4) relates
optimal discrimination to distance between the compared text distributions and stress-tests
specific systems. This is a conditional difficulty result, not proof that every detector
is always ineffective. [Jabarian and Imas's 2025 NBER working paper](https://www.nber.org/system/files/working_papers/w34223/w34223.pdf)
reports strong commercial performance in its tested settings, especially for Pangram.
It is a working paper and does not establish performance of all later product versions.
Keep positive and negative evidence rather than selecting only studies that support a
desired conclusion about bypassing detection.

[NIST's 2025 pilot overview](https://www.nist.gov/publications/nist-genai-pilot-overview-text-text-evaluation-results)
uses ranking and probability-error metrics while identifying its summarization scope.
Report AUROC alongside false positives and true positives at a frozen threshold, sample
counts and uncertainty. A low observed error rate with few human controls is weak evidence
of a low population error rate. Probabilities can also become miscalibrated under a shift
in domain, class prevalence or input length.

## Model cards are part of the experiment

The [released HC3 RoBERTa card](https://huggingface.co/Hello-SimpleAI/chatgpt-detector-roberta)
states that it trained on all HC3 data without a holdout. Evaluating that checkpoint on
HC3 cannot establish independent generalization. The [older OpenAI detector card](https://huggingface.co/openai-community/roberta-base-openai-detector)
describes a GPT-2-era task; it should not silently become a current universal detector.
Record architecture, labels, training overlap and input limits before scoring anything.

## Optional local baseline

The [repository's research directory](https://github.com/mihirduvedi/humanize-skill/tree/main/research) contains a runnable TF–IDF word/character
classifier and a surface-feature ablation, trained on hash-pinned historical English
[HC3 subsets](https://huggingface.co/datasets/Hello-SimpleAI/HC3). Questions and exact
normalized answer duplicates cannot cross splits. Calibration controls an empirical
false-positive target; it is not probability calibration or a population guarantee.

The baseline includes domain and prefix-length evaluations plus provenance-labeled
rewrite probes. Read its results and limitations before drawing conclusions. Its scores
are not Turnitin results, and assistant-written revisions never become human-labeled
training examples. Model fitting trains this optional baseline, not the assistant or the
humanize skill's model weights.
