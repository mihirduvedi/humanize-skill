# Research on detectors and writing style

Checked October 25, 2026. These notes distinguish public evidence, provider claims, and editorial judgment. They do not establish a reliable way to obtain a particular detector result.

## What GPTZero publicly discloses, by version

[GPTZero's support article](https://support.gptzero.me/articles/9585228410-how-do-i-interpret-burstiness-or-perplexity) says it replaced its perplexity-and-burstiness approach in autumn 2023. Do not describe that early design as its current algorithm.

The [February 2026 technical report](https://arxiv.org/html/2602.13042v1), sections 3.2–3.4, describes supervised document and sentence classification, a human/AI/mixed hierarchy, and training involving edited and paraphrased text. It explicitly keeps architecture and hyperparameters proprietary. Its evaluation is the provider's report, not independent verification. These disclosures do not reveal a phrase blacklist or allow exact reverse-engineering of an arbitrary prediction.

The later [GPTZero 4o announcement](https://gptzero.me/news/introducing-gptzero-4o), dated October 18, 2026, says that model is the default from September 20, with changed architecture, expanded training and heading masking. It also says punctuation changes do not determine the result. Treat these as provider disclosures rather than an independently reproduced mechanism or guarantee; the February report is not a complete specification of 4o.

The separate [AI Patterns feature](https://gptzero.me/news/ai-patterns) exposes a rhetorical taxonomy covering empty commentary, vague experts, inflated importance and other patterns. The provider explicitly says those patterns also occur in human writing. Pattern explanations do not disclose all classifier weights or show that removing a pattern will change a classification.

[GPTZero's result guide](https://support.gptzero.me/articles/4965048546-How-do-I-interpret-a-GPTZero-result) says the AI detection score is not the percentage of AI in a document. Distinguish a class probability from a measured fraction of authorship.

## Different detectors use different methods

For an engineering account, code references, model-card contamination checks, newer
rewriting benchmarks and the optional local experiment, see
[detector-engineering.md](detector-engineering.md). For improving the skill through
recorded revisions, see [revision-evaluation.md](revision-evaluation.md).

[Mitchell et al., DetectGPT, ICML 2023](https://proceedings.mlr.press/v202/mitchell23a.html) proposes a probability-curvature test using model likelihoods and perturbed text. This is a specific research method, not an explanation of every commercial system. A single rule about rare words, short sentences, or punctuation cannot be assumed to apply across architectures.

## Reliability depends on the evaluation

[Dugan et al., RAID, ACL 2024](https://aclanthology.org/2024.acl-long.674/) evaluates 12 detectors across domains, models, generation settings, and altered text. Findings depend on thresholds and target false-positive rates; generalization was uneven. The paper also identifies relatively strong cases, including GPTZero's robustness to the tested alterations. It does not justify saying that all detectors always fail, or that a change known to affect a 2024 model will work now.

[Weber-Wulff et al., 2023](https://doi.org/10.1007/s40979-023-00146-z) tested 14 tools and found substantial errors in the evaluated versions. Treat this as historical evidence about those systems and documents. Do not present its measured accuracy as a current product statistic.

[Liang et al., 2023](https://arxiv.org/html/2304.02819v3) tested seven detectors on 91 TOEFL essays and 88 US eighth-grade essays. The average false-positive rate for the TOEFL essays was 61.22%. This is a dataset- and time-specific finding about unequal error rates, not proof that a particular present-day result is wrong. It undermines the assumption that plain or predictable language cannot be human writing.

## What linguistic research can support

[Kobak et al., Science Advances 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12219543/) analyzes more than 15 million biomedical abstracts. Certain stylistic words rose sharply after widespread LLM adoption, including forms of "delve," "underscore," and "showcase." The analysis concerns aggregate vocabulary shifts. It does not supply GPTZero feature weights or prove the origin of an individual sentence. Normal words such as "findings" should not be banned.

[Guo et al., HC3, 2023](https://arxiv.org/html/2301.07597) compares recorded human answers with early ChatGPT answers. Its volunteers observed tendencies toward extended explanations, definitions, and summaries in that model's responses. The source data mix genres and the model is old. These observations can suggest an editing diagnosis but cannot define a timeless human voice. Corpus provenance is documented in the [authors' repository](https://github.com/Hello-SimpleAI/chatgpt-comparison-detection).

## Academic synthesis

[George Mason's literature-review guide](https://writingcenter.gmu.edu/writing-resources/research-based-writing/organizing-literature-reviews-the-basics) recommends organizing the review through topics connecting the sources. [Purdue OWL](https://owl.purdue.edu/owl/research_and_citation/conducting_research/writing_a_literature_review.html) similarly emphasizes synthesis and analysis. These are writing recommendations, not detector findings. For an academic review, replacing repeated relevance announcements with actual comparisons is a better-supported editorial choice than manufacturing a statistical writing fingerprint.

## How to use the evidence

1. Check which product and version a claim describes.
2. Separate a provider's performance claim from an independent benchmark.
3. Distinguish group-level tendencies from conclusions about one document.
4. Judge an edit by fidelity, clarity, voice, and the requirements of the genre.
5. Report a real test only if performed, with its actual scope and result.

The paired examples in `worked-examples.md` are editing demonstrations unless explicitly identified as dated source excerpts. The edited versions were written by an AI assistant; calling them "human-written" would misstate their provenance.
