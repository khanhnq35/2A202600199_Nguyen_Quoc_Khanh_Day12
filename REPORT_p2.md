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

--- Readiness Check (/ready) ---
HTTP/1.1 200 OK
{
  "ready": true,
  "in_flight_requests": 1
}
```

---

#### Exercise 5.2: Graceful Shutdown (Tắt máy êm ái)
Chúng ta đã cấu hình để Agent không bao giờ ngắt kết nối đột ngột với người dùng khi hệ thống bảo trì hoặc update.

**🕵️ Phân tích cơ chế:**
- **Signal Handling**: Hệ thống bắt tín hiệu `SIGTERM` (Signal 15) từ Cloud Platform.
- **Lifespan Context**: Sử dụng `lifespan` của FastAPI để chặn quá trình thoát cho đến khi biến `_in_flight_requests` trở về bằng 0 (hoặc timeout 30s).
- **Trải nghiệm người dùng**: Người dùng vẫn nhận được câu trả lời đầy đủ dù Server đang trong quá trình tắt.

**📝 Raw Test Output (Ex 5.2):**
```text
[16:07:11] INFO: Agent is ready!
[16:07:13] INFO: POST /ask?question=LargeTask HTTP/1.1" 200 OK
[16:07:16] INFO: Received signal 15 (SIGTERM)
[16:07:16] INFO: 🔄 Graceful shutdown initiated...
[16:07:16] INFO: Waiting for 0 in-flight requests...
[16:07:16] INFO: ✅ Shutdown complete
```

---

#### Exercise 5.3: Stateless Design (Redis Integration)
Chúng ta đã tách biệt lưu trữ (Storage) khỏi xử lý (Logic) để Agent có khả năng mở rộng không giới hạn.

**🕵️ Phân tích cơ chế:**
- **External Storage**: Sử dụng Redis để lưu `conversation_history`.
- **Session Management**: Dùng `session_id` để định danh cuộc hội thoại. Bất kỳ Instance nào cũng có thể xử lý request nếu có quyền truy cập vào cùng một Redis server.
- **Failover**: Nếu một Agent instance bị sập, dữ liệu người dùng không bị mất vì đã nằm an toàn trong Redis.

**📝 Raw Test Output (Ex 5.3):**
```text
[Turn 1] Question: "Hi, I am Khanh"
[Turn 1] Response: Success, SessionID: 1d7feea5-...
[Turn 2] Question: "What is my name?" with SessionID
[Turn 2] Response: Success (Agent maintains context)
[History Check] Count: 4 messages (Authenticated & Tracked)
```

---

#### Exercise 5.4: Load Balancing (Nginx)
Để phân phối traffic đều cho các Agent instances, chúng ta sử dụng Nginx làm Reverse Proxy.

**🕵️ Phân tích cấu hình (nginx.conf):**
- **Upstream**: Định nghĩa một nhóm các `agent` instances.
- **Algorithm**: Mặc định sử dụng Round Robin.
- **Benefits**: 
    - Giấu IP thật của các Agent instances (Security).
    - Tăng tính sẵn sàng: Nếu 1 instance die, Nginx tự động chuyển traffic sang instance khác.

---

#### Exercise 5.5: Final Delivery Checklist
Hệ thống đã được kiểm tra chéo (Self-test) dựa trên danh mục yêu cầu của bài Lab.

**🕵️ Kết quả rà soát:**
- **Code Integrity**: Mã nguồn đã được dọn dẹp, không còn hardcoded secrets, đã cấu hình .dockerignore và .env.example.
- **Service Verification**: Đã thực hiện gọi thử API live trên Railway, phản hồi đúng cấu trúc JSON và có đầy đủ lớp bảo mật.
- **Documentation**: Các file MISSION_ANSWERS.md và DEPLOYMENT.md đã được tạo đúng mẫu.

**=> Kết luận chung:** Hệ thống AI Agent đã sẵn sàng cho môi trường Production, đảm bảo các tiêu chí về Bảo mật (Security), Khả năng mở rộng (Scaling) và Độ tin cậy (Reliability).
