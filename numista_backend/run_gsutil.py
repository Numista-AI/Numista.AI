import subprocess

output = subprocess.check_output('gsutil ls "gs://numista-training-docs/Numista.AI Training Data/US Mint Coin Programs/"', shell=True).decode('utf-8')
print(output)
