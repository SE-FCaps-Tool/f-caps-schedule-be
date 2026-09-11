# Auto-Scheduling Algorithm — luồng tự động xếp lịch chấm cấp round

Phạm vi tài liệu: chỉ core CP-SAT solver + HTTP orchestration của round-level auto-scheduling
(`scheduler/scheduler.py`, `scheduler/candidates.py`, `scheduler/models.py`, `scheduler/validator.py`,
`domain/schedule_operations.py`, `routes/schedule_operations.py`, `routes/target_schedule_contract.py`).
Không cover council flow nội bộ (`services/councils.py`), room-assignment flow (xem
`docs/scheduling-flows/room-assignment.md`), hay manual-scheduling draft flow
(`manual_schedule_sessions`/`manual_scheduling.py`) — đó là 3 luồng khác, do agent khác phụ trách.

## 1. Tổng quan luồng

- **Mục đích:** với một round (đợt đánh giá) đã có group + project + timeslot + reviewer
  availability, tự động ghép **group → timeslot → tổ reviewer** bằng CP-SAT (OR-Tools), thỏa mọi
  ràng buộc cứng H1-H13, rồi persist thành một `ScheduleVersion` nháp (`DRAFT`) để Manager duyệt.
- **Khi nào chạy:** sau khi round setup xong — có ít nhất 1 group đã gán project với đúng 1 leader
  active, có ít nhất 1 timeslot active, và đủ reviewer (accepted invitation hoặc có availability
  record) theo `reviewer_count` cấu hình của round. Có thể chạy lại nhiều lần trên cùng round miễn
  round chưa ở trạng thái không cho rerun (`transition_round` chặn nếu round không hợp lệ để chuyển
  sang `SCHEDULING`).
- **Ai trigger:** chỉ role `ADMIN`/`MANAGER` (`_require(user, "ADMIN", "MANAGER")` —
  `schedule_operations.py:926`). Không có role LECTURER/STUDENT nào gọi được endpoint chạy thuật
  toán; họ chỉ đọc kết quả qua các endpoint GET.
- **Output mỗi lần chạy:** **KHÔNG PHẢI 1** mà là **3 `ScheduleVersion` `DRAFT`** cùng lúc trong 1
  transaction — mỗi bản ứng với một objective profile cố định (`LECTURER_COMPACT`, `LOAD_BALANCED`,
  `EARLY_FINISH`). Đây là tính năng đang triển khai theo
  `plans/260825-0105-scheduler-objective-variants/plan.md` (phase 01-03 đã completed, phase 04
  in_progress). Manager xem cả 3 bản, chọn 1 để activate; 2 bản còn lại vẫn tồn tại ở trạng thái
  `DRAFT` cho tới khi bị discard hoặc bị ghi đè bởi activation.
- Round chuyển state `... → SCHEDULING` ngay khi bắt đầu chạy (nếu chưa ở `SCHEDULING`/`SCHEDULED`);
  chuyển tiếp sang `SCHEDULED` chỉ khi có version được **activate** (không phải khi generate xong).

## 2. Entry points

Tất cả prefix `/api/v1`.

| Method + Path | Handler | File:line |
|---|---|---|
| `POST /rounds/{roundId}/schedule/run` | `run_scheduler` | `apps/api/app/routes/schedule_operations.py:925` |
| `GET /rounds/{roundId}/schedule/versions` | `list_schedule_versions` | `apps/api/app/routes/schedule_operations.py:621` |
| `GET /schedule/versions/{versionId}` | `schedule_version_detail` | `apps/api/app/routes/schedule_operations.py:649` |
| `GET /schedule/versions/compare/{versionA}/{versionB}` | `compare_schedule_versions` | `apps/api/app/routes/schedule_operations.py:686` |
| `DELETE /schedule/versions/{versionId}` | `delete_draft_version` | `apps/api/app/routes/schedule_operations.py:716` |
| `POST /schedule/versions/{versionId}/activate` | `activate_schedule_version` | `apps/api/app/routes/schedule_operations.py:1048` |
| `POST /rounds/{roundId}/schedule/publish/{versionId}` | `publish_schedule` | `apps/api/app/routes/schedule_operations.py:1748` |
| `POST /rounds/{roundId}/groups/{groupId}/h11-waiver` | `grant_h11_waiver` | `apps/api/app/routes/schedule_operations.py:1021` |
| `DELETE /rounds/{roundId}/groups/{groupId}/h11-waiver` | `revoke_h11_waiver` | `apps/api/app/routes/schedule_operations.py:1036` |

Core solver functions (không phải HTTP, gọi từ route trên):

| Function | File:line |
|---|---|
| `solve_schedule` (CP-SAT model + solve) | `apps/api/app/scheduler/scheduler.py:24` |
| `generate_candidates` | `apps/api/app/scheduler/candidates.py:17` |
| `validate_schedule` (H1-H13 độc lập với solver) | `apps/api/app/scheduler/validator.py:46` |
| `build_input_snapshot` | `apps/api/app/scheduler/snapshot.py:6` |

`target_schedule_contract.py` là lớp **nested contract** bọc lại đúng các hàm trên bằng
`success_payload` envelope, không có logic riêng, nhưng **map response khác**:

| Method + Path | Handler | Gọi thẳng | File:line |
|---|---|---|---|
| `GET /rounds/{roundId}/schedules` | `list_target_schedules` | `list_schedule_versions` | `target_schedule_contract.py:30` |
| `POST /rounds/{roundId}/schedules/generate` | `generate_target_schedule` | `run_scheduler` | `target_schedule_contract.py:36` |
| `GET /rounds/{roundId}/schedules/{scheduleId}` | `target_schedule_detail` | `schedule_version_detail` | `target_schedule_contract.py:51` |
| `POST /rounds/{roundId}/schedules/{scheduleId}/actions/set-active` | `set_target_schedule_active` | `activate_schedule_version` | `target_schedule_contract.py:60` |
| `POST /rounds/{roundId}/schedules/{scheduleId}/actions/discard` | `discard_target_schedule` | `delete_draft_version` | `target_schedule_contract.py:70` |

⚠️ `generate_target_schedule` (`target_schedule_contract.py:36-47`) gọi `run_scheduler()` y hệt route
gốc nhưng **chỉ map field của bản đầu tiên** (`version_id/status/scheduledCount/...`) vào response —
field `versions` (mảng chứa cả 3 draft) từ `ScheduleRunResponse` **không được forward**. Gọi qua path
`/schedules/generate` vẫn tạo đủ 3 `ScheduleVersion` trong DB, nhưng client chỉ nhìn thấy 1 bản qua
response này (phải gọi `GET .../schedules` riêng để thấy cả 3). Xem thêm mục 7.

## 3. Business logic từng bước

### 3.1. Pre-validate input (`_validate_scheduler_inputs`, `schedule_operations.py:140-231`)

Chạy **trước** khi đổi round state, raise `DomainError` (→ HTTP 422) sớm nếu thiếu:

1. Không có group nào gán vào round → `ROUND_GROUPS_REQUIRED`.
2. Không có timeslot `active=TRUE` nào → `ROUND_TIMESLOTS_REQUIRED`.
3. Có group chưa gán `project_id` → `ROUND_GROUP_PROJECT_REQUIRED`.
4. Có group không đúng **đúng 1** active Leader (`membership_role='LEADER' AND status='ACTIVE'`) →
   `ROUND_GROUP_LEADER_INVALID`.
5. Reviewer: nếu có `round_invitations.status='ACCEPTED'` — cần `len(accepted) >= reviewer_count`
   (`ROUND_REVIEWERS_ACCEPTANCE_REQUIRED`) và `len(accepted ∩ available_ở_active_timeslots) >=
   reviewer_count` (`ROUND_REVIEWER_AVAILABILITY_REQUIRED`). Nếu **không có accepted nào cả**, fallback
   kiểm tra `len(available theo lecturer_availabilities) >= reviewer_count`
   (`ROUND_REVIEWERS_INSUFFICIENT`).

### 3.2. Build `RoundInput` (`_round_input`, `schedule_operations.py:275-464`)

Query và chuẩn hóa toàn bộ input thuần túy từ DB thành dataclass `RoundInput` (immutable, không phụ
thuộc DB nữa từ đây):

- `round_type`, `expected_reviewer_count` = `rounds.reviewer_count`.
- `group_status`, `group_project`, `group_leader_valid` (đúng 1 active leader hay không) — từ
  `round_groups` JOIN `groups` JOIN `group_memberships`.
- `project_supervisors`: map `project_id → set(lecturer_id)` từ `project_supervisors`.
- `timeslots`: `(id, start_at, end_at, day_date, part)` — **part AM/PM tính bằng
  `EXTRACT(HOUR FROM start_at AT TIME ZONE 'Asia/Ho_Chi_Minh') < 13`**, hardcode SQL CASE
  (`schedule_operations.py:326-327`), lặp lại y hệt ở `_to_domain_sessions` (`:559`).
- `reviewer_ids` = `accepted_reviewer_ids` (từ `round_invitations` status ACCEPTED) nếu không rỗng,
  **fallback** sang `available_reviewer_ids` (mọi lecturer có record `AVAILABLE` bất kỳ) nếu round
  chưa có invitation nào ACCEPTED (`:340-358`).
- `existing_semester_load`: đếm số session mỗi lecturer đã có ở **round khác cùng semester** đang
  `ACTIVE`/`PUBLISHED` (dùng cho H12 semester quota + soft S1).
- `group_selected_slots` / `group_selection_mode`: từ `group_slot_preferences.selected=TRUE`, chỉ có
  ý nghĩa khi `rounds.group_selection_mode=TRUE`.
- `prior_reviewer_ids`: **chỉ tính khi `round_type IN ('DEFENSE_1','DEFENSE_1_2')`** — lecturer đã
  từng là council member của group đó ở round `DEFENSE_1_1`/`REVIEW_3` (`DEFENSE_1_1_TYPES`) đã
  `ACTIVE`/`PUBLISHED`.
- `remediation_verifier_ids`: từ `remediation_cases.verifier_lecturer_id` với status
  `OPEN/OVERDUE/PASSED`.
- `h11_waiver_groups`/`h11_waiver_actors`/`h11_waiver_reasons`: từ `h11_waivers.active=TRUE`.
- `committee_reviewer_sets`/`has_assigned_committees`: từ `round_committees` JOIN `committees` JOIN
  `committee_members`, **lọc chỉ giữ committee mà mọi member đều nằm trong `reviewer_ids` đã tính ở
  trên** (`eligible_pool.issuperset(member_ids)`).
- `h12_sessions_per_part`, `h12_sessions_per_day`, `h12_semester_quota`, `max_groups_per_timeslot`,
  `max_minutes_per_part`, `max_minutes_per_day`, `soft_weights`, `result_owner_mode` — copy thẳng từ
  cột `rounds` tương ứng (xem mục 5).

### 3.3. Candidate generation (`generate_candidates`, `candidates.py:17-68`)

Sinh trước toàn bộ tổ hợp `(group, timeslot, reviewer_tuple)` **hợp lệ theo hard filter**, để CP-SAT
model không cần biểu diễn lựa chọn chắc chắn vô nghĩa (giảm kích thước model đáng kể).

Với mỗi group (bỏ qua nếu `group_leader_valid[group]==False` hoặc `group_status` không thuộc tập
eligible của `round_type` — xem `_eligible` trong `validator.py:26-35`):

1. `allowed_reviewers` = reviewer không nằm trong `conflicts` với project đó, và không phải supervisor
   của project đó (H1, H8 lọc ngay từ bước sinh candidate, không đợi solver).
2. Với mỗi timeslot (bỏ qua nếu `group_selection_mode` bật và slot không nằm trong
   `group_selected_slots[group]` — H10 lọc sớm):
   - `available` = `allowed_reviewers` có `(reviewer, timeslot) ∈ lecturer_availability` (H7 lọc sớm).
   - Nếu `round_type ∈ DEFENSE_1_2_TYPES` (`DEFENSE_1_2`, `DEFENSE_1`) và **không có H11 waiver hợp
     lệ**: thu hẹp `available` chỉ còn reviewer thuộc `prior_reviewer_ids[group] ∪
     remediation_verifier_ids[group]` (H11 lọc sớm — continuity).
   - Sinh `reviewer_ids` tuple qua `_reviewer_tuples` (mục dưới).
3. Mỗi tổ hợp hợp lệ → 1 `Candidate(group_id, timeslot_id, start_at, end_at, day, part,
   reviewer_ids)`.

**`_reviewer_tuples` (`candidates.py:71-97`):**

- Nếu round **có** committee bound (`has_assigned_committees=True`): **chỉ** dùng
  `committee_reviewer_sets` có kích thước đúng `expected_reviewer_count` và **toàn bộ** member đều
  nằm trong `available` — **không tự bù người từ free pool** nếu committee thiếu người rảnh (comment
  code: "a Committee losing any member here drops out entirely").
- Nếu **không** có committee bound: tổ hợp tự do từ `available`, kích thước
  `expected_reviewer_count`. Nếu `C(|available|, k) <= FREE_POOL_REVIEWER_TUPLE_CAP` (=16) → liệt kê
  đủ; nếu vượt cap → `_bounded_free_pool_tuples` lấy **16 tổ hợp deterministic**, sinh bằng thuật toán
  rotated/stepped sampling xoay vòng offset theo `rotation_seed = group_id*1_000_003 + timeslot_id`
  để phủ đều mọi reviewer thay vì luôn ưu tiên 16 tổ hợp lexicographic đầu (xem journal
  `260825-0213-scheduler-candidate-bounding.md`).

### 3.4. CP-SAT model (`solve_schedule`, `scheduler.py:24-237`)

1. Nếu `generate_candidates` trả rỗng → trả thẳng `SolverResult("PARTIAL", (), unscheduled_reasons,
   ...)` không tạo model (mọi group đều unscheduled kèm lý do từ `reason_for_unscheduled`).
2. Một `bool var` cho mỗi candidate.
3. **Hard constraints** thêm vào model:
   - `add_at_most_one` mỗi group — 1 group tối đa 1 candidate được chọn (H4).
   - Nếu `max_groups_per_timeslot` cấu hình: tổng candidate chọn trong 1 timeslot ≤ giá trị đó (H13).
   - Với mỗi reviewer: `_add_resource_overlap_constraints` — quét candidate theo reviewer, sort theo
     `start_at`, dùng sliding-window "active list" để chặn **mọi cặp candidate cùng reviewer bị
     overlap thời gian** cùng được chọn (H2 — thuật toán sweep-line, không phải all-pairs O(n²) ngây
     thơ).
   - Với mỗi reviewer, mỗi `(day, part)` xuất hiện trong candidate của reviewer đó: tổng candidate
     chọn có reviewer này ≤ `h12_sessions_per_part` (H12 — **chỉ theo part, KHÔNG có constraint theo
     day tổng** dù `h12_sessions_per_day` tồn tại trong `RoundInput` — xem mục 7).
   - Nếu `h12_semester_quota` cấu hình: tổng candidate chọn có reviewer này ≤
     `max(0, quota - existing_semester_load[reviewer])` (H12 semester).
   - Nếu `max_minutes_per_part`/`max_minutes_per_day` cấu hình: tổng phút của candidate chọn (cùng
     reviewer, cùng day+part / cùng day) ≤ giá trị đó (H12 minute-based).
4. **Objective — kỹ thuật lexicographic-qua-bound** (không dùng multi-pass solve):
   ```
   primary_bonus = secondary_bound + balance_bound + profile_bound + 1
   maximize( Σ (primary_bonus + weighted_soft_score[i]) * var[i]  +  balance_expr  +  profile_expr )
   ```
   `primary_bonus` luôn lớn hơn tổng biên độ tối đa mọi thành phần phụ cộng lại, nên solver **luôn ưu
   tiên tối đa số group được xếp trước tiên**; trong cùng số group xếp được, mới xét tới
   `weighted_soft_score` (candidate-level, S1-S7 nhân `soft_weights` của round) + `balance_expr` +
   `profile_expr`.
   - `balance_expr`/`balance_weight`: **chỉ kích hoạt khi `objective_profile=="LEGACY"` VÀ
     `h12_semester_quota` có cấu hình** — cân bằng `min/max` số session giữa các reviewer theo
     semester load. Route production **không bao giờ** gọi với `objective_profile="LEGACY"` (xem mục
     5, 7) nên nhánh này chết trong production, chỉ chạy trong test/benchmark gọi `solve_schedule`
     trực tiếp.
   - `profile_expr` theo `objective_profile` (mục 3.5).
5. Solver: `cp_model.CpSolver()`, `max_time_in_seconds=time_limit_seconds` (payload, mặc định 10s),
   `random_seed=random_seed`, **`num_search_workers=1` cố định** (để kết quả reproducible cùng seed,
   đánh đổi tốc độ đa luồng).
6. Nếu status không phải `OPTIMAL`/`FEASIBLE` (tức `UNKNOWN`/`INFEASIBLE`/`MODEL_INVALID`): trả
   `PARTIAL` với mọi group unscheduled, **không đọc `solver.value()`** (comment code giải thích: đọc
   giá trị solver ở các status này có thể tạo session chồng giờ giả, bị `validate_schedule` reject).
   Đây là hardening đã áp dụng theo journal `260825-0213-scheduler-candidate-bounding.md`.
7. Nếu có kết quả: build `ScheduledSession` từ candidate được chọn, gọi **`validate_schedule` re-check
   độc lập ngay trong `solve_schedule`** — nếu invalid, raise `DomainError("SOLVER_OUTPUT_INVALID")`
   (crash cứng cả request, không fallback âm thầm).
8. Group nào không nằm trong selected → `reason_for_unscheduled` sinh lý do (mục 3.6).

### 3.5. Objective profile (3 profile cố định, `SchedulerObjectiveProfile` literal)

| Profile | Hàm | Ý tưởng | File:line |
|---|---|---|---|
| `LECTURER_COMPACT` | `_add_compactness_objective` | Thưởng 2 slot **liền kề đúng nghĩa** (end slot trước == start slot sau) cùng reviewer cùng day đều được chọn — dùng `bool_and`/`bool_or` reify biến `adjacent`. Trọng số cố định `100` mỗi cặp liền kề. Nghỉ giữa 2 phiên (gap thời gian thật) **không** tính liền kề — availability/break cấu hình vẫn được tôn trọng. | `scheduler.py:283-331` |
| `LOAD_BALANCED` | `_add_load_balance_objective` | `-1000*(max_load-min_load) - 1*(max_minutes-min_minutes) + compactness_expr` — ưu tiên chính là giảm chênh lệch **số session**, phụ là giảm chênh lệch **số phút**, rồi mới tới compactness (tái dùng `_add_compactness_objective`) làm tie-break phụ. | `scheduler.py:334-389` |
| `EARLY_FINISH` | `_add_early_finish_objective` | `-1000*latest_end_offset - Σ start_offset[i]*var[i]` — ưu tiên chính giảm **thời điểm kết thúc muộn nhất toàn round**, phụ ưu tiên bắt đầu sớm. | `scheduler.py:392-408` |
| `LEGACY` (default param, không dùng ở route production) | — (không thêm `profile_expr`) | Chỉ còn `balance_expr` (S1 global) nếu `h12_semester_quota` cấu hình. | `scheduler.py:32,141-152` |

Mỗi lần Manager gọi `POST .../schedule/run`, route lặp `SCHEDULE_VARIANT_PROFILES` (tuple 3 phần tử
cố định, `schedule_operations.py:70-74`) và gọi `solve_schedule` **3 lần**, dùng **chung 1
`candidate_pool`** đã sinh 1 lần (`:951-956,974`) — khác biệt giữa 3 bản chỉ đến từ objective, không
từ candidate set khác nhau. `random_seed` mỗi variant = `payload.random_seed + variant_index`
(0,1,2).

### 3.6. Soft score / lý do unscheduled

- `_candidate_soft_scores` (`scheduler.py:448-472`) tính điểm cho **từng candidate** trước khi đưa
  vào model — không phải điểm của lời giải cuối:
  - `S1`: tổng `(quota - existing_load) * preference_factor` cho mỗi reviewer trong candidate,
    `preference_factor` = `{"LOW":1,"MEDIUM":2,"HIGH":3}` theo `lecturer_load_preferences` (mặc định
    `MEDIUM`=2 nếu không có preference). Chỉ tính nếu `h12_semester_quota` có cấu hình.
  - `S2`: `1` nếu `round_type ∈ {REVIEW_2, REVIEW_2_1}` và **toàn bộ** reviewer_ids trùng khớp
    `prior_reviewer_ids[group]` (giữ đúng cặp Review 1 cho Review 2).
  - `S3`: (chỉ `DEFENSE_1/DEFENSE_1_2`) số reviewer trùng với `prior_reviewer_ids[group]`.
  - `S4`: `1` nếu `part ∈ {"AM","MORNING"}` — ưu tiên buổi sáng, luôn cộng bất kể round type.
  - `S5`: `1` nếu `day` không rỗng — thực chất luôn đúng với timeslot hợp lệ, gần như hằng số.
  - `S6`: giống công thức S3 nhưng áp dụng **mọi round type** (không giới hạn DEFENSE).
  - `S7`: số reviewer trong candidate **không phải** supervisor của project — do candidate đã loại
    supervisor từ bước sinh (3.3), giá trị này luôn bằng `expected_reviewer_count`.
  - `S8`, `S9`: nằm trong `_empty_soft_scores()` (khởi tạo `S1..S9=0`) nhưng **không bao giờ được set**
    trong `_candidate_soft_scores` — luôn `0`.
- Tất cả nhân với `soft_weights.get(rule, 0)` — **mặc định 0** nếu round không cấu hình
  `soft_weights` cho rule đó, nghĩa là **toàn bộ soft bonus tắt mặc định**.
- `reason_for_unscheduled` (`candidates.py:153-224`) chạy lại chuỗi hard-filter y hệt
  `generate_candidates` theo thứ tự ưu tiên cố định để suy ra 1 lý do "gần đúng nhất" (không phải
  chứng minh tối thiểu duy nhất — ghi chú thẳng trong onboarding doc): `NO_REVIEWER_AVAILABILITY` →
  `MISSING_LEADER` → `H1_CONFLICT` → `H8_CONFLICT` → `NO_TIMESLOT` → `NO_REVIEWER_AVAILABILITY` (theo
  slot) → `H11_CONTINUITY` → fallback `NO_TIMESLOT` generic.

### 3.7. Persist DRAFT version (`_persist_generated_schedule_draft`, `schedule_operations.py:782-921`)

Gọi 1 lần cho **mỗi** trong 3 profile, cùng transaction với `run_scheduler`:

1. `build_input_snapshot` đóng gói `RoundInput` + `groups`/`timeslots`/`reviewer_assignments` thành
   JSON để audit/replay, gắn thêm `unscheduled` (danh sách lý do dạng dict).
2. Insert 1 row `schedule_versions` (`status='DRAFT'`, `version_no` tăng dần trong round, snapshot,
   `algorithm_parameters` = `ScheduleRunPayload.model_dump()` **cộng thêm**
   `objective_profile`/`objective_label`/`metrics`/`scheduled_count`/`unscheduled_count`,
   `random_seed`, `solver_status`, `total_score=objective`, `soft_scores`, `created_by`).
3. Với mỗi `ScheduledSession`: insert `schedule_assignments` (**room_id luôn NULL** — solver không
   chọn phòng) + insert từng `schedule_assignment_reviewers` (snapshot `display_name` tại thời điểm
   generate, `is_result_owner` chỉ set `True` cho reviewer đầu tiên khi
   `result_owner_mode=True` và `round_type ∈ {DEFENSE_1_1, REVIEW_3, DEFENSE_2}`).
4. Insert 1 row `scheduler_jobs` (status `PARTIAL` nếu còn `unscheduled`, else `COMPLETED`) — bản ghi
   audit-style, không phải queue thật (xem mục 7).
5. Insert `audit_events` action `SCHEDULER_RUN`.

`run_scheduler` (`schedule_operations.py:924-1017`) gộp cả 3 kết quả vào response
`ScheduleRunResponse`: field top-level (`version_id`, `status`, `scheduled_count`, ...) = **bản đầu
tiên** (`LECTURER_COMPACT`) để tương thích client cũ, cộng field `versions` = mảng cả 3 summary.

### 3.8. Activate (`activate_schedule_version`, `schedule_operations.py:1047-1176`)

Biến 1 `DRAFT` version thành phương án vận hành — **không phải bước thuật toán** nhưng là bước kế
tiếp bắt buộc trong luồng:

1. Lock thứ tự Round → Version → Groups → Assignments (`FOR UPDATE` từng bước).
2. Chặn nếu `version.status != 'DRAFT'`, hoặc `groups.project_id` đã đổi khác snapshot lúc generate
   (`DRAFT_ASSIGNMENT_STALE`).
3. **Re-run `validate_schedule`** với `RoundInput` build lại **tại thời điểm activate** (dữ liệu có
   thể đã đổi từ lúc generate) — không tin snapshot cũ.
4. `lock_reviewer_ids` (advisory lock) rồi re-check overlap **cross-round toàn hệ thống** (reviewer
   đã bận ở version `ACTIVE`/`PUBLISHED` của round **khác**) → `409 REVIEWER_OVERLAP`.
5. Với mỗi assignment: `create_council` (services/councils.py, ngoài phạm vi doc này) rồi insert
   `sessions` (`status='PLANNED'`, `room_id` copy từ assignment = vẫn NULL).
6. Mọi version `DRAFT`/`ACTIVE` khác cùng round → `DISCARDED`. Round `SCHEDULING → SCHEDULED`.

### 3.9. Publish (`publish_schedule`, `schedule_operations.py:1747-1866`)

Không sinh lịch mới — chỉ khóa version `ACTIVE` hiện tại thành công bố chính thức:

1. Yêu cầu `version.status == 'ACTIVE'`.
2. Check **materialization đầy đủ**: mỗi assignment có đúng 1 session, đủ council member khớp
   reviewer snapshot.
3. `validate_publish_room_readiness` (room-assignment flow, ngoài phạm vi) — mọi session phải có
   phòng hợp lệ.
4. `ensure_publishable` (`domain/schedule_operations.py:4-9`) — version phải `ACTIVE` **và**
   `validate_schedule(...).valid` lần cuối trước khi publish.
5. Version published cũ (nếu có) → `DISCARDED`. Round → `PUBLISHED`. Sessions `PLANNED → SCHEDULED`.
   Ghi notification/outbox cho recipient bị ảnh hưởng.

## 4. Data model / bảng liên quan

| Bảng | Cột quan trọng | Vai trò trong auto-scheduling |
|---|---|---|
| `rounds` | xem đầy đủ ở mục 5 | Nguồn config thuật toán (per-round, không phải per-run) |
| `round_groups`, `groups`, `group_memberships` | `project_id`, `status`, `membership_role='LEADER'` | Xác định group nào được xếp, leader hợp lệ |
| `project_supervisors` | `project_id`, `lecturer_id` | H1 |
| `timeslots`, `round_days` | `active`, `start_at`, `end_at`, `day_date` | Trục thời gian; part AM/PM suy từ giờ |
| `round_invitations` | `lecturer_id`, `status='ACCEPTED'` | Reviewer pool chính |
| `lecturer_availabilities` | `lecturer_id`, `timeslot_id`, `state='AVAILABLE'` | H7 |
| `conflict_declarations` | `lecturer_id`, `project_id` (global, không theo round) | H8 |
| `group_slot_preferences` | `group_id`, `timeslot_id`, `selected` | H10 khi `group_selection_mode` |
| `h11_waivers` | `round_id`, `group_id`, `granted_by`, `reason`, `active` | Gỡ H11 continuity theo group |
| `remediation_cases` | `group_id`, `verifier_lecturer_id`, `status` | Continuity thay thế cho H11 |
| `round_committees`, `committees`, `committee_members` | `sequence_number` | Committee bound — ràng buộc tổ hợp reviewer |
| `schedule_versions` | `id`,`round_id`,`version_no`,`status`(`DRAFT/ACTIVE/PUBLISHED/DISCARDED`),`input_snapshot` jsonb,`algorithm_parameters` jsonb,`random_seed`,`solver_status`,`total_score`,`soft_scores` jsonb,`created_by`,`created_at`,`activated_at` | 1 row / profile / lần chạy — đối tượng trung tâm của versioning |
| `schedule_assignments` | `schedule_version_id`,`group_id`,`project_id`,`timeslot_id`,`room_id`(NULL lúc generate),`start_at`,`end_at`,`time_range` (generated tstzrange) | Kết quả solver, durable, độc lập với `sessions` operational |
| `schedule_assignment_reviewers` | `assignment_id`,`lecturer_id`,`is_result_owner`,`snapshot_name` | Reviewer snapshot tại thời điểm generate |
| `scheduler_jobs` | `round_id`,`status`,`attempt`,`schedule_version_id`,`random_seed`,`input_snapshot`,`algorithm_parameters` | Bản ghi audit mỗi lần solve (KHÔNG phải queue thật thi hành — xem mục 7) |
| `sessions` | `schedule_version_id`,`group_id`,`timeslot_id`,`room_id`,`status`,`council_id` NOT NULL | Chỉ tồn tại **sau activate**; nguồn dữ liệu operational thật |
| `council_members`/councils | reviewer immutable snapshot per session | Tạo tại activate (`create_council`), ngoài phạm vi doc này |
| `audit_events` | `action`(`SCHEDULER_RUN`,`SCHEDULE_VERSION_ACTIVATED`,`SCHEDULE_PUBLISHED`,`H11_WAIVER_GRANTED/REVOKED`),`after_json` | Audit trail |
| `notifications`/`outbox_jobs` | `event_type`(`SCHEDULE_CHANGED`,`SCHEDULE_PUBLISHED`) | Thông báo async, worker riêng xử lý outbox |

`scheduler/jobs.py` (`SchedulerJobStore`) và `scheduler/versions.py` (`VersionStore`) là **in-memory
seam** dùng cho test/thiết kế lifecycle thuần Python — production truth luôn là bảng
`scheduler_jobs`/`schedule_versions` thật, mutate trực tiếp trong route (không đi qua 2 class này).

## 5. Config / hằng số hiện tại

### 5.1. Cấu hình per-run — expose qua API (`ScheduleRunPayload`, `schedule_operations.py:82-85`)

| Field (JSON alias) | Kiểu, default, ràng buộc | Ghi chú |
|---|---|---|
| `randomSeed` | `int`, default `0` | Dùng trực tiếp cho variant đầu; 2 variant sau = `+1`, `+2` |
| `timeLimitSeconds` | `float`, default `10`, `0 < x <= 300` | Truyền thẳng `solver.parameters.max_time_in_seconds`, áp dụng **riêng cho mỗi lần solve trong 3 lần** (tổng thời gian tối đa 1 request có thể gần `3 * timeLimitSeconds`) |

### 5.2. Cấu hình per-round — cột bảng `rounds`, set lúc round setup (không phải lúc chạy)

| Cột | Default / constraint | Định nghĩa | Dùng ở đâu trong solver |
|---|---|---|---|
| `reviewer_count` | `2`, `CHECK > 0` | Số reviewer bắt buộc mỗi session | `expected_reviewer_count` — H5 |
| `h12_sessions_per_part` | `4`, `CHECK > 0` | Trần số session/reviewer/(day,part) | **Có** constraint trong CP-SAT (`_load_limits`) |
| `h12_sessions_per_day` | `8`, `CHECK > 0` | Trần số session/reviewer/day | **KHÔNG** có constraint trong CP-SAT — chỉ check post-hoc ở `validate_schedule` (xem mục 7) |
| `h12_semester_quota` | `NULL` (không giới hạn) | Trần tổng session/reviewer/semester | Có constraint trong CP-SAT + dùng cho soft S1 |
| `max_groups_per_timeslot` | `NULL` | H13 | Có constraint trong CP-SAT |
| `max_minutes_per_part` | `NULL`, thêm ở migration `0015` | H12 theo phút/part | Có constraint trong CP-SAT |
| `max_minutes_per_day` | `NULL`, thêm ở migration `0015` | H12 theo phút/day | Có constraint trong CP-SAT |
| `soft_weights` | `{}` jsonb | Map `rule_code → weight` cho S1-S7 (S8/S9 không dùng) | Nhân vào `weighted_scores` mỗi candidate; **mặc định 0 = tắt** nếu rule không có trong map |
| `result_owner_mode` | `false` | Có gán Result Owner tự động không | Chỉ set `is_result_owner=True` cho reviewer đầu tiên khi bật + đúng round type |
| `group_selection_mode` | `false` | Nhóm tự chọn slot hay không | H10 — lọc candidate theo `group_slot_preferences` |

### 5.3. Hardcode trong code — KHÔNG configurable qua API/DB hiện tại

| Hằng số | Giá trị | File:line | Ý nghĩa |
|---|---|---|---|
| `FREE_POOL_REVIEWER_TUPLE_CAP` | `16` | `candidates.py:14` | Trần số tổ hợp reviewer tự do/mỗi (group, timeslot) trước khi đưa vào CP-SAT |
| `SCHEDULE_VARIANT_PROFILES` | 3 phần tử cố định `(LECTURER_COMPACT, "Liền mạch GV")`, `(LOAD_BALANCED, "Cân bằng tải")`, `(EARLY_FINISH, "Kết thúc sớm")` | `schedule_operations.py:70-74` | Không có cách nào chạy ít hơn/nhiều hơn 3 profile, không đổi được nhãn qua API |
| `num_search_workers` | `1` | `scheduler.py:163` | Cố định để đảm bảo reproducibility theo seed, đánh đổi tốc độ |
| Compactness adjacency weight | `100` mỗi cặp liền kề | `scheduler.py:331` | Trọng số cứng trong objective `LECTURER_COMPACT` |
| `LOAD_BALANCED` weight | `-1000` × session-spread, `-1` × minute-spread | `scheduler.py:387` | Không cấu hình được tỉ lệ ưu tiên session-count vs minutes |
| `EARLY_FINISH` weight | `-1000` × latest-end, `-1`/phút × start-offset | `scheduler.py:405` | Tương tự, cố định tỉ lệ |
| AM/PM cutoff | giờ `< 13` (giờ VN) | `schedule_operations.py:326-327`, `:559`, `benchmark.py:18` | Lặp lại ở 3 chỗ, không đọc từ config |
| `preference_factor` (S1) | `{"LOW":1,"MEDIUM":2,"HIGH":3}` | `scheduler.py:454` | Không cấu hình được thang hệ số |
| `_eligible` status map theo round_type | dict hardcode | `validator.py:26-35` | Group status nào được coi là "đủ điều kiện" từng loại round |
| `primary_bonus` formula (lexicographic bound) | `secondary_bound+balance_bound+profile_bound+1` | `scheduler.py:154` | Kỹ thuật đảm bảo coverage luôn thắng soft score, không cấu hình được |
| H11 waiver actor bắt buộc | chuỗi `"MANAGER"` | `validator.py:41`, `schedule_operations.py:459` | Không có role khác được phép waiver |

## 6. Đối chiếu tài liệu cũ

| Doc | Trạng thái | Ghi chú cụ thể |
|---|---|---|
| `docs/SchedulingAlgorithm_v1.0 (1).md` | **Lỗi thời / không áp dụng cho hiện trạng** | Toàn bộ tài liệu là **đề xuất thiết kế tương lai** (skill GV, ma trận trọng số W_round/W_type, role CHAIR/SECRETARY, council batching theo ProjectType, H14-H16 mới, pha 0-6). Code hiện tại **không có** bảng skill, **không có** role CHAIR/SECRETARY trong constraint logic (`council_members.role` nếu tồn tại không được solver dùng), **không** batch nhiều group/hội đồng (mỗi group 1 session riêng), **không có** H14/H15/H16. Chỉ nên tham khảo như định hướng tương lai, không phải mô tả code hiện tại. |
| `docs/api/scheduling.md` | **Một phần đúng, một phần lỗi thời** | (a) §2 mô tả response `run` như 1 version duy nhất ("Một run tạo ScheduleVersion mới") — thực tế **luôn tạo 3 version** (`versions` array), doc không nhắc gì tới cơ chế 3-profile. (b) Error code liệt kê ở §2 (`ROUND_INPUTS_INCOMPLETE`, `SCHEDULE_RERUN_FORBIDDEN`, `ROUND_POSTPONED`) **không khớp** code — code thực tế raise `ROUND_GROUPS_REQUIRED`/`ROUND_TIMESLOTS_REQUIRED`/`ROUND_GROUP_PROJECT_REQUIRED`/`ROUND_GROUP_LEADER_INVALID`/`ROUND_REVIEWERS_ACCEPTANCE_REQUIRED`/`ROUND_REVIEWER_AVAILABILITY_REQUIRED`/`ROUND_REVIEWERS_INSUFFICIENT`/`ROUND_TRANSITION_NOT_ALLOWED`. (c) §3-§9 (activate, publish, immutable councils, h11-waiver, result-owner, controlled-change, room/H3 draft note) khớp đúng code hiện tại. |
| `docs/backend-onboarding/05-scheduling-feature-a-to-z.md` | **Đúng, cập nhật tốt** | 10 bước khớp sát code, kể cả mục "Rủi ro đã xác nhận" (registry thiếu H13/S9 trong danh sách, H12 daily-count chưa encode trong solver — đã xác nhận lại độc lập ở mục 7 dưới). Thiếu duy nhất 1 chi tiết: không nói rõ `run_scheduler` sinh **3 version/lần** (mô tả như 1 lần solve). |
| `docs/journals/260825-0213-scheduler-candidate-bounding.md` | **Đúng** | Khớp hoàn toàn `FREE_POOL_REVIEWER_TUPLE_CAP=16`, rotated/stepped sampling, và xử lý `UNKNOWN/INFEASIBLE/MODEL_INVALID` → `PARTIAL` thay vì đọc `solver.value()` trong code hiện tại. |
| `plans/260825-0105-scheduler-objective-variants/plan.md` | **Đúng, mô tả đúng tính năng đang triển khai** | 3 profile cố định, 1 candidate pool dùng chung cho cả 3 lần solve, giữ field response cũ + thêm `versions` — khớp code. 1 acceptance criterion trong plan **chưa tick**: "draft nhiều group hơn luôn xếp hạng trên draft ít group hơn" — code hiện tại **không** rank/sort 3 version theo `scheduled_count`, thứ tự trong `versions` cố định theo `SCHEDULE_VARIANT_PROFILES` (LECTURER_COMPACT, LOAD_BALANCED, EARLY_FINISH), đúng như plan tự ghi nhận còn dang dở. |
| `docs/project-reference/BusinessRules_CapstoneScheduler_v1.0.md` | **Một phần đúng, một phần lỗi thời** | H1, BR-SCH-02 (partial result kèm lý do cụ thể) khớp code. **H11 mô tả sai**: doc nói "Defense 1.2 phải giữ nguyên **Chủ tịch** đã chấm Defense 1.1" — code (`validator.py:130-151`, `candidates.py:48-51`) không có khái niệm Chair, H11 chỉ yêu cầu **≥1 reviewer bất kỳ** trong tập continuity (`prior_reviewer_ids ∪ remediation_verifier_ids`) xuất hiện lại, không bắt buộc đúng người giữ vai trò cụ thể nào. |
| `docs/project-reference/ERD_CapstoneScheduler_v1.0.md` | **Một phần đúng, một phần lỗi thời** | Cấu trúc tổng thể (`SCHEDULE_VERSIONS ||--o{ SESSIONS`, quan hệ tới TIMESLOTS/ROOMS/GROUPS) còn đúng. **Lỗi thời cụ thể**: doc mô tả bảng phi chuẩn hoá `session_reviewers` và cột `schedule_versions.is_active` boolean — đã bị thay bằng `council_members`/immutable councils (migration `0025_immutable_councils`, xác nhận chéo ở `docs/api/scheduling.md` §5) và cột `status` enum (`DRAFT/ACTIVE/PUBLISHED/DISCARDED`), schema hiện tại **không có** cột `is_active`. |

## 7. Giới hạn / edge case quan sát được trong code

- **H12 `sessions_per_day` không được CP-SAT enforce trực tiếp** — chỉ `h12_sessions_per_part` có
  constraint trong `solve_schedule` (`_load_limits` chỉ dùng `h12_sessions_per_part`, không dùng
  `h12_sessions_per_day`). Trần theo ngày chỉ bị `validate_schedule` bắt **sau khi** solver đã chọn
  xong; nếu vi phạm, `solve_schedule` raise `DomainError("SOLVER_OUTPUT_INVALID")` — crash cứng cả
  request thay vì solver tự tránh từ đầu (đã ghi nhận độc lập trong onboarding doc, xác nhận lại đúng
  ở code hiện tại).
- **`balance_expr` (S1 global load-balance qua semester quota) chết trong production** — chỉ kích
  hoạt khi `objective_profile=="LEGACY"`, nhưng route `run_scheduler` **luôn** gọi 1 trong 3 profile
  cố định (`LECTURER_COMPACT`/`LOAD_BALANCED`/`EARLY_FINISH`), không bao giờ `"LEGACY"`. Chỉ test và
  `benchmark.py` gọi `solve_schedule` trực tiếp mới chạm nhánh này.
- **Soft bonus S1-S7 tắt mặc định** — `soft_weights.get(rule, 0)`, round không set `soft_weights` thì
  toàn bộ soft score không ảnh hưởng objective (chỉ còn coverage + profile-specific term quyết định).
  `S8`/`S9` là 2 key chết hoàn toàn (định nghĩa trong `_empty_soft_scores` nhưng không có logic set).
- **Free-pool sampling không đầy đủ khi vượt cap 16** — với round nhiều reviewer tự do, một số tổ hợp
  reviewer hợp lệ về mặt hard-constraint sẽ **không bao giờ xuất hiện** trong CP-SAT model (bị cắt
  bởi `_bounded_free_pool_tuples`), nên "tối ưu" của solver chỉ tối ưu trong tập đã sample, không phải
  tối ưu toàn cục lý thuyết.
- **`generate_target_schedule` (target contract) làm mất field `versions`** — gọi `run_scheduler` đủ
  3 version trong DB nhưng response chỉ map bản đầu, client dùng path `/schedules/generate` không
  thấy trực tiếp 2 bản còn lại qua response đó (phải gọi `GET /schedules` riêng).
- **Reviewer pool fallback không tường minh** — nếu round chưa có `round_invitations` nào
  `ACCEPTED` (kể cả 0 invitation), `_round_input` fallback dùng **mọi** lecturer có record
  `AVAILABLE` bất kỳ làm reviewer pool, bỏ qua khái niệm "đã được mời". Cần cân nhắc khi thiết kế
  config mới — hành vi này là ngầm định, không có flag bật/tắt.
- **`scheduler/jobs.py` và `scheduler/versions.py` không phải runtime thật** — 2 in-memory store này
  chỉ dùng cho test/lifecycle-seam thuần Python; đọc code ở đây **không phản ánh** hành vi production
  (production ghi thẳng bảng `scheduler_jobs`/`schedule_versions` trong route).
- **`registry.py` liệt kê thiếu** — `HARD_RULES` chỉ có `H1..H12` (thiếu `H13` mà validator/solver đều
  dùng thật); `SOFT_RULES` có `S1..S8` (thiếu `S9` dù `_empty_soft_scores` khởi tạo tới `S9`). Đây là
  file liệt kê mã rule tĩnh, không ảnh hưởng logic runtime, nhưng có thể gây nhầm khi tra cứu.
