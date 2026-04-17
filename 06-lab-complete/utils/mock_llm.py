import random
import re

MESSAGES = [
    "Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.",
    "Bản demo này đang sử dụng Mock LLM. Bạn có thể cấu hình API Key thật để nhận câu trả lời thực tế.",
    "Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé."
]

def ask(question: str, history: list = None) -> str:
    # 1. Look for name in current question
    name_match = re.search(r"(?:tên tôi là|tôi là|gọi tôi là)\s+([A-ZÀ-Ỹa-zà-ỹ\s]+)", question, re.I)
    if name_match:
        name = name_match.group(1).strip()
        return f"Chào {name}! Tôi đã ghi nhớ tên của bạn vào Redis rồi nhé."

    # 2. Look for name in history
    user_name = None
    if history:
        for msg in history:
            if msg['role'] == 'user':
                match = re.search(r"(?:tên tôi là|tôi là|gọi tôi là)\s+([A-ZÀ-Ỹa-zà-ỹ\s]+)", msg['content'], re.I)
                if match:
                    user_name = match.group(1).strip()
    
    # 3. Handle "What is my name" question
    if re.search(r"tên tôi là gì", question, re.I):
        if user_name:
            return f"Tên bạn là {user_name}. Tôi nhớ bạn mà!"
        else:
            return "Bạn chưa giới thiệu tên. Hãy nói 'Tôi là [Tên]' để tôi ghi nhớ nhé."

    # Default random response
    return random.choice(MESSAGES)
