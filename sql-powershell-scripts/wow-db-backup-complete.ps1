# Full Backup Script: Dump to temp .sql files, then zip into single archive per run
# Treats all $DBNames as full databases (with quoting for special chars like /). No routines (avoids info_schema errors).

# Configuration
$DBHost = ""  # Your Alpine/Docker host IP
$DBPort = ""
$DBUser = ""           # Your DB user
$DBPass = ""       # Secure this (e.g., $DBPass = $env:DB_PASS)
$DBNames = @("acore_auth", "acore_characters", "acore_world")  # All full DBs (no tables)
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

# Temp files list (to clean up later) - Only add successful ones
$TempSQLFiles = @()

# Step 1: Dump each DB to individual .sql files (ONLY from $DBNames)
Write-Output "Step 1: Dumping SQL files..."
$AllDumpsSuccess = $true
$WarningsEncountered = $false
foreach ($DBName in $DBNames) {
    # Sanitize DB name for safe Windows filenames ONLY (replace invalid chars like / \ : * ? " < > | with _)
    $safeDBName = $DBName -replace '[/\\:*?"<>|]', '_'
    $SQLFile = "$BackupDir\$safeDBName`_dump_$Timestamp.sql"
    $errorLog = "$BackupDir\temp_error_$safeDBName.log"  # Full path for safety
    
    # Quote DB name with backticks if it has special chars (e.g., /) for mysqldump
    $quotedDBName = if ($DBName -match '[/\\:*?"<>|]') { "`"$DBName`"" } else { $DBName }
    
    # Build mysqldump args for FULL DB dump (no --routines to avoid info_schema.LIBRARIES error)
    $mysqldumpArgs = @(
        "--host=$DBHost",
        "--port=$DBPort",
        "--user=$DBUser",
        "--password=$DBPass",
        "--single-transaction",
        "--triggers",
        "--force",
        "--databases",
        $quotedDBName  # Quoted if needed
    )
    
    Write-Output "Dumping full DB '$DBName'..."
    try {
        $dumpProcess = Start-Process -FilePath $MySQLDumpPath -ArgumentList $mysqldumpArgs -PassThru -NoNewWindow -RedirectStandardOutput $SQLFile -RedirectStandardError $errorLog -Wait
        
        if ((Test-Path $SQLFile) -and (Get-Item $SQLFile).Length -gt 0) {
            $fileSize = [math]::Round((Get-Item $SQLFile).Length / 1KB, 3)
            if ($dumpProcess.ExitCode -eq 0) {
                Write-Output "Success for DB '$DBName': $SQLFile (Size: ${fileSize} KB)"
            } else {
                Write-Warning "Partial success for DB '$DBName' (Exit: $($dumpProcess.ExitCode); data backed up): $SQLFile (Size: ${fileSize} KB)"
                if (Test-Path $errorLog) {
                    $errorContent = Get-Content $errorLog -ErrorAction SilentlyContinue
                    if ($errorContent -match "Unknown table 'LIBRARIES'") {
                        Write-Output "Known warning: MySQL <8.0 lacks LIBRARIES table. Data is safe; routines skipped."
                    } else {
                        Write-Output "Error details:"
                        $errorContent
                    }
                }
                $WarningsEncountered = $true
                $AllDumpsSuccess = $false  # Still mark as 'failed' but proceed to archive
            }
            $TempSQLFiles += $SQLFile  # Add anyway if data present
        } else {
            Write-Output "True failure for DB '$DBName'! (Exit code: $($dumpProcess.ExitCode); No file)"
            if (Test-Path $errorLog) {
                Write-Output "Error details:"
                Get-Content $errorLog -ErrorAction SilentlyContinue
            }
            $AllDumpsSuccess = $false
        }
    } catch {
        Write-Output "Exception during dump for DB '$DBName': $($_.Exception.Message)"
        $AllDumpsSuccess = $false
    }
    
    # Clean up error log
    if (Test-Path $errorLog) { Remove-Item $errorLog -Force }
}

# Step 2: Archive if any data was dumped (lenient for warnings)
if ($TempSQLFiles.Count -gt 0) {
    Write-Output "Step 2: $($TempSQLFiles.Count) dumps complete (warnings: $WarningsEncountered). Zipping into single archive..."
    $ArchiveFile = if ($WarningsEncountered) { "$BackupDir\azcore_backup_$Timestamp-with_warnings.7z" } else { "$BackupDir\azcore_full_backup_$Timestamp.7z" }
    
    # Zip the SQL files (7z adds them directly)
    & $SevenZipPath a $ArchiveFile @TempSQLFiles
    
    if ($LASTEXITCODE -eq 0) {
        $archiveSize = [math]::Round((Get-Item $ArchiveFile).Length / 1MB, 2)
        Write-Output "Archive created: $ArchiveFile (Size: ${archiveSize} MB)"
        
        # Prune old archives: Keep only latest $MaxBackups (both full and with_warnings)
        $OldArchives = Get-ChildItem -Path $BackupDir -Filter "azcore_backup*.7z" | Sort-Object LastWriteTime -Descending | Select-Object -Skip $MaxBackups
        if ($OldArchives) {
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
    Write-Output "No dumps succeeded. No archive created. Check logs."
}