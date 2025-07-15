# Python Cache Cleanup Commands - SQL Analyzer Enterprise

## 🔧 FIXED POWERSHELL COMMANDS

### 1. Remove __pycache__ directories (CORRECTED)
```powershell
Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__" | ForEach-Object { $fullPath = Join-Path -Path (Get-Location) -ChildPath $_; if (Test-Path $fullPath) { Remove-Item -Path $fullPath -Recurse -Force; Write-Host "Removed: $fullPath" } }
```

### 2. Remove .pyc files
```powershell
Get-ChildItem -Path . -Recurse -File -Filter "*.pyc" | ForEach-Object { Remove-Item -Path $_.FullName -Force; Write-Host "Removed: $($_.FullName)" }
```

### 3. Remove .pyo files
```powershell
Get-ChildItem -Path . -Recurse -File -Filter "*.pyo" | ForEach-Object { Remove-Item -Path $_.FullName -Force; Write-Host "Removed: $($_.FullName)" }
```

### 4. Remove .pytest_cache directories
```powershell
Get-ChildItem -Path . -Recurse -Directory -Name ".pytest_cache" | ForEach-Object { $fullPath = Join-Path -Path (Get-Location) -ChildPath $_; if (Test-Path $fullPath) { Remove-Item -Path $fullPath -Recurse -Force; Write-Host "Removed: $fullPath" } }
```

### 5. ALL-IN-ONE PowerShell Command
```powershell
@("__pycache__", ".pytest_cache") | ForEach-Object { Get-ChildItem -Path . -Recurse -Directory -Name $_ | ForEach-Object { $fullPath = Join-Path -Path (Get-Location) -ChildPath $_; if (Test-Path $fullPath) { Remove-Item -Path $fullPath -Recurse -Force; Write-Host "Removed directory: $fullPath" } } }; @("*.pyc", "*.pyo") | ForEach-Object { Get-ChildItem -Path . -Recurse -File -Filter $_ | ForEach-Object { Remove-Item -Path $_.FullName -Force; Write-Host "Removed file: $($_.FullName)" } }
```

## 🐍 PYTHON ONE-LINERS

### 1. Simple Python cleanup
```python
python -c "import os, shutil; [shutil.rmtree(os.path.join(root, d)) for root, dirs, files in os.walk('.') for d in dirs if d == '__pycache__']; [os.remove(os.path.join(root, f)) for root, dirs, files in os.walk('.') for f in files if f.endswith(('.pyc', '.pyo'))]; print('Cache cleanup completed')"
```

### 2. Advanced Python cleanup with pathlib
```python
python -c "from pathlib import Path; import shutil; [shutil.rmtree(p) for p in Path('.').rglob('__pycache__')]; [p.unlink() for p in Path('.').rglob('*.pyc')]; [p.unlink() for p in Path('.').rglob('*.pyo')]; [shutil.rmtree(p) for p in Path('.').rglob('.pytest_cache')]; print('Advanced cleanup completed')"
```

## 💻 COMMAND PROMPT (Windows)

### 1. Remove __pycache__ directories
```cmd
for /d /r %i in (__pycache__) do @if exist "%i" rmdir /s /q "%i"
```

### 2. Remove .pyc files
```cmd
for /r %i in (*.pyc) do @if exist "%i" del /q "%i"
```

### 3. Remove .pyo files
```cmd
for /r %i in (*.pyo) do @if exist "%i" del /q "%i"
```

### 4. ALL-IN-ONE Command Prompt
```cmd
for /d /r %i in (__pycache__) do @if exist "%i" rmdir /s /q "%i" & for /r %i in (*.pyc) do @if exist "%i" del /q "%i" & for /r %i in (*.pyo) do @if exist "%i" del /q "%i" & for /d /r %i in (.pytest_cache) do @if exist "%i" rmdir /s /q "%i"
```

## 🔍 VERIFICATION COMMANDS

### PowerShell Verification
```powershell
$remaining = @(); $remaining += Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__" -ErrorAction SilentlyContinue; $remaining += Get-ChildItem -Path . -Recurse -File -Filter "*.pyc" -ErrorAction SilentlyContinue; $remaining += Get-ChildItem -Path . -Recurse -File -Filter "*.pyo" -ErrorAction SilentlyContinue; $remaining += Get-ChildItem -Path . -Recurse -Directory -Name ".pytest_cache" -ErrorAction SilentlyContinue; if ($remaining.Count -eq 0) { Write-Host "VERIFICATION PASSED: No cache files remaining!" -ForegroundColor Green } else { Write-Host "WARNING: $($remaining.Count) cache files still present" -ForegroundColor Yellow; $remaining | ForEach-Object { Write-Host "  - $($_.FullName)" } }
```

### Python Verification
```python
python -c "from pathlib import Path; remaining = list(Path('.').rglob('__pycache__')) + list(Path('.').rglob('*.pyc')) + list(Path('.').rglob('*.pyo')) + list(Path('.').rglob('.pytest_cache')); print(f'VERIFICATION: {len(remaining)} cache files remaining') if remaining else print('VERIFICATION PASSED: No cache files remaining!')"
```

## 🚀 RECOMMENDED USAGE

### For Regular Use (PowerShell)
```powershell
powershell -ExecutionPolicy Bypass -File simple_cache_cleanup.ps1
```

### For Cross-Platform (Python)
```bash
python python_cache_cleaner.py
```

### For Windows Batch
```cmd
cleanup_cache.bat
```

## ⚠️ SAFETY NOTES

1. **Always run from project root directory**
2. **Test in a backup/copy first if unsure**
3. **These commands are safe to run multiple times**
4. **They only remove Python cache files, not source code**
5. **Use verification commands to confirm cleanup**

## 🎯 DEPLOYMENT CHECKLIST

- [ ] Run cache cleanup script
- [ ] Verify no cache files remain
- [ ] Check project structure is intact
- [ ] Test application startup
- [ ] Proceed with deployment optimization
