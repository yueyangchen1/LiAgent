# LiAgent

*LiAgent* is a LM-based tool designed to extract and structure information from software licenses.

---

## 📂 Data & Empirical Study

> ### 📢 **Artifact Update (Revision)**
> In response to the latest feedback, we have significantly enriched the `data/` directory:
> - **Added comprehensive data analysis results** for all four Research Questions (RQ1-RQ4).
> - **Included the corresponding execution scripts** to ensure full reproducibility.
>
> **Detailed descriptions and execution instructions can be found in the [data/README.md](data/README.md) file.**

---
> All data used in our Research Questions (RQs) is located in the data/ directory:
> - Supply Chain: Data and signatures from Peatmoss.
> - RQ1 - RQ4: Includes repository licenses, issue discussions, chain conflicts, and license ground truth data.(Some of the data were supplemented after manual review in the later stage, so there might be slight differences between the results and those obtained from the code.)
> - Discussion: A summary of issues and discussions submitted to GitHub repositories and Hugging Face models to report our findings.
---

## 🚀 Run Instructions
### Configuration
Configure your model pool in LiAgent/config.yaml. You can list multiple providers and select which one to use later.

```yaml
models:
  gpt-4o:
    api_key: "YOUR_OPENAI_KEY"
    base_url: "https://api.openai.com/v1"
  deepseek-v3:
    api_key: "YOUR_DEEPSEEK_KEY"
    base_url: "https://api.deepseek.com"
```
### Model Selection
To select a specific model for analysis, set the model_name variable in LiAgent/analyseLicense.py:
```python
# In LiAgent/analyseLicense.py
model_name = "deepseek-v3"  # Must match a key in config.yaml
```

### Analyse license

Place your license files in LiAgent/license/, then execute:

```bash
cd LiAgent
python analyseLicense.py
````


## 📊 Output and Results
After processing, you can find the results in:

- Individual Summaries: Located in LiAgent/result/ (one file per license).

- Aggregated Results: A consolidated table LiAgent/result.csv summarizing all processed licenses.



## 📁 Project Structure

```bash
├── data/                       # Empirical data, analysis results, and scripts (See data/README.md)
├── LiAgent/                    # Core source code
│   ├── license/                # Input: Place license files here
│   ├── result/                 # Output: Individual analysis results
│   ├── config.yaml             # Configuration (API keys, models)
│   └── analyseLicense.py       # Main entry point
├── requirements.txt            # Project dependencies
└── README.md
```