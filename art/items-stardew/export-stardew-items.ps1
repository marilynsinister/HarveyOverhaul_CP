param([switch]$Install)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

# Mechanical export only: the artwork is in generated/*.png (built-in image_gen).
# Crop the atlas cells, sample without smoothing, reduce to a shared palette,
# and pack the original runtime layouts. Never draw replacement artwork here.
if (-not ('StardewItemExport' -as [type])) {
Add-Type -ReferencedAssemblies System.Drawing.Common,System.Drawing.Primitives,System.ComponentModel.Primitives,System.Private.Windows.Core -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;

public static class StardewItemExport
{
    static readonly string[] Hex = {
        "321E24", "4A2B2B", "643B35", "7F4C3B", "A56544", "C58450", "E6AD68",
        "FFF4D6", "F3E2B8", "DCC69B", "BEA57D", "96816A",
        "67472D", "925029", "B86B2F", "DE8D39", "F6B64E", "FFE080",
        "681F32", "982F3B", "BD3F3F", "E35445", "F48366",
        "293E2E", "3F5B36", "5A793E", "7F9A4D", "A9BD6B",
        "3B3C4F", "5C5D6D", "838493", "AEB2BF", "D3DADE", "F6F6E9",
        "2E4167", "435A97", "607BC1", "8CA9DF",
        "244E58", "347482", "5197A0", "85B9BB"
    };
    static readonly Color[] Palette = Array.ConvertAll(Hex, h => ColorTranslator.FromHtml("#" + h));

    static Color Match(Color c)
    {
        int best = 0;
        double score = double.MaxValue;
        for (int i = 0; i < Palette.Length; i++) {
            Color p = Palette[i];
            double dr = c.R-p.R, dg = c.G-p.G, db = c.B-p.B;
            double d = 0.30*dr*dr + 0.59*dg*dg + 0.11*db*db;
            if (d < score) { score = d; best = i; }
        }
        return Palette[best];
    }

    static Rectangle Bounds(Bitmap src, Rectangle cell)
    {
        int[] cols = new int[cell.Width], rows = new int[cell.Height];
        for (int y = 0; y < cell.Height; y++)
            for (int x = 0; x < cell.Width; x++)
                if (src.GetPixel(cell.X+x, cell.Y+y).A >= 192) { cols[x]++; rows[y]++; }
        // Ignore isolated export specks; keep narrow steam and handle shapes.
        int minX = cell.Width, minY = cell.Height, maxX = -1, maxY = -1;
        int minimum = Math.Max(2, Math.Min(cell.Width, cell.Height)/100);
        for (int x = 0; x < cols.Length; x++) if (cols[x] >= minimum) {
            minX = Math.Min(minX,x); maxX = Math.Max(maxX,x);
        }
        for (int y = 0; y < rows.Length; y++) if (rows[y] >= minimum) {
            minY = Math.Min(minY,y); maxY = Math.Max(maxY,y);
        }
        if (maxX < minX || maxY < minY) throw new Exception("Empty generated atlas cell.");
        return new Rectangle(cell.X+minX,cell.Y+minY,maxX-minX+1,maxY-minY+1);
    }

    static Bitmap Sprite(Bitmap src, Rectangle cell, int size)
    {
        Rectangle b = Bounds(src,cell);
        int limit = size == 16 ? 14 : 28;
        double scale = Math.Min((double)limit/b.Width,(double)limit/b.Height);
        int w = Math.Max(1,(int)Math.Round(b.Width*scale));
        int h = Math.Max(1,(int)Math.Round(b.Height*scale));
        int left = (size-w)/2, top = (size-h)/2;
        Bitmap dst = new Bitmap(size,size,PixelFormat.Format32bppArgb);
        for (int y = 0; y < h; y++) for (int x = 0; x < w; x++) {
            int sx = b.X + Math.Min(b.Width-1,(int)((x+0.5)*b.Width/w));
            int sy = b.Y + Math.Min(b.Height-1,(int)((y+0.5)*b.Height/h));
            Color c = src.GetPixel(sx,sy);
            if (c.A >= 128) dst.SetPixel(left+x,top+y,Match(c));
        }
        return dst;
    }

    public static void Export(string source, string target, int cols, int rows, int size)
    {
        using (Bitmap src = new Bitmap(source))
        using (Bitmap dst = new Bitmap(cols*rows*size,size,PixelFormat.Format32bppArgb)) {
            for (int i = 0; i < cols*rows; i++) {
                int col = i%cols, row = i/cols;
                int x0 = col*src.Width/cols, y0 = row*src.Height/rows;
                int x1 = (col+1)*src.Width/cols, y1 = (row+1)*src.Height/rows;
                using (Bitmap icon = Sprite(src,new Rectangle(x0,y0,x1-x0,y1-y0),size))
                    for (int y = 0; y < size; y++) for (int x = 0; x < size; x++)
                        dst.SetPixel(i*size+x,y,icon.GetPixel(x,y));
            }
            dst.Save(target,ImageFormat.Png);
        }
    }

    static void Blit(Bitmap dest, Bitmap src, Rectangle crop, int dx, int dy, int zoom)
    {
        for (int y = 0; y < crop.Height; y++) for (int x = 0; x < crop.Width; x++) {
            Color c = src.GetPixel(crop.X+x,crop.Y+y);
            if (c.A < 128) continue;
            for (int zy = 0; zy < zoom; zy++) for (int zx = 0; zx < zoom; zx++)
                dest.SetPixel(dx+x*zoom+zx,dy+y*zoom+zy,c);
        }
    }

    public static void Preview(string artDir)
    {
        using (Bitmap preview = new Bitmap(1152,448,PixelFormat.Format32bppArgb))
        using (Graphics g = Graphics.FromImage(preview))
        using (Font title = new Font("Segoe UI",13,FontStyle.Bold))
        using (Font label = new Font("Segoe UI",10))
        using (Brush ink = new SolidBrush(ColorTranslator.FromHtml("#F3E2B8")))
        using (Brush dim = new SolidBrush(ColorTranslator.FromHtml("#BEA57D"))) {
            g.Clear(ColorTranslator.FromHtml("#24222C"));
            g.DrawString("STARDEW VALLEY  /  HARVEY OVERHAUL",title,ink,20,12);
            g.DrawString("ДО  /  16 x 16",label,dim,20,57);
            g.DrawString("ПОСЛЕ  /  16 x 16",label,ink,20,160);
            string[] names = {"Бинт","Антисептик","Обезбол.","Травяной чай","Аптечка","Мазь","Фонарь","Сумка Харви","Бульон"};
            using (Bitmap before = new Bitmap(Path.Combine(artDir,"originals","medicalItems.png")))
            using (Bitmap after = new Bitmap(Path.Combine(artDir,"exports","medicalItems.png"))) {
                for (int i = 0; i < 9; i++) {
                    int dx = 20+i*124;
                    Blit(preview,before,new Rectangle(i*16,0,16,16),dx,72,5);
                    Blit(preview,after,new Rectangle(i*16,0,16,16),dx,188,5);
                    g.DrawString(names[i],label,dim,dx,274);
                }
            }
            g.DrawString("ПРЕДМЕТЫ АРЕНДА  /  16 x 16",label,ink,20,307);
            using (Bitmap arend = new Bitmap(Path.Combine(artDir,"exports","arendItems.png"))) {
                string[] arendNames = {"Шкатулка","Чай №7","Чашка Элин"};
                for (int i = 0; i < 3; i++) {
                    Blit(preview,arend,new Rectangle(i*16,0,16,16),20+i*124,337,5);
                    g.DrawString(arendNames[i],label,dim,20+i*124,420);
                }
            }
            g.DrawString("СПРАВОЧНИКИ  /  32 x 32",label,ink,510,307);
            using (Bitmap injury = new Bitmap(Path.Combine(artDir,"exports","injury-book.png")))
            using (Bitmap stress = new Bitmap(Path.Combine(artDir,"exports","stress-handbook.png"))) {
                Blit(preview,injury,new Rectangle(0,0,32,32),510,337,3);
                Blit(preview,stress,new Rectangle(0,0,32,32),650,337,3);
            }
            preview.Save(Path.Combine(artDir,"preview.png"),ImageFormat.Png);
        }
    }
}
'@
}

$artDir = $PSScriptRoot
$generatedDir = Join-Path $artDir 'generated'
$exportDir = Join-Path $artDir 'exports'
[StardewItemExport]::Export((Join-Path $generatedDir 'medical-grid.png'), (Join-Path $exportDir 'medicalItems.png'), 3, 3, 16)
[StardewItemExport]::Export((Join-Path $generatedDir 'arend-row.png'), (Join-Path $exportDir 'arendItems.png'), 3, 1, 16)
[StardewItemExport]::Export((Join-Path $generatedDir 'injury-book.png'), (Join-Path $exportDir 'injury-book.png'), 1, 1, 32)
[StardewItemExport]::Export((Join-Path $generatedDir 'stress-handbook.png'), (Join-Path $exportDir 'stress-handbook.png'), 1, 1, 32)
[StardewItemExport]::Preview($artDir)

if ($Install) {
    $cpRoot = Split-Path (Split-Path $artDir -Parent) -Parent
    $workspace = Split-Path $cpRoot -Parent
    Copy-Item -LiteralPath (Join-Path $exportDir 'medicalItems.png') -Destination (Join-Path $cpRoot 'assets\Items\medicalItems.png')
    Copy-Item -LiteralPath (Join-Path $exportDir 'arendItems.png') -Destination (Join-Path $cpRoot 'assets\Items\arendItems.png')
    Copy-Item -LiteralPath (Join-Path $exportDir 'injury-book.png') -Destination (Join-Path $workspace 'HarveyOverhaulInjury\assets\sprites\book.png')
    Copy-Item -LiteralPath (Join-Path $exportDir 'stress-handbook.png') -Destination (Join-Path $workspace 'HarveyStressMeter\assets\sprites\handbook.png')
    Copy-Item -LiteralPath (Join-Path $exportDir 'stress-handbook.png') -Destination (Join-Path $workspace 'HarveyStressMeter\assets\sprites\ui.png')
}
