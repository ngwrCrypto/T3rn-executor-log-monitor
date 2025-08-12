# **T3rn-Executor-Log-Monitor** 🛡️📜

> 🚀 Welcome to the world of log monitoring!  
> With this tool, you'll keep a watchful eye on your T3rn Executor logs and get instant Telegram alerts for important events.  

![Log Monitoring](https://i.imgur.com/6v3m6wP.png)

---

## **📂 File Tree Maze**

```
.
├── docker-compose.yaml   # Environment & config
├── Dockerfile            # Build instructions
├── monitor.py            # Log monitoring logic
└── requirements.txt      # Dependencies list
```

---

## **⚙️ Tech Stack Hoard**

- 🐳 **Docker**
- 🐍 **Python 3.11-slim**
- 📦 **Docker Python SDK**
- 🕸 **Aiohttp**
- 📡 **Telegram Bot API**
- 🔍 **Real-time log filtering**

---

## **📖 How It Works**
This script monitors Docker container logs in real time and sends matching messages to your **Telegram** chat.  

You can configure:
- **Keywords** to trigger alerts (e.g. `ERROR`, `WARNING`)
- **Success messages** to confirm execution steps  
All settings are in **`docker-compose.yaml`**.

---

## **🚀 Deploy on Server**

1. **Clone the repository**  
```bash
git clone https://github.com/yourusername/T3rn-Executor-Log-Monitor.git
cd T3rn-Executor-Log-Monitor
```

2. **Get your Telegram Bot token**  
   - Open Telegram and search for **@BotFather**  
   - Run `/newbot` and follow the steps to create your bot  
   - Run `/token` to get your bot token  
   - Copy the token (e.g., `123456789:ABCDEF...`)

3. **Edit `docker-compose.yaml`**  
    - nano docker-compose.yaml
   - Paste your token into the `TOKEN` field.

4. **Run the monitor**  
```bash

docker-compose up -d
 or 
 tmux new -s t3rn-monitor
 docker-compose up -d
```

5. **Start the bot in Telegram**  
   - Open your bot in Telegram  
   - Send `/start` to activate monitoring

---

## **🔧 Example docker-compose.yaml**
```yaml
version: '3.8'

services:
  log-monitor:
    build: .
    container_name: log-monitor
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - TOKEN=123456789:ABCDEF...
      - CONTAINER_NAME=executor-release-executor-1
      - KEYWORDS=ERROR,WARNING,warn
      - SUCCESS_PATTERNS="\"msg\":\"✅ Bid successful\",\"msg\":\"📦️ ✅ Tx batch item successful.\""
    restart: unless-stopped
```

---

## **🖼️ Screenshots**

**Telegram Alerts Example**  
![Telegram Alerts](https://i.imgur.com/Bl3YgRa.png)

**Live Log Monitoring**  
![Logs in Action](https://i.imgur.com/xqf9qNm.png)

---

## **💡 FAQ**

**Q:** What does this do?  
**A:** It monitors your container logs and sends matching messages to your Telegram chat.  

**Q:** Why is it not working?  
**A:** Make sure the container is running:  
```bash
docker ps
```
Then restart the monitor:  
```bash
docker-compose up -d --build
```

**Q:** How to add more keywords?  
**A:** Update the `KEYWORDS` variable in `docker-compose.yaml`.

---

## **🤝 Contributing**
Pull requests are welcome! Open an issue for feature requests or bug reports.

---

## **📜 License**
MIT — free to use, modify, and share.  
Code is open source — feel free to explore every line.

---

💬 *Now you’re part of the T3rn-Executor-Log-Monitor crew!*  
Logs are meant to be logged, tea is meant to be sipped! ☕🐍  
