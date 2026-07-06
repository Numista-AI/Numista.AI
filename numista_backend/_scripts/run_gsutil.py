# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import subprocess

output = subprocess.check_output('gsutil ls "gs://numista-training-docs/Numista.AI Training Data/US Mint Coin Programs/"', shell=True).decode('utf-8')
print(output)
