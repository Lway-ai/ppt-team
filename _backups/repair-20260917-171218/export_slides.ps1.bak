param(
  [Parameter(Mandatory=$true)][string]$Pptx,
  [Parameter(Mandatory=$true)][string]$OutDir,
  [int]$Width = 1600,
  [int]$Height = 900
)
$pp = $null
try { $pp = [Runtime.InteropServices.Marshal]::GetActiveObject('PowerPoint.Application') } catch { $pp = New-Object -ComObject PowerPoint.Application }
$pres = $pp.Presentations.Open($Pptx, $true, $false, $false)
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$n = $pres.Slides.Count
for ($i = 1; $i -le $n; $i++) {
  $pres.Slides.Item($i).Export((Join-Path $OutDir ('slide{0:d2}.png' -f $i)), 'PNG', $Width, $Height)
}
$pres.Close()
Write-Output ("exported " + $n + " slides to " + $OutDir)
