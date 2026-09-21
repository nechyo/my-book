# re:versing.zip

리버스 엔지니어링 기록을 GitHub Pages로 내는 정적 사이트.

본문만 쓰면 글 번호·목차·절 번호·그림/표/코드 번호·각주·개정 이력·참고자료 패널·주제별 색인이 자동으로 붙는다. 「PDF 내려받기」를 누르면 워터마크가 찍힌 A4 보고서로 나온다.

- 저장소: <https://github.com/nechyo/my-book>
- 주소: <https://reversing.zip> (Cloudflare → GitHub Pages)
- `nechyo.github.io/my-book`는 위 도메인으로 넘어갑니다.

---

## 1. 로컬에서 먼저 보기 (파이썬)

Ruby 없이, 파이썬만으로 사이트 전체를 실제 조판 그대로 띄운다. 발행 목록·주제별·소개·각 보고서 링크가 모두 동작한다.

```bash
python -m pip install markdown pyyaml pygments   # 처음 한 번
python tools/preview.py                          # http://localhost:8787
```

`published: false`로 공개 사이트에서 숨긴 글도 로컬 미리보기에서는 보인다. 종료는 <kbd>Ctrl</kbd>+<kbd>C</kbd>.

---

## 2. 배포

푸시하면 `.github/workflows/pages.yml`이 빌드·배포한다. Pages는 워크플로가 자동으로 활성화한다(`configure-pages` `enablement: true`).

```bash
git add -A
git commit -m "새 글"
git push
```

첫 빌드는 2~3분 걸린다. 진행 상황은 저장소 **Actions** 탭에서 볼 수 있다.

---

## 3. 글 쓰기

```powershell
.\tools\new.ps1 "문자열 난독화 추적" -Labels Windows,난독화
.\tools\new.ps1 "탐지 회피라는 표현" -Kind 관찰       # 도구 안 쓰는 글
```

필수는 `title`과 `date` 둘뿐. `tools`·`target`은 도구를 쓰지 않은 글이면 그냥 뺀다.

발행 후 알게 된 내용은 원문을 고치지 말고 덧붙인다.

```html
<div class="addendum" data-date="2026-09-21" markdown="1">추가로 확인한 내용.</div>
<div class="correction" data-date="2026-09-20" markdown="1">오류와 정정 내용.</div>
```

넣으면 문서 하단 「개정 이력」, 표제부 「최종 개정」, 목록 `개정 N회`가 자동으로 따라온다.

참고자료는 앞머리 `references:`에 적고 본문에서 `<cite data-ref="N"></cite>`로 끼운다. 그림·그래프는 코드 펜스에 `mermaid` 또는 `chart`를 지정한다.

---

## 4. 도메인 (`reversing.zip`)

`reversing.zip`은 Cloudflare에서 관리되며, GitHub Pages 앞단에 Cloudflare가 프록시로 붙어 있다. 저장소에는 다음이 반영되어 있다.

- `CNAME` 파일에 `reversing.zip`
- `_config.yml` — `url: "https://reversing.zip"`, `baseurl: ""` (최상위 도메인이므로 경로 접두사 없음)
- 워크플로는 `baseurl` 접두사 없이 빌드한다 (프로젝트 페이지의 `/my-book/` 접두사를 쓰지 않기 위함)

Cloudflare 쪽 DNS는 `nechyo.github.io`로 향하게 되어 있다. Cloudflare 프록시(주황 구름)를 쓰는 경우 SSL/TLS 모드는 **Full**로 둔다. GitHub의 도메인 검증까지 하려면 프록시를 잠시 끄고(회색 구름) apex A 레코드를 `185.199.108~111.153`으로 두거나, **Settings → Pages**의 검증용 `TXT` 레코드를 추가한다.

> 로컬 미리보기(`tools/preview.py`)는 항상 루트 경로를 쓰므로 도메인 설정과 무관하게 동작한다.

---

## 5. 예시 글

`_reports/`의 예시 2편은 `published: false`라 공개 사이트에는 안 뜬다(로컬 미리보기에서만 보인다). 진짜 글을 올릴 준비가 되면 지우거나 `published: true`로 바꾼다.

---

## 6. 구조

```
_config.yml              사이트 설정 (title / author / repo / url)
index.html               발행 목록
labels.html              주제별 색인
about.md                 이 기록에 대하여
_reports/*.md            글 (여기만 늘어난다)
_layouts/                base · report · page
_includes/               head · masthead · colophon · docket-no
assets/css/report.css    조판 (화면 + A4 인쇄 + 워터마크)
assets/js/report.js      목차·각주·개정 이력·참고자료 패널·다이어그램·그래프
tools/new.ps1            새 글 생성
tools/preview.py         로컬 미리보기 서버
.github/workflows/       빌드·배포
```

조판을 바꾸려면 `assets/css/report.css` 맨 위 토큰(종이색·잉크색·판면 폭·글꼴)만 고치면 된다.
