## Lab Task 4.4 - Cost Guard (Ngăn chặn cháy túi)

Tính năng này bảo vệ chủ sở hữu Agent khỏi các hóa đơn API khổng lồ nếu hệ thống bị lạm dụng.

### 🕵️ Phân tích cơ chế
- **Cơ chế**: Theo dõi token usage (input/output) theo thời gian thực.
- **Ngân sách**: 
    - User: $1.0/ngày.
    - Global: $10.0/ngày.
- **Xử lý vi phạm**: Trả về lỗi **402 Payment Required** ngay lập tức và chặn hoàn toàn các yêu cầu tiếp theo trong ngày.

### ✅ Kết quả thử nghiệm mô phỏng (Simulated Breach)
Hệ thống đã hạ ngân sách xuống cực thấp ($0.00001) để kiểm tra chốt chặn:

```text
1. First Request:
HTTP/1.1 200 OK
{"usage":{"requests_remaining":9,"budget_remaining_usd":2.4e-05}}

2. Second Request (Sau khi vượt ngưỡng 0.00001):
HTTP/1.1 402 Payment Required
{"detail":{"error":"Daily budget exceeded","used_usd":2.4e-05,"budget_usd":1e-05}}
```

---

### Exercise 5.1-5.5: Implementation notes

#### Exercise 5.1: Health Checks (Liveness & Readiness)
Chúng ta đã triển khai cơ chế giám sát giúp hệ thống Cloud (Railway/Render) quản lý vòng đời của Agent.

**🕵️ Phân tích cơ chế:**
- **/health (Liveness)**: Kiểm tra xem container có đang bị treo không. Tôi đã tích hợp thêm `psutil` để theo dõi cả mức độ chiếm dụng RAM. Nếu RAM > 90%, hệ thống sẽ báo `degraded`.
- **/ready (Readiness)**: Kiểm tra xem Agent đã sẵn sàng nhận request chưa (ví dụ: đã load xong Model/Weights). Dùng để điều phối traffic của Load Balancer.

**📝 Raw Test Output (Ex 5.1):**
```text
--- Liveness Check (/health) ---
HTTP/1.1 200 OK
{
  "status": "ok",
  "uptime_seconds": 4.6,
  "checks": {"memory": {"status": "ok", "used_percent": 82.2}}
}
```

---

#### Exercise 5.2: Graceful Shutdown (Tắt máy êm ái)
Chúng ta đã cấu hình để Agent không bao giờ ngắt kết nối đột ngột với người dùng khi hệ thống bảo trì hoặc update.

**🕵️ Phân tích cơ chế:**
- **Signal Handling**: Hệ thống bắt tín hiệu `SIGTERM` (Signal 15) từ Cloud Platform.
- **Lifespan Context**: Sử dụng `lifespan` của FastAPI để chặn quá trình thoát cho đến khi biến `_in_flight_requests` trở về bằng 0.

**📝 Raw Test Output (Ex 5.2):**
```text
[16:07:11] INFO: Agent is ready!
[16:07:16] INFO: Received signal 15 (SIGTERM)
[16:07:16] INFO: 🔄 Graceful shutdown initiated...
[16:07:16] INFO: ✅ Shutdown complete
```

---

#### Exercise 5.3: Stateless Design (Redis Integration)
Tách biệt hoàn toàn phần dữ liệu (State) ra khỏi xử lý (Compute).

**🕵️ Phân tích cơ chế:**
- **External Storage**: Thay vì lưu `history` trong RAM (dict), Agent sử dụng `redis.setex` và `redis.get`.
- **Session Continuity**: Người dùng có thể quay lại sau 1 giờ và vẫn tiếp tục cuộc hội thoại nhờ TTL (Time-to-live) được định nghĩa trong Redis.
- **Benefit**: Cho phép Restart Agent mà không làm mất lịch sử hội thoại của người dùng.

**📝 Raw Test Output (Ex 5.3):**
```text
--- Request (Session Persistence) ---
Served by: instance-6e58d5 | Storage: redis
Response: {"session_id":"fe813aa4...","question":"What is my name?..."}
Result: Agent correctly retrieved name from Redis.
```

---

#### Exercise 5.4: Scaling & Load Balancing (Nginx)
Phân phối traffic thông minh để tối ưu hiệu suất và khả năng chịu lỗi.

**🕵️ Phân tích cơ chế:**
- **Reverse Proxy**: Nginx đứng trước làm "mặt tiền" tiếp nhận request, giấu kiến trúc bên trong.
- **Upstream Pool**: Định nghĩa danh sách các Agent nodes.
- **Round Robin**: Nginx mặc định chuyển request luân phiên cho từng instance để tránh quá tải cho một node duy nhất.

**📝 Raw Test Output (Ex 5.4):**
```text
[Request 1] Serving Instance: instance-caf792
[Request 2] Serving Instance: instance-6e58d5
[Request 3] Serving Instance: instance-caf792
Result: Round Robin balancing between two instances verified.
```

---

#### Exercise 5.5: Final Delivery Checklist & Verification
Rà soát cuối cùng để đảm bảo hệ thống đạt chuẩn Production-ready.

**🕵️ Phân tích cơ chế:**
- **Sanity Check**: Kiểm tra toàn bộ checklist từ API Key đến Stateless Design.
- **Live Verification**: Kiểm thử thực tế trên hạ tầng Cloud (Railway/Render) để xác nhận config môi trường đã khớp với logic code.
- **Security Audit**: Xác nhận không có secret nào bị lộ trong Git history.

**📝 Raw Test Output (Ex 5.5):**
```text
--- Live Verification (Railway) ---
URL: https://outstanding-manifestation.../health
Status: 200 OK | Platform: Railway
All Checklist Items: [PASSED]
```

**=> Kết luận:** Hệ thống đã hoàn thành 100% các tiêu chí về Infrastructure, Security và Scalability.
