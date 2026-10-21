---
name: nominal-docs
description: Nominal's shared rules for writing docs and docstrings. Use when writing or editing any page in a docs site, a README, or a docstring in a Nominal repo.
---

# Nominal docs

- These are shared rules for all Nominal developer-facing docs.
- Each repo's `README.md` or `AGENTS.md` gives its folders, build commands and layout. Read it too.
- Docstrings: read the file for the language.
  - Python: [python.md](python.md)

## Contents

- [Structure](#structure)
  - [Guides](#guides)
  - [Examples](#examples)
  - [Reference](#reference)
- [Style](#style)
  - [General](#general)
  - [Accuracy and confidentiality](#accuracy-and-confidentiality)
  - [Audience](#audience)
  - [What to include](#what-to-include)
  - [Say the thing](#say-the-thing)
  - [Examples and code](#examples-and-code)
  - [Clear references](#clear-references)
  - [Lists and punctuation](#lists-and-punctuation)
  - [Links](#links)
  - [UI instructions](#ui-instructions)
  - [Terms](#terms)
  - [Files](#files)
  - [Visual](#visual)

## Structure

Most repos split docs into three types. Folders and names differ per project.

- Keep each page to one type.
- Link to another type rather than repeating it.

### Guides

- For: user doing a task with the product.
- Covers: how to get a task done, along the common path.
- Format: MyST Markdown pages

### Examples

- For: users looking for examples
- Covers: use-case driven examples that users can clone and modify or copy code from.
- Format: .py file, myst markdown, or Jupyter notebooks. Executable notebooks are preferred, as they are both user-friendly and testable.

### Reference

- For: a user looking up a specific class, function, field or limit.
- Covers: a library from an API perspective. 
- Format: mostly generated from docstrings, layout controlled with myst markdown+sphinx. 

## Style

### General

- Explain things concisely and clearly.
- Use short sentences, with one idea in each.
- Use the active voice and the present tense. Address the reader as "you".
- Do not re-explain things that are explained in another doc. Link to it instead.
- When mixing narration with code, use comments to explain the code as much as possible. Inline if they fit, otherwise above the code block.

### Accuracy and confidentiality

- Public repos are public, including `%` comments. Never include customer information.
- Accuracy is the top priority. Accurate doesn't mean complete.
- Say only what a source backs. Check claims against code, changelogs or an engineer.
- Frequency claims ("common", "usually") need evidence such as tickets, or stay out.
- Don't name private backend or frontend repos, the database, or other private stack details. Say "the underlying data store".
- Libraries a public client imports are public. Name them where the reader needs them, such as in imports.

### Audience

- The audience is developers and test engineers using Nominal, or likely future ones.
- They know their language and tools. Explain only what is specific to Nominal.
- Assume readers are new to Nominal. On advanced pages, link to introductory content.
- Describe the customer's application, not Nominal internals. A passed check means the check passed, not that the test plan did.

### What to include

- Include a sentence only if the reader acts on it or needs it for the next step.
- Give the instruction, not the mechanism behind it.
- Exact rules and rare edge cases go in reference pages or error messages.
- Too much detail at once overwhelms. Leaving out common failure modes frustrates. Balance the two.
- Match page length to the task. No filler sections, recaps or stacked caveats.
- Assume widely used standards. Write "ISO 8601", don't explain it.
- Nominal limitations that may change: show what works ("this example exports format X"), not the limit ("Nominal only supports X").
- Limits set by outside standards or protocols: state them plainly, with the workaround.
- Embed a small concept rather than make the reader switch pages.

### Say the thing

- Don't announce. Delete a sentence that only says the next one is worth reading ("Let's take a look:").
- Don't describe the page. Readers can see its structure.
- The lead paragraph (`{.lead}`) says what the subject does and what it needs, in one or two sentences. It doesn't list the sections.
- Don't sell. State what the code does, not how good it is: no "seamless", "powerful", "easy", "simply" or "just".
- Don't grade sources ("the client docs explain this well"). Link or quote them.
- Cut empty openers: "note that", "it is worth noting", "in fact", "of course", "interestingly", "importantly", "the key insight is".
- No rhetorical shape: no triples for rhythm, no one-line paragraph for effect, no metaphor where a plain name exists.
- To test a sentence, delete it and reread the paragraph. If nothing is lost, leave it out.

### Examples and code

- Lead each section with what the feature is for. Make the example show exactly that.
- Use values a reader would really use.
- Leave out filters, options and placeholders the point doesn't need. Don't invent filters.
- To show syntax, use placeholders (`WHERE name = <channel name>`), not made-up literals.
- Examples under about 30 lines follow these rules strictly. Full applications can relax them.

### Clear references

- Every "this", "that" and "it" must be clear to the reader.
- Referring back to an earlier section is fine ("the tags section above").
- Referring back to a specific item far away is not ("the query two pages up").
- "Also counts" and similar work only in the same sentence as the thing they point to.
- Better: explain it with the original item, unless that makes it too dense.

### Lists and punctuation

- Explain in prose. Open sections with sentences, not a list.
- Numbered lists for steps.
- Bullets only for short, parallel items a reader scans.
- Separate facts looked up on their own stay a list, one point per item.
- Items that depend on each other, or form one explanation, become prose.
- A long item is a reason to trim it, not to drop the list.
- Use semicolons rarely. Use one only when it reads faster than two sentences.

### Links

- Link wherever it helps, even if the page already links there.
- Don't link the same place in every paragraph.

### UI instructions

- Write UI labels exactly as on screen, checked against the source. For example, **CONFIRM & INGEST**.
- Name screen elements by their on-screen labels, not code names.
- No label? Use the common term: "sidebar", not "rail".

### Terms

- Use one term for one concept, every time. Don't swap in a synonym to make a paragraph read better.
- Use the names Nominal uses: asset, dataset, channel, workbook, profile. Where this is ambiguous (physical asset vs nominal asset) use a qualifier like "nominal asset" or "metadata asset" consistently. Only use this qualifier when it is actually ambiguous.
- "REST API" or "gRPC API", never bare "API". The SDKs are APIs too.
- UI labels keep their own wording: "API key", the **API keys** page.
- Graphical interface: "user interface" or "UI". Command line: "CLI", "command line interface" or "terminal interface".
- Product: "Nominal" or "the Nominal platform", not "Nominal Core".
- "Nominal for Developers" is only the client-access product without the UI. Use "Nominal" for anything the whole platform does.
- Don't use "load bearing" unless the topic is physical loads.

### Files

- No draft status in files, including comments ("pending rewrite").
- Some markers are intentional, such as `% SCREENSHOT:`. Ask before removing one.
- Provenance comments (`% Source: <commit>, <path>`) are fine if they don't name private repos.

### Visual

- Don't lower text contrast.
- Click targets are at least about 16 px square.

