import subprocess

subprocess.run([
    'gcloud.cmd', 'sql', 'users', 'create', 'eric123',
    '--host=%', '--instance=numista-coin-db',
    '--password=Num1sta#2026CoinData'
])
