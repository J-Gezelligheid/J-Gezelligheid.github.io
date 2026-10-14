"""Run Git using the existing OS proxy, without changing Git or OS configuration."""
import os
import subprocess
import sys
import urllib.request

environment = os.environ.copy()
for scheme, proxy in urllib.request.getproxies().items():
    if scheme in ('http', 'https'):
        environment[scheme.upper() + '_PROXY'] = proxy
environment['GIT_TERMINAL_PROMPT'] = '0'
environment['GCM_INTERACTIVE'] = 'Never'
raise SystemExit(subprocess.run(['git', *sys.argv[1:]], env=environment).returncode)
