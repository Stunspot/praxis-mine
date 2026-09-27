# Install Praxis Mine in Claude

Use this path for a Claude environment that supports custom Skills.

## What you need

- `claude/praxis-mine-v1.2.0.zip` inside the supplied complete customer kit;
- permission to upload a custom Skill;
- a Claude product and workspace where custom Skills are available.

## Install

1. Keep the Claude ZIP unchanged. Do not unpack, merge, or recompress it.
2. Open Claude's current Skills manager or custom-Skill import control.
3. Upload `praxis-mine-v1.2.0.zip`.
4. Confirm the host reports the Skill imported or enabled.
5. Start a fresh chat.
6. Ask:

   > Use Praxis Mine to assess this outside skill and steal only the good bits.

7. Supply a public link, an uploaded candidate folder, or a concise description of the candidate and your current baseline.

## Expected result

Claude should identify the capability gap, preserve evidence and unknowns, choose a bounded disposition, and name a falsifiable next test. An accepted upload proves only import. A listed Skill proves discovery. The first useful assessment proves one representative behavior under that exact host and conversation.

## Use the local visual explorer

The complete kit also contains a local desktop explorer. On a computer with Python 3.11 or newer, use its `Open.cmd` or `Open.command` launcher and follow the [mine-room guide](MINE-ROOM.md). Importing the Claude Skill does not establish that a hosted Claude environment can launch this local browser workspace or access your desktop ledger.

## If upload is unavailable

The current account, product, or workspace may not expose custom Skills. The package is still statically valid, but it is not installed in that host. Do not “repair” the ZIP to work around a missing product control.

## If upload is rejected

From the extracted complete-kit root, run `python tools/verify_release.py . --component-only` to check the embedded archives against the included manifests and hashes. If verification fails, get a fresh complete ZIP from the product’s Additional Files. If verification passes and the host still rejects the Skill, preserve the host error and follow [Troubleshooting](TROUBLESHOOTING.md#claude-rejects-the-skill-zip).
