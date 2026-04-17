# Day 12 Lab - Mission Answers

## Part 1-4: (Đã hoàn thành ở phần trước)

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes

#### Reliability (5.1-5.2)
- **Health Check**: Triển khai /health (Liveness) và /ready (Readiness).
- **Graceful Shutdown**: Hệ thống bắt tín hiệu SIGTERM và hoàn thành các request dở dang.

#### Scaling & Stateless (5.3-5.4)
Hệ thống sử dụng Redis làm cơ sở dữ liệu Session trung tâm, cho phép mở rộng không giới hạn instance mà vẫn giữ được ngữ cảnh hội thoại.

**📝 Raw Test Output (Proper Scaling Logs):**
```text
--- Request 1 (Initial) ---
Served by: instance-caf792 | Storage: redis
Response: {"session_id":"fe813aa4...","question":"Hi, I am Khanh..."}

--- Request 2 (Session Persistence) ---
Served by: instance-6e58d5 | Storage: redis
Response: {"session_id":"fe813aa4...","question":"What is my name?..."}
```

#### Final Delivery (5.5)
Hệ thống đã Pass toàn bộ Checklist nộp bài.
- **Railway Check**: {"status":"ok","platform":"Railway"}
- **Security Check**: API Key + JWT hoạt động ổn định.
