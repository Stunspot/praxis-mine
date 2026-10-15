# Rebuild Praxis Mine 1.3.0

Use Python 3.11 or later from this repository. The current constructor is `tools/build_purpose_release.py`; earlier builder scripts and release directories retain their historical versions.

Supply the accepted previous complete kit with `python -B tools/build_purpose_release.py --baseline "path-to-prior-complete-kit.zip" --suffix=-rebuild-check`. The exact required SHA-256 is `8b68272a0d8a8a96921d949929e05348438df1ac772a81adf74cdb788d800d60`. On the canonical owner checkout the default baseline is `release-candidates/current-v1.2.1/Praxis-Mine-v1.2.1.zip`. Keep that original kit unchanged; it supplies retained guides and historical proof while the constructor replaces all active runtime mirrors from `source/plugin/skills/praxis-mine` and uses current delivery companions. No network service is needed during construction.

The builder writes a new `release-candidates/purpose-v1.3.0-rebuild-check` candidate, refreshes the current `release-v1.3.0` assembly and current delivery ZIP, and checks the complete manifest plus the nested Claude archive against the actual runtime. Existing other candidate directories remain preserved. Use a unique suffix to retain another build.

Behavioral acceptance covers ordinary task input, saved return, material handling where useful and writable storage recovery; it does not establish audience outcomes or fresh macOS execution. Current raw outcomes are retained under `verification/purpose-release-20261015/` in this checkpoint.
