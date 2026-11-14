# Shared helpers: dynamically find Maya PID/window; actions: send / list / btns / click <name>
param([string]$action, [string]$arg1)
Add-Type -AssemblyName UIAutomationClient,UIAutomationTypes,System.Windows.Forms
$root = [System.Windows.Automation.AutomationElement]::RootElement
$allwins = $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
$mayWin = $null; $mayaPid = 0
foreach ($w in $allwins) {
  if ($w.Current.ClassName -eq 'TmainWindow' -and $w.Current.Name -match 'MAYA') {
    $mayWin = $w; $mayaPid = $w.Current.ProcessId; break
  }
}
if (-not $mayWin) { Write-Output "NO_MAYA_WINDOW"; exit 1 }
if ($action -eq 'send') {
  $editCond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Edit)
  $edits = $mayWin.FindAll([System.Windows.Automation.TreeScope]::Descendants, $editCond)
  $target = $null
  foreach ($e in $edits) { if ($e.Current.Name -match 'MEL|嵌入式语言') { $target = $e; break } }
  if (-not $target) { Write-Output "NO_CMDLINE"; exit 1 }
  $vp = $target.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
  $vp.SetValue($arg1)
  $target.SetFocus()
  Start-Sleep -Milliseconds 200
  [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
  Write-Output "SENT_OK pid=$mayaPid"
} elseif ($action -eq 'title') {
  Write-Output "TITLE: $($mayWin.Current.Name)"
} elseif ($action -eq 'btns') {
  $btnCond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button)
  $btns = $mayWin.FindAll([System.Windows.Automation.TreeScope]::Descendants, $btnCond)
  foreach ($b in $btns) { Write-Output ("BTN: " + $b.Current.Name) }
} elseif ($action -eq 'click') {
  $btnCond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $arg1)
  $btns = $mayWin.FindAll([System.Windows.Automation.TreeScope]::Descendants, $btnCond)
  foreach ($b in $btns) {
    try { $b.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Write-Output "CLICKED: $arg1"; break } catch {}
  }
}
