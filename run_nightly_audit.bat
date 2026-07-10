@echo off
REM ============================================================
REM  run_nightly_audit.bat
REM  Nightly launcher for the Numista.AI system data audit.
REM  Registered with Windows Task Scheduler to run at 2:00 AM.
REM  Also registered with GCP Cloud Scheduler as a backup.
REM ============================================================
cd /d "C:\Users\ericd\Documents\MyVertexProject"
echo [%date% %time%] Starting nightly audit... >> scratch\audit_scheduler.log
call numista_backend\.venv\Scripts\activate.bat
python numista_backend\nightly_data_audit.py >> scratch\audit_scheduler.log 2>&1
echo [%date% %time%] Nightly audit complete. >> scratch\audit_scheduler.log
REM Run the auto-resolver 30 seconds after audit
timeout /t 30 /nobreak > nul
python numista_backend\auto_resolve_audit.py >> scratch\audit_scheduler.log 2>&1
echo [%date% %time%] Auto-resolver complete. >> scratch\audit_scheduler.log
