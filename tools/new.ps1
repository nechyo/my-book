<#
.SYNOPSIS
  새 글을 초안으로 만든다. 앞머리와 절 뼈대까지 채운다.

.DESCRIPTION
  -Type 으로 글 종류를 고르면 그 종류에 맞는 앞머리 항목, 절 뼈대, 부품 틀이 들어간다.
  종류는 한글과 영문 어느 쪽으로 적어도 된다.

    리버싱   re      바이너리 심층분석 (기본값)
    관찰     obs     도구 없이 공개 정보로 짚는 글
    위협     ti      위협 행위자·캠페인 보고서 (라자루스 등). 소식 묶음 틀이 같이 들어간다
    침해대응 ir      침해사고 대응 보고서
    기술보안 ts      취약점·기술 보안 보고서
    동향     digest  여러 소식을 묶은 보고서

  어느 종류든 앞머리 items: 에 소식을 나열하면 소식 묶음이 된다.
  -Series 를 주면 같은 시리즈끼리 묶여 '제N호'가 자동으로 붙는다.
  -Tlp 가 CLEAR 가 아니면 published: false 까지 넣어 공개 사이트에는 절대 올라가지 않게 한다.

  새 글은 _reports/_drafts/ 에 초안으로 생긴다. 이 폴더는 git 에 올라가지 않고 Jekyll 도
  읽지 않는다. 로컬 미리보기에서는 「초안」 표시를 달고 보인다. 다 쓰면
  python tools/publish.py _reports/_drafts/<파일>.md 로 점검하고 발행한다.
  VS Code 터미널에서 실행하면 만든 파일을 바로 편집기에 연다.

.EXAMPLE
  .\tools\new.ps1 "문자열 난독화 추적" -Labels Windows,난독화
  .\tools\new.ps1 "9월 라자루스 동향" -Type ti -Series "라자루스 추적" -Actor "Lazarus Group"
  .\tools\new.ps1 "개발망 침해 대응" -Type ir -Severity 높음 -Tlp AMBER
  .\tools\new.ps1 "OO 제품 인증 우회" -Type ts
  .\tools\new.ps1 "주간 위협 동향" -Type digest -Series "주간 동향"
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true, Position = 0)]
  [string] $Title,

  [ValidateSet("리버싱", "관찰", "위협", "침해대응", "기술보안", "동향",
               "re", "obs", "ti", "ir", "ts", "digest")]
  [string]   $Type = "re",

  [string]   $Slug,
  [string[]] $Labels = @(),
  [string]   $Kind,
  [string]   $Series,
  [string]   $Actor,

  [ValidateSet("CLEAR", "GREEN", "AMBER", "AMBER+STRICT", "RED")]
  [string]   $Tlp = "CLEAR",

  [ValidateSet("긴급", "높음", "중간", "낮음", "critical", "high", "medium", "low")]
  [string]   $Severity,

  [string]   $Subtitle,
  [string]   $Target,
  [string]   $Tools
)

$ErrorActionPreference = "Stop"

$typeMap = @{ "리버싱" = "re"; "관찰" = "obs"; "위협" = "ti"; "침해대응" = "ir"; "기술보안" = "ts"; "동향" = "digest" }
$t = if ($typeMap.ContainsKey($Type)) { $typeMap[$Type] } else { $Type.ToLower() }

$kindMap = @{ "re" = "심층분석"; "obs" = "관찰"; "ti" = "위협 인텔리전스"; "ir" = "침해대응"; "ts" = "기술보안"; "digest" = "동향" }
if (-not $Kind) { $Kind = $kindMap[$t] }

$sevMap = @{ "critical" = "긴급"; "high" = "높음"; "medium" = "중간"; "low" = "낮음" }
if ($Severity -and $sevMap.ContainsKey($Severity)) { $Severity = $sevMap[$Severity] }
$Tlp = $Tlp.ToUpper()

$root  = Split-Path -Parent $PSScriptRoot
$dir   = Join-Path $root "_reports\_drafts"
$today = Get-Date -Format "yyyy-MM-dd"
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }

if (-not $Slug) {
  $ascii = ($Title -replace '[^\p{IsBasicLatin}]', ' ').ToLower()
  $ascii = ($ascii -replace '[^a-z0-9]+', '-').Trim('-')
  if ($ascii.Length -ge 3) { $Slug = $ascii } else { $Slug = "$t-" + (Get-Date -Format "yyyyMMdd-HHmm") }
}
$path = Join-Path $dir "$Slug.md"
$live = Join-Path (Join-Path $root "_reports") "$Slug.md"
if (Test-Path $live) { throw "같은 이름으로 발행한 글이 있습니다: $live  ( -Slug 로 다른 이름을 주세요 )" }
if (Test-Path $path) { throw "이미 있는 파일입니다: $path  ( -Slug 로 다른 이름을 주세요 )" }

function Q([string] $s) { '"' + (($s -replace '\\', '\\') -replace '"', '\"') + '"' }

$fm = New-Object System.Collections.Generic.List[string]
$fm.Add('---')
$fm.Add('title: ' + (Q $Title))
if ($Subtitle) { $fm.Add('subtitle: ' + (Q $Subtitle)) } else { $fm.Add('# subtitle: "부제"') }
$fm.Add('date: __DATE__')
$fm.Add('kind: ' + $Kind)

if ($Series) { $fm.Add('series: ' + (Q $Series)) }
elseif ($t -eq 'ti' -or $t -eq 'digest') { $fm.Add('# series: "라자루스 추적"          # 같은 이름끼리 묶여 제N호가 붙는다') }

if ($t -eq 'ir') { $fm.Add('status: 대응 중') }

$private = $Tlp -ne 'CLEAR'
if ($private) { $fm.Add('published: false                     # TLP:' + $Tlp + ' 이라 공개 사이트에 올리지 않는다. 로컬 미리보기·PDF 전용') }
if ($private -or $t -in @('ti', 'ir', 'ts', 'digest')) { $fm.Add('tlp: ' + $Tlp) }

if ($Severity) { $fm.Add('severity: ' + $Severity) }
elseif ($t -eq 'ir') { $fm.Add('severity: 중간                        # 긴급 / 높음 / 중간 / 낮음') }
elseif ($t -eq 'ts') { $fm.Add('# severity: 중간') }

if ($t -eq 'ti') {
  if ($Actor) { $fm.Add('actor: ' + (Q $Actor)) }
  else { $fm.Add('actor: "행위자 이름"                 # 그룹 번호(라자루스는 G0032)를 쓰면 이름·별칭·MITRE 출처가 자동으로 붙는다') }
  $fm.Add('# aliases: [APT38, "Hidden Cobra"]    # 그룹 번호를 쓰면 비워 둬도 ATT&CK 별칭이 들어간다')
} elseif ($Actor) {
  $fm.Add('actor: ' + (Q $Actor))
}

if ($t -in @('ti', 'ir', 'digest')) { $fm.Add('period: "__DATE__ ~ __DATE__"') }

if ($Target) { $fm.Add('target: ' + (Q $Target)) }
elseif ($t -eq 're') { $fm.Add('# target: "sample.exe · SHA-256 ..."') }
if ($Tools) { $fm.Add('tools: ' + (Q $Tools)) }
elseif ($t -eq 're') { $fm.Add('# tools: "IDA Pro, x64dbg"') }

if ($Labels.Count -gt 0) { $fm.Add('labels: [' + (($Labels | ForEach-Object { Q $_ }) -join ', ') + ']') }
else { $fm.Add('labels: []') }

switch ($t) {
  'ti' {
    $fm.Add('# meta:')
    $fm.Add('#   대상 산업: 암호화폐, 방산')
    $fm.Add('#   신뢰도: 중간')
  }
  'ir' {
    $fm.Add('meta:')
    $fm.Add('  최초 탐지: __DATE__ 09:00')
    $fm.Add('  영향 범위: 영향받은 시스템과 계정')
    $fm.Add('  대응 상태: 격리 완료, 원인 분석 중')
  }
  'ts' {
    $fm.Add('meta:')
    $fm.Add('  적용 대상: 제품·버전·환경')
    $fm.Add('  # CVE: CVE-YYYY-NNNNN')
  }
}

$abstract = @{
  're'     = '두세 문장으로 요지. 목록과 검색에도 이 문장이 쓰인다.'
  'obs'    = '무엇을 짚었고 어디까지 확인했는지 두세 문장.'
  'ti'     = '이번 호에서 확인한 활동의 요지를 두세 문장으로.'
  'ir'     = '무엇이, 언제, 어디까지 영향을 줬고 지금 어떤 상태인지 두세 문장.'
  'ts'     = '무엇이 문제이고 누가 영향을 받으며 무엇을 하면 되는지 두세 문장.'
  'digest' = '이번 호에 묶은 소식의 흐름을 두세 문장으로.'
}
$fm.Add('abstract: >')
$fm.Add('  ' + $abstract[$t])

if ($t -eq 'ti' -or $t -eq 'digest') {
  $fm.Add('items:')
  $fm.Add('  - title: "첫 번째 소식"')
  $fm.Add('    date: __DATE__')
  $fm.Add('    tag: 분류')
  $fm.Add('    summary: |')
  $fm.Add('      무엇이 있었고 무엇을 확인했는지 두세 문장.')
  $fm.Add('    # refs: [1]')
  $fm.Add('    # note: 이 소식을 어떻게 보는지 한 줄')
  $fm.Add('  - title: "두 번째 소식"')
  $fm.Add('    date: __DATE__')
  $fm.Add('    tag: 분류')
  $fm.Add('    summary: |')
  $fm.Add('      내용.')
}

$refExample = @{
  'ti' = @('Lazarus Group (G0032)', 'MITRE ATT&CK', 'https://attack.mitre.org/groups/G0032/')
  'ir' = @('Incident Handling Guide (SP 800-61)', 'NIST', 'https://csrc.nist.gov/pubs/sp/800/61/r3/final')
}
$ref = if ($refExample.ContainsKey($t)) { $refExample[$t] } else { @('PE 포맷 사양', 'Microsoft Learn', 'https://learn.microsoft.com/windows/win32/debug/pe-format') }
$fm.Add('# references:')
$fm.Add('#   - title: "' + $ref[0] + '"')
$fm.Add('#     source: ' + $ref[1])
$fm.Add('#     url: ' + $ref[2])
$fm.Add('#     accessed: __DATE__')
$fm.Add('---')

$body = @{}
$body['re'] = @'
## 출발점

어디서 시작했고 무엇이 비어 있었는지. 인용은 <cite data-ref="1"></cite>처럼 끼운다.

## 확인한 것

## 미해결

-
'@
$body['obs'] = @'
## 출발점

## 짚어 본 것

## 정리

## 미해결

-
'@
$body['ti'] = @'
## 종합 평가

이번 호 소식을 묶어 볼 때 드러나는 흐름.

## 공격 흐름

```timeline
__DATE__ | 확인한 활동
* __DATE__ | 핵심 사건은 줄 앞에 * 를 붙인다
```

## 전술·기법

```attack
초기 침투 | T1566.001 | 스피어피싱 첨부 | 근거
실행 | T1204.002 | 사용자 실행: 악성 파일 | 근거
```

## 침해 지표

```ioc
[네트워크]
example.com | 자리표시자. 실제 값으로 바꾼다
[파일]
sha256 0000000000000000000000000000000000000000000000000000000000000000 | 자리표시자
```

## 귀속 근거

## 탐지·대응 권고

## 미해결

-
'@
$body['ir'] = @'
## 개요

## 타임라인

```timeline
[탐지]
* __DATE__ 09:00 | 최초 탐지 경위
[대응]
__DATE__ 10:30 | 격리 조치
```

## 침입 경로

## 영향 범위

## 침해 지표

```ioc
[네트워크]
192.0.2.10 | 자리표시자 (문서용 예약 대역)
[호스트]
C:\Users\Public\example.exe | 자리표시자
```

## 전술·기법

```attack
초기 침투 | T1190 | 공개 애플리케이션 취약점 악용 | 근거
```

## 대응 조치

## 재발 방지 권고

## 미해결

-
'@
$body['ts'] = @'
## 배경

## 기술 분석

## 영향

## 탐지 방법

## 대응 권고

## 미해결

-
'@
$body['digest'] = @'
## 종합 평가

이번 호 소식을 묶어 볼 때 드러나는 흐름.
'@

$text = ($fm -join "`n") + "`n`n" + $body[$t] + "`n"
$text = ($text -replace "`r`n", "`n").Replace('__DATE__', $today)
[System.IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding $false))

Write-Host ""
Write-Host "  초안을 만들었습니다:  _reports/_drafts/$Slug.md"
Write-Host "  종류:                $Kind"
Write-Host "  미리보기:            http://localhost:8787/r/$Slug/  (tools/preview.py --watch 가 켜져 있으면 저장할 때마다 새로 고침)"
Write-Host "  그림:                편집기에 붙여 넣으면 _reports/_drafts/img/$Slug/ 에 저장됩니다"
if ($private) {
  Write-Host ""
  Write-Host "  TLP:$Tlp 문서라 발행하지 않습니다. 초안 폴더에 둔 채 미리보기에서 PDF로 뽑으세요."
} else {
  Write-Host "  발행:                python tools/publish.py _reports/_drafts/$Slug.md"
}
Write-Host ""
Write-Host "  초안 폴더는 git 에 올라가지 않습니다. 번호·목차·시리즈 호수·개정 이력·참고자료 패널은 자동입니다."
Write-Host ""

if ($env:TERM_PROGRAM -eq 'vscode') {
  $code = Get-Command code -ErrorAction SilentlyContinue
  if ($code) { & $code.Source -r $path }
}
