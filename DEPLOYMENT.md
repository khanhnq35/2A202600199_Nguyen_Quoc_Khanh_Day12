# Deployment Information - AI Agent Day 12

## Public URLs

### 1. Railway (Primary)
- **URL**: [https://outstanding-manifestation-production-c4c3.up.railway.app](https://outstanding-manifestation-production-c4c3.up.railway.app)
- **Status**: Live 🟢

### 2. Render (Secondary/IaC)
- **URL**: [https://ai-agent-khanh.onrender.com/](https://ai-agent-khanh.onrender.com/)
- **Status**: Live 🟢

## Test Commands

### 1. Health Check
```bash
curl https://outstanding-manifestation-production-c4c3.up.railway.app/health
# Expected: {"status": "ok", "uptime_seconds": ...}
```

### 2. Security Test (API Key)
```bash
# Gửi request không có key (Mong đợi 401)
curl -i https://outstanding-manifestation-production-c4c3.up.railway.app/ask

# Gửi request với đúng key
curl -X POST https://outstanding-manifestation-production-c4c3.up.railway.app/ask \
  -H "X-API-Key: YOUR_AGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello Agent"}'
```

## Infrastructure Settings (Environment Variables)
- `PORT`: Tự động (8000)
- `AGENT_API_KEY`: [Cấu hình trên Dashboard]
- `JWT_SECRET`: [Cấu hình trên Dashboard]
- `REDIS_URL`: [Chỉ dùng cho bản Scaling/Stateless]

## Deployment Screenshots
*Các ảnh screenshot đang nằm trong folder `screenshots/` (nếu có).*
- [x] Dashboard Railway
- [x] Dashboard Render
- [x] Test API thành công
