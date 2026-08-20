# FE Guide — Lecturer Supervised Projects

## Endpoint

```http
GET /api/v1/lecturer/me/supervised-projects
```

Backend tự lọc theo lecturer đang đăng nhập. FE không truyền `lecturerId`.

## Response

```json
{
  "data": [
    {
      "id": 1,
      "code": "DEMO-P01",
      "title": "Demo Project 1 - Smart Campus",
      "status": "ACTIVE",
      "semesterId": 1,
      "semesterCode": "SE-2026-2027",
      "supervisorType": "MAIN",
      "group": {
        "id": 1,
        "code": "DEMO-G01",
        "memberCount": 5,
        "leader": {
          "id": 1,
          "name": "Student 1",
          "code": "SV001"
        },
        "members": [
          {
            "id": 1,
            "code": "SV001",
            "name": "Student 1",
            "role": "LEADER",
            "status": "ACTIVE"
          },
          {
            "id": 2,
            "code": "SV002",
            "name": "Student 2",
            "role": "MEMBER",
            "status": "ACTIVE"
          }
        ]
      }
    }
  ],
  "meta": {
    "page": 1,
    "pageSize": 1,
    "total": 1
  }
}
```

Project chưa được gắn group sẽ trả:

```json
"group": null
```

## Field notes

- `supervisorType`: `MAIN` là GVHD chính, `CO` là đồng hướng dẫn.
- `group.leader`: trưởng nhóm hiện tại, có thể `null` nếu dữ liệu group chưa hợp lệ.
- `group.members`: danh sách thành viên active của group, leader được đánh dấu bằng `role: "LEADER"`.
- `group.memberCount`: số thành viên active, tương ứng với độ dài `group.members`.
- API hiện trả toàn bộ danh sách; `meta` chưa phải pagination thật.

FE nên hiển thị fallback khi `group` hoặc `leader` là `null`, không được giả định mọi project đều đã có group.
