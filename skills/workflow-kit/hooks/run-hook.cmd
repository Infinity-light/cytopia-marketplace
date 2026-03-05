: <<"::CMDLITERAL"
@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_NAME=%~1"
if "%SCRIPT_NAME%"=="" exit /b 0
shift

set "BASH_EXE="
if defined ProgramFiles if exist "%ProgramFiles%\Git\bin\bash.exe" set "BASH_EXE=%ProgramFiles%\Git\bin\bash.exe"
if not defined BASH_EXE if defined ProgramFiles if exist "%ProgramFiles%\Git\usr\bin\bash.exe" set "BASH_EXE=%ProgramFiles%\Git\usr\bin\bash.exe"
if not defined BASH_EXE if defined ProgramFiles(x86) if exist "%ProgramFiles(x86)%\Git\bin\bash.exe" set "BASH_EXE=%ProgramFiles(x86)%\Git\bin\bash.exe"
if not defined BASH_EXE if defined ProgramFiles(x86) if exist "%ProgramFiles(x86)%\Git\usr\bin\bash.exe" set "BASH_EXE=%ProgramFiles(x86)%\Git\usr\bin\bash.exe"
if not defined BASH_EXE for %%I in (bash.exe) do set "BASH_EXE=%%~$PATH:I"

if not defined BASH_EXE exit /b 0

"%BASH_EXE%" "%SCRIPT_DIR%%SCRIPT_NAME%" %*
exit /b 0
::CMDLITERAL
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
SCRIPT_NAME="${1:-}"

if [ -z "$SCRIPT_NAME" ]; then
  exit 0
fi
shift || true

exec bash "${SCRIPT_DIR}/${SCRIPT_NAME}" "$@"
