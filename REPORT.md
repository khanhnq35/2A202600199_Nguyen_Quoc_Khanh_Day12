# Project Report: AI Agent Deployment & Security

## Lab Task 3.1 - Cloud Deployment (Railway)

Chúng ta đã đưa ứng dụng AI Agent từ môi trường local lên Cloud hoàn tất.

### ⚙️ Quy trình triển khai
1. **Thiết lập CLI**: Cài đặt Railway CLI toàn cục.
2. **Khởi tạo Project**: Tạo project `outstanding-manifestation` trên hạ tầng Railway.
3. **Cấu hình môi trường**: Thiết lập biến môi trường `PORT` và `AGENT_API_KEY` trực tiếp trên Cloud Dashboard/CLI.
4. **Deploy**: Sử dụng NIXPACKS builder để tự động hóa quy trình build và run ứng dụng Python.

### 🌐 Thông tin triển khai
- **Public URL**: [https://outstanding-manifestation-production-c4c3.up.railway.app](https://outstanding-manifestation-production-c4c3.up.railway.app)
- **Cấu hình phần cứng**: Railway Starter (512MB RAM, Shared CPU).

### ✅ Kết quả kiểm tra (Verification)
| Endpoint | URL | Kết quả | Ghi chú |
|----------|-----|---------|---------|
| **Health Check** | `/health` | **200 OK** | Trả về thông tin uptime và confirm nền tảng `Railway`. |
| **Agent Ask** | `/ask` | **200 OK** | Phản hồi chính xác với JSON body. |

---

## Lab Task 3.2 - Cloud Deployment (Render Blueprint)

Chúng ta đã triển khai thêm một phiên bản dự phòng trên Render bằng phương pháp Infrastructure as Code (Blueprint).

### 🛠️ So sánh Railway vs Render

| Tiêu chí | Railway | Render (Blueprint) |
|----------|---------|-------------------|
| **Phương thức** | CLI-based (`railway up`) | Git-based (`render.yaml`) |
| **Độ phủ** | Đơn giản, nhanh gọn. | Quản lý hạ tầng bằng code chuyên nghiệp. |
| **Khả năng Scaling** | Thủ công qua Dashboad. | Tự động định nghĩa Resource qua YAML. |
| **Public URL** | [outstanding-manifestation...](https://outstanding-manifestation-production-c4c3.up.railway.app) | [ai-agent-khanh.onrender.com](https://ai-agent-khanh.onrender.com/) |

### ✅ Kết quả kiểm tra Render
- **Status**: Live 🟢
- **Health Check**: `https://ai-agent-khanh.onrender.com/health` -> **Success**
- **Mock LLM**: Phản hồi tốt tương tự phiên bản Railway.

---

## Lab Task 4.1 - API Key Authentication

Chúng ta đã triển khai lớp bảo vệ đầu tiên cho API bằng cơ chế kiểm tra Header Token.

### 🕵️ Phân tích Code
- **Cơ chế**: Sử dụng `APIKeyHeader` của FastAPI để bắt header `X-API-Key`.
- **Logic kiểm tra**: Hàm `verify_api_key` so khớp key từ Header với biến môi trường `AGENT_API_KEY`.
- **Xử lý lỗi**:
    - Thiếu Key: Trả về **401 Unauthorized**.
    - Sai Key: Trả về **403 Forbidden**.

### ✅ Kết quả Unit Test (Local)
| Request Header | Status Code | Phản hồi |
|----------------|-------------|----------|
| (Empty) | **401** | Missing API key |
| `X-API-Key: wrong-key` | **403** | Invalid API key |
| `X-API-Key: my-secret-123` | **200** | Success (Mock Agent response) |

### 📝 Raw Test Output (Task 4.1)
```text
1. No Key Request:
HTTP/1.1 401 Unauthorized
{"detail":"Missing API key. Include header: X-API-Key: <your-key>"}

2. Wrong Key Request:
HTTP/1.1 403 Forbidden
{"detail":"Invalid API key."}

3. Correct Key Request:
HTTP/1.1 200 OK
{"question":"hello","answer":"Agent đang hoạt động tốt! (mock response)..."}
```

---

## Lab Task 4.2 - JWT Authentication (Advanced)

Chúng ta đã nâng cấp hệ thống bảo mật từ API Key tĩnh sang JWT (JSON Web Token) động và phân quyền theo vai trò (RBAC).

### 🏛️ Phân tích cơ chế
- **Stateless**: Server không cần lưu session, mọi thông tin (username, role) nằm trong Token.
- **Phân quyền (RBAC)**: 
    - `user`: Chỉ được gọi endpoint `/ask`.
    - `admin`: Được phép truy cập `/admin/stats` để theo dõi hệ thống.

### ✅ Kết quả kiểm thử phân quyền
| API Endpoint | Role: User (student) | Role: Admin (teacher) | Ý nghĩa |
|--------------|----------------------|-----------------------|---------|
| `/auth/token`| Thành công (200) | Thành công (200) | Cấp Token đúng định dạng JWT |
| `/ask` | Thành công (200) | Thành công (200) | Cả 2 đều có quyền hỏi Agent |
| `/admin/stats`| **Bị chặn (403)** | **Thành công (200)** | Phân quyền đúng theo thiết kế |

### 📝 Raw Test Output (Task 4.2)
```text
1. Login (student):
{"access_token":"eyJhbGciOiJIUzI1NiI...","token_type":"bearer",...}

2. Authorized Request (/ask):
HTTP/1.1 200 OK
{"question":"Test JWT","answer":"Đây là câu trả lời từ AI agent (mock)..."}

3. Unauthorized Request (User -> Admin Endpoint):
HTTP/1.1 403 Forbidden
{"detail":"Admin only"}

4. Login (teacher - Admin):
{"access_token":"eyJhbGciOiJIUzI1NiI...","token_type":"bearer",...}

5. Authorized Admin Request (/admin/stats):
HTTP/1.1 200 OK
{"total_users":"N/A (in-memory demo)","global_cost_usd":2.1e-05,...}
```

---

## Lab Task 4.3 - Rate Limiting (Giới hạn truy cập)

Cơ chế này ngăn chặn việc spam request làm quá tải hệ thống hoặc tiêu tốn tài nguyên LLM.

### 🕵️ Phân tích cơ chế
- **Thuật toán**: Sliding Window Counter (Cửa sổ trượt 60 giây).
- **Phân cấp (Tiers)**: 
    - `User`: 10 requests / phút.
    - `Admin`: 100 requests / phút.

### ✅ Kết quả thử nghiệm thực tế (Local)
Tôi đã spam 12 request liên tiếp bằng tài khoản `student`:

```text
--- Request 1-10 ---
HTTP/1.1 200 OK
{"question":"Request 1...10","usage":{"requests_remaining":9...0}}

--- Request 11-12 ---
HTTP/1.1 429 Too Many Requests
{
  "detail": {
    "error": "Rate limit exceeded",
    "limit": 10,
    "retry_after_seconds": 59
  }
}
```

---

## Lab Task 4.4 - Cost Guard (Ngăn chặn cháy túi)

Tính năng này bảo vệ chủ sở hữu Agent khỏi các hóa đơn API khổng lồ nếu hệ thống bị lạm dụng.

### 🕵️ Phân tích cơ chế
- **Cơ chế**: Theo dõi token usage (input/output) theo thời gian thực.
- **Ngân sách**: 
    - User: $1.0/ngày.
    - Global: $10.0/ngày.

### ✅ Kết quả thử nghiệm mô phỏng (Simulated Breach)
Tôi đã hạ ngân sách xuống cực thấp ($0.00001) để kiểm tra:

```text
1. First Request:
HTTP/1.1 200 OK
{"usage":{"requests_remaining":9,"budget_remaining_usd":2.4e-05}}

2. Second Request (Sau khi vượt ngưỡng 0.00001):
HTTP/1.1 402 Payment Required
{"detail":{"error":"Daily budget exceeded","used_usd":2.4e-05,"budget_usd":1e-05}}
```

**=> Kết luận:** Hệ thống bảo mật (Part 4) đã hoàn tất với đầy đủ các lớp bảo vệ: Authentication, Authorization, Traffic Control (Rate Limit) và Financial Control (Cost Guard).
