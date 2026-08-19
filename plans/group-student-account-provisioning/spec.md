# Spec: Tạo và quản lý student trực tiếp trong group

**Date:** 2026-08-19
**Status:** Draft

---

## Problem Statement

Hiện backend chỉ tạo group với các student đã tồn tại trong bảng `students`; chưa có API thêm student vào group sau khi group được tạo, cũng chưa có API sửa hồ sơ student hoặc bắt student mới đổi mật khẩu. Manager cần một luồng nhất quán để thêm student vào group, tự tạo account/profile khi cần và bảo vệ tài khoản mới bằng session giới hạn.

---

## User Stories

- **[P1]** As a Manager, I want to add an existing or new student to an existing group so that group membership and student account data are created in one operation.
  Accepted when: one successful request creates or finds the account, creates or finds the student profile, creates the active membership, and returns the member details; any failure rolls back all writes.

- **[P1]** As a Manager, I want to edit a student's profile separately from group membership so that name, email, and student code remain consistent across the system.
  Accepted when: `PATCH /api/v1/students/{student_id}` validates unique email/student code and updates the linked account/profile without changing membership history.

- **[P1]** As a newly created Student, I want to log in with the default password derived from my email and be forced to change it before using the application.
  Accepted when: login returns `must_change_password: true`, the session is restricted to identity/password endpoints, and all other protected APIs reject the session until the password is changed.

- **[P1]** As a Manager, I want to change a member's `LEADER`/`MEMBER` role without editing the student account so that group leadership remains a membership concern.
  Accepted when: exactly one active Leader is enforced per group and role changes are audited.

- **[P2]** As a Manager, I want to see whether a student account is newly provisioned or has completed the first password change so that I can follow up operationally.
  Accepted when: student/account responses expose the password-change-required state without exposing any password.

- **[P3]** _(out of scope — noted for future)_ Automated email delivery, password-reset links, SSO provisioning, and bulk student import from a new API are not part of this feature.

---

## Functional Requirements

1. **FR-01 — Add member to existing group:** Add `POST /api/v1/groups/{group_id}/members` for `ADMIN` and `MANAGER`. The request contains `student_code`, `email`, `display_name`, and membership `role` (`LEADER` or `MEMBER`); it never accepts a password.

2. **FR-02 — Existing student resolution:** If `student_code` already exists, the service must resolve the linked account and reject an email/account mismatch with a deterministic `409` error. It must reject adding a student who already has an active membership in another group in the same applicable semester.

3. **FR-03 — New account/profile provisioning:** If the student does not exist, create `accounts`, `account_roles(STUDENT)`, and `students` in the same transaction. The generated initial password is the email local-part (the substring before `@`), normalized to lowercase; only its Argon2 hash is persisted and the password is never returned by an API.

4. **FR-04 — Membership invariants:** Create an active `group_memberships` row. Enforce 4–5 active members, no duplicate student in a group, and exactly one active `LEADER`. A failed invariant returns `422` and leaves no partial account/profile/membership writes.

5. **FR-05 — Edit student profile:** Add `PATCH /api/v1/students/{student_id}` for `ADMIN` and `MANAGER` to update `display_name`, `email`, and/or `student_code`. Enforce uniqueness, normalize email/code consistently with existing APIs, and write an audit event.

6. **FR-06 — Edit membership role:** Add/retain `PATCH /api/v1/groups/{group_id}/members/{student_id}` for role changes. It must preserve the one-active-Leader invariant and audit the previous/new role.

7. **FR-07 — Preserve membership history:** Student removal continues through the existing dropout flow; do not hard-delete the student/account or rewrite historical memberships. `joined_at`, `left_at`, status, actor, and reason remain authoritative.

8. **FR-08 — First-login marker:** Add an account-level `must_change_password` boolean, default `false`; newly provisioned students set it to `true`. Existing seeded/imported accounts retain their current behavior unless explicitly marked by the provisioning flow.

9. **FR-09 — Login contract:** `POST /api/v1/auth/login` returns `must_change_password`. A newly provisioned student can authenticate with email + generated initial password, but the resulting session is marked `PASSWORD_CHANGE_REQUIRED`.

10. **FR-10 — Restricted session:** While password change is required, backend authorization permits only `GET /api/v1/auth/me`, `GET /api/v1/me`, `POST /api/v1/auth/change-password`, and `POST /api/v1/auth/logout`. Other authenticated endpoints return `403` with code `PASSWORD_CHANGE_REQUIRED`; FE-only redirects are insufficient.

11. **FR-11 — Change password:** Add `POST /api/v1/auth/change-password` with `current_password` and `new_password`. Validate the current password, require a new password policy of at least 12 characters, prevent reuse of the current password, update the Argon2 hash, clear `must_change_password`, and upgrade the current session to normal access.

12. **FR-12 — No password disclosure:** No create, list, detail, login, audit, or error response may contain the initial password, password hash, or password reset secret.

13. **FR-13 — Response schemas:** Student and group-member responses include `student_id`, `student_code`, `display_name`, `email`, membership `role`, membership `status`, and `must_change_password` where applicable. OpenAPI request/response examples must show the nested member contract.

14. **FR-14 — Concurrency:** Account email uniqueness, student-code uniqueness, active-membership uniqueness, and one-active-Leader constraints must be enforced transactionally at the database/application boundary. Concurrent duplicate requests must return a safe conflict response rather than duplicate profiles.

---

## Non-Functional Requirements

- **Performance:** Add-member and profile-update requests should complete in p95 < 500 ms under normal local deployment, excluding database cold start.
- **Security:** Passwords use Argon2 hashing; initial passwords are never logged or returned; restricted-session checks run server-side on every protected request; all mutations require CSRF protection and role authorization.
- **Auditability:** 100% of provisioning, profile updates, role changes, dropout/removal, password changes, and restricted-session upgrades create immutable audit events.
- **Consistency:** A failed add-member request leaves zero new account, student, or membership rows.
- **Availability:** The feature follows the existing API availability and PostgreSQL transaction guarantees; no background worker is required for provisioning.

---

## Success Criteria

- [ ] A Manager can add a new student to an existing group with one API call; account, role, profile, and membership are all present after `201`.
- [ ] A duplicate email/student code or active cross-group membership produces a deterministic `409`/`422` response and no partial records.
- [ ] The initial password is absent from database plaintext, logs, audit payloads, and HTTP responses in automated security tests.
- [ ] A newly provisioned student can log in, receives `must_change_password: true`, and receives `403 PASSWORD_CHANGE_REQUIRED` from a normal protected API.
- [ ] After a successful password change, the same session can call normal Student APIs and `must_change_password` is `false`.
- [ ] Group membership remains valid with 4–5 active members and exactly one active Leader after add, role change, and dropout scenarios.
- [ ] OpenAPI documents request/response fields and examples for all new endpoints without `additionalProp1` placeholders.

---

## Out of Scope

- Returning or emailing the generated initial password.
- Password-reset email/token workflows.
- SSO/Google/Microsoft provisioning.
- Bulk account/student import API redesign.
- Automatic reassignment of a student from one active group to another.
- Editing historical membership records or hard-deleting accounts/students.

---

## Assumptions

- The email local-part is the requested initial password convention; the feature remains security-sensitive because this value is predictable.
- `ADMIN` and `MANAGER` are the only roles allowed to provision or edit students/groups.
- Student email and student code are globally unique; a student cannot belong to two active groups in the same semester.
- Existing dropout and group-leader domain rules remain authoritative.
- The current cookie/CSRF session architecture remains in place; restricted access is added to its authorization dependency.

---

## [NEEDS CLARIFICATION]

- [ ] Confirm whether the initial password local-part must preserve dots/underscores/case or always be normalized to lowercase exactly as specified.
- [ ] Confirm whether an existing Student with `must_change_password = true` may be added to another group, or must complete password change first.
