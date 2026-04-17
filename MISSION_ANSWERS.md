# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production (Đã hoàn thành)
## Part 2: Docker (Đã hoàn thành)
## Part 3: Cloud Deployment (Đã hoàn thành)
## Part 4: API Security (Đã hoàn thành)

## Part 5: Scaling & Reliability

### Exercise 5.1: Health Checks
- **Cơ chế**: Dùng /health (Liveness) và /ready (Readiness).
- **Kết quả**: Server tự báo cáo trạng thái RAM/Uptime để Cloud tự restart khi cần.

### Exercise 5.2: Graceful Shutdown
- **Cơ chế**: Bắt tín hiệu SIGTERM và đợi request hoàn tất.
- **Kết quả**: Không ngắt kết nối đột ngột với người dùng trong quá trình bảo trì.

### Exercise 5.3: Stateless Design
- **Cơ chế**: Lưu Conversation History vào Redis thay vì RAM.
- **Kết quả**: Bất kỳ Instance nào cũng có thể tiếp tục cuộc hội thoại của người dùng.

### Exercise 5.4: Scaling & Load Balancing
- **Cơ chế**: Sử dụng Nginx làm Reverse Proxy điều phối traffic Round Robin.
- **Kết quả**: Tăng khả năng chịu tải và tính sẵn sàng cho hệ thống.

### Exercise 5.5: Final Delivery Checklist
- **Cơ chế**: Rà soát 100% checklist nộp bài và verify live trên Railway.
- **Kết quả**: Hệ thống đạt chuẩn Production-ready.
