#!/usr/bin/env python3
import subprocess

subprocess.run(['uv', 'lock'], check=True)
subprocess.run(['git', 'add', 'uv.lock'], check=True)
