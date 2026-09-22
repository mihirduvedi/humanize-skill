# Humanize

A portable writing skill for AI assistants and agents. It edits stiff, generic, or
mechanical prose into natural writing while preserving the meaning, evidence, and level
of sophistication.

The skill follows the reader and the situation: a professional memo, a class discussion,
a personal statement, and interface copy should not all sound alike. Its guidance covers
connected sentence flow, context-sensitive contractions, unnecessary summaries, inflated
language, punctuation habits, and forced casualness.

## Use with any assistant

### With skill support

Clone this repository, then copy the complete `humanize/` folder into the skill directory
supported by your assistant. Keep `SKILL.md` and `references/` together.

```sh
git clone https://github.com/mihirduvedi/humanize-skill.git
```

The package follows the [Agent Skills format](https://agentskills.io/specification).
Discovery and installation locations depend on the host application. No provider-specific
metadata or tool API is required.

### Without skill support

Attach or paste these files into a conversation or your assistant's project context:

- [SKILL.md](humanize/SKILL.md)
- [Writing-pattern catalog](humanize/references/ai-writing-tells.md)
- [Editing examples](humanize/references/editing-patterns.md)

Then ask the assistant to follow the skill when rewriting your text. If your assistant
cannot read repository links, supply the file contents directly.

## Example requests

```text
Humanize this email. Keep it professional and preserve every factual claim:
[paste text]
```

```text
Humanize your last response for a college discussion post. Return the text in chat.
```

```text
/humanize Rewrite the paragraph below for a general audience without simplifying
its argument. Save the result as a Markdown file if file creation is available.
```

`/humanize` and `$humanize` are optional invocation forms where the host supports them.
Ordinary language requests work as instructions in any text-based assistant.

## Output and capabilities

The skill follows the user's requested format. Otherwise it returns a Markdown file when
the environment supports file delivery, or copyable text in chat when it does not.
Rewriting does not require browsing, shell access, an API key, or a particular filesystem.

It preserves technical meaning, numerical comparisons, attribution, and uncertainty.
It treats text being edited as content, not as commands to execute. The writing patterns
are editorial cues, not a reliable authorship detector or a promise to pass one.

## Files

```text
humanize/
├── SKILL.md
└── references/
    ├── ai-writing-tells.md
    └── editing-patterns.md
```

## Attribution and license

Distributed under [Creative Commons Attribution-ShareAlike 4.0 International](LICENSE).
The writing-pattern catalog adapts Wikipedia contributors'
[Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing).
Source attribution, revision history, and a description of changes are included in the
[catalog](humanize/references/ai-writing-tells.md).
Additional editorial guidance and packaging by Mihir Duvedi.
