# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import subprocess

subprocess.run([
    'gcloud.cmd', 'sql', 'users', 'set-password', 'root',
    '--host=%', '--instance=numista-coin-db',
    '--password=Num1sta#2026CoinData'
])
