import os
import asyncio
import docker
import aiohttp
from typing import Optional, List, Dict, Any

# ===== Configuration from ENV =====
TOKEN: str = os.getenv("TOKEN", "")
CONTAINER_NAME: str = os.getenv("CONTAINER_NAME", "")
KEYWORDS: List[str] = os.getenv("KEYWORDS", "ERROR,WARNING").split(",")

user_chat_id: Optional[int] = None
last_update_id: int = 0

if not TOKEN:
    raise ValueError("[ERROR] TOKEN is not set in environment variables!")
if not CONTAINER_NAME:
    raise ValueError("[ERROR] CONTAINER_NAME is not set in environment variables!")

# Get the chat_id on startup by listening for the /start command
async def get_chat_id() -> None:
    global user_chat_id, last_update_id
    async with aiohttp.ClientSession() as session:
        print(f"[INFO] Waiting for /start in Telegram chat...")
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

# Send message to Telegram
async def send_to_telegram(session: aiohttp.ClientSession, message: str) -> None:
    if user_chat_id is None:
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        await session.post(url, data={"chat_id": user_chat_id, "text": message})
    except Exception as e:
        print(f"[ERROR] send_to_telegram: {e}")

# Monitor the container logs
async def monitor_container(container: docker.models.containers.Container, session: aiohttp.ClientSession) -> None:
    print(f"[INFO] Monitoring container: {container.name}")
    try:
        for line in container.logs(stream=True, follow=True):
            log_line: str = line.decode("utf-8", errors="ignore").strip()
            if any(keyword in log_line for keyword in KEYWORDS):
                print(f"[MATCH] {container.name}: {log_line}")
                await send_to_telegram(session, f"[{container.name}] {log_line}")
    except Exception as e:
        print(f"[ERROR] monitor_container: {e}")

# Main
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
