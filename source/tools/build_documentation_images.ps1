param(
    [Parameter(Mandatory = $true)]
    [string]$ReadmeBackground,

    [Parameter(Mandatory = $true)]
    [string]$PagesBackground,

    [Parameter(Mandatory = $true)]
    [string]$SocialBackground
)

$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Drawing

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$outputDir = Join-Path $repoRoot "docs\assets\brand"
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

function New-Brush {
    param(
        [int]$Alpha,
        [int]$Red,
        [int]$Green,
        [int]$Blue
    )

    return [System.Drawing.SolidBrush]::new(
        [System.Drawing.Color]::FromArgb($Alpha, $Red, $Green, $Blue)
    )
}

function Draw-CoverImage {
    param(
        [System.Drawing.Graphics]$Graphics,
        [System.Drawing.Image]$Image,
        [int]$Width,
        [int]$Height
    )

    $sourceRatio = $Image.Width / $Image.Height
    $targetRatio = $Width / $Height

    if ($sourceRatio -gt $targetRatio) {
        $sourceHeight = $Image.Height
        $sourceWidth = [int]($sourceHeight * $targetRatio)
        $sourceX = [int](($Image.Width - $sourceWidth) / 2)
        $sourceY = 0
    }
    else {
        $sourceWidth = $Image.Width
        $sourceHeight = [int]($sourceWidth / $targetRatio)
        $sourceX = 0
        $sourceY = [int](($Image.Height - $sourceHeight) / 2)
    }

    $destination = [System.Drawing.Rectangle]::new(0, 0, $Width, $Height)
    $source = [System.Drawing.Rectangle]::new(
        $sourceX,
        $sourceY,
        $sourceWidth,
        $sourceHeight
    )
    $Graphics.DrawImage(
        $Image,
        $destination,
        $source,
        [System.Drawing.GraphicsUnit]::Pixel
    )
}

function Render-BrandImage {
    param(
        [string]$InputPath,
        [string]$OutputName,
        [int]$Width,
        [int]$Height,
        [int]$TitleSize,
        [int]$SubtitleSize,
        [int]$KickerSize,
        [int]$DispositionSize,
        [int]$TextX,
        [int]$TitleY,
        [int]$TextWidth,
        [string]$Subtitle
    )

    $sourceImage = [System.Drawing.Image]::FromFile((Resolve-Path $InputPath).Path)
    $canvas = [System.Drawing.Bitmap]::new($Width, $Height)
    $canvas.SetResolution(144, 144)
    $graphics = [System.Drawing.Graphics]::FromImage($canvas)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.InterpolationMode =
        [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $graphics.PixelOffsetMode =
        [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $graphics.TextRenderingHint =
        [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit

    Draw-CoverImage -Graphics $graphics -Image $sourceImage -Width $Width -Height $Height

    $shade = [System.Drawing.Drawing2D.LinearGradientBrush]::new(
        [System.Drawing.Rectangle]::new(0, 0, [int]($Width * 0.72), $Height),
        [System.Drawing.Color]::FromArgb(248, 2, 7, 14),
        [System.Drawing.Color]::FromArgb(6, 2, 7, 14),
        [System.Drawing.Drawing2D.LinearGradientMode]::Horizontal
    )
    $graphics.FillRectangle($shade, 0, 0, [int]($Width * 0.72), $Height)

    $cyan = New-Brush -Alpha 255 -Red 25 -Green 216 -Blue 255
    $gold = New-Brush -Alpha 255 -Red 248 -Green 190 -Blue 63
    $white = New-Brush -Alpha 255 -Red 247 -Green 250 -Blue 252
    $muted = New-Brush -Alpha 255 -Red 182 -Green 201 -Blue 214
    $linePen = [System.Drawing.Pen]::new(
        [System.Drawing.Color]::FromArgb(210, 25, 216, 255),
        [Math]::Max(3, [int]($Height / 180))
    )

    $fontFamily = [System.Drawing.FontFamily]::new("Bahnschrift")
    $kickerFont = [System.Drawing.Font]::new(
        $fontFamily,
        $KickerSize,
        [System.Drawing.FontStyle]::Bold,
        [System.Drawing.GraphicsUnit]::Pixel
    )
    $titleFont = [System.Drawing.Font]::new(
        $fontFamily,
        $TitleSize,
        [System.Drawing.FontStyle]::Bold,
        [System.Drawing.GraphicsUnit]::Pixel
    )
    $subtitleFont = [System.Drawing.Font]::new(
        $fontFamily,
        $SubtitleSize,
        [System.Drawing.FontStyle]::Regular,
        [System.Drawing.GraphicsUnit]::Pixel
    )
    $dispositionFont = [System.Drawing.Font]::new(
        $fontFamily,
        $DispositionSize,
        [System.Drawing.FontStyle]::Bold,
        [System.Drawing.GraphicsUnit]::Pixel
    )

    $format = [System.Drawing.StringFormat]::new()
    $format.Trimming = [System.Drawing.StringTrimming]::EllipsisWord
    $format.FormatFlags = [System.Drawing.StringFormatFlags]::LineLimit

    $kickerY = $TitleY - [int]($KickerSize * 1.8)
    $graphics.DrawString(
        "COLLABORATIVE DYNAMICS  /  CAPABILITY ASSAY",
        $kickerFont,
        $cyan,
        [System.Drawing.RectangleF]::new(
            $TextX,
            $kickerY,
            $TextWidth,
            [int]($KickerSize * 1.5)
        ),
        $format
    )

    $graphics.DrawString(
        "PRAXIS MINE",
        $titleFont,
        $white,
        [System.Drawing.RectangleF]::new(
            $TextX,
            $TitleY,
            $TextWidth,
            [int]($TitleSize * 1.25)
        ),
        $format
    )

    $lineY = $TitleY + [int]($TitleSize * 1.2)
    $graphics.DrawLine(
        $linePen,
        $TextX,
        $lineY,
        $TextX + [int]($TextWidth * 0.72),
        $lineY
    )

    $subtitleY = $lineY + [int]($SubtitleSize * 0.72)
    $graphics.DrawString(
        $Subtitle,
        $subtitleFont,
        $muted,
        [System.Drawing.RectangleF]::new(
            $TextX,
            $subtitleY,
            $TextWidth,
            [int]($SubtitleSize * 2.8)
        ),
        $format
    )

    $dispositionY = $subtitleY + [int]($SubtitleSize * 2.55)
    $graphics.DrawString(
        "PILOT  /  QUARRY  /  ADAPT  /  MONITOR  /  REJECT",
        $dispositionFont,
        $gold,
        [System.Drawing.RectangleF]::new(
            $TextX,
            $dispositionY,
            $TextWidth,
            [int]($DispositionSize * 1.5)
        ),
        $format
    )

    $outputPath = Join-Path $outputDir $OutputName
    if ([System.IO.Path]::GetExtension($outputPath) -eq ".jpg") {
        $jpegCodec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() |
            Where-Object { $_.MimeType -eq "image/jpeg" }
        $encoderParameters = [System.Drawing.Imaging.EncoderParameters]::new(1)
        $encoderParameters.Param[0] = [System.Drawing.Imaging.EncoderParameter]::new(
            [System.Drawing.Imaging.Encoder]::Quality,
            [long]92
        )
        $canvas.Save($outputPath, $jpegCodec, $encoderParameters)
        $encoderParameters.Dispose()
    }
    else {
        $canvas.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)
    }

    $dispositionFont.Dispose()
    $subtitleFont.Dispose()
    $titleFont.Dispose()
    $kickerFont.Dispose()
    $fontFamily.Dispose()
    $format.Dispose()
    $linePen.Dispose()
    $muted.Dispose()
    $white.Dispose()
    $gold.Dispose()
    $cyan.Dispose()
    $shade.Dispose()
    $graphics.Dispose()
    $canvas.Dispose()
    $sourceImage.Dispose()

    return $outputPath
}

$outputs = @(
    Render-BrandImage `
        -InputPath $ReadmeBackground `
        -OutputName "praxis-mine-readme-hero.png" `
        -Width 2244 `
        -Height 701 `
        -TitleSize 104 `
        -SubtitleSize 35 `
        -KickerSize 22 `
        -DispositionSize 24 `
        -TextX 120 `
        -TitleY 184 `
        -TextWidth 1180 `
        -Subtitle "Mine outside AI systems. Keep only the capability delta."

    Render-BrandImage `
        -InputPath $PagesBackground `
        -OutputName "praxis-mine-pages-hero.png" `
        -Width 1896 `
        -Height 829 `
        -TitleSize 104 `
        -SubtitleSize 37 `
        -KickerSize 22 `
        -DispositionSize 24 `
        -TextX 100 `
        -TitleY 230 `
        -TextWidth 930 `
        -Subtitle "Mine outside AI systems.`nKeep only the capability delta."

    Render-BrandImage `
        -InputPath $SocialBackground `
        -OutputName "praxis-mine-social-preview.jpg" `
        -Width 1280 `
        -Height 640 `
        -TitleSize 78 `
        -SubtitleSize 27 `
        -KickerSize 17 `
        -DispositionSize 18 `
        -TextX 72 `
        -TitleY 168 `
        -TextWidth 660 `
        -Subtitle "Mine outside AI systems.`nKeep only the capability delta."
)

foreach ($output in $outputs) {
    $image = [System.Drawing.Image]::FromFile($output)
    "{0} {1}x{2}" -f $output, $image.Width, $image.Height
    $image.Dispose()
}
