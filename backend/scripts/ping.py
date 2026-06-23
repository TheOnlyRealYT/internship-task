import httpx
from datetime import datetime, timezone

sent_at = datetime.now(timezone.utc)
response = httpx.get(
    "http://localhost:80/api/v1/ping",
    params={"client_sent_at": sent_at.isoformat()}
)
received_at = datetime.now(timezone.utc)

round_trip_ms = (received_at - sent_at).total_seconds() * 1000
print(f"Round trip: {round_trip_ms:.2f}ms")
print(response.json())