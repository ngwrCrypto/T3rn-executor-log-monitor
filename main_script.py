import asyncio
import docker
import aiohttp
from typing import Optional, List, Dict, Any

# ===== Configuration =====
TOKEN: str = "ВАШ_BOT_TOKEN"  # Insert your Telegram bot token here
CONTAINER_NAME: str = "executor-release-executor-1"  # Name of the container to monitor
KEYWORDS: List[str] = ["ERROR", "WARNING"]  # Keywords for log filtering

user_chat_id: Optional[int] = None
last_update_id: int = 0

# Get the chat_id on startup by listening for the /start command
async def get_chat_id() -> None:
    """
    Polls the Telegram API to find the user's chat_id by listening for the /start command.
    """
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

# Send a message to Telegram
async def send_to_telegram(session: aiohttp.ClientSession, message: str) -> None:
    """
    Sends a message to the user's chat_id in Telegram.
    
    Args:
        session: An aiohttp.ClientSession object.
        message: The message string to be sent.
    """
    if user_chat_id is None:
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        await session.post(url, data={"chat_id": user_chat_id, "text": message})
    except Exception as e:
        print(f"[ERROR] send_to_telegram: {e}")

# Monitor the container logs
async def monitor_container(container: docker.models.containers.Container, session: aiohttp.ClientSession) -> None:
    """
    Monitors the logs of a given Docker container, filters for keywords,
    and sends matching log lines to Telegram.

    Args:
        container: A docker.models.containers.Container object.
        session: An aiohttp.ClientSession object.
    """
    print(f"[INFO] Monitoring container: {container.name}")
    try:
        for line in container.logs(stream=True, follow=True):
            log_line: str = line.decode("utf-8", errors="ignore").strip()
            if any(keyword in log_line for keyword in KEYWORDS):
                print(f"[MATCH] {container.name}: {log_line}")
                await send_to_telegram(session, f"[{container.name}] {log_line}")
    except Exception as e:
        print(f"[ERROR] monitor_container: {e}")

# Main execution loop
async def main() -> None:
    """
    The main coroutine that sets up the Docker client, finds the container,
    and starts the monitoring process.
    """
    client: docker.DockerClient = docker.from_env()
    containers: List[docker.models.containers.Container] = [
        c for c in client.containers.list() if c.name == CONTAINER_NAME
    ]
    if not containers:
        print(f"[ERROR] No container found with name '{CONTAINER_NAME}'")
        return

    await get_chat_id()

    async with aiohttp.ClientSession() as session:
        tasks: List[asyncio.Task] = [monitor_container(c, session) for c in containers]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())