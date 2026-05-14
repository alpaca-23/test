$ProjectDir = "c:\Users\takahiro\OneDrive\init_programming\ai-news-digest"
$EnvFile    = "$ProjectDir\.env"
$Python     = "$ProjectDir\.venv\Scripts\python.exe"

Get-Content $EnvFile | Where-Object { $_ -match "^\s*[^#]" } | ForEach-Object {
    $key, $value = $_ -split "=", 2
    [System.Environment]::SetEnvironmentVariable($key.Trim(), $value.Trim(), "Process")
}

& $Python "$ProjectDir\main.py"
