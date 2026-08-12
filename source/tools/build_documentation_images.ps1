param()

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$outputDir = Join-Path $repoRoot "docs\assets\brand"
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

function New-Canvas([int]$Width,[int]$Height) {
    $bitmap = [System.Drawing.Bitmap]::new($Width,$Height)
    $bitmap.SetResolution(144,144)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $graphics.Clear([System.Drawing.Color]::FromArgb(2,7,13))
    $bg = [System.Drawing.Drawing2D.LinearGradientBrush]::new(
        [System.Drawing.Rectangle]::new(0,0,$Width,$Height),
        [System.Drawing.Color]::FromArgb(2,7,13),
        [System.Drawing.Color]::FromArgb(4,24,38),
        24.0
    )
    $graphics.FillRectangle($bg,0,0,$Width,$Height)
    $bg.Dispose()
    @{Bitmap=$bitmap;Graphics=$graphics}
}

function Add-Grid($Graphics,[int]$Width,[int]$Height,[int]$Step=48) {
    $pen=[System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(22,25,216,255),1)
    for($x=0;$x -le $Width;$x+=$Step){$Graphics.DrawLine($pen,$x,0,$x,$Height)}
    for($y=0;$y -le $Height;$y+=$Step){$Graphics.DrawLine($pen,0,$y,$Width,$y)}
    $pen.Dispose()
}

function Draw-Text($Graphics,[string]$Text,[float]$X,[float]$Y,[float]$Width,[float]$Height,[float]$Size,[System.Drawing.Color]$Color,[System.Drawing.FontStyle]$Style=[System.Drawing.FontStyle]::Regular) {
    $font=[System.Drawing.Font]::new("Bahnschrift",$Size,$Style,[System.Drawing.GraphicsUnit]::Pixel)
    $brush=[System.Drawing.SolidBrush]::new($Color)
    $format=[System.Drawing.StringFormat]::new()
    $format.Trimming=[System.Drawing.StringTrimming]::EllipsisWord
    $format.FormatFlags=[System.Drawing.StringFormatFlags]::LineLimit
    $Graphics.DrawString($Text,$font,$brush,[System.Drawing.RectangleF]::new($X,$Y,$Width,$Height),$format)
    $format.Dispose();$brush.Dispose();$font.Dispose()
}

function Draw-Diamond($Graphics,[float]$CenterX,[float]$CenterY,[float]$Radius,[System.Drawing.Color]$Fill,[System.Drawing.Color]$Stroke) {
    $points=[System.Drawing.PointF[]]@(
        [System.Drawing.PointF]::new($CenterX,$CenterY-$Radius),
        [System.Drawing.PointF]::new($CenterX+$Radius,$CenterY),
        [System.Drawing.PointF]::new($CenterX,$CenterY+$Radius),
        [System.Drawing.PointF]::new($CenterX-$Radius,$CenterY)
    )
    $brush=[System.Drawing.SolidBrush]::new($Fill)
    $pen=[System.Drawing.Pen]::new($Stroke,[Math]::Max(2,$Radius/12))
    $Graphics.FillPolygon($brush,$points);$Graphics.DrawPolygon($pen,$points)
    $pen.Dispose();$brush.Dispose()
}

function Draw-RoundedPanel($Graphics,$Brush,$Pen,[System.Drawing.RectangleF]$Rect,[float]$Radius) {
    $path=[System.Drawing.Drawing2D.GraphicsPath]::new()
    $d=$Radius*2
    $path.AddArc($Rect.X,$Rect.Y,$d,$d,180,90)
    $path.AddArc($Rect.Right-$d,$Rect.Y,$d,$d,270,90)
    $path.AddArc($Rect.Right-$d,$Rect.Bottom-$d,$d,$d,0,90)
    $path.AddArc($Rect.X,$Rect.Bottom-$d,$d,$d,90,90)
    $path.CloseFigure()
    $Graphics.FillPath($Brush,$path);$Graphics.DrawPath($Pen,$path)
    $path.Dispose()
}

function Save-Png($Bitmap,[string]$Name) {
    $path=Join-Path $outputDir $Name
    $Bitmap.Save($path,[System.Drawing.Imaging.ImageFormat]::Png)
    $path
}

function New-ReadmeHero {
    $w=1600;$h=720;$canvas=New-Canvas $w $h;$g=$canvas.Graphics;Add-Grid $g $w $h 64
    $cyan=[System.Drawing.Color]::FromArgb(25,216,255)
    $cyanSoft=[System.Drawing.Color]::FromArgb(156,236,255)
    $gold=[System.Drawing.Color]::FromArgb(248,190,63)
    $rockBrush=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(18,40,54))
    $rockBrush2=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(27,54,68))
    $goldBrush=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(220,248,190,63))
    $cyanPen=[System.Drawing.Pen]::new($cyan,8)
    $thinCyan=[System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(130,25,216,255),3)
    $g.FillPolygon($rockBrush,[System.Drawing.Point[]]@(
        [System.Drawing.Point]::new(0,460),[System.Drawing.Point]::new(230,375),
        [System.Drawing.Point]::new(470,445),[System.Drawing.Point]::new(690,360),
        [System.Drawing.Point]::new(870,455),[System.Drawing.Point]::new(1000,420),
        [System.Drawing.Point]::new(1000,720),[System.Drawing.Point]::new(0,720)))
    $g.FillPolygon($rockBrush2,[System.Drawing.Point[]]@(
        [System.Drawing.Point]::new(0,570),[System.Drawing.Point]::new(255,500),
        [System.Drawing.Point]::new(430,565),[System.Drawing.Point]::new(660,500),
        [System.Drawing.Point]::new(870,590),[System.Drawing.Point]::new(1000,535),
        [System.Drawing.Point]::new(1000,720),[System.Drawing.Point]::new(0,720)))
    $g.FillPolygon($goldBrush,[System.Drawing.Point[]]@(
        [System.Drawing.Point]::new(90,552),[System.Drawing.Point]::new(285,488),
        [System.Drawing.Point]::new(430,528),[System.Drawing.Point]::new(618,470),
        [System.Drawing.Point]::new(814,548),[System.Drawing.Point]::new(935,510),
        [System.Drawing.Point]::new(818,579),[System.Drawing.Point]::new(610,512),
        [System.Drawing.Point]::new(430,568),[System.Drawing.Point]::new(270,530)))
    $g.DrawLine($cyanPen,1020,104,1020,620)
    $g.DrawArc($thinCyan,910,235,220,220,200,300)
    $g.DrawLine($thinCyan,1020,360,1205,360)
    $g.DrawLine($thinCyan,1020,300,1155,190)
    $g.DrawLine($thinCyan,1020,420,1155,530)
    Draw-Diamond $g 1315 360 118 ([System.Drawing.Color]::FromArgb(210,248,190,63)) $cyan
    Draw-Diamond $g 1315 360 48 ([System.Drawing.Color]::FromArgb(255,255,224,136)) ([System.Drawing.Color]::White)
    Draw-Text $g "SOURCE SYSTEM" 82 82 420 50 24 $cyanSoft ([System.Drawing.FontStyle]::Bold)
    Draw-Text $g "ASSAY" 934 60 180 50 24 $cyan ([System.Drawing.FontStyle]::Bold)
    Draw-Text $g "CAPABILITY DELTA" 1190 545 340 50 24 $gold ([System.Drawing.FontStyle]::Bold)
    Draw-Text $g "Keep the mechanism. Leave the authority, dependencies, and theater." 82 132 690 105 34 ([System.Drawing.Color]::FromArgb(245,248,251)) ([System.Drawing.FontStyle]::Bold)
    $thinCyan.Dispose();$cyanPen.Dispose();$goldBrush.Dispose();$rockBrush2.Dispose();$rockBrush.Dispose()
    $path=Save-Png $canvas.Bitmap "praxis-mine-readme-hero.png";$g.Dispose();$canvas.Bitmap.Dispose();$path
}

function New-PagesHero {
    $w=1200;$h=800;$canvas=New-Canvas $w $h;$g=$canvas.Graphics;Add-Grid $g $w $h 50
    $cyan=[System.Drawing.Color]::FromArgb(25,216,255)
    $gold=[System.Drawing.Color]::FromArgb(248,190,63)
    $white=[System.Drawing.Color]::FromArgb(245,248,251)
    $muted=[System.Drawing.Color]::FromArgb(182,201,214)
    $panelBrush=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(225,3,18,30))
    $cyanPen=[System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(170,25,216,255),3)
    $goldPen=[System.Drawing.Pen]::new($gold,6)
    Draw-Text $g "THE DISPOSITION BOARD" 64 54 760 60 38 $white ([System.Drawing.FontStyle]::Bold)
    Draw-Text $g "A decision surface for one bounded capability delta" 67 112 770 45 23 $muted
    Draw-Diamond $g 1070 105 46 ([System.Drawing.Color]::FromArgb(220,248,190,63)) $cyan
    $labels=@(
        @("PILOT","Run a bounded trial"),@("QUARRY","Keep the artifact"),
        @("ADAPT","Rewrite the mechanism"),@("MONITOR","Watch for a trigger"),
        @("REJECT","Record why it stays out"))
    for($i=0;$i -lt $labels.Count;$i++){
        $y=202+($i*105);$rect=[System.Drawing.RectangleF]::new(64,$y,1072,82)
        Draw-RoundedPanel $g $panelBrush $cyanPen $rect 16
        Draw-Text $g ("0{0}" -f ($i+1)) 88 ($y+22) 58 34 20 $cyan ([System.Drawing.FontStyle]::Bold)
        $labelColor=if($i -eq 2){$gold}else{$white}
        Draw-Text $g $labels[$i][0] 160 ($y+17) 230 45 26 $labelColor ([System.Drawing.FontStyle]::Bold)
        Draw-Text $g $labels[$i][1] 410 ($y+19) 620 42 23 $muted
        if($i -eq 2){$g.DrawLine($goldPen,1040,$y+20,1040,$y+62)}
    }
    Draw-Text $g "No automatic adoption. No hidden execution. Every outcome gets evidence and a reason." 65 739 1060 38 20 $gold ([System.Drawing.FontStyle]::Bold)
    $goldPen.Dispose();$cyanPen.Dispose();$panelBrush.Dispose()
    $path=Save-Png $canvas.Bitmap "praxis-mine-pages-hero.png";$g.Dispose();$canvas.Bitmap.Dispose();$path
}

function New-SocialCard {
    $w=1200;$h=630;$canvas=New-Canvas $w $h;$g=$canvas.Graphics;Add-Grid $g $w $h 60
    $cyan=[System.Drawing.Color]::FromArgb(25,216,255)
    $gold=[System.Drawing.Color]::FromArgb(248,190,63)
    $white=[System.Drawing.Color]::FromArgb(248,250,252)
    $muted=[System.Drawing.Color]::FromArgb(182,201,214)
    $goldBrush=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(28,248,190,63))
    $cyanPen=[System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(120,25,216,255),3)
    $g.FillEllipse($goldBrush,780,72,350,350);$g.DrawEllipse($cyanPen,810,102,290,290)
    Draw-Diamond $g 955 247 135 ([System.Drawing.Color]::FromArgb(215,248,190,63)) $cyan
    Draw-Diamond $g 955 247 55 ([System.Drawing.Color]::FromArgb(255,255,226,142)) $white
    Draw-Text $g "COLLABORATIVE DYNAMICS  /  CAPABILITY ASSAY" 65 58 710 42 20 $cyan ([System.Drawing.FontStyle]::Bold)
    Draw-Text $g "PRAXIS MINE" 60 132 720 105 76 $white ([System.Drawing.FontStyle]::Bold)
    Draw-Text $g "Mine outside AI systems." 65 270 650 48 31 $white ([System.Drawing.FontStyle]::Bold)
    Draw-Text $g "Keep only the capability delta." 65 320 680 48 31 $gold ([System.Drawing.FontStyle]::Bold)
    Draw-Text $g "PILOT   /   QUARRY   /   ADAPT   /   MONITOR   /   REJECT" 65 498 1065 42 20 $cyan ([System.Drawing.FontStyle]::Bold)
    Draw-Text $g "Evidence before adoption." 65 555 640 36 20 $muted
    $cyanPen.Dispose();$goldBrush.Dispose()
    $path=Save-Png $canvas.Bitmap "praxis-mine-social-card.png";$g.Dispose();$canvas.Bitmap.Dispose();$path
}

$outputs=@(New-ReadmeHero;New-PagesHero;New-SocialCard)
$legacy=Join-Path $outputDir "praxis-mine-social-preview.jpg"
if(Test-Path -LiteralPath $legacy){Remove-Item -LiteralPath $legacy}
foreach($output in $outputs){
    $image=[System.Drawing.Image]::FromFile($output)
    $hash=(Get-FileHash -LiteralPath $output -Algorithm SHA256).Hash.ToLowerInvariant()
    "{0} {1}x{2} sha256:{3}" -f $output,$image.Width,$image.Height,$hash
    $image.Dispose()
}
