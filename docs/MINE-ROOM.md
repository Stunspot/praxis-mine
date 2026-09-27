# Rediscover and compare useful mechanisms

Open Praxis Mine to survey what you have mined, recover why a mechanism mattered, or choose the next experiment. **Blackglass — Crimson** presents an extraction gallery grouped by source. **SNAPFRAME** traces a source through its findings to recorded judgments and next tests. Both open the full evidence in a focused reader and keep a comparison bench available across the collection.

## Open your collection

Extract the complete customer ZIP. With Python 3.11 or newer available, double-click **Open.cmd** on Windows. On macOS, run `python3 codex/praxis-mine/skills/praxis-mine/workspace/open.py` from the extracted folder; **Open.command** runs the same action after `chmod +x Open.command`. Standalone skill packages include their own launchers.

The launcher confirms the matching local service, reconnects an existing instance, finds a free loopback port after a collision, and starts again after reboot. The room uses `PRAXIS_MINE_DATA_HOME` when set, otherwise `.praxis-mine/data` in your user folder. **Local ledger** reveals the active location. Your agent uses the same SQLite store through `scripts/praxis_mine.py`.

If earlier work is missing, confirm its data location before recording it again. Launch with `--data-root "your folder"` to open an existing native data home; the CLI calls this option `--data-home`. Opening the original data home retains its full recorded history. **Import native manifest** brings source and candidate content into the selected collection and creates new run records; it does not import evaluations, revision histories, or existing runs. The package contains no private research history and does not silently import another collection.

## Choose how to explore

Use **Environment** to choose between two presentations of the same records. The browser remembers your choice. Preferences from the retired environments reset to Blackglass — Crimson.

**Blackglass — Crimson** uses near-black glass, neutral illuminated rims, soft shadows, and clean red interaction signals. Its **Extraction gallery** groups findings beneath their actual source. Each card exposes the useful mechanism and the next recorded test before you open it. The filter deck stays beside the gallery on wide screens; the gallery uses the remaining width instead of reserving space for an always-open dossier. Registered sources without findings remain available as source records.

**SNAPFRAME** uses precise decision nodes and branching circuit lines on a dark field. In **Evidence circuit**, choose a source from the horizontal source rail. The circuit connects that recorded source to its findings and each finding's latest native evaluation and next test. Select a source, mechanism, or judgment node to read the corresponding native record. A registered source with no findings has an explicit empty state; no relationship is invented to complete a diagram.

A finding without a native evaluation can still contain source evidence or an earlier recorded disposition. The circuit states the missing evaluation separately. Its latest-judgment view is an overview; the reader preserves the complete evaluation history.

## Narrow the collection and follow its history

Use **Find a mechanism or source**, then select a recorded disposition to narrow the results. Dispositions are categories, not stages every finding must pass through. On small screens, **Filter collection** expands the disposition and order controls; search and view selection stay visible. **Order** sorts recent activity, earliest activity, or titles. The count shows how many findings match. **Show the whole collection** clears an empty search result and its filters.

Choose **Activity trail** to browse dated sources, findings, runs, and evaluations. Its **Show** control can focus on one record kind. Open an event to inspect it, then return to **Extraction gallery** or **Evidence circuit**. **Refresh** retrieves changes made by your agent or another window.

## Read a finding without losing the collection

Select a card or circuit node to open the reader. It brings the mechanism, source, recorded evidence, risks, judgments, and next falsifiable test into focus. Source links and **Recorded connections** follow native keys. They are recorded relationships, not endorsements.

Use **Previous** and **Next** to move between findings in the current filtered collection. **Back to collection**, **Close finding**, or Escape closes the reader. Selection is retained so you can resume at the same finding. On wide screens, the reading content can spread into columns; on smaller screens it stacks.

Open **Revision history** for preserved native versions. **Inspect complete native record** exposes the full record and provenance. An absent evaluation is stated explicitly. Priority scores guide attention; they do not establish fitness or authorize adoption.

## Compare two or three findings

Use **+ To bench** on a gallery card or **+ Compare** in a circuit or reader. The fixed comparison bench keeps the selected findings visible while you explore. Add at least two, then select **Compare**. The comparison aligns mechanism, capability delta, next falsifiable test, why you cared, possible use, evidence state, evidence, costs and risks, and source. Missing material reads **Not recorded**.

Remove a finding with its bench chip or **Remove** in the comparison. The bench holds at most three findings. **Close comparison** or Escape returns to the collection. Selected findings and bench choices are remembered in this browser for the active ledger; they do not alter recorded judgments.

## Record, revise, and hand off

**Ledger tools** contains **Record source**, **Record candidate**, **Import native manifest**, **Export ledger**, and **Export report**. Begin with a source so each finding has provenance. Record its locator and access posture, then the mechanism, why you cared, applicability, and project connection. These are native candidate tags available to your agent.

**Edit record** updates a source, run, or candidate. **Save record** checks the expected revision inside a SQLite transaction. If another editor changed it, preserve your draft, close the editor, reopen the current record, and reconcile before saving again. Unknown native fields remain intact. A candidate's source identity stays fixed to preserve its recorded relationship.

**Record evaluation** uses the native scoring and disposition gate. Enter the capability delta, evidence, next test, benefit scores, and risks. Editing cannot bypass this gate or silently select `adopt`. An evaluation is superseded by a new evaluation rather than overwritten.

**Project handoff** downloads the finding and native ledger pointer. It neither installs nor executes the candidate. **Export ledger** downloads versioned JSONL with records, relations, events, and audit rows; **Export report** downloads the Markdown report. Back up the separate data home. Updating application files does not reset it.

## Import and recovery

Manifest import retains uploaded bytes in `.workspace/imports` inside the data home and checks source references before import. An unexpected storage failure can leave a partial run because the established importer commits individual records. Inspect the ledger before retrying.

If the room cannot load, use **Refresh**. Reopen through the launcher if its session expired. If launch fails, run the same command with `--serve` to see the error. The room binds only to `127.0.0.1`, requires its launch token, and rejects foreign Host and Origin access. Keep the tokenised Open URL private.

The workspace has no cloud dependency and does not browse or execute candidates. Arm's Reach remains dormant. Desktop shortcuts require your request. macOS launchers are supplied; native macOS execution has not been verified.
