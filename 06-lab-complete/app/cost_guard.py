import time
import logging
from dataclasses import dataclass, field
from fastapi import HTTPException
from app.config import settings

logger = logging.getLogger(__name__)

# Standard Pricing (Mock)
PRICE_PER_1K_INPUT_TOKENS = 0.00015   # $0.15/1M input
PRICE_PER_1K_OUTPUT_TOKENS = 0.0006   # $0.60/1M output

@dataclass
class UsageRecord:
    user_id: str
    input_tokens: int = 0
    output_tokens: int = 0
    request_count: int = 0
    day: str = field(default_factory=lambda: time.strftime("%Y-%m-%d"))

    @property
    def total_cost_usd(self) -> float:
        input_cost = (self.input_tokens / 1000) * PRICE_PER_1K_INPUT_TOKENS
        output_cost = (self.output_tokens / 1000) * PRICE_PER_1K_OUTPUT_TOKENS
        return round(input_cost + output_cost, 6)

class CostGuard:
    def __init__(self, daily_budget_usd: float = 1.0):
        self.daily_budget_usd = daily_budget_usd
        self._records: dict[str, UsageRecord] = {}

    def _get_record(self, user_id: str) -> UsageRecord:
        today = time.strftime("%Y-%m-%d")
        record = self._records.get(user_id)
        if not record or record.day != today:
            self._records[user_id] = UsageRecord(user_id=user_id, day=today)
        return self._records[user_id]

    def check_budget(self, user_id: str) -> None:
        record = self._get_record(user_id)
        if record.total_cost_usd >= self.daily_budget_usd:
            logger.warning(f"Budget breach for {user_id}: ${record.total_cost_usd}")
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "Daily budget exceeded",
                    "used": record.total_cost_usd,
                    "limit": self.daily_budget_usd
                }
            )

    def record_usage(self, user_id: str, input_tokens: int, output_tokens: int) -> UsageRecord:
        record = self._get_record(user_id)
        record.input_tokens += input_tokens
        record.output_tokens += output_tokens
        record.request_count += 1
        return record

    def get_stats(self, user_id: str) -> dict:
        record = self._get_record(user_id)
        return {
            "daily_cost_usd": record.total_cost_usd,
            "daily_budget_usd": self.daily_budget_usd,
            "requests_today": record.request_count,
            "used_pct": round(record.total_cost_usd / self.daily_budget_usd * 100, 2) if self.daily_budget_usd > 0 else 0
        }

# Singleton instance
cost_guard = CostGuard(daily_budget_usd=settings.daily_budget_usd)
