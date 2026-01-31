' ============================================================
'   OMEGA SILENT LAUNCHER - VBScript Wrapper
' ============================================================
'   Purpose: Launch OMEGA_SILENT_LAUNCHER.bat with NO visible
'            window whatsoever. Truly invisible execution.
'
'   USAGE:
'     1. Double-click this .vbs file
'     2. Add to Task Scheduler for auto-start on login
'     3. Add to Windows Startup folder
'
'   This script uses WScript.Shell to run the batch file
'   with a hidden window style (vbHide = 0).
' ============================================================

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
scriptPath = fso.GetParentFolderName(WScript.ScriptFullName)
batchFile = scriptPath & "\OMEGA_SILENT_LAUNCHER.bat"

' Check if batch file exists
If fso.FileExists(batchFile) Then
    ' Run batch file hidden (0 = vbHide)
    ' Parameters: command, window style, wait for completion
    WshShell.Run """" & batchFile & """", 0, False
Else
    ' Log error if batch file not found
    logFile = scriptPath & "\logs\omega_vbs_error.log"
    Set logStream = fso.OpenTextFile(logFile, 8, True)
    logStream.WriteLine Now & " - ERROR: Batch file not found: " & batchFile
    logStream.Close
End If

Set WshShell = Nothing
Set fso = Nothing
