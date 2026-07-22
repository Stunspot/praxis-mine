# Praxis Mine: quick start

Use this path to reach a first result without confusing a valid package with an installed or healthy host integration.

## Procedure

1. Extract the canonical release ZIP into a new directory.
2. Open a terminal in that extracted release directory and run:

   ```text
   python tools/verify_release.py .
   ```

3. Continue only when the verifier returns `"ok": true` with no findings.
4. Choose one host and complete the [Codex installation](INSTALL-CODEX.md) or [Claude installation](INSTALL-CLAUDE.md).
5. Start a fresh task or chat after the host reloads the package.
6. Begin with this family starter prompt:

   > Assess this outside skill and steal only the good bits.

7. Supply the context named under [Choose the skill](#choose-the-skill). For consequential work, review the [boundaries](LIMITATIONS.md) first.
8. Confirm the expected skill is discoverable and that the response addresses the named job. Record discovery and invocation separately; neither is proved by the ZIP.

## Choose the skill

### praxis-mine

Use when: Use for evidence-bounded assessment of outside skills/praxis; discovery is not adoption or installation.

Bring this context when available:

- what mining evaluates
- candidate dispositions and their meaning
- evidence/cost/risk/overlap report
- why discovery and adoption differ

## If first value does not appear

1. Re-run the static verifier.
2. Confirm the installed family version is `0.1.0` and no stale duplicate is being selected.
3. Invoke the intended handle by name once to distinguish a routing problem from an installation problem.
4. Follow [support and recovery](SUPPORT.md) with the requested evidence bundle.
