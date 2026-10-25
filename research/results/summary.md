# Results of the local HC3 detector experiment

Run October 25, 2026. This is an English, historical ChatGPT research baseline. It is not
Turnitin, a current universal detector, or evidence that a rewrite is human-authored.
The public dataset revision and file hashes are recorded in `data-manifest.json`.

The run used 4,702 source-labeled documents: 1,752 training, 548 threshold-calibration,
500 in-domain test and 1,902 out-of-domain test documents. Each included question has
one human and one ChatGPT answer. Development uses finance and computer-science
Wikipedia; medicine and open QA remain outside training and threshold selection.

Question groups and exact normalized answer duplicates cannot cross splits. Semantic
near-duplicates, repeated authors and unknown upstream contamination remain possible.
Both answers must have at least 40 words, which selects a subset of the original corpus;
only 251 open-QA pairs met the selection and deduplication rules. Source labels were
not independently authenticated. No private assignment was used.

## Word/character TF–IDF model

| Evaluation | Documents (human / AI) | AUROC | Human false positives | AI detected |
| --- | ---: | ---: | ---: | ---: |
| in domain test | 500 (250 / 250) | 0.9908 | 0/250 (0.00%) | 205/250 (82.00%) |
| medicine | 1400 (700 / 700) | 0.9996 | 0/700 (0.00%) | 666/700 (95.14%) |
| open qa | 502 (251 / 251) | 0.8797 | 1/251 (0.40%) | 79/251 (31.47%) |

AUROC measures ranking across thresholds, not classification accuracy. The threshold
was selected using 274 calibration human answers to allow at most 1% observed false
positives, with ties handled conservatively. Two calibration false positives were
observed (0.73%); this does not guarantee a population error rate below 1%.

The 0/250 human false positives in the in-domain test have an approximate Wilson 95%
upper bound of 1.51%. The high medicine score does not erase the lower open-QA recall,
and may reflect historical dataset styles or artifacts. These results do not establish
performance on current generators or ordinary student literature reviews.

## Surface-feature ablation

| Evaluation | Documents (human / AI) | AUROC | Human false positives | AI detected |
| --- | ---: | ---: | ---: | ---: |
| in domain test | 500 (250 / 250) | 0.9002 | 5/250 (2.00%) | 89/250 (35.60%) |
| medicine | 1400 (700 / 700) | 0.9587 | 12/700 (1.71%) | 60/700 (8.57%) |
| open qa | 502 (251 / 251) | 0.5473 | 53/251 (21.12%) | 30/251 (11.95%) |

This model uses eight summaries of length, rhythm, word diversity, punctuation and
layout. Its poor transfer to open QA illustrates why those features should not become
universal writing rules. The experiment does not isolate a causal effect of any one feature.

## Same-question length comparison

The following uses the word/character model on the same 43 question pairs throughout;
both original answers had at least 200 whitespace words. Prefix lengths and the frozen
threshold are varied as specified, while question membership and class balance are fixed.

| Evaluation | Documents (human / AI) | AUROC | Human false positives | AI detected |
| --- | ---: | ---: | ---: | ---: |
| full | 86 (43 / 43) | 0.9951 | 0/43 (0.00%) | 36/43 (83.72%) |
| first 50 words | 86 (43 / 43) | 0.8951 | 1/43 (2.33%) | 16/43 (37.21%) |
| first 100 words | 86 (43 / 43) | 0.9389 | 0/43 (0.00%) | 21/43 (48.84%) |
| first 200 words | 86 (43 / 43) | 0.9838 | 0/43 (0.00%) | 28/43 (65.12%) |

This is a small, selected cohort. The complete JSON also contains length-specific
eligible cohorts for each domain; those have different question membership and must
not be read as a pure comparison of length. Some cells have only one question pair,
which is insufficient for a general conclusion despite a numerically perfect AUROC.

## Constructed revision probes

The twelve before/after pairs are assistant-generated on both sides and were not used
for detector training or threshold selection. Their detector scores were not used to
search for or tune wording. The word/character model lowered its score on seven pairs,
raised it on four and left one unchanged; the surface model raised eleven and left one
unchanged. At the frozen thresholds, the lexical model flagged one original and no
revisions, while the surface model flagged neither originals nor revisions.

Most originals were already below threshold, so the flag counts do not demonstrate a
new bypass capability. The cases are short, constructed development probes that also
inform the editing references; they are not independent tests of the final skill or a
blind human preference study. The useful conclusion is that detector responses differed,
while editorial quality still required checking facts, logic, quotations and cadence.

## Verification and reproducibility

Sixteen unit tests cover grouping, duplicate leakage, dataset integrity, conservative
thresholds and ties, known confusion metrics, invalid/empty inputs, matched length
selection and protected fixture text. Training and local model-loading/scoring were
exercised, as were expected CLI errors. See `../README.md` for commands and scope.
The local run also saves a split manifest containing hashes, not answer text; it can be
regenerated from the pinned data and deterministic code.

The separate forward review caught and corrected two fidelity errors before accepting
six final examples. That review was performed by the same assistant, with no commercial
API, neural checkpoint inference, blind reviewer or assistant-model fine-tuning.
