# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. **Hardcoded Secrets**: Lưu API Key trực tiếp trong code (Vd: `AGENT_API_KEY = "my-key"`).
2. **Fixed Port**: Fix cứng port 8000 thay vì dùng biến môi trường `PORT` từ Cloud.
3. **In-memory Storage**: Lưu trữ session trong RAM thay vì Redis (dễ mất dữ liệu khi restart/scale).
4. **Lack of Authentication**: Endpoint không có lớp bảo mật trên local.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| **Config**  | `.env` / Hardcoded | Environment Variables | Bảo mật secret key |
| **Security**| No Auth | JWT / API Key | Ngăn chặn truy cập trái phép |
| **Scaling** | Single process | Multiple instances | Chịu tải cao |
| **Storage** | RAM | Redis | Đảm bảo tính nhất quán dữ liệu |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. **Base image**: `python:3.10-slim`.
2. **Working directory**: `/app`.
3. **Multi-stage**: Giúp giảm kích thước image và tăng tính bảo mật (loại bỏ build tools).

### Exercise 2.3: Image size comparison
- **Develop**: ~900 MB (bao gồm đầy đủ SDK/Tools)
- **Production**: ~200 MB (chỉ bao gồm runtime cần thiết)
- **Difference**: Giảm ~75% kích thước.

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- **URL**: [https://outstanding-manifestation-production-c4c3.up.railway.app](https://outstanding-manifestation-production-c4c3.up.railway.app)
- **Platform**: Railway (Automated Build & Deploy)

### Exercise 3.2: Render deployment
- **URL**: [https://ai-agent-khanh.onrender.com/](https://ai-agent-khanh.onrender.com/)
- **Method**: Infrastructure as Code (render.yaml)

## Part 4: API Security

### Exercise 4.1-4.3: Test results
Hệ thống đã được bảo mật với 3 lớp: API Key, JWT (RBAC) và Rate Limiting.
- **API Key**: Chặn truy cập nặc danh (401/403).
- **JWT**: Phân quyền Admin/User thành công.
- **Rate Limit**: Chặn SPAM thành công (429) sau 10 requests/phút.

### Exercise 4.4: Cost guard implementation
- **Cơ chế**: Theo dõi token usage thực tế và quy đổi ra USD.
- **Chốt chặn**: Chặn ngay lập tức (402) khi user vượt định mức $1/ngày.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes

#### Exercise 5.1-5.2: Reliability
- **Liveness/Readiness**: `/health` và `/ready` endpoints giúp Cloud Platform quản lý container.
- **Graceful Shutdown**: Server bắt tín hiệu SIGTERM và đợi request hoàn tất trước khi tắt.

#### Exercise 5.3-5.4: Scaling & Stateless
- **Redis Integration**: Chuyển session từ RAM sang Redis giúp hệ thống chạy multi-instance.
- **Load Balancing**: Nginx phân phối tải đều cho các Agent instances.
