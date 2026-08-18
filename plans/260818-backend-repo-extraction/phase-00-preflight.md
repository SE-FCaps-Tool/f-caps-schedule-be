# Phase 00 — Preflight, inventory và source snapshot

1. Xác nhận source/target paths; target chưa chứa backend copy nhầm.
2. Kiểm tra source Compose, postgres readiness và volume capstonedefensescheduler_postgres_data.
3. Tạo W:\f-caps-schedule-be-artifacts\source-backend-inventory.json và source-backend-hashes.json ngoài target. Inventory phân loại copy, exclude-fe, generated-not-copy.
4. Ghi W:\f-caps-schedule-be-artifacts\source-db-baseline.json bằng read-only queries.
5. Tạo custom dump trong source container, copy ra W:\f-caps-schedule-be-artifacts\db\source-20260818.dump, chạy pg_restore --list để validate, rồi xóa temporary dump trong source container. Mỗi lệnh phải kiểm tra container ID và exit code. Sau docker cp, tính SHA256 dump trên host và so với sha256sum của file trong source container trước khi xóa; mismatch là abort.

Expected: source healthy, exact baseline, readable custom archive, source unchanged.
Abort: health/baseline/hash/dump failure, empty ID hoặc source mutation.
