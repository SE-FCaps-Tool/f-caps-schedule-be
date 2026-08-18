# Phase 07 — Cutover: remove old Docker backend and old database

Run only after Phase 06 passes and the owner has confirmed the destructive cutover. Preserve W:\f-caps-schedule-be-artifacts\db\source-20260818.dump and its checksum first.

1. Stop and remove only the old backend services from the old Compose project: api, worker and postgres. Do not delete source files. The old web container is not part of the new backend and may be stopped separately if it is no longer needed.
2. Verify old containers are absent and target containers use different IDs/volume.
3. Remove the old Docker volume capstonedefensescheduler_postgres_data only after target read-only parity has been captured and the external dump is readable.
4. Start target BE on its canonical host ports if desired; otherwise keep the temporary external override. Validate /health and Alembic current again.
5. Record the cutover evidence and leave the target volume as the only active local scheduler database.

Rollback before deleting the old volume: stop target, restart old Compose backend from the retained source volume. Rollback after deleting the old volume is restore-only from the retained dump into a fresh volume; this is why the dump and checksum are mandatory.

Never delete the source repository. Do not use docker compose down -v on the old project as a shortcut because it can remove unintended volumes.
