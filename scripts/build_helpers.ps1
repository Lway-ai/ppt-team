# build_helpers.ps1 - RFIC 会议风格 PPT 建页函数库（PowerPoint COM 管线）
# 用法: . .\scripts\build_helpers.ps1  然后 New-Deck / Add-BlankSlide / Add-TextBox / Add-FooterBand / Close-Deck
# 纪律（AGENTS.md / SKILL.md 第十-十二节）:
#   - 禁止 python-pptx 保存; 本库全部走 COM, 位置赋值用 [single]
#   - 中文文本必须经 UTF-8 文件传入(Get-Content -Encoding UTF8), 严禁内联在命令行
#   - 形状命名契约: 页脚色带=FooterBand 页码=PageNo 会话号=SessionId 容器=KeyBox* 便签=NoteBox 结论条=TakeawayStrip
#   - .Text 赋值后字体会被重置, 赋值后再 Set-Font

$script:EMU_PT = 12700.0

function HexColor {
  # '#RRGGBB' 或 'RRGGBB' -> Office COM 的 RGB 整数(字节序 R + G*256 + B*65536)。
  # 直接把 0x197084 传给 Font.Color.RGB 会得到反色 #847019 —— 必须经本函数转换!
  param([Parameter(Mandatory=$true)][string]$Hex)
  $h = $Hex.TrimStart('#')
  $r = [Convert]::ToInt32($h.Substring(0, 2), 16)
  $g = [Convert]::ToInt32($h.Substring(2, 2), 16)
  $b = [Convert]::ToInt32($h.Substring(4, 2), 16)
  return $r + $g * 256 + $b * 65536
}

function New-Deck {
  param([Parameter(Mandatory=$true)][string]$Path)
  $app = $null
  try { $app = [Runtime.InteropServices.Marshal]::GetActiveObject('PowerPoint.Application') }
  catch { $app = New-Object -ComObject PowerPoint.Application }
  $pres = $app.Presentations.Add(0)  # msoFalse: 不带窗口
  # 960x540pt = 12192000x6858000 EMU
  $pres.PageSetup.SlideWidth  = 960
  $pres.PageSetup.SlideHeight = 540
  $pres | Add-Member -NotePropertyName ScriptPath -NotePropertyValue $Path -Force
  Write-Output $pres
}

function Add-BlankSlide {
  param([Parameter(Mandatory=$true)]$Pres)
  # ppLayoutBlank = 12
  $s = $Pres.Slides.Add($Pres.Slides.Count + 1, 12)
  Write-Output $s
}

function Set-Font {
  param($Range, [string]$Latin = 'Calibri', [string]$EastAsia = '微软雅黑',
        [int]$Size = 32, [switch]$Bold, [switch]$Italic,
        [int]$ColorRGB = 0x000000)
  # 注意: 数学区(OMML)形状严禁调用本函数改字体 —— COM 对数学区静默无效, 只能 raw-zip 拼 XML
  $Range.Font.Name = $Latin
  $Range.Font.NameFarEast = $EastAsia
  $Range.Font.Size = $Size
  $Range.Font.Bold = [int][bool]$Bold
  $Range.Font.Italic = [int][bool]$Italic
  $Range.Font.Color.RGB = $ColorRGB
}

function Add-TextBox {
  param([Parameter(Mandatory=$true)]$Slide,
        [Parameter(Mandatory=$true)][string]$Name,
        [float]$Left, [float]$Top, [float]$Width, [float]$Height,
        [string]$TextFile,          # UTF-8 文本文件路径(支持中文/多行)
        [string]$Text = '',
        [int]$Size = 32, [int]$ColorRGB = 0x000000,
        [string]$Latin = 'Calibri', [string]$EastAsia = '微软雅黑',
        [switch]$Bold, [switch]$Italic,
        [int]$Align = 1)            # 1=左 2=居中
  $tb = $Slide.Shapes.AddTextbox(1, [single]$Left, [single]$Top, [single]$Width, [single]$Height)
  $tb.Name = $Name
  if ($TextFile) {
    $content = Get-Content -Path $TextFile -Encoding UTF8 -Raw
    $content = $content -replace "`r`n", [char]11 -replace "`n", [char]11
    $tb.TextFrame.TextRange.Text = $content.TrimEnd([char]11)
  } else {
    $tb.TextFrame.TextRange.Text = $Text
  }
  Set-Font -Range $tb.TextFrame.TextRange -Latin $Latin -EastAsia $EastAsia -Size $Size -Bold:$Bold -Italic:$Italic -ColorRGB $ColorRGB
  $tb.TextFrame.TextRange.ParagraphFormat.Alignment = $Align
  $tb.TextFrame.WordWrap = -1
  Write-Output $tb
}

function Add-Picture {
  param([Parameter(Mandatory=$true)]$Slide,
        [Parameter(Mandatory=$true)][string]$Name,
        [Parameter(Mandatory=$true)][string]$Image,
        [float]$Left, [float]$Top, [float]$Width, [float]$Height)
  $pic = $Slide.Shapes.AddPicture($Image, 0, -1, [single]$Left, [single]$Top, [single]$Width, [single]$Height)
  $pic.Name = $Name
  Write-Output $pic
}

function Add-FooterBand {
  param([Parameter(Mandatory=$true)]$Slide,
        [string]$AssetsDir = (Join-Path $PSScriptRoot '..\assets'),
        [string]$PageNo = '',      # 字符串页码(封面请传 '0')
        [string]$SessionId = '',   # 如 'RMo1A-1'
        [int]$PageColorRGB = 0x000000)
  $band = Join-Path $AssetsDir 'footer_band.png'
  if (-not (Test-Path $band)) { throw "缺页脚色带素材: $band (先跑 scripts/make_footer_band.py)" }
  $b = $Slide.Shapes.AddPicture($band, 0, -1, [single]0, [single]502, [single]960, [single]38)
  $b.Name = 'FooterBand'
  if ($PageNo -ne '') {
    $p = $Slide.Shapes.AddTextbox(1, [single]440, [single]506, [single]80, [single]30)
    $p.Name = 'PageNo'
    $p.TextFrame.TextRange.Text = $PageNo
    Set-Font -Range $p.TextFrame.TextRange -Size 20 -ColorRGB $PageColorRGB
    $p.TextFrame.TextRange.ParagraphFormat.Alignment = 2
  }
  if ($SessionId -ne '') {
    $s = $Slide.Shapes.AddTextbox(1, [single]780, [single]508, [single]170, [single]26)
    $s.Name = 'SessionId'
    $s.TextFrame.TextRange.Text = $SessionId
    Set-Font -Range $s.TextFrame.TextRange -Size 14 -ColorRGB $PageColorRGB
    $s.TextFrame.TextRange.ParagraphFormat.Alignment = 2
  }
  Write-Output $b
}

function Add-Title {
  param([Parameter(Mandatory=$true)]$Slide,
        [Parameter(Mandatory=$true)][string]$TextFile,
        [int]$Size = 48, [int]$ColorRGB = 0x197084)   # 默认=官方模板 48pt 青绿; Zou 变体传 44/0x000000
  Add-TextBox -Slide $Slide -Name 'Title' -Left 40 -Top 20 -Width 880 -Height 60 `
    -TextFile $TextFile -Size $Size -Bold -ColorRGB $ColorRGB -Align 2 -Latin 'Calibri' | Out-Null
}

function Close-Deck {
  param([Parameter(Mandatory=$true)]$Pres, [string]$Path = '')
  if ($Path -eq '') { $Path = $Pres.ScriptPath }
  $presFolder = Split-Path $Path -Parent
  if ($presFolder -and -not (Test-Path $presFolder)) { New-Item -ItemType Directory -Force -Path $presFolder | Out-Null }
  $Pres.SaveAs((Resolve-PathCompatible $Path))
  $Pres.Close()
}

function Resolve-PathCompatible { param([string]$P) return $P }

# 结束后由调用方决定是否退出 PowerPoint 进程; 多轮建页请复用同一 $pres 句柄(串行写入纪律)
