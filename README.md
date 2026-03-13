# Watcher 

> Real-time AI GPU health coach. Watches your GPU metrics, diagnoses bottlenecks, and explains fixes in plain English.


## one command setup

```bash
# Clone the repo 
git clone <repo-url>
cd watcher

# add nvidia container toolkit (execute one setup-nvidia-gpu.sh file) - skip if already have
bash setup-nvidia-gpu.sh

# Start with docker-compose
docker-compose up --build
```

Then open: **http://localhost:8000**


things to add -
- [x] read nvidia-smi
- [x] rule based diagnosis
- [x] llm based diagnosis & reasoning
- [ ] add vsison sdk to monitor
- [ ] monitor via prometheus
- [ ] make cli version