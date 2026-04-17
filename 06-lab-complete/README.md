# Lab 12 — Complete Production Agent

Kết hợp TẤT CẢ những gì đã học trong 1 project hoàn chỉnh.

## Checklist Deliverable

- [x] Dockerfile (multi-stage, < 500 MB)
- [x] docker-compose.yml (agent + redis)
- [x] .dockerignore
- [x] Health check endpoint (`GET /health`)
- [x] Readiness endpoint (`GET /ready`)
- [x] API Key authentication
- [x] Rate limiting
- [x] Cost guard
- [x] Config từ environment variables
- [x] Structured logging
- [x] Graceful shutdown
- [x] Public URL ready (Railway / Render config)

---

## Cấu Trúc

```
06-lab-complete/
├── app/
│   ├── main.py         # Entry point — Unified Backend + UI
│   ├── ...
├── static/             # High-Tech UI Dashboard (HTML/CSS/JS)
├── utils/
│   └── mock_llm.py     # Smart Mock LLM with memory
├── Dockerfile          # Unified Multi-stage build
├── ...
```

---

## 🎨 Integrated UI Dashboard
Hệ thống hiện đã tích hợp sẵn giao diện Web. Truy cập địa chỉ gốc (`/`) để sử dụng:
- **Xác thực JWT**: Đăng nhập trực tiếp trên web.
- **Trí nhớ (Memory)**: Agent nhớ tên bạn qua Redis.
- **Theo dõi Instance**: Xem ID container đang xử lý request.

---

## ⚙️ Thông số Production (Lab 06 Compliance)
- **Rate Limit**: 10 requests / minute.
- **Daily Budget**: $10.0.
- **Auth**: API Key + JWT (Bearer).
- **Storage**: Stateless (Redis support).

---

## Chạy Local

```bash
# 1. Setup
cp .env.example .env

# 2. Chạy với Docker Compose
docker compose up

# 3. Test
curl http://localhost/health

# 4. Lấy API key từ .env, test endpoint
API_KEY=$(grep AGENT_API_KEY .env | cut -d= -f2)
curl -H "X-API-Key: $API_KEY" \
     -X POST http://localhost/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What is deployment?"}'
```

---

## Deploy Railway (< 5 phút)

```bash
# Cài Railway CLI
npm i -g @railway/cli

# Login và deploy
railway login
railway init
railway variables set OPENAI_API_KEY=sk-...
railway variables set AGENT_API_KEY=your-secret-key
railway up

# Nhận public URL!
railway domain
```

---

## Deploy Render

1. Push repo lên GitHub
2. Render Dashboard → New → Blueprint
3. Connect repo → Render đọc `render.yaml`
4. Set secrets: `OPENAI_API_KEY`, `AGENT_API_KEY`
5. Deploy → Nhận URL!

---

## Kiểm Tra Production Readiness

```bash
python check_production_ready.py
```

Script này kiểm tra tất cả items trong checklist và báo cáo những gì còn thiếu.
