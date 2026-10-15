param(
    [Parameter(Mandatory=$true)]
    [string]$HistoryFile
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

function Get-RecentFolders {
    if (-not (Test-Path -LiteralPath $HistoryFile)) { return @() }

    $seen = @{}
    $result = New-Object System.Collections.Generic.List[string]

    foreach ($line in Get-Content -LiteralPath $HistoryFile -ErrorAction SilentlyContinue) {
        $path = $line.Trim()
        if ([string]::IsNullOrWhiteSpace($path)) { continue }
        $key = $path.ToLowerInvariant()
        if ($seen.ContainsKey($key)) { continue }
        if (-not (Test-Path -LiteralPath $path -PathType Container)) { continue }
        $seen[$key] = $true
        $result.Add($path)
        if ($result.Count -ge 5) { break }
    }
    return @($result)
}

function Save-RecentFolder([string]$SelectedPath, [string[]]$Existing) {
    $ordered = New-Object System.Collections.Generic.List[string]
    $seen = @{}

    foreach ($path in @($SelectedPath) + @($Existing)) {
        if ([string]::IsNullOrWhiteSpace($path)) { continue }
        $key = $path.ToLowerInvariant()
        if ($seen.ContainsKey($key)) { continue }
        $seen[$key] = $true
        $ordered.Add($path)
        if ($ordered.Count -ge 5) { break }
    }

    Set-Content -LiteralPath $HistoryFile -Value $ordered -Encoding UTF8
}

$recent = @(Get-RecentFolders)
$script:selectedPath = $null

$form = New-Object System.Windows.Forms.Form
$form.Text = 'HS2 Mission Editor - Maps folder'
$form.StartPosition = 'CenterScreen'
$form.Size = New-Object System.Drawing.Size(820, 380)
$form.MinimumSize = New-Object System.Drawing.Size(650, 330)
$form.MaximizeBox = $false
$form.FormBorderStyle = 'FixedDialog'

$label = New-Object System.Windows.Forms.Label
$label.Text = 'Choose one of the 5 most recent maps folders:'
$label.AutoSize = $true
$label.Location = New-Object System.Drawing.Point(18, 18)
$form.Controls.Add($label)

$list = New-Object System.Windows.Forms.ListBox
$list.Location = New-Object System.Drawing.Point(20, 48)
$list.Size = New-Object System.Drawing.Size(765, 190)
$list.HorizontalScrollbar = $true
$list.Font = New-Object System.Drawing.Font('Segoe UI', 10)
$form.Controls.Add($list)

if ($recent.Count -gt 0) {
    for ($i = 0; $i -lt $recent.Count; $i++) {
        [void]$list.Items.Add(('{0}. {1}' -f ($i + 1), $recent[$i]))
    }
    $list.SelectedIndex = 0
} else {
    [void]$list.Items.Add('No recent folder saved yet.')
    $list.Enabled = $false
}

$useButton = New-Object System.Windows.Forms.Button
$useButton.Text = 'Use selected folder'
$useButton.Location = New-Object System.Drawing.Point(20, 258)
$useButton.Size = New-Object System.Drawing.Size(190, 42)
$useButton.Enabled = ($recent.Count -gt 0)
$form.Controls.Add($useButton)

$browseButton = New-Object System.Windows.Forms.Button
$browseButton.Text = 'Choose another folder...'
$browseButton.Location = New-Object System.Drawing.Point(225, 258)
$browseButton.Size = New-Object System.Drawing.Size(205, 42)
$form.Controls.Add($browseButton)

$cancelButton = New-Object System.Windows.Forms.Button
$cancelButton.Text = 'Cancel'
$cancelButton.Location = New-Object System.Drawing.Point(650, 258)
$cancelButton.Size = New-Object System.Drawing.Size(135, 42)
$form.Controls.Add($cancelButton)

$form.AcceptButton = $useButton
$form.CancelButton = $cancelButton

$chooseSelected = {
    if ($recent.Count -gt 0 -and $list.SelectedIndex -ge 0) {
        $script:selectedPath = $recent[$list.SelectedIndex]
        $form.DialogResult = [System.Windows.Forms.DialogResult]::OK
        $form.Close()
    }
}

$useButton.Add_Click($chooseSelected)
$list.Add_DoubleClick($chooseSelected)

$browseButton.Add_Click({
    $dlg = New-Object System.Windows.Forms.FolderBrowserDialog
    $dlg.Description = 'Select the maps_ap.src folder used by HS2 Mission Editor'
    $dlg.ShowNewFolderButton = $false
    if ($recent.Count -gt 0) {
        $dlg.SelectedPath = $recent[0]
    }

    if ($dlg.ShowDialog($form) -eq [System.Windows.Forms.DialogResult]::OK) {
        $script:selectedPath = $dlg.SelectedPath
        $form.DialogResult = [System.Windows.Forms.DialogResult]::OK
        $form.Close()
    }
})

$cancelButton.Add_Click({
    $form.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
    $form.Close()
})

[void]$form.ShowDialog()

if (-not [string]::IsNullOrWhiteSpace($script:selectedPath)) {
    Save-RecentFolder -SelectedPath $script:selectedPath -Existing $recent
    [Console]::Out.WriteLine($script:selectedPath)
}
