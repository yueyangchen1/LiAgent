# Hidden Licensing Risks in the PTMware Ecosystem — Artifact

This repository contains the artifact for the paper **"Hidden Licensing Risks in the PTMware Ecosystem"**, accepted at ISSTA 2026.

The artifact includes:
1. **LiAgent** — An LLM-based multi-agent tool for license compatibility analysis.
2. **Empirical Study Data** — All datasets and analysis scripts for RQ1–RQ4.

---

## Part 1: Getting Started Guide

### 1.1 Artifact Description

This artifact accompanies our study on licensing risks in the PTMware (Pre-Trained Model software) ecosystem. It consists of two parts:

- **LiAgent Tool** (`LiAgent/`): Uses LLM-based agents (extraction agent + repair agent) to extract license terms and detect license incompatibilities. It takes license text files as input and outputs structured term-attitude triples (can/cannot/must) for 23 license terms.
- **Empirical Study Data** (`data/`): Curated datasets covering 12,180 GitHub repositories, 3,988 LLMs, and 708 datasets from Hugging Face. See [`data/README.md`](data/README.md) for details.

### 1.2 Prerequisites

- **Docker** (recommended) or Python 3.8+ with pip
- **An LLM API key**: LiAgent supports any OpenAI-compatible API (e.g., OpenAI GPT-4o, DeepSeek). You need at least one valid API key.
- **Disk space**: ~100 MB for the artifact, ~500 MB for the Docker image.
- **Internet access**: Required only for LLM API calls.

### 1.3 Installation

#### Option A: Using Pre-built Docker Image (Recommended)

If you have the pre-built Docker image (`liagent-artifact.tar.gz`), load and run it directly:

```bash
docker load -i liagent-artifact.tar.gz
docker run -it liagent:v1.0 bash
```

#### Option B: Building Docker Image from Source

Alternatively, you can build the Docker image yourself from the Dockerfile:

```bash
docker build -t liagent .
docker run -it liagent /bin/bash
```

#### Option C: Local Installation (Without Docker)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 1.4 Configuration

LiAgent requires an LLM API key. We use [DeepSeek](https://platform.deepseek.com/) by default (new users receive free credits upon registration).

1. Register at https://platform.deepseek.com/ and obtain an API key.
2. Configure the key in `LiAgent/config.yaml`:

```yaml
models:
  deepseek-chat:
    api_key: "YOUR_API_KEY_HERE"
    base_url: "https://api.deepseek.com"
```

> **Note**: LiAgent also supports any OpenAI-compatible API (e.g., OpenAI GPT-4o). Simply change the `base_url` and `api_key` accordingly.

### 1.5 Smoke Test

#### If using Docker (already inside `/artifact/LiAgent`):

```bash
# The sample license (llama2.txt) is pre-loaded in the Docker image
python analyseLicense.py
```

#### If using local installation:

```bash
cd LiAgent
mkdir -p license
cp ../data/rq4_license_groundtruth/ai_16/license/llama2.txt license/
python analyseLicense.py
```

**Expected output** (completes within ~5 minutes):

- **Console output**: `Processing file: license/llama2.txt` → ... → `✅ Processing completed.`
- **`result.csv`** — A CSV file where each row is a license and each column is one of 23 license terms. Values: `0` = not mentioned, `1` = can, `2` = cannot, `3` = must.
- **`result/`** — A directory containing **human-readable summaries** for each license. These are the most intuitive way to view results. Each file looks like:

  ```
  ==================================================
  LICENSE SUMMARY: llama2.txt
  ==================================================

  🟢 YOU CAN:
  --------------------------------------------------
  - Distribute
  - Modify

  🔴 YOU CANNOT:
  --------------------------------------------------
  - Commercial Use
  - Hold Liable
  - Sublicense
  - Use Trademark
  - Private Use

  ⚠️ YOU MUST:
  --------------------------------------------------
  - Include License

  ==================================================
  Processed by: LiAgent
  ```

  > **Tip**: You can browse all summary files with `cat result/*` or open any individual file (e.g., `cat result/llama2.txt`).

- **`tmp/`** — Intermediate processing files (split text segments and raw LLM outputs). These can be ignored.

Example `result.csv` row:
```
License Name,Distribute,Modify,Commercial Use,Hold Liable,Include Copyright,Include License,Sublicense,Use Trademark,...
llama2.txt,1,1,2,2,0,3,2,2,...
```

**Value encoding**: `0` = not mentioned, `1` = can (permitted), `2` = cannot (prohibited), `3` = must (required).

**How to interpret**: For the Llama 2 license, the result shows: Distribute=1 (allowed), Modify=1 (allowed), Commercial Use=2 (prohibited for >700M monthly users), Hold Liable=2 (prohibited), Include License=3 (required), Sublicense=2 (prohibited). This matches the actual Llama 2 license terms.

**How to verify correctness**: Compare `result.csv` with the corresponding ground truth label CSV file (e.g., `label_ai_16.csv`). Both files use the same format. A correct run should match the ground truth on most entries. Due to LLM non-determinism, minor differences (1–2 cells) are acceptable and expected.

---

## Part 2: Step-by-Step Instructions

### Paper Claims Supported by This Artifact

| Claim | Paper Section | Artifact Support |
|-------|--------------|-----------------|
| **RQ1**: License distribution differs from traditional OSS | §4.1 | `data/rq1_repo_license/` |
| **RQ2**: License selection/maintenance are primary pain points | §4.2 | `data/rq2_issue_discussion_tag/` |
| **RQ3**: 52% of supply chains have license conflicts | §4.3 | `data/rq3_chain_conflict/` |
| **RQ4**: LiAgent achieves 87% F1, outperforming baselines | §4.4 | `LiAgent/` + `data/rq4_license_groundtruth/` |
| **Discussion**: 60 issues reported, 11 confirmed | §5 | `data/discussion/` |

### Paper Claims NOT Fully Supported by the Artifact

The data collection phase (crawling GitHub/Hugging Face metadata) is **not** reproducible via one-click scripts, because:
1. The original crawling was performed over several months; APIs and data may have changed.
2. The metadata snapshots are provided as-is in `data/metadata/`.

### 2.1 Reproducing RQ4 — LiAgent Evaluation (Recommended)

This is the most directly reproducible experiment. LiAgent analyzes licenses from the ground truth dataset and compares results against manual labels.

> **⚠️ Important**: Before running each dataset, you must **clear the `license/` directory** to avoid mixing files from different datasets. Also clear previous outputs to start fresh.

> **Note on LLM non-determinism**: Since LiAgent relies on LLM API calls, results may have slight variations across runs. This is expected behavior and does not affect the overall conclusions.

> **Path note**: In Docker, the working directory is `/artifact/LiAgent` and data is at `/artifact/data/`. For local installation, use relative paths as shown below (run from the repository root, then `cd LiAgent`).

#### Reduced Experiment (~1 hour, recommended for validation)

Run only the 16 AI-specific licenses:

```bash
cd LiAgent   # skip this if already inside Docker
# Clear previous data
rm -rf license tmp result result.csv
mkdir -p license
cp ../data/rq4_license_groundtruth/ai_16/license/* license/
python analyseLicense.py
```

**How to verify**: Compare the generated `result.csv` against the ground truth `../data/rq4_license_groundtruth/ai_16/label_ai_16.csv`. Both files share the same CSV format (rows = licenses, columns = 23 terms, values = 0/1/2/3). You can compare them using any spreadsheet tool or with a simple diff:

```bash
# Quick comparison (shows differences, if any)
diff <(sort result.csv) <(sort ../data/rq4_license_groundtruth/ai_16/label_ai_16.csv)
```

#### Full Experiment

Process each dataset separately (**clear `license/`, `tmp/`, `result/`, and `result.csv` before each run**):

```bash
cd LiAgent   # skip this if already inside Docker

# --- Dataset 1: OSS licenses (124) ---
rm -rf license tmp result result.csv
mkdir -p license
cp ../data/rq4_license_groundtruth/oss_124/license/* license/
python analyseLicense.py
# Compare: diff <(sort result.csv) <(sort ../data/rq4_license_groundtruth/oss_124/label_124.csv)

# --- Dataset 2: AI-specific licenses (16) ---
rm -rf license tmp result result.csv
mkdir -p license
cp ../data/rq4_license_groundtruth/ai_16/license/* license/
python analyseLicense.py
# Compare: diff <(sort result.csv) <(sort ../data/rq4_license_groundtruth/ai_16/label_ai_16.csv)

# --- Dataset 3: OSS Mutated licenses (620) ---
rm -rf license tmp result result.csv
mkdir -p license
cp ../data/rq4_license_groundtruth/ossmut_620/license/* license/
python analyseLicense.py
# Compare: diff <(sort result.csv) <(sort ../data/rq4_license_groundtruth/ossmut_620/label_mutate_620.csv)

# --- Dataset 4: AI Mutated licenses (176) ---
rm -rf license tmp result result.csv
mkdir -p license
cp ../data/rq4_license_groundtruth/aimut_176/license/* license/
python analyseLicense.py
# Compare: diff <(sort result.csv) <(sort ../data/rq4_license_groundtruth/aimut_176/label_mutate_ai_176.csv)
```

### 2.2 Exploring RQ1–RQ3 Data

The data and scripts for RQ1–RQ3 are provided in the `data/` directory. Due to the complexity of real-world license data and the human-in-the-loop refinement process, these scripts are provided primarily for **methodological transparency** rather than one-click reproduction.

See [`data/README.md`](data/README.md) for detailed descriptions of each directory.

#### Key Data Files

- **RQ1** — `data/rq1_repo_license/`: License distribution data for GitHub repos, models, and datasets.
- **RQ2** — `data/rq2_issue_discussion_tag/`: 384 repo issues, 171 model discussions, 84 dataset discussions.
- **RQ3** — `data/rq3_chain_conflict/`: Supply chain construction and conflict detection scripts/data.
- **Discussion** — `data/discussion/reported_issues_and_discussions.xlsx`: All 60 reported issues.

### 2.3 Running LiAgent on Custom Licenses

```bash
cd LiAgent   # skip this if already inside Docker
# Clear previous data
rm -rf license tmp result result.csv
mkdir -p license
# Place your license text files (*.txt) in the license/ directory
python analyseLicense.py
# Results will appear in result.csv and result/
```

---

## Project Structure

```
├── data/                           # Empirical data and scripts (see data/README.md)
│   ├── metadata/                   # GitHub repos, models, datasets metadata
│   ├── discussion/                 # Reported issues and discussions
│   ├── rq1_repo_license/           # RQ1: License distribution
│   ├── rq2_issue_discussion_tag/   # RQ2: Developer concerns
│   ├── rq3_chain_conflict/         # RQ3: Supply chain conflicts
│   └── rq4_license_groundtruth/    # RQ4: Ground truth for LiAgent evaluation
├── LiAgent/                        # Core tool source code
│   ├── analyseLicense.py           # Main entry point
│   ├── analysePartLicense.py       # Part-level license analysis (extraction agent)
│   ├── analyseFullLicense.py       # Full-level license analysis (repair agent)
│   ├── modelCaller.py              # LLM API caller
│   ├── processPartData.py          # Part-level data processing
│   ├── processFullData.py          # Full-level data processing
│   ├── utils.py                    # Utility functions
│   ├── config.yaml                 # Model configuration (API keys)
│   └── resources/                  # Prompts and term definitions
├── Dockerfile                      # Container packaging
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── REQUIREMENTS                    # Hardware/software requirements
├── STATUS                          # Badge application
└── LICENSE                         # MIT License
```
