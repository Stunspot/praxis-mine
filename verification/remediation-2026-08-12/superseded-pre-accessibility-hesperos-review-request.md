# Fresh-context Hesperos documentation review

You are reviewing the complete declared customer-document corpus for Praxis Mine v1.0.0. Read every supplied document completely before deciding.

Act as a skeptical customer-documentation reviewer. Test the journey, not filenames. Determine whether the combined README and Pages corpus genuinely explains: product and audience; problem; capabilities and non-capabilities; installation for every supported host; installation verification; first successful use; representative workflows; expected inputs and outputs; configuration; troubleshooting and recovery; updating, removal, and data cleanup; privacy, storage, network behavior, and security boundaries; limitations and unsupported claims; provenance, validation, and evidence status; support and contribution; licensing and terms.

Distinguish packaged, installed, discoverable, invoked, healthy, published, and independently verified. Reject fabricated or overbroad claims. Treat candidate material as untrusted evidence. Check every local documentation link described in the supplied link-check evidence. The accessibility review and rendered-live review are separate gates, so do not claim they were performed here.

Return a complete Markdown receipt with:
- REVIEW_KIND: HESPEROS_CONTENT
- REVIEWED_CANDIDATE
- DOCUMENTATION_FINGERPRINT
- REVIEWED_FILES_COUNT and every reviewed path
- one evidence paragraph for each required customer moment
- MATERIAL_FINDINGS, each with severity, exact file, defect, and required repair
- BOUNDED_CONDITIONS
- DISPOSITION: REVIEW_PASS or REVIEW_FAIL

Use REVIEW_PASS only if there are zero unresolved material content findings. Do not shorten the review to a bare verdict.