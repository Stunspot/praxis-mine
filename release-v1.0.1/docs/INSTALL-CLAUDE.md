# Install Praxis Mine in Claude

Use this path for a Claude environment that supports custom Skills.

## What you need

- `claude/praxis-mine-v1.0.1.zip` from the complete customer kit or GitHub release;
- permission to upload a custom Skill;
- a Claude product and workspace where custom Skills are available.

## Install

1. Keep the Claude ZIP unchanged. Do not unpack, merge, or recompress it.
2. Open Claude's current Skills manager or custom-Skill import control.
3. Upload `praxis-mine-v1.0.1.zip`.
4. Confirm the host reports the Skill imported or enabled.
5. Start a fresh chat.
6. Ask:

   > Use Praxis Mine to assess this outside skill and steal only the good bits.

7. Supply a public link, an uploaded candidate folder, or a concise description of the candidate and your current baseline.

## Expected result

Claude should identify the capability gap, preserve evidence and unknowns, choose a bounded disposition, and name a falsifiable next test. An accepted upload proves only import. A listed Skill proves discovery. The first useful assessment proves one representative behavior under that exact host and conversation.

## If upload is unavailable

The current account, product, or workspace may not expose custom Skills. The package is still statically valid, but it is not installed in that host. Do not “repair” the ZIP to work around a missing product control.

## If upload is rejected

Compare the file hash with the detached `archive-custody.json` release asset.
Download a fresh copy when it differs. If the hash matches, preserve the host
error and follow [Troubleshooting](TROUBLESHOOTING.md#claude-rejects-the-skill-zip).
