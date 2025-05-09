# Grid'5000 OAR Experiment Commands

This file documents the key commands used to run and manage experiments on Grid'5000 using OAR.

---

## 1. Setup Script

Create the experiment script and make it executable:

```bash
nano run_experiment.sh   # Paste your experiment code here
chmod +x run_experiment.sh
```

## 2. Job Submission

Below are various `oarsub` commands used to launch jobs with different resources.

### 🔹 Basic Submissions

```bash
# CPU-only job (did not use GPU)
oarsub -l "nodes=2/core=16,walltime=2:00:00" ~/run_experiment.sh
oarsub -l "nodes=2/core=64,walltime=12:00:00" ~/run_experiment.sh
```
### 🔹 GPU Jobs
```bash
# Basic GPU job
oarsub -l nodes=1/gpu=1,walltime=12:00:00 ~/run_experiment.sh

# GPU with 'exotic' type
oarsub -t exotic -l "nodes=1/gpu=1,walltime=5:00:00" ~/run_experiment.sh

# GPU with constraints (excluding T4, requiring ≥ 40GB GPU RAM)
oarsub -t exotic -l "nodes=1/gpu=1,walltime=12:00:00" -p "gpu_model!='T4' and gpu_mem>=40960" ~/run_experiment.sh

# With night resource reservation
oarsub -t exotic -l "nodes=1/gpu=1,walltime=05:00:00" -t night -p "gpu_model!='T4' and gpu_mem>=40960" ~/run_experiment.sh
oarsub -t exotic -l nodes=1/gpu=1,walltime=12:00:00 -t night -p gpu_model!='T4' and gpu_mem>=40960 ~/run_experiment.sh

# GPU job without 'exotic'
oarsub -l nodes=1/gpu=1,walltime=10:00:00 -t night -p "gpu_mem>=40960" ~/run_experiment.sh
oarsub -l nodes=1/gpu=1,walltime=05:25:00 -p "gpu_mem>=40960" ~/run_experiment.sh
```

### 🔹 Architecture Constraints
```bash
# Use only x86_64 CPUs
oarsub -l nodes=4/core=64,walltime=12:00:00 -p "cpuarch != 'ppc64le'" ~/run_experiment.sh
```

## 3. Monitoring & Logs
```bash
# Check running jobs
oarstat -u

# Check details of a specific job
oarstat -f -j [job_id]

# View job output
cat OAR.<job_id>.stdout
```

## 4. File Transfer and Disk Usage
```bash
# Copy folder to Grid'5000
scp -r ~/your_folder site.grid5000.fr:~/destination/

# Show largest files
du -ah ~/ | sort -rh | head -n 10

# Sync while excluding files (e.g., virtualenvs)
rsync -av --exclude='myenv' source_folder/ destination_folder/

# Check disk quota
quota -s
```

## 5. Node Discovery (Using jq and oarnodes)
```bash
# List Alive nodes with GPU and x86_64 CPUs
oarnodes -J | jq 'to_entries[] | select(.value.state == "Alive" and .value.gpu != null and .value.cpuarch == "x86_64") | .value.network_address'

# List architectures of Alive GPU nodes
oarnodes -J | jq 'to_entries[] | select(.value.state == "Alive" and .value.gpu != null and .value.cpuarch != null) | .value.cpuarch'
```

## Notes
Only some commands work differently depending on the type of the reserved material — test each one with oarsub -C (check mode) before real submission.

Also adjust paths, and preferrably use full paths for job submission (avoid using `~`).

Adjust `gpu_model`, `gpu_mem`, and `cpuarch` constraints to suit available resources on your Grid'5000 site.