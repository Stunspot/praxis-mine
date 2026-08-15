# Source adapters

The v0.1 miner deliberately supports two acquisition forms:

1. Curated JSON manifests for web directories, repositories, papers, services, and manually researched candidates.
2. Read-only local directory scans that identify candidate skill or software roots and hash their visible files.

Use external search, browser, repository, or research tools to gather evidence, then normalize it into a manifest. This keeps acquisition replaceable: skills.sh, GitHub, a vendor catalog, a local archive, or a Firecrawl result can feed the same ledger without becoming the mine's architecture.

Before automating a new source, record:

- stable source key and locator;
- source kind and expected value;
- access method, authentication, and credential custody;
- terms, license, robots, and redistribution posture;
- rate limit and polite cadence;
- incremental cursor, hash, or date strategy;
- failure behavior and stop conditions;
- raw-evidence retention and deletion policy;
- estimated money, time, storage, and context cost.

Prefer official APIs, feeds, repository metadata, and local checkouts. Use hosted crawling only when measured acquisition failures justify its cost and custody tradeoff.
