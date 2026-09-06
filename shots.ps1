# Juri icin tutarli ekran goruntusu seti uretir.
$root = 'C:\Users\Serdar\Desktop\Ressam-Portfolyo'
$site = "$root\site"
$out  = "$root\shots"
$tmp  = 'C:\Users\Serdar\AppData\Local\Temp\claude\C--Users-Serdar\a88640d8-b5d5-4395-8a71-2e0da20f0ecf\scratchpad'
$edge = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
New-Item -ItemType Directory -Force -Path $out | Out-Null

function Render($file, $hash, $scroll, $w, $h, $name) {
  $src = [IO.File]::ReadAllText((Join-Path $site $file))
  $inj = "<script>[300,900,1800,2800,3800].forEach(function(t){setTimeout(function(){" +
         "document.querySelectorAll('[data-reveal]').forEach(function(e){e.classList.add('is-in')});" +
         "window.scrollTo(0,$scroll);dispatchEvent(new Event('scroll'));},t)});</script>"
  $tf = Join-Path $site ("_s_" + $name + ".html")
  [IO.File]::WriteAllText($tf, ($src -replace '</body>', ($inj + '</body>')), [Text.UTF8Encoding]::new($false))
  $png = Join-Path $out ($name + '.png')
  $size = "--window-size=$w,$h"
  & $edge --headless=new --disable-gpu --hide-scrollbars $size --force-device-scale-factor=1 `
          --virtual-time-budget=26000 --screenshot="$png" --user-data-dir="$tmp\epshots" `
          (([uri]$tf).AbsoluteUri + $hash) 2>$null | Out-Null
  "  $name.png"
}

function RenderMobile($file, $hash, $scroll, $name) {
  $src = [IO.File]::ReadAllText((Join-Path $site $file))
  $inj = "<script>[300,900,1800,2800].forEach(function(t){setTimeout(function(){" +
         "document.querySelectorAll('[data-reveal]').forEach(function(e){e.classList.add('is-in')});" +
         "window.scrollTo(0,$scroll);dispatchEvent(new Event('scroll'));},t)});</script>"
  $tf = Join-Path $site ("_s_" + $name + ".html")
  [IO.File]::WriteAllText($tf, ($src -replace '</body>', ($inj + '</body>')), [Text.UTF8Encoding]::new($false))
  $wrap = '<!doctype html><html><head><meta charset=utf-8><style>html,body{margin:0}iframe{width:390px;height:844px;border:0;display:block}</style></head><body><iframe src="_s_' + $name + '.html' + $hash + '"></iframe></body></html>'
  $wf = Join-Path $site ("_sw_" + $name + ".html")
  [IO.File]::WriteAllText($wf, $wrap, [Text.UTF8Encoding]::new($false))
  $png = Join-Path $out ($name + '.png')
  & $edge --headless=new --disable-gpu --hide-scrollbars --allow-file-access-from-files `
          --window-size=390,844 --force-device-scale-factor=1 `
          --virtual-time-budget=24000 --screenshot="$png" --user-data-dir="$tmp\epshots" `
          ([uri]$wf).AbsoluteUri 2>$null | Out-Null
  "  $name.png"
}

'ASKI';    Render 'aski.html'    ''      0    1440 900  'aski-1-acilis'
           Render 'aski.html'    ''      1900 1440 1100 'aski-2-eser'
           Render 'aski.html'    '#envanter' 12000 1440 1100 'aski-3-envanter'
           RenderMobile 'aski.html' ''   1500 'aski-4-mobil'
'FASIKUL'; Render 'fasikul.html' ''      0    1440 900  'fasikul-1-acilis'
           Render 'fasikul.html' ''      1500 1440 1100 'fasikul-2-forma'
           Render 'fasikul.html' '#katalog' 0 1440 1100 'fasikul-3-katalog'
           RenderMobile 'fasikul.html' '' 1400 'fasikul-4-mobil'
'KUTUK';   Render 'kunye.html'   ''      0    1440 900  'kutuk-1-acilis'
           Render 'kunye.html'   ''      1000 1440 1100 'kutuk-2-kutuk'
           Render 'kunye.html'   '#/kayit/dag-sirti' 0 1440 1100 'kutuk-3-kayit'
           RenderMobile 'kunye.html' ''  900  'kutuk-4-mobil'
'DUZ';     Render 'duz.html'     ''      0    1440 900  'duz-1-acilis'
           Render 'duz.html'     '#/son' 0    1440 1100 'duz-2-eserler'
           Render 'duz.html'     '#/sergiler' 0 1440 900 'duz-3-metin'
           RenderMobile 'duz.html' '#/son' 0  'duz-4-mobil'
"`nbitti: $out"
