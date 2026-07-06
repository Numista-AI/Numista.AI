# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import subprocess

# Get token
token = subprocess.check_output('gcloud auth print-access-token', shell=True).decode('utf-8').strip()

# Start proxy
proxy_process = subprocess.Popen([
    'cloud-sql-proxy.exe', 
    '--token', token,
    'studio-9101802118-8c9a8:us-central1:numista-coin-db', 
    '--port', '3307'
])

proxy_process.wait()
