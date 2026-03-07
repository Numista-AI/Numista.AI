import subprocess

subprocess.run([
    'gcloud.cmd', 'sql', 'users', 'set-password', 'root',
    '--host=%', '--instance=numista-coin-db',
    '--password=Num1sta#2026CoinData'
])
