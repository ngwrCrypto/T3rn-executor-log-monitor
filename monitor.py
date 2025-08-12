import asyncio
import docker
import aiohttp
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

# ===== Config from env =====
TOKEN: str = os.getenv("TOKEN", "")
CONTAINER_NAME: str = os.getenv("CONTAINER_NAME", "")
KEYWORDS: List[str] = [k.strip() for k in os.getenv("KEYWORDS", "").split(",") if k.strip()]
SUCCESS_PATTERNS: List[str] = [p.strip() for p in os.getenv("SUCCESS_PATTERNS", "").split(",") if p.strip()]

user_chat_id: Optional[int] = None
last_update_id: int = 0

# === Get chat_id ===
async def get_chat_id() -> None:
    global user_chat_id, last_update_id
    async with aiohttp.ClientSession() as session:
        while user_chat_id is None:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            if last_update_id:
                url += f"?offset={last_update_id + 1}"
            try:
                async with session.get(url) as resp:
                    data: Dict[str, Any] = await resp.json()
                    for update in data.get("result", []):
                        last_update_id = update["update_id"]
                        if "message" in update and "text" in update["message"]:
                            if update["message"]["text"] == "/start":
                                user_chat_id = update["message"]["chat"]["id"]
                                print(f"[INFO] Received chat_id: {user_chat_id}")
                                await send_to_telegram(session, "✅ Log monitoring started")
                                return
            except Exception as e:
                print(f"[ERROR] get_chat_id: {e}")
            await asyncio.sleep(2)

# === Send to Telegram ===
async def send_to_telegram(session: aiohttp.ClientSession, message: str) -> None:
    if user_chat_id is None:
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        await session.post(url, data={"chat_id": user_chat_id, "text": message})
    except Exception as e:
        print(f"[ERROR] send_to_telegram: {e}")

# === Monitor container logs ===
async def monitor_container(container: docker.models.containers.Container, session: aiohttp.ClientSession) -> None:
    print(f"[INFO] Monitoring container: {container.name}")
    try:
        for line in container.logs(stream=True, follow=True, since=int(datetime.now().timestamp())):
            log_line: str = line.decode("utf-8", errors="ignore").strip()
            if should_notify(log_line):
                formatted_message = format_log_message(log_line, container.name)
                print(f"[MATCH] {container.name}: {formatted_message}")
                await send_to_telegram(session, formatted_message)
    except Exception as e:
        print(f"[ERROR] monitor_container: {e}")

# === Filtering logic ===
def should_notify(log_line: str) -> bool:
    return (
        any(k.lower() in log_line.lower() for k in KEYWORDS) or
        any(p in log_line for p in SUCCESS_PATTERNS)
    )

# === Format log for Telegram ===
def format_log_message(raw_log: str, container_name: str) -> str:
    try:
        log_data = json.loads(raw_log)
        timestamp = datetime.fromtimestamp(log_data.get("time", datetime.now().timestamp()) / 1000)
        level = log_data.get("level", "info").upper()

        pretty_json = json.dumps(log_data, indent=2, ensure_ascii=False)

        return (
            f"📅 {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"📌 Level: {level}\n"
            f"📦 {container_name}\n\n"
            f"{pretty_json}"
        )
    except Exception:

        return (
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"📦 {container_name}\n\n"
            f"{raw_log}"
        )

# === Main ===
async def main() -> None:
    client: docker.DockerClient = docker.from_env()
    containers = [c for c in client.containers.list() if c.name == CONTAINER_NAME]
    if not containers:
        print(f"[ERROR] No container found with name '{CONTAINER_NAME}'")
        return

    await get_chat_id()

    async with aiohttp.ClientSession() as session:
        tasks = [monitor_container(c, session) for c in containers]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
