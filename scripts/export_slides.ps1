param(
  [Parameter(Mandatory=$true)][string]$Pptx,
  [Parameter(Mandatory=$true)][string]$OutDir,
  [int]$Width = 1600,
  [int]$Height = 900
)
$pp = $null
try { $pp = [Runtime.InteropServices.Marshal]::GetActiveObject('PowerPoint.Application') } catch { $pp = New-Object -ComObject PowerPoint.Application }
$pptxFullPath = (Get-Item -LiteralPath $Pptx -ErrorAction Stop).FullName
$outDirItem = New-Item -ItemType Directory -Force -Path $OutDir -ErrorAction Stop
$outDirFullPath = $outDirItem.FullName
$pres = $pp.Presentations.Open($pptxFullPath, $true, $false, $false)
$n = $pres.Slides.Count
for ($i = 1; $i -le $n; $i++) {
  $pres.Slides.Item($i).Export((Join-Path $outDirFullPath ('slide{0:d2}.png' -f $i)), 'PNG', $Width, $Height)
}
$pres.Close()
Write-Output ("exported " + $n + " slides to " + $outDirFullPath)
