# Deployment Information - AI Agent Production (Lab 06)

## Public URL
**URL**: [https://ai-agent-khanh.onrender.com/](https://ai-agent-khanh.onrender.com/)

## Platform
**Render** (Infrastructure as Code via `render.yaml`)

## Test Commands

### 1. Health Check
```bash
curl https://ai-agent-khanh.onrender.com/health
```
**Actual Response Log:**
```json
{"status":"ok","uptime_seconds":597.6,"platform":"Render","timestamp":"2026-04-17T10:25:27.769730+00:00"}
```

### 2. API Test (with X-API-Key authentication)
```bash
curl -X POST https://ai-agent-khanh.onrender.com/ask \
  -H "X-API-Key: YOUR_AGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello Agent, this is a security test via X-API-Key."}'
```
**Actual Response Log:**
```json
{
  "question": "Hello Agent, this is a security test via X-API-Key.",
  "answer": "Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.",
  "session_id": "api_client",
  "instance": "instance-190e08",
  "timestamp": "2026-04-17T10:27:58.144862+00:00"
}
```

## Environment Variables Set
- `PORT`: Tự động nhận diện (8000)
- `REDIS_URL`: Kết nối đến Render Redis instance
- `AGENT_API_KEY`: Khóa bảo mật cho các endpoint quản trị/metrics
- `JWT_SECRET`: Khóa bí mật để ký và xác thực JWT token
- `LOG_LEVEL`: `info` (Production standard)
- `RATE_LIMIT_PER_MINUTE`: `10` (Đúng yêu cầu Lab 06)
- `DAILY_BUDGET_USD`: `10.0` (Đúng yêu cầu Lab 06)

## Screenshots
- [x] **Deployment dashboard**: Dashboard Render hiển thị dịch vụ Web và Redis xanh (Healthy).
- [x] **Service running**: Log hệ thống hiển thị Agent khởi động và kết nối Redis thành công.
- [x] **Test results**: Kết quả gọi API thành công hiển thị trên Dashboard UI của chúng tôi.

---
*Generated: 2026-04-17*
