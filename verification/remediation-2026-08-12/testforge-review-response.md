# TestForge adversarial verification receipt

REVIEW_KIND: TESTFORGE_ADVERSARIAL

REVIEWED_CANDIDATE: 652cf4cddf72ef9f616fe02720dade53f9dac270

DOCUMENTATION_FINGERPRINT: 3156678139da35ba703ed716ebf81c3ba7f1bc30e6850baaef28236b6f6b235b

CLAIM_UNDER_TEST: The frozen local candidate is a coherent, evidence-bounded public-documentation and presentation remediation expected to pass a controlled publication transition. This receipt does not claim that the candidate is published or live.

## Evidence examined

- All 27 declared customer documents and the current documentation manifest.
- Canonical Praxis Mine skill, evaluator, vendored storage implementation, metadata, and integration tests.
- Current Pages layout, stylesheet, navigation, recovery route, Open Graph wiring, and deterministic image builder.
- Direct pixel-inspection receipt for the README hero, Pages hero, and social card, including exact dimensions and SHA-256 hashes.
- Hesperos fresh-context content review bound to candidate and documentation fingerprint.
- Separate accessibility review bound to candidate and documentation fingerprint, with browser and assistive-technology conditions explicitly unexecuted.
- Plugin validation, skill validation, 3 integration tests, frozen release verifier, Hesperos lint, deterministic image regeneration, candidate-integrity check, UTF-8 and LF checks, and public-surface credential-pattern scan.
- Direct HTTP crawl of the currently deployed pre-remediation Pages site.
- Current GitHub repository, Pages, remote-head, and ruleset evidence.

## Adversarial probes

1. CLAIM DRIFT: PASS. The docs distinguish packaged, installed, discoverable, invoked, ledger-healthy, first value, published, and directory-published. No candidate text claims live publication or host behavior that was not executed.
2. CUSTOMER JOURNEY: PASS. Orientation, both supported host paths, install verification, first value, workflows, inputs and outputs, ledger configuration, troubleshooting, update/removal/data cleanup, privacy/network/security, limitations, provenance, support, contribution, license, and terms are present and substantively reviewed.
3. SOURCE RECONCILIATION: PASS. Local-only storage, optional Python ledger, revision history, backup integrity verification, restore-as-new-store behavior, JSONL export, non-overwrite behavior, and the absence of automatic adoption reconcile with the inspected implementation and tests.
4. VISUAL SET: PASS WITH DIRECT PIXEL EVIDENCE. Three different files, dimensions, aspect ratios, and compositions were opened and inspected. The social card visibly contains the exact product title and identifying line. Wiring resolves to the intended surfaces in source.
5. PAGES PRESENTATION: PASS LOCALLY. The current source has semantic landmarks, skip navigation, labelled navigation, visible focus, strong measured contrast, responsive layout, horizontally scrollable code and data tables, reduced-motion handling, a custom recovery page, accurate Open Graph metadata, and useful primary navigation.
6. SCOPE AND CUSTODY: PASS. The candidate diff is exactly allowlisted. Frozen release-v0.1.0 and release-v1.0.0 trees are unchanged. No unrelated work is staged in the governed candidate.
7. DETERMINISTIC EVIDENCE: PASS. Plugin and skill validators pass under explicit UTF-8 mode; all 3 integration tests pass; the frozen release verifier reports ok with zero findings; the history and nested-archive pattern scan reports zero findings; image regeneration reproduces exact hashes.
8. REVIEW BINDING: PASS. The final Hesperos and accessibility receipts name candidate 652cf4cddf72ef9f616fe02720dade53f9dac270 and fingerprint 3156678139da35ba703ed716ebf81c3ba7f1bc30e6850baaef28236b6f6b235b. The earlier Hesperos receipt is marked superseded and the accessibility receipt that overstated browser evidence is marked rejected.
9. LIVE CLAIM: NOT ESTABLISHED. Remote main remains a744734e3481382e01415b19c29551d1527e259c. The deployed site still serves the old visual set and generic GitHub 404. The candidate has not been rendered live.
10. PUBLICATION CONTROL: BLOCKED EXTERNALLY. Active GitHub ruleset 20249478 requires line-ending-policy. The workflow is manual-only to avoid consuming unavailable hosted Actions minutes, and no current required-check result can be produced. No authority to disable the ruleset has been granted.

## Material findings

No unresolved material defect was found in the frozen local candidate.

## Residual risks

- The final candidate is not published and has not been inspected in its deployed rendered form.
- GitHub-hosted Actions capacity is unavailable by user report; the required line-ending-policy status cannot be generated.
- Browser interaction, keyboard traversal, screen reader, zoom, localization, representative-user, fresh-host installation, host discovery, natural-language invocation, and customer outcomes remain unexecuted.
- The public-surface scan is a bounded pattern scan, not proof that no sensitive information exists.
- Legal and security documents are product guidance, not professional certification.

## Publication gate

Do not call this repository PASS until all of the following occur:

1. Obtain explicit authority for the exact ruleset transition or restore hosted-check capacity.
2. Publish the final evidence commit to main without triggering unavailable automatic Actions.
3. Verify the ruleset is restored unchanged if it was temporarily disabled.
4. Confirm remote main equals the final commit.
5. Wait for the Pages deployment to rebuild.
6. Crawl every rendered route and navigation target, verify the custom 404, and check all links.
7. Open and inspect the live README hero, live Pages hero, and live social card.
8. Confirm live Open Graph metadata uses the exact new social-card URL, dimensions, type, title, and alt text.
9. Recompute the final documentation fingerprint and confirm it remains unchanged.

DISPOSITION: READY_WITH_RESIDUAL_RISK