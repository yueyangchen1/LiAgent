# Data & Scripts for Empirical Study (RQ1–RQ4)

This directory contains the datasets and analysis scripts for the empirical study presented in our paper. Below we describe the overall workflow, what each script does, and what data is provided.

---

## Important Notes for Reviewers

> **Reproducibility Statement:**
>
> The scripts in this repository are provided for **methodological transparency** — they document the exact logic and algorithms used in our analysis. However, they are **not designed for one-click end-to-end execution**, and this is by design rather than an oversight. Here's why:
>
> 1. **Human-in-the-loop refinement**: Real-world license data from HuggingFace and GitHub is inherently noisy and non-standard. Throughout the research, we manually inspected and corrected intermediate outputs (e.g., normalizing license name variants, fixing metadata mismatches, merging rare categories). These manual adjustments are not captured in the scripts.
>
> 2. **Iterative development**: The scripts were developed and refined over an extended research period. Some intermediate files were renamed, restructured, or merged as our methodology evolved.
>
> 3. **What we provide instead**: Rather than requiring reviewers to re-run the entire pipeline, we provide:
>    - All scripts showing our methodology and algorithms
>    - The **final curated datasets** used to produce the paper's results
>    - Raw metadata so reviewers can verify our data sources
>
> **Reviewer focus**: We recommend focusing on (1) the provided **final data files** that directly support our findings, and (2) the **script logic** that documents our methodology. The scripts serve as a detailed supplement to the paper's method section.

---

## Overall Workflow

```
Raw Metadata (3,988 models, 708 datasets, 12,180 repos)
    │
    ├──▶ RQ1: License distribution analysis
    │     • Compare PTMware vs traditional OSS license distributions
    │     • Compare Company vs Individual model licenses
    │     • Compare licenses across AI task types
    │     • Statistical testing via Permutation Tests
    │
    ├──▶ RQ2: Developer concern analysis
    │     • Temporal analysis of license-related Issues/Discussions
    │     • Tag distribution and response time patterns
    │
    ├──▶ RQ3: Supply chain license conflict detection
    │     • Build supply chains: Repo→Model, Model→Dataset, Model→BaseModel
    │     • Detect license incompatibilities using 23-term license vectors
    │     • Summarize conflict statistics
    │
    └──▶ RQ4: LiAgent evaluation
          • Ground truth labels for 140 original + 796 mutated licenses
          • Used to evaluate the LiAgent tool (see ../LiAgent/)
```

---

## Shared Data

### `metadata/` — Raw Metadata from HuggingFace & GitHub

These are the foundational data files used across multiple RQs:

| File | Description |
|------|-------------|
| `models_metadata_3988.json` | Metadata for 3,988 HuggingFace models (name, license, tags, etc.) |
| `datasets_metadata_708.json` | Metadata for 708 HuggingFace datasets |
| `repos_models_map.json` | Mapping from GitHub repositories to their associated models |
| `List of signatures in huggingface.xlsx` | HuggingFace organization signature list |

### `discussion/` — Reported Issues

| File | Description |
|------|-------------|
| `reported_issues_and_discussions.xlsx` | All 60 license issues we reported to developers (§5 Discussion) |

---

## RQ1: License Distribution (`rq1_repo_license/`)

*Paper Section: §4.1*

### Finding 1: PTMware vs Traditional OSS (`hypothesis1/`)

**Goal**: Show that license distribution in AI model/dataset ecosystems differs significantly from traditional open-source software.

**Workflow**:

1. **Count license distributions** — Separate scripts analyze license usage for GitHub repos, HuggingFace models, and datasets respectively. Each script reads metadata and outputs frequency counts grouped by license type.
   - `github_repo/analyse_repo_license_distribution.py` — Analyzes 12,180 GitHub repos (metadata in `github_repo_metadata.zip`)
   - `model_and_dataset/analyse_model_license.py` — Analyzes 3,988 models
   - `model_and_dataset/analyse_dataset_license.py` — Analyzes 708 datasets

2. **Classify licenses** — `model_and_dataset/check_ai_or_oss.py` maps each license name to SPDX standard and classifies it as either traditional OSS (group 0) or AI-specific (group 1), using a reference list (`ai_license_daxie.json`).

3. **Merge results** — `model_and_dataset/merge_model_dataset_license.py` combines the model and dataset distributions into a unified file for statistical testing.

4. **Statistical test** — `Permutation_Test.py` performs a permutation test comparing PTMware vs GitHub repo license distributions, reporting p-value and Cramér's V.

**Key data files provided**:
- `github_repo/license_stats_12180.json` — Final license distribution for 12,180 repos
- `model_and_dataset/model_and_dataset_license_distribution.json` — Final merged distribution
- `model_and_dataset/ai_license_daxie.json` — AI-specific license list

> **Why this can't run end-to-end**: Steps 1→2→3 involve manual inspection of license name variants (e.g., "Apache 2" vs "Apache-2.0" vs "apache2") and intermediate file adjustments before each step.

### Finding 2: Company vs Individual (`hypothesis2/`)

**Goal**: Compare license choices between company-owned and individual-owned models.

**Workflow**:

1. `analyse_model_license_with_com_task.py` — Splits the 3,988 models into Company/Individual groups using `company_owner_id.txt`, and also groups by task type using `model_task.json`.

2. `Permutation_Test.py` — Permutation test comparing company vs individual license distributions.

**Key data files provided**:
- `company_owner_id.txt` — List of organization IDs identified as companies
- `model_task.json` — Model-to-task-type mapping
- `model_license_stats_extended.json` — Output with company/individual/task breakdowns

### Finding 3: Across AI Task Types (`hypothesis3/`)

**Goal**: Test whether license preferences differ across AI task categories (NLP, CV, Audio, etc.).

**Workflow**: `Permutation_Test.py` reads pre-computed license distributions for each task type and performs pairwise permutation tests.

**Key data files provided**: `license_distribution/` contains 7 JSON files (Audio, Computer_Vision, Multimodal, Natural_Language_Processing, No_Task, Other, Reinforcement_Learning), each with the license frequency data for that category.

---

## RQ2: Developer Concerns (`rq2_issue_discussion_tag/`)

*Paper Section: §4.2*

### Data Files

| File | Description |
|------|-------------|
| `repo_issue_384.json` | 384 sampled GitHub repository issues related to licensing |
| `model_discussion_171.json` | 171 model discussions from HuggingFace |
| `dataset_discussion_84.json` | 84 dataset discussions from HuggingFace |

These are the final curated datasets used directly in the paper's analysis.

### Script

`distribute_time.py` — Analyzes temporal features of discussions/issues: time from project creation to issue, time to close, and tag-based distribution. Time intervals: 0–1 day, 1–7 days, 7–30 days, 30–60 days, 60–90 days, 90–180 days, 180–365 days, 365+ days, null (unclosed).

> **Note**: The script expects a pre-processed input file with restructured fields. The three JSON files above are the final research data; the script documents the analytical logic used to produce the paper's temporal statistics.

---

## RQ3: Supply Chain Conflict Detection (`rq3_chain_conflict/`)

*Paper Section: §4.3*

This is the most complex analysis module. It detects license incompatibilities across AI supply chains.

### Conflict Detection Method

All conflict detection uses a **23-term license vector** model:
- Each license is encoded as a vector of 23 terms, each with an attitude: `1` (permitted), `2` (prohibited), `3` (required)
- **Conflict rule**: A conflict exists when one license prohibits a term that another permits, or one requires a term that another does not

The term labels are provided in `label_ai_16.csv` (for AI licenses) and `label_oss_124.csv` (for OSS licenses).

### Supply Chain Structure

We analyze three types of supply chains:

| Chain Type | Directory | Description |
|-----------|-----------|-------------|
| Repo → Model | `repo_model/` | GitHub repo licenses vs. their derived model licenses |
| Model → Dataset | `model_dataset/` | Model licenses vs. their training dataset licenses |
| Model → Base Model | `model_and_basemodel/` | Fine-tuned model licenses vs. base model licenses |

### Scripts (same pattern in each subdirectory)

Each tier follows the same 3-step pattern:

1. **Build chains** (`make_*_chain.py`) — Constructs supply chain relationships from metadata
2. **Detect conflicts** (`check_license_incompatibility.py`) — Applies the 23-term vector model to identify incompatibilities
3. **Analyze statistics** (`analyse_conflict_count_license.py`) — Summarizes conflict counts and patterns

The root directory also contains versions that perform end-to-end analysis across the complete Repo→Model→Dataset chain.

### Key Data Files Provided

| File | Description |
|------|-------------|
| `repo-model-dataset_chain.txt` | Complete supply chains: Repo→Model→Dataset (4.66 MB) |
| `model_and_basemodel/model-basemodel_chain.txt` | Model→BaseModel lineage chains |
| `license_name_map.json` | License name to standardized ID mapping |
| `mismatch_dict_model.json` | Manual corrections for model name mismatches |
| `mismatch_dict_dataset.json` | Manual corrections for dataset name mismatches |
| `label_ai_16.csv` | 23-term vector labels for 16 AI-specific licenses |
| `label_oss_124.csv` | 23-term vector labels for 124 OSS licenses |

> **Why this can't run end-to-end**: The chain construction relies on intermediate metadata files (mapping repos to models, models to datasets) that were iteratively refined through manual correction of name mismatches and metadata inconsistencies. The `mismatch_dict_*.json` files represent the accumulated manual corrections, but the intermediate pipeline state they were applied to is not preserved as a single static snapshot.

---

## RQ4: LiAgent Evaluation (`rq4_license_groundtruth/`)

*Paper Section: §4.4*

This directory contains **ground truth data only** — no scripts. It provides manually labeled license term vectors for evaluating the LiAgent tool (see `../LiAgent/` for the tool itself).

| Subdirectory | Content | Label File |
|-------------|---------|------------|
| `ai_16/` | 16 AI-specific licenses (e.g., Llama 2, Gemma, BigCode) | `label_ai_16.csv` |
| `oss_124/` | 124 traditional OSS licenses (e.g., MIT, GPL, Apache) | `label_124.csv` |
| `aimut_176/` | 176 AI license mutations (term additions/removals via LLM) | `label_mutate_ai_176.csv` |
| `ossmut_620/` | 620 OSS license mutations | `label_mutate_620.csv` |

Each subdirectory contains:
- `license/` — Raw license text files (`.txt`)
- `label_*.csv` — Ground truth labels (23 terms × attitudes: 0/1/2/3)

**To evaluate LiAgent**: Copy license files into `../LiAgent/license/`, run `python analyseLicense.py`, then compare `result.csv` against the corresponding label CSV. See the main [README](../README.md) for detailed instructions.

---

## Directory Structure

```
data/
├── README.md
├── metadata/                              # Shared raw metadata
│   ├── models_metadata_3988.json
│   ├── datasets_metadata_708.json
│   ├── repos_models_map.json
│   └── List of signatures in huggingface.xlsx
├── discussion/
│   └── reported_issues_and_discussions.xlsx
├── rq1_repo_license/                      # RQ1: License distribution
│   ├── repos_license_map.json
│   ├── hypothesis1/
│   │   ├── Permutation_Test.py
│   │   ├── github_repo/
│   │   │   ├── analyse_repo_license_distribution.py
│   │   │   ├── github_repo_metadata.zip
│   │   │   └── license_stats_12180.json
│   │   └── model_and_dataset/
│   │       ├── analyse_model_license.py
│   │       ├── analyse_dataset_license.py
│   │       ├── check_ai_or_oss.py
│   │       ├── merge_model_dataset_license.py
│   │       ├── ai_license_daxie.json
│   │       └── model_and_dataset_license_distribution.json
│   ├── hypothesis2/
│   │   ├── analyse_model_license_with_com_task.py
│   │   ├── Permutation_Test.py
│   │   ├── company_owner_id.txt
│   │   ├── model_license_stats_extended.json
│   │   └── model_task.json
│   └── hypothesis3/
│       ├── Permutation_Test.py
│       └── license_distribution/          # 7 task-type JSON files
├── rq2_issue_discussion_tag/              # RQ2: Developer concerns
│   ├── repo_issue_384.json
│   ├── model_discussion_171.json
│   ├── dataset_discussion_84.json
│   └── distribute_time.py
├── rq3_chain_conflict/                    # RQ3: Supply chain conflicts
│   ├── repo-model-dataset_chain.txt       # Complete chain data (4.66 MB)
│   ├── license_name_map.json
│   ├── mismatch_dict_model.json
│   ├── mismatch_dict_dataset.json
│   ├── label_ai_16.csv
│   ├── label_oss_124.csv
│   ├── make_repo_model_chain.py
│   ├── check_license_incompatibility.py
│   ├── repo_model/
│   │   ├── make_repo_model_chain.py
│   │   ├── check_license_incompatibility.py
│   │   └── analyse_conflict_count_license.py
│   ├── model_dataset/
│   │   ├── make_model_dataset_chain.py
│   │   ├── check_license_incompatibility.py
│   │   └── analyse_conflict_count_license.py
│   └── model_and_basemodel/
│       ├── make_model_chain.py
│       ├── make_model_basemodel_chain.py
│       ├── check_license_incompatibility.py
│       ├── check_pair_license_incompatibility.py
│       ├── analyse_conflict_count_license.py
│       └── model-basemodel_chain.txt
└── rq4_license_groundtruth/               # RQ4: Ground truth for LiAgent
    ├── ai_16/          (16 licenses + labels)
    ├── oss_124/        (124 licenses + labels)
    ├── aimut_176/      (176 mutated licenses + labels)
    └── ossmut_620/     (620 mutated licenses + labels)
```
