# Software & Deployment — The Synthetic Germinal Center

## GPU Server Access

- **Host:** `172.16.1.80`
- **User:** `michael`
- **SSH:** Key-based auth (ed25519) — no password needed
- **Connect:** `ssh michael@172.16.1.80`
- **GPU:** NVIDIA GeForce RTX 2080 Ti (11 GB VRAM)

## Simulation Deployment

### One-time setup (already done if running)
```bash
# Copy simulation code to server
scp -r experiments/EXP_002/simulation michael@172.16.1.80:~/gc_simulation/

# Install JAX with CUDA on server
ssh michael@172.16.1.80 "pip3 install --user 'jax[cuda12]' numpy matplotlib tqdm pytest"
```

### Run simulation
```bash
# Paper-accurate (dt=0.002, 21 days)
ssh michael@172.16.1.80 "cd ~/gc_simulation && python3 run.py --days 21 --seed 42"

# Quick test
ssh michael@172.16.1.80 "cd ~/gc_simulation && python3 run.py --days 3 --seed 42"
```

### Check GPU status
```bash
ssh michael@172.16.1.80 "nvidia-smi"
```

## Other Services on Server

Ollama runs on the server for the lab agent (port 11434, ~800 MiB VRAM).
It can coexist with the simulation — total VRAM usage stays under 11 GB.
Only stop Ollama if VRAM is tight:
```bash
ssh michael@172.16.1.80 "sudo systemctl stop ollama"
# Restart after: sudo systemctl start ollama
```
