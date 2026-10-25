# Commercial detector methods and open reconstruction

Checked October 25, 2026. Recheck version-sensitive claims before use. This reference
supports method research, not a promise that edited writing will receive any score.

## Sources that change the analysis

- **Turnitin:** the [August 2024 white paper, pp. 7–8](https://www.buffalo.edu/content/www/lms/guides-instructors/integrations/turnitin/_jcr_content/root/maincontent/par/download/file.res/Turnitin%E2%80%99s%20AI%20Writing%20Detection%20Model%20Architecture%20and%20Testing%20Protocol.pdf)
  discloses transformer window classification and weighted sentence aggregation.
  It is historical, not a full current specification. The [current guide](https://guides.turnitin.com/hc/en-us/articles/22774058814093-Using-the-AI-Writing-Report)
  defines the percentage as a share of qualifying prose, independent of similarity.
- **Pangram:** [4's model card](https://www.pangram.com/research/model-card/pangram-4)
  describes a shared backbone, prediction heads and sequence decoding. [4.1](https://www.pangram.com/research/model-card/pangram-4-1)
  retains training/inference and adds class probabilities. Do not infer private parameters.
- **Originality.ai:** its [method article](https://originality.ai/blog/how-does-ai-content-detection-work)
  concerns an earlier model. [5.0's announcement](https://originality.ai/blog/introducing-originality-5-0-and-max)
  changes scores from confidence to estimated text composition. Do not transfer old semantics.
- **Sapling:** the [API reference](https://sapling.ai/docs/api/detector/)
  separates document confidence from character-weighted `ai_fraction`, derived from
  sentence scores. October 2026 changed sentence scoring. Record the returned version.
- **Copyleaks:** [responses](https://docs.copyleaks.com/reference/data-types/ai-detector/ai-text-detector-response/)
  expose versions and section classifications; deprecated fields may persist in examples.
  The [sandbox](https://docs.copyleaks.com/guides/ai-detector/ai-text-detection/) returns mocks, not real predictions.
- **Binoculars:** the [authors' open code](https://github.com/ahans30/Binoculars)
  permits actual algorithm inspection. `metrics.py` returns log-loss quantities without
  exponentiation; `detector.py` divides them and uses model-specific thresholds.

## Research discipline

Distinguish reconstruction of a published reporting rule, inspection of an open algorithm,
controlled observation of a closed service, and recovery of private model parameters.
Success at one does not establish the others. Synthetic arithmetic examples are not
detector evaluations. State which components remain supplied or assumed.

Sentence highlights depend on context and processing. They do not identify independent
phrase weights. No source above supplies a universal blacklist. A single before/after
score cannot isolate a causal feature or establish transfer to other detectors.

For authorized empirical research, fix the version/settings, retain exact inputs and raw
outputs, repeat unchanged controls, vary one defined property and reserve unseen examples
for evaluation. Report false positives and false negatives alongside any detection rate.
Do not substitute provider benchmarks for a test on the user's exact document.
