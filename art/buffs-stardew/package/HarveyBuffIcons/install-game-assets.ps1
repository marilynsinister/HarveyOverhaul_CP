param([string]$GameModsRoot='D:\Games\Steam\steamapps\common\Stardew Valley\Mods\HarveyOverhaul')
$ErrorActionPreference='Stop'
$exports=Join-Path $PSScriptRoot 'exports'
$gameRoot=[IO.Path]::GetFullPath($GameModsRoot)
function Find-ModRoot([string]$uniqueId){
    $matches=@(foreach($directory in Get-ChildItem -LiteralPath $gameRoot -Directory){
        $manifestPath=Join-Path $directory.FullName 'manifest.json'
        if(-not(Test-Path -LiteralPath $manifestPath)){continue}
        $manifest=Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
        if($manifest.UniqueID -eq $uniqueId){$directory.FullName}
    })
    if($matches.Count -ne 1){throw ('Expected exactly one installed mod: '+$uniqueId)}
    return $matches[0]
}
$cpRoot=Find-ModRoot 'marilynsinister.HarveyOverhaul'
$stressRoot=Find-ModRoot 'marilynsinister.HarveyStressMeter'

function Find-Buff($document,[string]$id){
    $entries=@(foreach($change in $document.Changes){
        if($change.Target -ne 'Data/Buffs' -or $null -eq $change.Entries){continue}
        $property=$change.Entries.PSObject.Properties[$id]
        if($null -ne $property){$property.Value}
    })
    if($entries.Count -ne 1){throw ('Expected exactly one buff entry: '+$id)}
    return $entries[0]
}

function Prepare-IconUpdate([string]$path,[string]$id,[int]$index){
    $text=[IO.File]::ReadAllText($path)
    $before=$text | ConvertFrom-Json
    $entry=Find-Buff $before $id
    $entry.IconSpriteIndex=$index
    $pattern='("'+[regex]::Escape($id)+'"\s*:\s*\{[\s\S]*?"IconSpriteIndex"\s*:\s*)\d+'
    $regex=[regex]::new($pattern)
    if($regex.Matches($text).Count -ne 1){throw ('Ambiguous icon index: '+$id)}
    $changed=$regex.Replace($text,[System.Text.RegularExpressions.MatchEvaluator]{param($match) $match.Groups[1].Value+[string]$index})
    $after=$changed | ConvertFrom-Json
    if(($before | ConvertTo-Json -Depth 100 -Compress) -cne ($after | ConvertTo-Json -Depth 100 -Compress)){
        throw ('Unexpected data change while updating '+$id)
    }
    return [PSCustomObject]@{Path=$path;Text=$changed;Id=$id;Index=$index}
}

# Prepare and validate both edits before writing to the game directory.
$updates=@(
    (Prepare-IconUpdate (Join-Path $cpRoot 'assets\Code\buffsStress.json') 'buffStressClearMind' 164),
    (Prepare-IconUpdate (Join-Path $cpRoot 'assets\Code\eventsScars.json') 'buffStressFireMemory' 165)
)
$files=@(
    @{Source='harveyBuffIcons.png';Target=(Join-Path $cpRoot 'assets\Tilesheets\harveyBuffIcons.png')},
    @{Source='harveyBuffIcons.json';Target=(Join-Path $cpRoot 'assets\Tilesheets\harveyBuffIcons.json')},
    @{Source='mishapBuffIcons.png';Target=(Join-Path $cpRoot 'assets\Items\mishapBuffIcons.png')},
    @{Source='injuryIcon.png';Target=(Join-Path $cpRoot 'assets\Tilesheets\injuryIcon.png')},
    @{Source='stressIcons.png';Target=(Join-Path $cpRoot 'assets\Tilesheets\stressIcon.png')},
    @{Source='stressIcons.png';Target=(Join-Path $stressRoot 'assets\sprites\stressIcons.png')}
)
foreach($file in $files){if(-not(Test-Path -LiteralPath (Join-Path $exports $file.Source))){throw ('Missing export: '+$file.Source)}}
$backupRoot=Join-Path $PSScriptRoot 'game-before'
foreach($target in @($files | ForEach-Object {$_.Target})+@($updates | ForEach-Object {$_.Path})){
    if(-not $target.StartsWith($gameRoot.TrimEnd('\')+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Target outside selected game mod directory'}
    $relative=$target.Substring($gameRoot.TrimEnd('\').Length+1)
    $backup=Join-Path $backupRoot $relative
    if((Test-Path -LiteralPath $target) -and -not(Test-Path -LiteralPath $backup)){
        New-Item -ItemType Directory -Force -Path (Split-Path $backup -Parent) | Out-Null
        Copy-Item -LiteralPath $target -Destination $backup
    }
}
foreach($file in $files){Copy-Item -LiteralPath (Join-Path $exports $file.Source) -Destination $file.Target -Force}
foreach($update in $updates){[IO.File]::WriteAllText($update.Path,$update.Text,[System.Text.UTF8Encoding]::new($false))}
foreach($file in $files){
    if((Get-FileHash -LiteralPath (Join-Path $exports $file.Source)).Hash -ne (Get-FileHash -LiteralPath $file.Target).Hash){throw ('Installed file mismatch: '+$file.Target)}
}
foreach($update in $updates){
    $installed=Get-Content -LiteralPath $update.Path -Raw | ConvertFrom-Json
    if((Find-Buff $installed $update.Id).IconSpriteIndex -ne $update.Index){throw ('Installed buff index mismatch: '+$update.Id)}
}
Write-Output 'Installed and verified: 5 PNG files, the atlas map, and 2 icon-index updates.'
Write-Output ('Previous game files: '+$backupRoot)
