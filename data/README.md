# Data & Empirical Study Artifacts

This directory contains the datasets and scripts used for the empirical study (RQ1-RQ4). Due to the complexity of software license data and the long-term nature of this research, we provide this guide to clarify the data processing workflow.

---

## 🏗 Workflow & Directory Details

We organized the artifacts based on the research questions (RQs) and data sources. Each folder contains the necessary scripts and their corresponding datasets.

> **⚠️ Note on Script Execution and Data Consistency:**
> These scripts were developed and evolved over a long-term research period. Since real-world software license data is often noisy and non-standard, the processing pipeline involves **Human-in-the-loop Refinement**. 
> 
> 1. **Manual Intervention:** To ensure the highest data integrity, some intermediate files were manually adjusted (e.g., structural normalization, merging rare categories, or filtering irrelevant noise) where automated scripts reached their limits.
> 2. **Script Maintenance:** The scripts are provided primarily for **methodological transparency**. Due to the complexity of the research, some legacy scripts may require specific environment configurations and may not support "one-click" end-to-end execution.
> 3. **Recommended Approach:** To verify our findings, we strongly recommend using the **curated datasets** provided in each folder, as they represent the final, manually-verified versions used in the manuscript.

---

### 1. `rq1_repo_license/`
*Focus: License distribution*

* **Hypothesis 1 :** The `github_repo/` and `model_and_dataset/` sub-directories contain scripts and results for extracting license information from GitHub repositories, models, and datasets.
* **Hypothesis 2 :** Contains scripts used to distinguish between **Company** models and **Individual** models.
* **Hypothesis 3 :** Includes datasets and comparison scripts that categorize models based on their specific tasks (e.g., NLP, CV, etc.).

### 2. `rq2_issue_discussion_tag/`
*Focus: Analysis of developer concerns.*
- **Content:** Processed data extracted randomly from GitHub repository issues, Model discussions, and Dataset discussions.
- **Key Scripts:** Includes analysis scripts for temporal metrics (e.g., close time) and other metadata indicators across these three platforms.

### 3. `rq3_chain_conflict/`
*Focus: Tiered supply chain construction and conflict detection.*
To avoid redundant data recording and ensure structural clarity, we implemented a **Tiered Construction** approach:
- **Root Directory:** Scripts for the end-to-end chain construction (`Repository -> Model -> Dataset`) and overall license conflict analysis.
- **`repo_model/`:** Scripts for building the `Repository -> Model` supply chain and identifying conflicts.
- **`model_dataset/`:** Scripts for building the `Model -> Dataset` supply chain and identifying conflicts.
- **`model_and_basemodel/`:** Scripts specifically for the `Model -> Base Model` lineage and its associated license compatibility.

### 4. `rq4_license_groundtruth/`
*Focus: LiAgent.*
- **Content:** Contains the manually verified **Ground Truth** for the licenses used in the *LiAgent* experimental evaluation.

---

## 📂 Directory Structure

```bash
├── metadata/               # Github repositories models and datasets metadata
├── discussion/                 # Issue record
├── rq1_repo_license/           # Script and data used to obtain the distribution situation of licenses
├── rq2_issue_discussion_tag/   # Script and data for analyzing the situations that developers are concerned about
├── rq3_chain_conflict/         # Scripts and data for building the supply chain based on metadata and identifying conflicts
└──  rq4_license_groundtruth/    # The groundtruth of the license dataset