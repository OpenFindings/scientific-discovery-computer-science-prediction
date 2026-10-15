# Artifact-only patch explanation protocol v1

## Frozen question

For the same automatically generated patch, does an accurate natural-language
explanation plus a concrete behavioral-difference example improve human review
of correct and defective patches compared with a patch-only presentation?

This protocol does not treat explanation quality, an LLM judge, or passing
developer tests as a human review outcome.

## Pilot boundary

The first local pilot is artifact-only. It checks material schemas, deterministic
condition construction, label separation, and whether the presentation object
omits gold labels. Built-in fixtures are synthetic engineering diagnostics and
must never be reported as participant observations.

The real-material gate requires a version-pinned Defects4J checkout, a supported
Java runtime, independently verified correct/plausible patch labels, and an
explanation factuality audit. A participant study would require separate
authorization and is out of scope here.

## Conditions and outcomes reserved for a future authorized study

- `patch_only`
- `patch_plus_explanation`

Primary outcome: accuracy in identifying correct versus defective patches.
Secondary outcomes: decision time, confidence calibration, false acceptance of
defective patches, and identification of the patch's behavioral impact.

The future study must randomize and blind condition presentation, stratify by
patch difficulty and reviewer experience, include an inaccurate/misleading
explanation condition only if separately justified, and predeclare mixed-effects
or paired analyses before collecting data.
