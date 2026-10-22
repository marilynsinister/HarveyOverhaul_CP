param([switch]$Install)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

# Mechanical sprite export. All artwork comes from the saved image_gen results.
if (-not ('HarveyBuffSpriteExport' -as [type])) {
Add-Type -ReferencedAssemblies System.Drawing.Common,System.Drawing.Primitives,System.ComponentModel.Primitives,System.Private.Windows.Core,System.Collections -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Text;

public static class HarveyBuffSpriteExport
{
    static readonly string[] Hex = {
        "321E24", "4A2B2B", "643B35", "7F4C3B", "A56544", "C58450", "E6AD68",
        "FFF4D6", "F3E2B8", "DCC69B", "BEA57D", "96816A",
        "67472D", "925029", "B86B2F", "DE8D39", "F6B64E", "FFE080",
        "681F32", "982F3B", "BD3F3F", "E35445", "F48366", "F6A697", "D77D82",
        "293E2E", "3F5B36", "5A793E", "7F9A4D", "A9BD6B", "CAE09B",
        "3B3C4F", "5C5D6D", "838493", "AEB2BF", "D3DADE", "F6F6E9",
        "2E4167", "435A97", "607BC1", "8CA9DF", "BBDCF1",
        "244E58", "347482", "5197A0", "85B9BB", "B9E4D4",
        "2C254B", "453258", "654878", "876399", "AE89BC", "D5B6DB",
        "202436", "35435A", "547593", "7BA5BB", "BAD8DF"
    };
    static readonly Color[] Palette = Array.ConvertAll(Hex, h => ColorTranslator.FromHtml("#"+h));

    static Color Quantize(Color c)
    {
        int best=0; double distance=double.MaxValue;
        for(int i=0;i<Palette.Length;i++) {
            Color p=Palette[i]; double r=c.R-p.R,g=c.G-p.G,b=c.B-p.B;
            double d=0.3*r*r+0.59*g*g+0.11*b*b;
            if(d<distance){distance=d;best=i;}
        }
        return Palette[best];
    }

    static Bitmap Cell(Bitmap src,int columns,int rows,int index)
    {
        int col=index%columns,row=index/columns;
        int x0=col*src.Width/columns,y0=row*src.Height/rows;
        int x1=(col+1)*src.Width/columns,y1=(row+1)*src.Height/rows;
        int[] xs=new int[x1-x0],ys=new int[y1-y0];
        for(int y=y0;y<y1;y++)for(int x=x0;x<x1;x++)
            if(src.GetPixel(x,y).A>=192){xs[x-x0]++;ys[y-y0]++;}
        int minX=x1,minY=y1,maxX=-1,maxY=-1;
        int threshold=Math.Max(2,Math.Min(x1-x0,y1-y0)/100);
        for(int x=0;x<xs.Length;x++)if(xs[x]>=threshold){minX=Math.Min(minX,x+x0);maxX=Math.Max(maxX,x+x0);}
        for(int y=0;y<ys.Length;y++)if(ys[y]>=threshold){minY=Math.Min(minY,y+y0);maxY=Math.Max(maxY,y+y0);}
        if(maxX<minX || maxY<minY)throw new Exception("Empty generated cell "+index);
        int width=maxX-minX+1,height=maxY-minY+1;
        double scale=Math.Min(14.0/width,14.0/height);
        int w=Math.Max(1,(int)Math.Round(width*scale)),h=Math.Max(1,(int)Math.Round(height*scale));
        int left=(16-w)/2,top=(16-h)/2;
        Bitmap icon=new Bitmap(16,16,PixelFormat.Format32bppArgb);
        for(int y=0;y<h;y++)for(int x=0;x<w;x++) {
            Color c=src.GetPixel(minX+Math.Min(width-1,(int)((x+0.5)*width/w)),minY+Math.Min(height-1,(int)((y+0.5)*height/h)));
            if(c.A>=128)icon.SetPixel(left+x,top+y,Quantize(c));
        }
        return icon;
    }

    static void Paste(Bitmap dst,Bitmap icon,int index,int columns)
    {
        for(int y=0;y<16;y++)for(int x=0;x<16;x++)
            dst.SetPixel((index%columns)*16+x,(index/columns)*16+y,icon.GetPixel(x,y));
    }
    static Bitmap Tile(Bitmap atlas,int index,int columns)
    {
        return atlas.Clone(new Rectangle((index%columns)*16,(index/columns)*16,16,16),PixelFormat.Format32bppArgb);
    }

    public static void Build(string root)
    {
        string generated=Path.Combine(root,"generated"),exports=Path.Combine(root,"exports");
        using(Bitmap main=new Bitmap(256,176,PixelFormat.Format32bppArgb)) {
            for(int group=0;group<11;group++)using(Bitmap src=new Bitmap(Path.Combine(generated,"group-"+group.ToString("00")+".png"))) {
                int columns=group==10?3:4,rows=group==10?2:4,count=group==10?4:16;
                for(int i=0;i<count;i++)using(Bitmap icon=Cell(src,columns,rows,i))Paste(main,icon,group*16+i,16);
            }
            using(Bitmap extra=new Bitmap(Path.Combine(generated,"extra-effects.png")))
                for(int i=0;i<2;i++)using(Bitmap icon=Cell(extra,2,1,i))Paste(main,icon,164+i,16);
            main.Save(Path.Combine(exports,"harveyBuffIcons.png"),ImageFormat.Png);
            using(Bitmap mishap=new Bitmap(96,16,PixelFormat.Format32bppArgb)) {
                for(int i=0;i<5;i++)using(Bitmap icon=Tile(main,159+i,16))Paste(mishap,icon,i,6);
                using(Bitmap last=new Bitmap(Path.Combine(generated,"group-10.png")))
                using(Bitmap scar=Cell(last,3,2,4))Paste(mishap,scar,5,6);
                mishap.Save(Path.Combine(exports,"mishapBuffIcons.png"),ImageFormat.Png);
            }
        }
        Repack(Path.Combine(generated,"stress-handbook.png"),Path.Combine(exports,"stressIcons.png"),7,3);
        Repack(Path.Combine(generated,"legacy-injuries.png"),Path.Combine(exports,"injuryIcon.png"),4,3);
    }

    static void Repack(string source,string target,int columns,int rows)
    {
        using(Bitmap src=new Bitmap(source))using(Bitmap dst=new Bitmap(columns*16,rows*16,PixelFormat.Format32bppArgb)) {
            for(int i=0;i<columns*rows;i++)using(Bitmap icon=Cell(src,columns,rows,i))Paste(dst,icon,i,columns);
            dst.Save(target,ImageFormat.Png);
        }
    }

    public static string Validate(string file,int width,int height,int count,bool distinct)
    {
        using(Bitmap atlas=new Bitmap(file)) {
            if(atlas.Width!=width || atlas.Height!=height)throw new Exception("Wrong dimensions: "+file);
            int columns=width/16;var seen=new Dictionary<string,int>();var duplicates=new List<string>();
            for(int i=0;i<(width/16)*(height/16);i++) {
                int opaque=0;var signature=new StringBuilder();
                for(int y=0;y<16;y++)for(int x=0;x<16;x++) {
                    Color c=atlas.GetPixel((i%columns)*16+x,(i/columns)*16+y);
                    if(c.A!=0 && c.A!=255)throw new Exception("Partial alpha in "+file);
                    if(c.A>0){opaque++;if(x==0||y==0||x==15||y==15)throw new Exception("Cell edge touched: "+file+" #"+i);}
                    signature.Append(c.A==0?"00000000":c.ToArgb().ToString("X8"));
                }
                if(i>=count){if(opaque>0)throw new Exception("Reserved atlas cell is not empty: "+i);continue;}
                if(opaque<12)throw new Exception("Missing/too small icon: "+file+" #"+i);
                if(distinct){string key=signature.ToString();if(seen.ContainsKey(key))duplicates.Add(seen[key]+"="+i);else seen[key]=i;}
            }
            return duplicates.Count>0?"DUPLICATES "+string.Join(", ",duplicates):"OK";
        }
    }

    static void DrawIcon(Bitmap dst,Bitmap src,int index,int columns,int dx,int dy,int zoom)
    {
        for(int y=0;y<16;y++)for(int x=0;x<16;x++) {
            Color c=src.GetPixel((index%columns)*16+x,(index/columns)*16+y);
            if(c.A==0)continue;
            for(int yy=0;yy<zoom;yy++)for(int xx=0;xx<zoom;xx++)dst.SetPixel(dx+x*zoom+xx,dy+y*zoom+yy,c);
        }
    }

    public static void Gallery(string root,string[] labels,int start,int count,string filename,string title)
    {
        int cols=7,cellWidth=164,cellHeight=140,rows=(count+cols-1)/cols;
        using(Bitmap atlas=new Bitmap(Path.Combine(root,"exports","harveyBuffIcons.png")))
        using(Bitmap image=new Bitmap(cols*cellWidth,58+rows*cellHeight,PixelFormat.Format32bppArgb))
        using(Graphics g=Graphics.FromImage(image))
        using(Font heading=new Font("Segoe UI",15,FontStyle.Bold))
        using(Font font=new Font("Segoe UI",9))
        using(Brush ink=new SolidBrush(ColorTranslator.FromHtml("#F3E2B8")))
        using(Brush dim=new SolidBrush(ColorTranslator.FromHtml("#BEA57D"))) {
            g.Clear(ColorTranslator.FromHtml("#24222C"));g.DrawString(title,heading,ink,20,14);
            for(int i=0;i<count;i++) {
                int x=(i%cols)*cellWidth,y=58+(i/cols)*cellHeight,index=start+i;
                DrawIcon(image,atlas,index,16,x+42,y,5);
                using(StringFormat format=new StringFormat { Trimming=StringTrimming.EllipsisWord, FormatFlags=StringFormatFlags.LineLimit })
                    g.DrawString(index.ToString("000")+"  "+labels[index],font,dim,new RectangleF(x+6,y+82,cellWidth-10,54),format);
            }
            image.Save(Path.Combine(root,filename),ImageFormat.Png);
        }
    }

    public static void Overview(string root)
    {
        using(Bitmap image=new Bitmap(1152,1040,PixelFormat.Format32bppArgb))
        using(Graphics g=Graphics.FromImage(image))
        using(Font heading=new Font("Segoe UI",16,FontStyle.Bold))
        using(Font small=new Font("Segoe UI",11))
        using(Brush ink=new SolidBrush(ColorTranslator.FromHtml("#F3E2B8"))) {
            g.Clear(ColorTranslator.FromHtml("#24222C"));
            g.DrawString("БАФФЫ И ДЕБАФФЫ ХАРВИ  /  166 ИКОНОК",heading,ink,20,14);
            using(Bitmap atlas=new Bitmap(Path.Combine(root,"exports","harveyBuffIcons.png")))
                for(int i=0;i<166;i++)DrawIcon(image,atlas,i,16,20+(i%16)*68,58+(i/16)*68,4);
            g.DrawString("СПРАВОЧНИК  /  21 ИКОНКА",small,ink,20,820);
            using(Bitmap ui=new Bitmap(Path.Combine(root,"exports","stressIcons.png")))
                for(int i=0;i<21;i++)DrawIcon(image,ui,i,7,20+(i%7)*64,850+(i/7)*56,3);
            g.DrawString("ДОПОЛНИТЕЛЬНЫЕ ТРАВМЫ",small,ink,530,820);
            using(Bitmap injury=new Bitmap(Path.Combine(root,"exports","injuryIcon.png")))
                for(int i=0;i<12;i++)DrawIcon(image,injury,i,4,530+(i%4)*64,850+(i/4)*56,3);
            g.DrawString("МЕЛКИЕ НЕПРИЯТНОСТИ",small,ink,820,820);
            using(Bitmap mishap=new Bitmap(Path.Combine(root,"exports","mishapBuffIcons.png")))
                for(int i=0;i<6;i++)DrawIcon(image,mishap,i,6,820+(i%3)*64,850+(i/3)*56,3);
            image.Save(Path.Combine(root,"preview.png"),ImageFormat.Png);
        }
    }
}
'@
}

$artRoot=$PSScriptRoot
[HarveyBuffSpriteExport]::Build($artRoot)
$exports=Join-Path $artRoot 'exports'
foreach($check in @(@('harveyBuffIcons.png',256,176,166),@('mishapBuffIcons.png',96,16,6),@('stressIcons.png',112,48,21),@('injuryIcon.png',64,48,12))) {
    $status=[HarveyBuffSpriteExport]::Validate((Join-Path $exports $check[0]),$check[1],$check[2],$check[3],$true)
    Write-Output ($check[0]+': '+$status)
    if($status -ne 'OK'){throw $status}
}
$cpRoot=Split-Path (Split-Path $artRoot -Parent) -Parent
$workspace=Split-Path $cpRoot -Parent
$map=Get-Content -LiteralPath (Join-Path $cpRoot 'assets\Tilesheets\harveyBuffIcons.json') -Raw | ConvertFrom-Json
$originalMap=Get-Content -LiteralPath (Join-Path $artRoot 'originals\harveyBuffIcons.json') -Raw | ConvertFrom-Json
foreach($originalProperty in $originalMap.PSObject.Properties){if($map.($originalProperty.Name) -ne $originalProperty.Value){throw ('Original sprite index changed: '+$originalProperty.Name)}}
Copy-Item -LiteralPath (Join-Path $cpRoot 'assets\Tilesheets\harveyBuffIcons.json') -Destination (Join-Path $exports 'harveyBuffIcons.json')
$labels=New-Object string[] 166
foreach($property in $map.PSObject.Properties){$labels[[int]$property.Value]=$property.Name}
foreach($source in Get-ChildItem -LiteralPath (Join-Path $cpRoot 'assets\Code') -Filter *.json){
    $raw=[IO.File]::ReadAllText($source.FullName)
    if(-not $raw.Contains('"Data/Buffs"')){continue}
    $data=$raw | ConvertFrom-Json
    foreach($change in $data.Changes){if($change.Target -ne 'Data/Buffs'){continue};foreach($entry in $change.Entries.PSObject.Properties){if($map.PSObject.Properties.Name -contains $entry.Name -and $entry.Value.DisplayName){$labels[[int]$map.($entry.Name)]=$entry.Value.DisplayName}}}
}
[HarveyBuffSpriteExport]::Gallery($artRoot,$labels,0,75,'preview-treatment.png','ЛЕЧЕНИЕ И ФАЗЫ ТРАВМ  /  16 x 16')
[HarveyBuffSpriteExport]::Gallery($artRoot,$labels,75,91,'preview-debuffs.png','ТРАВМЫ, СТРЕСС И ОСЛОЖНЕНИЯ  /  16 x 16')
[HarveyBuffSpriteExport]::Overview($artRoot)
if($Install){
    Copy-Item -LiteralPath (Join-Path $exports 'harveyBuffIcons.png') -Destination (Join-Path $cpRoot 'assets\Tilesheets\harveyBuffIcons.png')
    Copy-Item -LiteralPath (Join-Path $exports 'mishapBuffIcons.png') -Destination (Join-Path $cpRoot 'assets\Items\mishapBuffIcons.png')
    Copy-Item -LiteralPath (Join-Path $exports 'stressIcons.png') -Destination (Join-Path $cpRoot 'assets\Tilesheets\stressIcon.png')
    Copy-Item -LiteralPath (Join-Path $exports 'stressIcons.png') -Destination (Join-Path $workspace 'HarveyStressMeter\assets\sprites\stressIcons.png')
    Copy-Item -LiteralPath (Join-Path $exports 'injuryIcon.png') -Destination (Join-Path $cpRoot 'assets\Tilesheets\injuryIcon.png')
}
