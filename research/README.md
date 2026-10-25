# Local detector research lab

This optional lab trains a small historical English HC3 baseline so detector engineering
claims can be checked against an actual experiment. It is separate from the portable
writing skill, which needs no Python packages, model downloads or API keys.

## Reproduce

From the repository root, using Python 3.12:

```sh
python3 -m venv research/.venv
research/.venv/bin/python -m pip install -r research/requirements.txt
research/.venv/bin/python -m unittest discover -s research -p 'test_*.py' -v
research/.venv/bin/python research/detector_lab.py fetch --data-dir research/cache/data
research/.venv/bin/python research/detector_lab.py run --data-dir research/cache/data --output-dir research/cache/run --pairs-per-domain 700 --rewrite-cases research/rewrite_cases.json
research/.venv/bin/python research/detector_lab.py score --model research/cache/run/word_char.joblib --input research/README.md
```

The fetch command downloads about 18 MB from a fixed public dataset revision and checks
SHA-256 hashes. Raw data and trained models are not committed. Only load joblib models
you created yourself and trust; joblib is not a safe format for untrusted downloads.
Scoring runs locally, and these commands do not upload the input text to any service.

## Design

The dataset is [Hello-SimpleAI/HC3](https://huggingface.co/datasets/Hello-SimpleAI/HC3),
revision `4d0ff18143b5a7e1b1e79beb540c04549d1e59d3`. Its card declares CC BY-SA 4.0;
consult the original corpus sources for their provenance and applicable terms.
The generator is historical ChatGPT, not a representative sample of current models.

For each question, use the first human and ChatGPT answer with at least 40 whitespace
words. Keep one answer of each class, exclude exact normalized duplicates and repeated
questions, and deterministically sample up to 700 pairs per domain. Question hashes
group related answers across train/calibration/test; exact normalized answer hashes also
cannot cross splits. The process does not detect all semantic near-duplicates, repeated
authors or unknown upstream contamination.

Finance and computer-science Wikipedia questions supply development data. Their question
groups are split approximately 60/20/20 using a fixed hash rule. Medicine and open QA
are held outside training and threshold selection. All models use the same partition.

Two deliberately different models are fitted:

- A surface-feature logistic regression uses length, sentence-length summaries, word
  diversity and punctuation ratios, exposing how superficial distinctions can behave.
- A word/character TF–IDF logistic regression learns lexical and local character patterns.
  Its vocabulary, inverse-document frequencies and weights are fitted only on training data.

The calibration threshold targets at most 1% observed human false positives, handling ties
conservatively. This is threshold selection, not probability calibration or a guarantee.
The test report includes AUROC, average precision, Brier score on the balanced dataset,
counts, false positives, true positives and approximate Wilson intervals. Brier scores
are not evidence of calibrated probabilities in another population.

Length conditions use the first 50, 100 or 200 whitespace words only when both answers
to a question meet that length. This keeps matched question membership and class balance
within a condition; different length conditions still contain different eligible questions.
Very small eligible sets do not support strong conclusions.
An additional common cohort keeps only in-domain question pairs whose two answers have
at least 200 words, then compares all prefix lengths on exactly those same questions.

## Revision probes

`rewrite_cases.json` contains 12 assistant-generated before/after pairs. Both versions
remain AI-generated for provenance purposes. All factual scenarios, quotations and locators
in that file are explicitly fictional. The cases exercise reasons, consequences, additions,
qualifications, quotation preservation, count preservation, useful pauses and deletions.

The cases were fixed before examining their detector scores, then used once for the
reported comparison; no detector-driven rewrite search was performed. Two fixture
corrections clarified a supplied cause and reduced clause chaining before the scores were
examined. They are development probes and editorial examples, not an independent human
preference study or unseen tests of the final skill, since related examples enter its references.

Joining ideas lowered some scores and raised others. The surface model's response differed
from the lexical model, so use conjunctions for their actual logical relationship rather
than as a general detector trick. The frozen `results/hc3-results.json` contains all results,
including regressions, while `results/summary.md` explains the scope.

## What was and was not run

Both local classifiers were trained and evaluated. Unit tests cover leakage guards,
dataset integrity, thresholds, confusion metrics, empty inputs, pairing and fixture invariants.
The CLI was exercised for training, successful scoring and expected error paths.

The research also inspected neural detector model cards and primary implementations,
but did not run those neural checkpoints, commercial APIs, full DetectGPT, Fast-DetectGPT,
Ghostbuster or a watermark generator. No Turnitin, GPTZero or other commercial pass rate
was measured. The writing skill's instructions and examples changed; no assistant model
weights were fine-tuned.
