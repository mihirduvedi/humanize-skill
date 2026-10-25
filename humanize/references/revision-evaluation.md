# Improve the skill through evidence, not a score-chasing loop

Use when the user requests sustained improvement, experiments or training. Ordinary
rewriting needs the editing workflow, not a benchmark project. A skill is a set of
instructions and examples; changing it does not fine-tune the assistant's model weights.

## Keep provenance, quality and detection separate

For every example, record its source, audience, supplied facts, protected quotations and
desired editorial change. Mark an assistant-generated revision as assistant-generated,
even if a detector calls it human. Label real source writing by its documented provenance,
not a score. Never add a generated rewrite to a human training class because it passed.

An edit can improve clarity while raising a detector score. A lower score can also follow
from deleting essential qualifications, writing errors or changing the meaning. Therefore
check the text itself before interpreting the detector result.

## A bounded improvement cycle

1. Diagnose one recurring failure from actual feedback, such as a detached explanation
   or a paragraph that repeatedly announces why its evidence matters.
2. Add the smallest instruction and a few contrastive examples that resolve that failure.
   Include a case where the proposed edit would be wrong, so the rule has a boundary.
3. Freeze a different set of cases before evaluating. Group variants of the same source
   together, and keep some genres or source groups outside development.
4. Generate revisions using the updated instructions, then review fidelity, logical
   connections, register and flow. Retain exact quotes and locators; count preservation
   alone cannot establish factual or semantic fidelity.
   Check that a smoother connection has not supplied a missing premise: "not randomly
   assigned" does not establish that participants volunteered, for example. Preserve all
   punctuation inside protected strings rather than silently adapting it to the new sentence.
5. If detector testing is authorized and available, save the exact input hash, product or
   checkpoint, settings, threshold, date, raw output and unedited control. Repeated queries
   to the same passage are development feedback, not fresh independent validation.
6. Record improvements, regressions and unchanged cases. Promote a change when its
   editorial benefit survives counterexamples and new cases; describe any detector gain
   only within the tests that support it. Stop when acceptance criteria are met.

Do not rewrite a protected assignment, publish text, upload private drafts or start a
recurring automation merely because the user asks to improve the skill. Follow the
scope and authorization actually present in the conversation.

## Reader review rubric

| Check | What a useful revision does | Failure that blocks acceptance |
| --- | --- | --- |
| Meaning | Preserves the supplied claims and qualifications | Adds cause, certainty, facts, opinions or experience |
| Evidence | Keeps exact quotations, citations and locators intact | Smooths quoted wording or moves a citation onto a different claim |
| Connection | Chooses a conjunction that expresses a supported relationship | Uses "because" or "therefore" for an association |
| Sentence flow | Joins dependent explanations and cuts empty commentary | Makes every thought a short beat or joins everything into one chain |
| Register | Fits the writer, genre and reader | Adds forced slang, inflated diction or fake personality |
| Substance | Explains the distinction or implication directly | Keeps the same generic announcement under different synonyms |

For subjective review, hide which version is earlier if an independent reviewer is
available. State whether review was independent, self-reviewed or not performed; an
assistant cannot report its own judgment as a blind human preference study.

## Interpreting experimental results

Keep false positives and missed AI examples visible alongside aggregate accuracy. Hold
thresholds fixed for out-of-domain tests, and report each input length separately with
eligible sample counts. A document classifier does not automatically localize authorship
within a mixed paragraph. Test another independently trained model before claiming
transfer, and do not equate any historical open baseline with a current commercial service.

In the October 25, 2026 local HC3 experiment, connected-prose revisions changed scores in
opposite directions across two models: the word/character model decreased on seven of
twelve probes, increased on four and was unchanged on one; the surface model increased
on eleven and was unchanged on one. Both sides were assistant-generated, the probes
were short and constructed, and no commercial model was queried. These observations
support a narrower conclusion: the score response depended on the detector, so conjunction
use should follow meaning and reader flow rather than a presumed universal fingerprint.

The corresponding code, split design, raw metrics and reproducibility instructions are
in the portable repository's `research/` directory. These numbers are an experiment
record, not an ongoing promise or proof that the skill improved commercial pass rates.
