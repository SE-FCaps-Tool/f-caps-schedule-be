# Phase 01 — Copy exact backend artifacts

Copy all allowlisted files byte-for-byte, preserving paths, including workbook. Không copy source .git, FE paths, generated caches, secrets hoặc local environments.

Verification:
- path inventory target có apps/api, apps/worker, tools, infra/docker/api.Dockerfile, docs, plans, specs, metadata và workbook;
- SHA256 hashes khớp source allowlist;
- FE source/FE Dockerfile không tồn tại;
- docs/plans có thể giữ text FE vì đây không phải runtime coupling.

Abort on any unapproved rewrite, missing artifact, copied FE artifact hoặc workbook bị thiếu.
