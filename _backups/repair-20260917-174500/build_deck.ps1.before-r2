# build_deck.ps1 - round 0 skeleton build for FM_IQ_Receiver_RFIC2024.pptx (19 slides, variant 2)
# ASCII-only source. All CJK text comes from UTF-8 JSON files (AGENTS.md rule 3).
# COM discipline: attach to running PowerPoint (GetActiveObject), only touch OUR Presentation, never Quit.
$ErrorActionPreference = 'Stop'
$root   = 'D:\wanglei\project\TDA7707_GNSS\E_project\multi_agent_PPT_zcode'
$exdir  = Join-Path $root 'examples\fm_iq_receiver_rmo01a'
$assets = Join-Path $exdir 'assets'

. (Join-Path $root 'scripts\build_helpers.ps1')
Import-StyleProfile -Path (Join-Path $root 'scripts\style.json') | Out-Null

$content = Get-Content (Join-Path $exdir 'deck_content.json') -Encoding UTF8 -Raw | ConvertFrom-Json
$emph    = Get-Content (Join-Path $exdir 'deck_emph.json')    -Encoding UTF8 -Raw | ConvertFrom-Json
$t16     = Get-Content (Join-Path $exdir 'table16.json')      -Encoding UTF8 -Raw | ConvertFrom-Json
$deck    = Join-Path $exdir 'FM_IQ_Receiver_RFIC2024.pptx'

function Add-SpecShape {
  param($slide, $sp)
  if ($sp.pic) {
    $img = Join-Path $assets $sp.pic
    if (-not (Test-Path $img)) { throw ('missing asset: ' + $img) }
    Add-Picture -Slide $slide -Name $sp.name -Image $img -Left $sp.x -Top $sp.y -Width $sp.w -Height $sp.h | Out-Null
    return
  }
  $txt = [string]$sp.text
  $txt = $txt.Replace("`r", '').Replace("`n", [string][char]13)
  $col = HexColor $sp.color
  if ($sp.box) {
    $shp = 1
    if ($sp.shape -eq 'round') { $shp = 5 }        # msoShapeRoundedRectangle
    if ($sp.shape -eq 'arrowR') { $shp = 33 }      # msoShapeRightArrow
    $sh = $slide.Shapes.AddShape($shp, [single]$sp.x, [single]$sp.y, [single]$sp.w, [single]$sp.h)
    $sh.Name = $sp.name
    $sh.Fill.ForeColor.RGB = HexColor $sp.fill
    $sh.Fill.Solid()
    $sh.Line.ForeColor.RGB = HexColor $sp.line
    $sh.Line.Weight = [single]$sp.linew
    $sh.TextFrame.VerticalAnchor = 3
    $sh.TextFrame.MarginLeft = 4; $sh.TextFrame.MarginRight = 4
    $sh.TextFrame.MarginTop = 2;  $sh.TextFrame.MarginBottom = 2
    $sh.TextFrame.WordWrap = -1
    $sh.TextFrame.TextRange.Text = $txt
    Set-Font -Range $sh.TextFrame.TextRange -Size $sp.size -Bold:([bool]$sp.bold) -ColorRGB $col
    $sh.TextFrame.TextRange.ParagraphFormat.Alignment = $sp.align
  }
  else {
    $sh = Add-TextBox -Slide $slide -Name $sp.name -Left $sp.x -Top $sp.y -Width $sp.w -Height $sp.h `
      -Text $txt -Size $sp.size -ColorRGB $col -Bold:([bool]$sp.bold) -Italic:([bool]$sp.italic) -Align $sp.align
  }
  if ($sp.spaceAfter) { $sh.TextFrame.TextRange.ParagraphFormat.SpaceAfter = [single]$sp.spaceAfter }
  if ($sp.bullet) {
    $tr = $sh.TextFrame.TextRange
    $n = $tr.Paragraphs().Count
    for ($p = 1; $p -le $n; $p++) {
      $para = $tr.Paragraphs($p, 1)
      if ($para.Text.Length -gt 0) {
        $first = $para.Characters(1, 1)
        if ($first.Text -eq [string][char]0x2022) { $first.Font.Color.RGB = HexColor '197084' }
      }
    }
  }
}

function Fix-PageNo {
  param($slide)
  # default PageNo box (80pt) wraps "N of 19"; with wrap off autofit snaps width back to text,
  # so pin geometry: no autosize, no wrap, fixed 140pt centered box
  $pn = $slide.Shapes.Item('PageNo')
  $pn.TextFrame.AutoSize = 0
  $pn.TextFrame.WordWrap = 0
  $pn.Left = [single]410.0
  $pn.Width = [single]140.0
  $pn.Height = [single]30.0
}

# ---- slide 1: cover ----
$pres = New-Deck -Path $deck
$s1 = Add-BlankSlide -Pres $pres
foreach ($sp in $content.slides.'1') { Add-SpecShape $s1 $sp | Out-Null }
# cover title: 2 manual lines; pin planned geometry (est 118.8pt <= 132*1.02+2)
$ct = $s1.Shapes.Item('CoverTitle')
$ct.TextFrame.AutoSize = 0
$ct.Height = [single]132.0
Add-FooterBand -Slide $s1 -PageNo '0' | Out-Null
Fix-PageNo $s1

# ---- slides 2..19: title + footer + spec shapes ----
for ($i = 2; $i -le 19; $i++) {
  $s = Add-BlankSlide -Pres $pres
  $ttf = Join-Path $env:TEMP ('deck_title_' + $i + '.txt')
  [System.IO.File]::WriteAllText($ttf, [string]$content.titles."$i", (New-Object System.Text.UTF8Encoding($false)))
  if ($i -eq 6) {
    # p6 title keeps short form (no chain terms -> no short/full term conflict; chips + p2 carry full forms)
    Add-Title -Slide $s -TextFile $ttf
  }
  else {
    Add-Title -Slide $s -TextFile $ttf
  }
  $ttl = $s.Shapes.Item('Title')
  $ttl.Height = 66
  if ($i -eq 3) {
    # widest title: widen box so the single-line est stays green (centered text, visual margins intact)
    $ttl.Left = [single]24.0
    $ttl.Width = [single]912.0
  }
  Add-FooterBand -Slide $s -PageNo (('{0} of 19') -f ($i - 1)) | Out-Null
  Fix-PageNo $s
  foreach ($sp in $content.slides."$i") { Add-SpecShape $s $sp | Out-Null }
  if ($i -eq 7) {
    # pin Bullets7: heuristic est 4 lines vs PowerPoint autofit 2 lines; planned box keeps est green
    $b7 = $s.Shapes.Item('Bullets7')
    $b7.TextFrame.AutoSize = 0
    $b7.Height = [single]124.0
  }
  if ($i -eq 6) {
    # pin Bullets6 against the 0.55em heuristic (para2 est 282pt vs avail 284pt is 1 line in Calibri)
    $b6 = $s.Shapes.Item('Bullets6')
    $b6.TextFrame.AutoSize = 0
    $b6.Height = [single]80.0
  }
}

# ---- slide 16: three-line academic table ----
$s16 = $pres.Slides.Item(16)
$nRows = 1 + @($t16.data).Count
$gf = $s16.Shapes.AddTable($nRows, 3, [single]$t16.x, [single]$t16.y, [single]$t16.w, [single](28 * $nRows))
$gf.Name = 'Table16'
$tbl = $gf.Table
$tbl.Columns.Item(1).Width = [single]$t16.cols[0]
$tbl.Columns.Item(2).Width = [single]$t16.cols[1]
$tbl.Columns.Item(3).Width = [single]$t16.cols[2]
for ($r = 1; $r -le $nRows; $r++) {
  $tbl.Rows.Item($r).Height = 28
  for ($c = 1; $c -le 3; $c++) {
    $cell = $tbl.Cell($r, $c)
    $ctf = $cell.Shape.TextFrame
    $ctf.MarginTop = 1; $ctf.MarginBottom = 1; $ctf.MarginLeft = 6; $ctf.MarginRight = 6
    $ctf.VerticalAnchor = 3
    $cell.Shape.Fill.ForeColor.RGB = HexColor 'FFFFFF'
    $cell.Shape.Fill.Solid()
    for ($b = 1; $b -le 6; $b++) { try { $cell.Borders($b).Visible = 0 } catch { } }
    if ($r -eq 1) {
      $ctf.TextRange.Text = [string]$t16.header[$c - 1]
      Set-Font -Range $ctf.TextRange -Size 18 -Bold -ColorRGB (HexColor '000000')
      $ctf.TextRange.ParagraphFormat.Alignment = 2
      $cell.Borders(1).Visible = -1; $cell.Borders(1).Weight = 2.25; $cell.Borders(1).ForeColor.RGB = HexColor '000000'
      $cell.Borders(3).Visible = -1; $cell.Borders(3).Weight = 2.25; $cell.Borders(3).ForeColor.RGB = HexColor '000000'
    }
    else {
      $ctf.TextRange.Text = [string]$t16.data[$r - 2][$c - 1]
      if ($c -eq 2) {
        Set-Font -Range $ctf.TextRange -Size 18 -Bold -ColorRGB (HexColor '0070C0')
        $ctf.TextRange.ParagraphFormat.Alignment = 2
      }
      elseif ($c -eq 1) {
        Set-Font -Range $ctf.TextRange -Size 18 -ColorRGB (HexColor '000000')
        $ctf.TextRange.ParagraphFormat.Alignment = 1
      }
      else {
        Set-Font -Range $ctf.TextRange -Size 18 -ColorRGB (HexColor '000000')
        $ctf.TextRange.ParagraphFormat.Alignment = 1
      }
      if ($r -eq $nRows) {
        $cell.Borders(3).Visible = -1; $cell.Borders(3).Weight = 1.5; $cell.Borders(3).ForeColor.RGB = HexColor '000000'
      }
    }
  }
}
Add-TextBox -Slide $s16 -Name 'Note16' -Left 60 -Top 458 -Width 840 -Height 24 -Text ([string]$t16.footnote) -Size 16 -ColorRGB (HexColor '000000') -Align 1 | Out-Null

# ---- emphasis runs ----
foreach ($e in $emph) {
  $s = $pres.Slides.Item([int]$e.slide)
  $sh = $s.Shapes.Item([string]$e.shape)
  $tr = $sh.TextFrame.TextRange
  $find = [string]$e.find
  $ix = $tr.Text.IndexOf($find)
  if ($ix -ge 0) {
    $rr = $tr.Characters($ix + 1, $find.Length)
    $rr.Font.Color.RGB = HexColor $e.color
    if ($e.bold) { $rr.Font.Bold = -1 }
  }
  else { Write-Output ('WARN emph miss: slide ' + $e.slide + ' [' + $e.shape + '] ' + $e.find) }
}

Close-Deck -Pres $pres -Path $deck
Write-Output ('deck saved: ' + $deck)
