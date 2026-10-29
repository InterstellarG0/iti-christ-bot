# Improvement Loop, Christ Bot and every ITI project

This is the loop used for the v1.2.8 Send freeze fix and the v1.2.9 Mary
cross-topic, written down so the next change follows the same path. It
applies to every project, not only Christ Bot. One loop, one change, one
version. No change is called verified unless its tests actually ran, and
no change is called fixed on a phone until Anthony tests it there.

## The loop

1. **Report.** Record the exact words, the exact link or file, the device
   and browser, and the version shown. A report without a version is a
   guess. Do not patch the wrong build. The hosted static build, the
   single-file phone build, the Python desktop build, and the local
   server web UI are different code paths. Name which one froze, failed,
   or misbehaved.
2. **Reproduce.** Reproduce the exact conversation or steps before
   claiming a fix. Run the real code path, in code checks and on a real
   device where the failure happened. If it cannot be reproduced, say so
   and instrument it, do not guess a cause.
3. **Verify against the source.** Check every cited passage, number,
   date, and link against the actual source text: the corpus file for
   Scripture, a named translation for another scripture, the live page
   for a live check. Every claim carries source, passage or locator,
   tradition, and confidence. Counts, dates, and feast lists that differ
   between sources are reported as differing, never certified as one
   number.
4. **Diagnose the narrowest cause.** Name one cause, with evidence. A
   GPT conversation, a summary, or a similar case is a lead, not a
   diagnosis. Check it against the actual files before applying it.
   Claims that do not match the build are not treated as defects in
   that build.
5. **Fix one change.** Apply the smallest fix that removes the cause.
   Keep guardrails intact: Scripture only from the corpus, text separate
   from interpretation, no invented passages, no coercion, no false
   privacy claims. A fix that changes wording, topics, or features is a
   different change and gets its own loop.
6. **Test.** Rerun the full regression set, add one test that proves the
   fix and would have caught the bug, and test the real device or browser
   where it failed. Record what ran, what passed, and what is still
   untested. A builder check is not user confirmation.
7. **Release.** Bump the version in every file that names it, write the
   change in the README with what was checked and what is still open,
   rebuild the deliverable, and verify a fresh extract. Keep the last
   known-good version intact. Hosted and public links update only on
   Anthony's explicit approval, and the version the link actually serves
   is named with every link.
8. **Monitor and learn.** The loop closes only on Anthony's
   confirmation, never on silence. Record the lesson in memory and in
   AGENTS.md where it changes how work is done, and carry the next open
   item into the next loop with its evidence attached.

## Graph, in words

Report -> Reproduce -> Verify against source -> Diagnose narrowest cause
-> Fix one change -> Test -> Release -> Monitor and learn -> back to
Report for the next item.

Branches: a test failure goes back to Diagnose, never forward to
Release. A blocked step stops fully, with one clear in-person step for
Anthony, and resumes only on his word. A new idea found during a loop
goes into the next loop, it does not expand the current one.

## Evidence ledger, for every loop

- Version before, version after.
- Exact report, with link, device, and version shown.
- Source checks, with file names and locators.
- Cause, with the file and line or measurement that proves it.
- Fix, with files changed.
- Tests run, with counts and the one new test.
- What is still untested or unresolved, stated plainly.
- Who confirmed it, and when.

## Christ Bot examples

- v1.2.8: report was a phone Send freeze on the hosted link. Reproduction
  in Node showed a per-reply scan of 40,236 verses. Verification was
  against the phone template, not the server web UI, so the server
  timeout claim was not applied to the static build. Fix was a topic
  index built once plus a Send busy guard. Tests were 30 Python tests
  plus Node conversation and benchmark checks. Release kept v1.2.7 as
  known-good. Anthony confirmed it works on 2026-10-29.
- v1.2.9: report was a question with no answer, Mary in the Quran.
  Verification checked every Ethiopian passage in the corpus file and
  every Quran locator against Sahih International on Quran.com. Fix was
  one new special topic, mirroring the evidence topic, with source and
  confidence labels. Tests 31 and 32 prove the passage, the labels, the
  absence of Quran quotation, and that every locator is retrievable.

## Rules that do not change

- Never use horizontal rules or em dashes in chat replies.
- Outbound messages and public shares only with Anthony's approval.
- X posts are drafts only. Anthony posts on X himself.
- Keep the last known-good build. Never call a build verified unless
  its tests actually ran.
- A failed or blocked check does not prove something does not exist.
- When Anthony says stop, stop fully. When he returns, just work.
