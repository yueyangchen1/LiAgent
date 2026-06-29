FROM python:3.10-slim

LABEL maintainer="LiAgent Authors"
LABEL description="Artifact for 'Hidden Licensing Risks in the PTMware Ecosystem' (ISSTA 2026)"

# Set working directory
WORKDIR /artifact

# Install basic utilities (editor for config, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends vim nano && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire artifact
COPY . .

# Create the license input directory for LiAgent
RUN mkdir -p LiAgent/license

# Copy sample licenses for smoke test
RUN cp data/rq4_license_groundtruth/ai_16/license/llama2.txt LiAgent/license/

# Set default working directory to LiAgent
WORKDIR /artifact/LiAgent

# Default command: show help
CMD ["bash", "-c", "echo '=== LiAgent Artifact (ISSTA 2026) ===' && echo '' && echo 'Quick Start:' && echo '  1. Configure your API key in config.yaml' && echo '  2. Run: python analyseLicense.py' && echo '  3. Check results in result.csv and result/' && echo '' && echo 'For full instructions, see /artifact/README.md' && echo '' && exec bash"]
