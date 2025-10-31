# Full Backup Script: Dump to temp .sql files, then zip into single archive per run
# Assumes mysqldump is at $MySQLDumpPath (full path for UA reliability).

# Configuration
$DBHost = ""  # Your Alpine/Docker host IP
$DBPort = ""
$DBUser = ""           # Your DB user
$DBPass = ""       # Secure this (e.g., $DBPass = $env:DB_PASS)
$DBNames = @("acore_auth", "acore_characters")  # The two DBs to backup
$BackupDir = ""  # Local Windows folder (create it)
$MaxBackups = 10
$SevenZipPath = ""  # Adjust if different
$MySQLDumpPath = ""  # Full path to mysqldump.exe

# Validate tools
if (!(Test-Path $MySQLDumpPath)) {
    Write-Error "mysqldump.exe not found at $MySQLDumpPath. Update path or install MySQL."
    exit 1
}
if (!(Test-Path $SevenZipPath)) {
    Write-Error "7z.exe not found at $SevenZipPath. Install 7-Zip."
    exit 1
}

# Create backup directory if it doesn't exist
if (!(Test-Path $BackupDir)) { 
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    Write-Output "Created backup directory: $BackupDir"
}

# Generate timestamp for filenames
$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm"

# Temp files list (to clean up later)
$TempSQLFiles = @()

# Step 1: Dump each DB to individual .sql files
Write-Output "Step 1: Dumping SQL files..."
$AllDumpsSuccess = $true
foreach ($DBName in $DBNames) {
    $SQLFile = "$BackupDir\$DBName`_dump_$Timestamp.sql"
    $TempSQLFiles += $SQLFile
    
    # Dump with minimal args (no --routines to avoid issues)
    $mysqldumpArgs = @(
        "--host=$DBHost",
        "--port=$DBPort",
        "--user=$DBUser",
        "--password=$DBPass",
        "--single-transaction",
        "--triggers",
        "--force",
        $DBName
    )
    
    Write-Output "Dumping $DBName..."
    $errorLog = "temp_error_$DBName.log"  # Relative to script dir; UA should handle
    $dumpProcess = Start-Process -FilePath $MySQLDumpPath -ArgumentList $mysqldumpArgs -PassThru -NoNewWindow -RedirectStandardOutput $SQLFile -RedirectStandardError $errorLog -Wait
    
    if ($dumpProcess.ExitCode -eq 0 -and (Test-Path $SQLFile)) {
        $fileSize = (Get-Item $SQLFile).Length / 1KB
        Write-Output "Success for ${DBName}: $SQLFile (Size: ${fileSize} KB)"
    } else {
        Write-Output "Failed for ${DBName}! (Exit code: $($dumpProcess.ExitCode))"
        if (Test-Path $errorLog) {
            Write-Output "Error details:"
            Get-Content $errorLog
        }
        $AllDumpsSuccess = $false
    }
    
    # Clean up error log
    if (Test-Path $errorLog) { Remove-Item $errorLog -Force }
}

# Step 2: If all dumps succeeded, zip them into a single archive
if ($AllDumpsSuccess) {
    Write-Output "Step 2: All dumps complete. Zipping into single archive..."
    $ArchiveFile = "$BackupDir\azcore_full_backup_$Timestamp.7z"
    
    # Zip the SQL files (7z adds them directly)
    & $SevenZipPath a $ArchiveFile @TempSQLFiles
    
    if ($LASTEXITCODE -eq 0) {
        $archiveSize = (Get-Item $ArchiveFile).Length / 1MB
        Write-Output "Archive created: $ArchiveFile (Size: ${archiveSize} MB)"
        
        # Prune old archives: Keep only latest $MaxBackups
        $OldArchives = Get-ChildItem -Path $BackupDir -Filter "azcore_full_backup_*.7z" | Sort-Object LastWriteTime -Descending | Select-Object -Skip $MaxBackups
        if ($OldArchives) {  # Fixed: Was $OldBackups (typo)
            $OldArchives | Remove-Item -Force
            Write-Output "Pruned old archives. Kept latest $MaxBackups."
        }
        
        # Clean up temp SQL files
        $TempSQLFiles | Remove-Item -Force -ErrorAction SilentlyContinue
        Write-Output "Temp SQL files cleaned up."
    } else {
        Write-Output "Zipping failed! (Exit: $LASTEXITCODE) Keeping temp SQL files for inspection."
    }
} else {
    Write-Output "One or more dumps failed. No archive created. Check temp SQL files in $BackupDir."
}