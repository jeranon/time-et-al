# Get the path to your project directory
$projectDir = "O:\time_app"

# Find all empty directories within the project directory
$emptyDirs = Get-ChildItem -Path $projectDir -Recurse -Directory | Where-Object { (Get-ChildItem -Path $_.FullName).Count -eq 0 }

# For each empty directory, create a .gitkeep file inside it
$emptyDirs | ForEach-Object { New-Item -Path $_.FullName -Name ".gitkeep" -ItemType "file" -Force }
