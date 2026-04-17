# Report: Lab Task 1.1 - Phát hiện Anti-patterns

Dưới đây là các vấn đề (anti-patterns) được phát hiện trong file `01-localhost-vs-production/develop/app.py`:

| STT | Vấn đề | Chi tiết | Tại sao là anti-pattern? |
|-----|--------|----------|--------------------------|
| 1 | **Hardcoded Secrets** | `OPENAI_API_KEY` và `DATABASE_URL` được viết trực tiếp trong code. | Dễ bị lộ khi push lên GitHub/GitLab. Nên dùng environment variables (.env). |
| 2 | **Thiếu Config Management** | Các biến như `DEBUG`, `MAX_TOKENS` được fix cứng. | Khó thay đổi cấu hình giữa các môi trường (Dev, Staging, Prod) mà không sửa code. |
| 3 | **Sử dụng `print()` thay vì Logging** | Dùng `print()` để log thông tin và log cả secret key. | `print()` không hỗ trợ log levels, log rotation, và log ra secret key mang lại rủi ro bảo mật lớn. |
| 4 | **Không có Health Check Endpoint** | Thiếu route `/health` hoặc `/ready`. | Platform (Docker, K8s, Cloud Run) không biết tình trạng của agent để tự động restart khi lỗi. |
| 5 | **Host/Port cố định** | `host="localhost"` và `port=8000` được fix cứng. | Agent sẽ không thể nhận traffic từ bên ngoài (trên Cloud) và không linh hoạt theo port do platform cấp. |
| 6 | **Reload Mode bật mặc định** | `reload=True` trong `uvicorn.run`. | Tốn tài nguyên và không an toàn khi chạy trong môi trường production. |

---

## Report: Lab Task 1.2 - Chạy Basic Version

### ⚙️ Thiết lập môi trường
- Tạo virtual environment mới tại `.venv`.
- Cài đặt các thư viện: `fastapi==0.115.0`, `uvicorn[standard]==0.30.0`.

### 🚀 Kết quả chạy thử
- Server khởi chạy thành công tại `http://localhost:8000`.
- **Lỗi phát hiện khi test:** Lệnh `curl` theo hướng dẫn của Lab (truyền JSON body) bị lỗi **422 Unprocessable Entity**.
- **Nguyên nhân:** Hàm `ask_agent(question: str)` trong `app.py` đang mặc định hiểu `question` là query parameter thay vì body parameter.
- **Khắc phục:** Phải gọi API theo dạng `curl "http://localhost:8000/ask?question=Hello" -X POST`.

### 🧐 Quan sát: Có Production-ready không?
**KHÔNG.** Ngoài các anti-patterns đã liệt kê ở Task 1.1, việc chạy thực tế cho thấy thêm các vấn đề:
1. **API Design lỗi thời:** POST request dùng query parameter thay vì JSON body là một thiết kế không tốt và không bảo mật.
2. **Thiếu Input Validation chuyên sâu:** Chỉ check kiểu `str` cơ bản, không có Pydantic model để quản lý schema.
3. **Internal Error Handling:** Không có try-except block để xử lý khi mock_llm gặp lỗi, có thể gây sập server (500 error) mà không có thông báo rõ ràng cho user.

---

## Report: Lab Task 1.3 - So sánh Develop vs Production

Dựa trên việc phân tích mã nguồn giữa hai phiên bản, dưới đây là bảng so sánh chi tiết:

### Exercise 1.3: Comparison table (Verified by execution ✅)

| Feature | Develop (Basic) | Production (Advanced) | Tại sao quan trọng? |
|---------|---------|------------|---------------------|
| **Config** | Hardcoded trong code. Chạy thử: Không check được lỗi config trước khi run. | Environment Variables. Chạy thử: **Fail-fast** và cảnh báo khi thiếu key. | Bảo mật secrets và linh hoạt môi trường. |
| **Health Check** | Không có. Chạy thử: Platform không thể scan status. | Có `/health` & `/ready`. Chạy thử: **Hoạt động tốt**, trả về JSON status. | Giúp tự động phục hồi và điều phối traffic. |
| **Logging** | Dùng `print()`. Chạy thử: Log lộn xộn, chứa secret. | Structured JSON Logging. Chạy thử: **Sạch sẽ, dễ parse**, không chứa secret. | Dễ dàng debug và monitor ở scale lớn. |
| **Shutdown** | Tắt đột ngột. Chạy thử: Kết nối bị ngắt ngay lập tức. | Graceful Shutdown. Chạy thử: **Xử lý signal**, hoàn thành task trước khi nghỉ. | Tăng độ ổn định và tin cậy cho hệ thống. |
| **Binding & Port** | `localhost:8000`. | `0.0.0.0` + dynamic port. Chạy thử: **Nhận request ngoài container**. | Bắt buộc để deploy lên Cloud/Docker. |
| **Input API** | Query string (Lỗi validation nếu dùng JSON). | JSON Body. Chạy thử: **Validate chuẩn**, dễ mở rộng schema. | Bảo mật và tuân thủ chuẩn REST API. |

---

## 🏁 Checkpoint 1: Tổng kết kiến thức

Dưới đây là tóm tắt các kiến thức cốt lõi đã học được sau Phần 1:

### 1. Tại sao Hardcode Secrets lại nguy hiểm?
- **Rò rỉ bảo mật:** Nếu push code lên GitHub/GitLab, các API Key và mật khẩu database sẽ bị lộ ngay lập tức. Kẻ xấu có thể dùng tool scan để lấy cắp và trục lợi (ví dụ: dùng hết quota OpenAI của bạn).
- **Khó quản lý:** Mỗi khi muốn đổi key, bạn phải sửa code và deploy lại toàn bộ app.

### 2. Cách sử dụng Environment Variables đúng chuẩn
- **Tách biệt Config và Code:** Sử dụng file `.env` (không được push lên Git) và dùng thư viện như `python-dotenv` hoặc `pydantic-settings` để đọc biến môi trường.
- **Linh hoạt:** Dễ dàng thay đổi cấu hình cho từng môi trường (Development, Staging, Production) mà không cần chạm vào code.

### 3. Vai trò của Health Check Endpoint (`/health` & `/ready`)
- **Liveness Probe (`/health`):** Giúp Cloud Platform biết app còn "sống" hay đã treo. Nếu app treo, platform sẽ tự động restart container.
- **Readiness Probe (`/ready`):** Giúp Load Balancer biết app đã sẵn sàng nhận request chưa (đã load xong model, đã kết nối xong DB chưa). Tránh việc gửi request vào app khi nó đang khởi động.

### 4. Graceful Shutdown là gì?
- **Định nghĩa:** Là khả năng của ứng dụng khi nhận tín hiệu tắt (SIGTERM) sẽ không dừng đột ngột mà sẽ:
    1. Ngừng nhận request mới.
    2. Chờ các request đang xử lý hoàn tất.
    3. Đóng các kết nối database/cache một cách an toàn.
- **Lợi ích:** Tránh mất mát dữ liệu và đảm bảo trải nghiệm người dùng không bị gián đoạn khi thực hiện update hoặc scale-down hệ thống.

---

## Report: Lab Task 2.1 - Dockerfile Cơ Bản

Sau khi phân tích `02-docker/develop/Dockerfile`, dưới đây là câu trả lời cho các câu hỏi tìm hiểu:

### 1. Base image là gì?
- Base image là `python:3.11`. Đây là image đầy đủ của Python 3.11 dựa trên Debian, dung lượng khá lớn (~1 GB) nhưng chứa đầy đủ công cụ cần thiết cho việc phát triển.

### 2. Working directory là gì?
- Working directory là `/app`. Đây là thư mục gốc bên trong container nơi mã nguồn và các tệp tin sẽ được sao chép vào và các câu lệnh sau đó sẽ được thực thi tại đây.

### 3. Tại sao COPY requirements.txt trước?
- **Docker Layer Caching:** Docker build theo từng layer. Nếu chúng ta copy `requirements.txt` và chạy `pip install` trước, Docker sẽ cache layer này lại. 
- Khi bạn sửa code ở `app.py` nhưng không thêm thư viện mới, Docker sẽ dùng lại cache của layer cài đặt thư viện, giúp build cực nhanh (chỉ mất vài giây thay vì phải cài lại toàn bộ thư viện từ đầu).

### 4. CMD vs ENTRYPOINT khác nhau thế nào?
- **CMD:** Cung cấp lệnh mặc định cho container. Người dùng có thể dễ dàng ghi đè (override) lệnh này bằng cách truyền lệnh mới đằng sau `docker run`.
- **ENTRYPOINT:** Thiết lập lệnh chính cho container, khó ghi đè hơn (phải dùng flag `--entrypoint`). Thường dùng để biến container thành một file thực thi (executable).
- **Sự kết hợp:** Nếu dùng cả hai, ENTRYPOINT sẽ là lệnh chính, và CMD sẽ đóng vai trò là tham số mặc định cho lệnh đó.

---

## Report: Lab Task 2.2 - Build và Run Docker Image

### 🏗️ Build Image
- **Lệnh thực hiện:** `docker build -f 02-docker/develop/Dockerfile -t my-agent:develop .`
- **Kết quả:** Build thành công image `my-agent:develop`.

### 🚀 Chạy Container & Test
- **Lệnh chạy:** `docker run -d -p 8000:8000 --name my-agent-develop my-agent:develop`
- **Thử nghiệm với Curl:**
    - Lệnh mẫu `curl ... -d '{"question": "..."}'` vẫn bị lỗi **422 Unprocessable Entity** do code `app.py` trong folder này vẫn giữ thiết kế cũ (nhận query param thay vì JSON body).
    - Test thành công khi sử dụng query parameter.

### 📊 Thống kê Image
- **Kích thước Image:** **~1.67 GB** (Disk Usage).
- **Base Image:** `python:3.11`.

### 🧐 Quan sát: Có Production-ready không?
**KHÔNG.** Các lý do chính bao gồm:
1. **Dung lượng quá lớn:** 1.67 GB là quá nặng cho một agent đơn giản, gây tốn tài nguyên lưu trữ và kéo dài thời gian deploy/pull image.
2. **Security:** Image chứa đầy đủ build tools, shell và các package không cần thiết của Debian, làm tăng diện tích tấn công (attack surface).
3. **Layer chưa tối ưu:** Mọi thứ được gói trong một stage duy nhất, không tách biệt được môi trường build và môi trường run.
4. **Secrets:** Nếu có secrets được copy vào trong quá trình build, chúng sẽ tồn tại vĩnh viễn trong các layer của image.

---

## Report: Lab Task 2.3 - Multi-stage Build (Tối ưu hóa Image)

Sau khi triển khai kỹ thuật Multi-stage build, chúng ta đã giải quyết triệt để các vấn đề của phiên bản trước.

### 🕵️ Phân tích cơ chế
- **Stage 1 (Builder):** Sử dụng `python:3.11-slim`, cài đặt các công cụ build (`gcc`, `libpq-dev`) để biên dịch các thư viện Python. Các thư viện được cài vào thư mục `/root/.local`.
- **Stage 2 (Runtime):** Cũng sử dụng `python:3.11-slim` nhưng mục tiêu là sạch nhất có thể. Nó chỉ copy kết quả đã cài đặt (`/root/.local`) từ stage 1 sang. Toàn bộ bộ công cụ build nặng nề (gcc) bị bỏ lại ở stage 1.
- **Security:** Chạy ứng dụng dưới quyền **non-root user** (`appuser`), hạn chế rủi ro nếu container bị tấn công.

### 📊 So sánh kích thước Image

| Image Tag | Kích thước (Disk Usage) | Ghi chú |
|-----------|-------------------------|---------|
| `my-agent:develop` | **1.67 GB** | Single-stage, đầy đủ build tools, nặng nề. |
| `my-agent:advanced` | **262 MB** | **Multi-stage**, cực kỳ nhẹ, tối ưu cho production. |

**=> Image giảm được khoảng 84% dung lượng!**

### 💡 Tại sao Image nhỏ hơn?
1. **Loại bỏ Build Tools:** Các package như `gcc` và bộ nhớ tạm của `apt` chiếm rất nhiều dung lượng nhưng không cần thiết khi chạy ứng dụng. Multi-stage đã loại bỏ chúng ở image cuối cùng.
2. **Sử dụng Slim Image:** Cả hai stage đều dùng `3.11-slim` thay vì bản `3.11` đầy đủ, giúp giảm base layer từ ~1GB xuống ~100MB.
3. **Loại bỏ Cache:** Chỉ copy những gì cần thiết, không copy các file log, cache cài đặt của pip.

---

## Report: Lab Task 3.1 - Cloud Deployment (Railway)

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

## Report: Lab Task 3.2 - Cloud Deployment (Render Blueprint)

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

## Report: Lab Task 4.1 - API Key Authentication

Chúng ta đã triển khai lớp bảo vệ đầu tiên cho API bằng cơ chế kiểm tra Header Token.

### 🕵️ Phân tích Code
- **Cơ chế**: Sử dụng `APIKeyHeader` của FastAPI để bắt header `X-API-Key`.
- **Logic kiểm tra**: Hàm `verify_api_key` so khớp key từ Header với biến môi trường `AGENT_API_KEY`.
- **Xử lý lỗi**:
    - Thiếu Key: Trả về **401 Unauthorized**.
    - Sai Key: Trả về **403 Forbidden**.
- **Ưu điểm**: Đơn giản, dễ triển khai cho hệ thống B2B hoặc tích hợp nội bộ.
- **Nhược điểm**: Key cố định, khó quản lý khi có hàng ngàn user khác nhau (cần chuyển sang JWT).

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

## Report: Lab Task 4.2 - JWT Authentication (Advanced)

Chúng ta đã nâng cấp hệ thống bảo mật từ API Key tĩnh sang JWT (JSON Web Token) động và phân quyền theo vai trò (RBAC).

### 🏛️ Phân tích cơ chế
- **Stateless**: Server không cần lưu session, mọi thông tin (username, role) nằm trong Token.
- **Phân quyền (RBAC)**: 
    - `user`: Chỉ được gọi endpoint `/ask`.
    - `admin`: Được phép truy cập `/admin/stats` để theo dõi hệ thống.
- **Security Headers**: Đã cấu hình các header bảo mật (`X-Frame-Options`, `X-Content-Type-Options`) và ẩn thông tin Server.

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

**=> Kết luận:** Hệ thống đã đạt tiêu chuẩn sản xuất (Production-ready) về mặt bảo mật và phân quyền.

