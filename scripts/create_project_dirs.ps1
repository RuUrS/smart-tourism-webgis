# 在 Windows PowerShell 中运行：
# powershell -ExecutionPolicy Bypass -File scripts/create_project_dirs.ps1

$Base = "smart-tourism-webgis"
$Dirs = @(
  "$Base/frontend/public/data",
  "$Base/backend/routers",
  "$Base/backend/services",
  "$Base/backend/schemas",
  "$Base/data/raw",
  "$Base/data/processed",
  "$Base/data/database",
  "$Base/docs/thesis",
  "$Base/docs/screenshots",
  "$Base/docs/api",
  "$Base/scripts",
  "$Base/notebooks"
)

foreach ($Dir in $Dirs) {
  New-Item -ItemType Directory -Force -Path $Dir | Out-Null
}

Write-Host "项目目录已创建：$Base"
