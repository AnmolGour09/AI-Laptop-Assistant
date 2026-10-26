#!/usr/bin/env python3
"""Wrapper script to load environment variables and run the agent."""

import os
import sys
import subprocess
from pathlib import Path

# Load environment variables from .env
env_path = Path(__file__).parent / '.env'
env_vars = os.environ.copy()

if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    env_vars[key] = value
                    print(f"✓ Loaded {key}")
else:
    print(f"ERROR: .env file not found at {env_path}")
    sys.exit(1)

# Run agent.py with the environment variables
result = subprocess.run(
    [sys.executable, str(Path(__file__).parent / 'agent.py')] + sys.argv[1:],
    env=env_vars,
    cwd=str(Path(__file__).parent)
)
sys.exit(result.returncode)

