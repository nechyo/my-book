---
title: "SBOM의 과거, 현재, 미래"
subtitle: "SBOM은 왜 나왔고 어디까지 왔나"
date: 2026-10-06
kind: 관찰
series: "SBOM"
labels: [SBOM, 공급망]
abstract: >
  SBOM은 소프트웨어에 들어간 구성요소와 그 관계를 적은 명세서입니다. 지금 쓰이는 형식 가운데 SPDX는
  2010년 오픈소스 라이선스 준수를 위해 만들어지기 시작했습니다. 2014년 미국 하원 법안(통과되지
  않음)은 같은 목록으로 취약점을 확인하자고 했고, 2018년에는 보안을 앞세운 CycloneDX가
  나왔습니다. 2021년 미국 행정명령과 NTIA 최소 요소가 기준을 세운 뒤, Log4Shell이 그 목록의
  쓸모와 한계를 한꺼번에 드러냈습니다. 지금 미국 의료기기는 법으로 SBOM 제출을 요구하고, EU는
  2027년 12월부터 SBOM 작성을 요구합니다. 미국 연방 조달에서는 기관이 고르는 계약 조건이고, 한국은
  공공분야 SBOM 제출을 2027년까지 제도화하겠다고 했습니다. SBOM은 무엇이 들었는지까지는 답합니다.
  그 목록이 맞는지, 믿어도 되는지는 아직 다 풀리지 않았습니다.
references:
  - title: "Review of the December 2021 Log4j Event"
    source: "Cyber Safety Review Board"
    url: "https://www.cisa.gov/sites/default/files/publications/CSRB-Report-on-Log4-July-11-2022_508.pdf"
    date: 2022-07-11
  - title: "Marking the Conclusion of NTIA's SBOM Process"
    source: "NTIA"
    url: "https://www.ntia.gov/blog/marking-conclusion-ntia-s-sbom-process"
    date: 2022-04-09
  - title: "The Minimum Elements For a Software Bill of Materials (SBOM)"
    source: "NTIA"
    url: "https://www.ntia.gov/files/ntia/publications/sbom_minimum_elements_report.pdf"
    date: 2021-07-12
    note: "U.S. Department of Commerce"
  - title: "AI 일상화 시대를 준비하는 SW 공급망 보안 강화 로드맵"
    source: "관계부처 합동"
    url: "https://www.kisa.or.kr/2060204/form?postSeq=24&page=1"
    date: 2026-06-24
    note: "KISA 게시, 첨부 PDF는 2026-07-06 생성본"
  - title: "2026 Minimum Elements for a Software Bill of Materials (SBOM)"
    source: "CISA 외 공동 작성 기관"
    url: "https://www.cisa.gov/sites/default/files/2026-07/2026_cisa_sbom_minimum_elements_508c.pdf"
    date: 2026-07-29
    note: "버전 2.1"
  - title: "Overview – SPDX"
    source: "SPDX · Linux Foundation"
    url: "https://spdx.dev/about/overview/"
    accessed: 2026-10-04
  - title: "CycloneDX History"
    source: "OWASP CycloneDX"
    url: "https://cyclonedx.org/about/history/"
    accessed: 2026-10-04
  - title: "ECMA-424: CycloneDX Bill of materials specification"
    source: "Ecma International"
    url: "https://ecma-international.org/publications-and-standards/standards/ecma-424/"
    accessed: 2026-10-04
    note: "2판(2025년 12월)"
  - title: "The Linux Foundation Launches Open Compliance Program"
    source: "Linux Foundation"
    url: "https://www.linuxfoundation.org/press/press-release/the-linux-foundation-launches-open-compliance-program"
    date: 2010-08-10
  - title: "ISO/IEC 5962:2021 Information technology — SPDX® Specification V2.2.1"
    source: "ISO"
    url: "https://www.iso.org/standard/81870.html"
    accessed: 2026-10-04
    note: "2021년 8월 발행"
  - title: "SBOM 표준"
    source: "SK텔레콤"
    url: "https://sktelecom.github.io/guide/supply-chain/sbom/standards/"
    date: 2026-07-13
    note: "오픈소스 가이드"
  - title: "org/apache/logging/log4j/log4j-core/2.14.1"
    source: "Maven Central"
    url: "https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-core/2.14.1/"
    accessed: 2026-10-04
    note: "jar, .sha1, .pom"
  - title: "CycloneDX Bill of Materials Standard v1.6 (JSON Schema)"
    source: "OWASP CycloneDX"
    url: "https://cyclonedx.org/schema/bom-1.6.schema.json"
    accessed: 2026-10-04
  - title: "SBOM FAQ"
    source: "NTIA"
    url: "https://www.ntia.gov/files/ntia/publications/sbom_faq_20200821.pdf"
    date: 2020-08-21
    note: "Multistakeholder Process on Software Component Transparency"
  - title: "SPDX Workgroup Releases Software Package Data Exchange Standard to Widespread Industry Support"
    source: "Linux Foundation"
    url: "https://www.linuxfoundation.org/press/press-release/spdx-workgroup-releases-software-package-data-exchange-standard-to-widespread-industry-support"
    date: 2011-08-17
  - title: "라이선스 소개"
    source: "OLIS · 한국저작권위원회"
    url: "https://www.olis.or.kr/license/introduction.do"
    accessed: 2026-10-04
  - title: "저작권법 [법률 제9625호, 2009. 4. 22., 일부개정]"
    source: "국가법령정보센터"
    url: "https://www.law.go.kr/법령/저작권법/(09625,20090422)"
    date: 2009-04-22
    note: "제정·개정이유 탭"
  - title: "H.R. 5793 (IH) — Cyber Supply Chain Management and Transparency Act of 2014"
    source: "GovInfo"
    url: "https://www.govinfo.gov/content/pkg/BILLS-113hr5793ih/html/BILLS-113hr5793ih.htm"
    date: 2014-12-04
    note: "U.S. Government Publishing Office"
  - title: "H.R.5793 - Cyber Supply Chain Management and Transparency Act of 2014"
    source: "Congress.gov"
    url: "https://www.congress.gov/bill/113th-congress/house-bill/5793"
    accessed: 2026-10-04
    note: "진행 경과"
  - title: "BILLSTATUS-113hr5793"
    source: "GovInfo"
    url: "https://www.govinfo.gov/bulkdata/BILLSTATUS/113/hr/BILLSTATUS-113hr5793.xml"
    accessed: 2026-10-04
    note: "법안 진행 기록 XML"
  - title: "Improving the Nation's Cybersecurity (Executive Order 14028)"
    source: "Federal Register"
    url: "https://www.federalregister.gov/documents/2021/05/17/2021-10460/improving-the-nations-cybersecurity"
    date: 2021-05-17
    note: "2021년 5월 12일 서명"
  - title: "정보통신망 이용촉진 및 정보보호 등에 관한 법률 제45조(정보통신망의 안정성 확보 등)"
    source: "국가법령정보센터"
    url: "https://www.law.go.kr/법령/정보통신망이용촉진및정보보호등에관한법률/제45조"
    accessed: 2026-10-04
  - title: "정보통신망 이용촉진 및 정보보호 등에 관한 법률 제48조의3(침해사고의 신고 등)"
    source: "국가법령정보센터"
    url: "https://www.law.go.kr/법령/정보통신망이용촉진및정보보호등에관한법률/제48조의3"
    accessed: 2026-10-04
  - title: "SW 공급망 보안 가이드라인 1.0 (전체본, 요약본)"
    source: "한국인터넷진흥원"
    url: "https://www.kisa.or.kr/2060204/form?postSeq=15&page=1"
    date: 2024-05-13
  - title: "「디지털의료기기 전자적 침해행위 보안지침」 제정 고시"
    source: "식품의약품안전처"
    url: "https://www.mfds.go.kr/brd/m_211/view.do?seq=14894"
    date: 2025-04-29
    note: "고시 제2025-30호, 누리집 고시일 칸 표기는 2025-04-21"
  - title: "범부처 정보보호 종합대책 발표"
    source: "관계부처 합동"
    url: "https://www.fsc.go.kr/no010101/85452"
    date: 2025-10-22
    note: "보도자료, 금융위원회 누리집 게시"
  - title: "Highly Evasive Attacker Leverages SolarWinds Supply Chain to Compromise Multiple Global Victims With SUNBURST Backdoor"
    source: "FireEye"
    url: "https://cloud.google.com/blog/topics/threat-intelligence/evasive-attacker-leverages-solarwinds-supply-chain-compromises-with-sunburst-backdoor"
    date: 2020-12-13
    note: "Google Cloud Blog"
  - title: "Advanced Persistent Threat Compromise of Government Agencies, Critical Infrastructure, and Private Sector Organizations"
    source: "CISA"
    url: "https://www.cisa.gov/news-events/cybersecurity-advisories/aa20-352a"
    date: 2020-12-17
    note: "AA20-352A, 이후 갱신"
  - title: "M-22-18: Enhancing the Security of the Software Supply Chain through Secure Software Development Practices"
    source: "OMB"
    url: "https://bidenwhitehouse.archives.gov/wp-content/uploads/2022/09/M-22-18.pdf"
    date: 2022-09-14
    note: "백악관 기록 보관 사이트"
  - title: "M-26-05: Adopting a Risk-based Approach to Software and Hardware Security"
    source: "OMB"
    url: "https://www.whitehouse.gov/wp-content/uploads/2026/01/M-26-05-Adopting-a-Risk-based-Approach-to-Software-and-Hardware-Security.pdf"
    date: 2026-01-23
  - title: "Cybersecurity in Medical Devices: Refuse to Accept Policy for Cyber Devices and Related Systems Under Section 524B of the FD&C Act"
    source: "Federal Register"
    url: "https://www.govinfo.gov/content/pkg/FR-2023-03-30/html/2023-06646.htm"
    date: 2023-03-30
  - title: "21 U.S.C. 360n-2 — Ensuring cybersecurity of devices"
    source: "GovInfo"
    url: "https://www.govinfo.gov/content/pkg/USCODE-2024-title21/html/USCODE-2024-title21-chap9-subchapV-partA-sec360n-2.htm"
    accessed: 2026-10-04
    note: "United States Code, 2024 Edition"
  - title: "Regulation (EU) 2024/2847 (Cyber Resilience Act)"
    source: "EUR-Lex"
    url: "https://eur-lex.europa.eu/eli/reg/2024/2847/oj"
    date: 2024-11-20
  - title: "Software Bill of Materials (SBOM) for Artificial Intelligence – Minimum Elements"
    source: "G7 Cybersecurity WG"
    url: "https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/KI/SBOM-for-AI_minimum-elements.html"
    date: 2026-05-12
    note: "G7 Cybersecurity Working Group, 독일 BSI 게시"
  - title: "Too Much of a Good Thing: (In-)Security of Mandatory Security Software for Financial Services in South Korea"
    source: "USENIX Security 2025"
    url: "https://www.usenix.org/conference/usenixsecurity25/presentation/yun"
    date: 2025-08-13
  - title: "工业和信息化部发言人就绿色上网过滤软件问题答记者问"
    source: "중국 공업정보화부"
    url: "https://chicago.china-consulate.gov.cn/ywsz/kj/202508/t20250807_11684234.htm"
    date: 2009-06-30
    note: "주시카고 중국 총영사관 게재본"
  - title: "Analysis of the Green Dam Censorware System"
    source: "University of Michigan"
    url: "https://jhalderm.com/pub/gd/"
    date: 2009-06-11
    note: "Revision 2.41"
  - title: "Investigating Large Scale HTTPS Interception in Kazakhstan"
    source: "ACM IMC 2020"
    url: "https://censoredplanet.org/assets/Kazakhstan.pdf"
    date: 2020-10-27
    note: "doi:10.1145/3419394.3423665"
  - title: "Continuing to Protect our Users in Kazakhstan"
    source: "Mozilla"
    url: "https://blog.mozilla.org/netpolicy/2020/12/18/kazakhstan-root-2020/"
    date: 2020-12-18
  - title: "Protecting our Users in Kazakhstan"
    source: "Mozilla"
    url: "https://blog.mozilla.org/security/2019/08/21/protecting-our-users-in-kazakhstan/"
    date: 2019-08-21
  - title: "Protecting Chrome users in Kazakhstan"
    source: "Google Security Blog"
    url: "https://security.googleblog.com/2019/08/protecting-chrome-users-in-kazakhstan.html"
    date: 2019-08-21
  - title: "Government removes mandatory pre-installation of Sanchar Saathi App"
    source: "PIB"
    url: "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2198110"
    date: 2025-12-03
    note: "Ministry of Communications, India"
  - title: "Правительство включит новые цифровые продукты в перечень программ для обязательной предустановки"
    source: "Правительство России"
    url: "http://government.ru/news/55977/"
    date: 2025-08-21
    note: "распоряжения №2240-р, №2241-р"
  - title: "Saiba como instalar o Módulo de Segurança do BB"
    source: "Banco do Brasil"
    url: "https://blog.bb.com.br/saiba-como-instalar-o-modulo-de-seguranca-do-bb/"
    date: 2023-01-03
    note: "2026-04-06 수정"
  - title: "ROK-UK Joint Cyber Security Advisory: DPRK state-linked cyber actors conduct software supply chain attacks"
    source: "국가정보원 · 영국 NCSC"
    url: "https://eng.nis.go.kr/ECM/1_3_1_1.do?seq=83&currentPage=1"
    date: 2023-11-23
    note: "첨부 PDF"
  - title: "3CX Software Supply Chain Compromise Initiated by a Prior Software Supply Chain Compromise; Suspected North Korean Actor Responsible"
    source: "Mandiant"
    url: "https://cloud.google.com/blog/topics/threat-intelligence/3cx-software-supply-chain-compromise"
    date: 2023-04-20
    note: "Google Cloud Blog"
  - title: "Mandiant Security Update – Initial Intrusion Vector"
    source: "3CX"
    url: "https://www.3cx.com/blog/news/mandiant-security-update2/"
    date: 2023-04-20
  - title: "backdoor in upstream xz/liblzma leading to ssh server compromise"
    source: "oss-security"
    url: "https://www.openwall.com/lists/oss-security/2024/03/29/4"
    date: 2024-03-29
  - title: "UK and Republic of Korea issue warning about DPRK state-linked cyber actors attacking software supply chains"
    source: "NCSC"
    url: "https://www.ncsc.gov.uk/news/uk-republic-of-korea-issue-warning-dprk-state-linked-cyber-actors-attacking-software-supply-chains"
    date: 2023-11-23
  - title: "컨테이너 이미지 SBOM 비교 가능성 및 해석 한계에 관한 실증 연구"
    source: "정보처리학회논문지"
    url: "https://doi.org/10.3745/TKIPS.2026.15.7.571"
    accessed: 2026-10-04
    note: "15권 7호, 2026년 7월"
  - title: "Minimum Requirements for Vulnerability Exploitability eXchange (VEX)"
    source: "CISA"
    url: "https://www.cisa.gov/sites/default/files/2023-04/minimum-requirements-for-vex-508c.pdf"
    accessed: 2026-10-04
    note: "2023년 4월 발행"
  - title: "sbom-unifier: Integration Framework for Heterogeneous SBOMs"
    source: "arXiv"
    url: "https://arxiv.org/abs/2608.30708"
    date: 2026-08-31
  - title: "The Impact of SBOM Generators on Vulnerability Assessment in Python: A Comparison and a Novel Approach"
    source: "arXiv"
    url: "https://arxiv.org/abs/2409.06390"
    date: 2024-09-10
  - title: "JBomAudit: Assessing the Landscape, Compliance, and Security Implications of Java SBOMs"
    source: "NDSS 2025"
    url: "https://www.ndss-symposium.org/wp-content/uploads/2025-322-paper.pdf"
    date: 2025-02-24
    note: "doi:10.14722/ndss.2025.240322"
  - title: "국･내외 SW공급망보안 현황 및 SBOM 도구 실증 결과보고서"
    source: "한국정보보호산업협회"
    url: "https://www.kisia.or.kr/main/gmb_file.php?board_title=gmb_oneboard&filedb=(20260629013421)71(0).pdf&filen=(20260629013421)71(0).pdf"
    accessed: 2026-10-04
    note: "과기정통부·IITP 과제 4차년도 실증, PDF 생성일 2026-01-15"
  - title: "Trustworthy and Confidential SBOM Exchange"
    source: "arXiv"
    url: "https://arxiv.org/abs/2509.13217"
    date: 2026-03-12
    note: "v3, USENIX Security '26 게재 예정"
---
## 시작

2021년 12월 Apache Log4j의 원격 코드 실행 취약점 CVE-2021-44228이 공개됐습니다. 패치를 적용하기 전에 먼저 풀어야 할 문제가 있었습니다. 우리 시스템 어디에 Log4j가 들어 있는가 하는 문제였습니다. 이 사태를 조사한 미국 사이버안전검토위원회(CSRB)의 보고서에 따르면 Log4j에는 쓰는 곳을 모아 둔 포괄적인 "고객 명단"이 없었고, 어느 제품에 하위 시스템으로 들어갔는지 정리한 목록도 없었습니다. 이 때문에 방어가 늦어졌고, 기업과 공급업체는 Log4j를 어디에 쓰는지 찾느라 허둥댔습니다. 위원회는 Log4j를 "고질적 취약점(endemic vulnerability)"이라 부르며, 취약한 Log4j가 앞으로 여러 해, 어쩌면 10년 이상 시스템에 남을 것으로 내다봤습니다 <cite data-ref="1"></cite>.

위원회는 SBOM을 쓰는 조직들을 대표하는 단체들과도 이야기를 나눴습니다. SBOM으로 취약한 Log4j 배포를 찾아냈다고 보고한 곳은 한 군데도 없었습니다. 위원회가 예로 든 SBOM의 한계는 세 가지입니다. 필드 설명이 제각각이고, 목록에 오른 구성요소에 버전 정보가 빠져 있으며, 그런 차이 때문에 받는 쪽에서 자동으로 처리하지 못한다는 것입니다 <cite data-ref="1"></cite>.

NTIA가 2022년 4월에 쓴 글은 반대로 말합니다. SBOM을 쓰던 기업들은 Log4j가 자기 소프트웨어 패키지에 들어 있는지, 들어 있다면 어디에 있는지 빠르게 확인해 취약점을 격리하고 고칠 수 있었다는 것입니다. 이 글에는 그렇게 말한 근거가 된 사례나 자료가 나와 있지 않습니다 <cite data-ref="2"></cite>.

SBOM은 소프트웨어 안에 무엇이 들었는지 적는 문서입니다. 형식을 다 갖춰도 그 목록이 맞는지, 받은 쪽이 그 목록을 믿어도 되는지는 따로 따져야 합니다.

## SBOM

미국 통신정보관리청(NTIA)의 정의로 SBOM은 "소프트웨어를 만드는 데 쓰인 여러 구성요소의 세부 정보와 공급망 관계를 담은 공식 기록"입니다 <cite data-ref="3"></cite>. 과학기술정보통신부와 국가정보원이 2026년 6월 공개한 SW 공급망 보안 강화 로드맵은 SBOM을 "SW를 구성하는 전체 컴포넌트들의 구성요소와 의존 관계를 기술한 것"이라고 설명하고, 국내에서는 SW 구성요소 명세서나 SW 자재명세서라고도 부른다고 덧붙였습니다 <cite data-ref="4"></cite>. 두 정의 모두 구성요소와 그 사이의 관계를 담으라고 합니다.

### 최소 요소

NTIA가 2021년에 정한 최소 요소는 세 부분으로 이뤄집니다. 데이터 필드, 자동화 지원, 그리고 SBOM을 요청하고 만들고 쓰는 관행과 절차입니다 <cite data-ref="3"></cite>. 관행 쪽에는 "알려진 미지(known unknowns)"라는 항목이 있습니다. 의존 관계를 끝까지 다 적지 못했다면, 더 기대는 것이 없는 구성요소와 의존 관계를 아예 모르는 구성요소를 구별해 표시하라는 요구입니다 <cite data-ref="3"></cite>.

최소 요소의 개정판은 2026년 7월 29일에 나왔습니다. 미국 사이버보안·기반시설보안청(CISA)이 국가안보국(NSA), 연방수사국(FBI), 그리고 한국을 포함한 13개국 기관과 함께 낸 문서로, NTIA의 2021년 최소 요소를 갱신해 대체합니다. 데이터 필드는 일곱 개에서 열일곱 개가 됐습니다. "알려진 미지"는 "모르는 정보의 명시적 식별(Explicitly Identifying Unknown Information)"로 이름을 바꾸면서, 알지만 일부러 뺀 정보와 정말 모르는 정보를 나눠 적게 했습니다 <cite data-ref="5"></cite>.

| 2021년 NTIA (7개) | 2026년 개정판 (17개) |
|---|---|
| 공급자 이름 | 구성요소 생산자 |
| 구성요소 이름 | 구성요소 이름 |
| 구성요소 버전 | 구성요소 버전 |
| 기타 고유 식별자 | 구성요소 식별자 |
| 의존 관계 | 구성요소 의존 관계 |
| SBOM 데이터 작성자 | SBOM 작성자, **SBOM 작성자 서명** |
| 작성 시각 | SBOM 시각(마지막 갱신 시각) |
| | **구성요소 해시값, 해시 알고리즘, 라이선스** |
| | **SBOM 형식 이름·버전, 생성 도구 이름·버전, SBOM 버전, 생성 맥락** |

굵은 글씨가 새로 생긴 필드입니다 <cite data-ref="5"></cite>. 이 가운데 생성 맥락은 SBOM을 수명주기의 어느 단계에서, 어떤 데이터로 만들었는지 적는 칸입니다. 소스 코드로 만들었으면 "빌드 전", 바이너리 분석 도구로 만들었으면 "빌드 후"라고 적는 식입니다. 만든 단계에 따라 구성요소 데이터가 달라질 수 있다는 것이 개정판의 설명입니다 <cite data-ref="5"></cite>.

개정판에 따르면 2021년에는 도입 초기라 실수를 받아들이는 관행을 따로 둬야 했지만, 그동안 기술이 발전해 이제는 받는 쪽이 SBOM 데이터가 정확하리라고 기대해도 됩니다. 새로 들어간 작성자 서명은 주장된 서명자가 실제로 서명했고 서명 뒤에 내용이 바뀌지 않았음을 보증합니다. 그런데 SBOM 데이터가 정확한지, 다뤄야 할 범위를 다 덮는지, 빠진 것은 없는지 확인하는 일은 서명과 다른 품질 기준이 필요하다며 최소 요소의 범위 밖으로 뺐습니다. 그런 확인에는 오픈소스 저장소나 바이너리 분석 도구로 SBOM에 없는 구성요소를 찾아볼 수 있다고 적었습니다 <cite data-ref="5"></cite>.

### SPDX와 CycloneDX

기계가 읽으려면 형식이 정해져 있어야 합니다. NTIA는 2021년에 SPDX, CycloneDX, SWID 태그 세 가지를 들었습니다 <cite data-ref="3"></cite>. 2026년 개정판은 SWID 태그를 뺐습니다. 여러 도구가 지원하는 널리 쓰이는 형식이 아니라는 이유였고, 지금 널리 쓰이는 형식은 SPDX와 CycloneDX 둘이라고 적었습니다 <cite data-ref="5"></cite>.

| | SPDX | CycloneDX |
|---|---|---|
| 관리 주체 | 리눅스 재단 <cite data-ref="6"></cite> | OWASP, Ecma International TC54 <cite data-ref="7"></cite> <cite data-ref="8"></cite> |
| 시작 | 2010년, 오픈소스 라이선스 준수 <cite data-ref="6"></cite> <cite data-ref="9"></cite> | 2018년, 보안 중심 BOM 표준 <cite data-ref="7"></cite> |
| 국제 표준 | ISO/IEC 5962:2021(SPDX 2.2.1) <cite data-ref="10"></cite> | ECMA-424(2024년 6월 1판 CycloneDX 1.6, 2025년 12월 2판 CycloneDX 1.7) <cite data-ref="7"></cite> <cite data-ref="8"></cite> |
| 최근 판의 변화 | 3.0에서 보안·빌드·데이터셋·AI 프로파일 <cite data-ref="6"></cite> | 1.5 AI 투명성·설정·데이터, 1.6 암호 자산·증명, 1.7 인용·특허 <cite data-ref="7"></cite> |

SPDX는 2010년 2월 리눅스 재단 산하 FOSSBazaar의 작업 그룹에서 초안 작업을 시작했습니다. 처음 이름은 Package Facts였고, 그해 8월 리눅스 재단 오픈 컴플라이언스 프로그램의 한 축으로 발표됐습니다 <cite data-ref="6"></cite>. 2024년 4월 나온 SPDX 3.0.0에는 보안, 빌드, 데이터셋, AI 프로파일이 들어갔습니다 <cite data-ref="6"></cite>. ISO/IEC 5962:2021로 국제 표준이 된 것은 2021년 8월 발행된 SPDX 2.2.1이고, ISO는 몇 달 안에 새 판으로 대체할 예정이라고 안내하고 있습니다 <cite data-ref="10"></cite>.

CycloneDX의 연혁 페이지는 2018년 3월에 나온 1.0을 "최초의 범용, 보안 중심 BOM 표준"이라고 소개합니다. 처음부터 소프트웨어와 하드웨어 구성요소를 함께 다뤘고, 패키지 식별자 Package URL(purl)을 보안 용도로 처음 내놓은 것도 1.0이라는 것이 CycloneDX 쪽 설명입니다. 서비스는 2020년 5월 1.2부터 다뤘습니다 <cite data-ref="7"></cite>. 그 뒤로도 다루는 대상은 계속 늘었습니다. 2023년 6월 1.5에는 AI 투명성과 설정·데이터 구성요소가, 2024년 4월 1.6에는 양자내성암호 대비를 위한 암호 자산과 증명(attestation)이, 2025년 10월 1.7에는 인용과 특허 정보가 들어갔습니다 <cite data-ref="7"></cite>. 1.6은 2024년 6월 ECMA-424 1판으로 <cite data-ref="7"></cite>, 1.7은 2025년 12월 ECMA-424 2판으로 표준이 됐습니다 <cite data-ref="8"></cite>.

어느 형식을 쓸지는 만드는 쪽이 정하라는 것이 개정판의 권고입니다. 구성요소 생산자나 SBOM 작성자는 조직, 산업, 분야 사정에 맞춰 형식을 고르고, 받는 조직은 널리 쓰이고 서로 호환되며 기계가 처리할 수 있는 형식이라면 받아 주라는 내용입니다 <cite data-ref="5"></cite>. 받는 쪽이 원하는 형식을 밝혀 두기도 합니다. SK텔레콤은 공급사가 제출할 SBOM으로 CycloneDX(JSON)를 권하지만 두 형식 모두 받습니다 <cite data-ref="11"></cite>.

### 실제 SBOM 예시

설명용으로 줄여 만든 CycloneDX 1.6 문서입니다. 구성요소에는 Log4Shell 시기의 log4j-core 2.14.1을 넣었습니다. 해시는 Maven Central에서 내려받은 log4j-core-2.14.1.jar로 직접 계산했고, SHA-1은 Maven Central이 함께 공개한 값과 일치합니다 <cite data-ref="12"></cite>. CycloneDX 1.6 JSON 스키마 검증도 통과합니다 <cite data-ref="13"></cite>.

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.6",
  "serialNumber": "urn:uuid:35822ff2-f2bb-4bb8-b4b0-af9136fa8c99",
  "version": 1,
  "metadata": {
    "timestamp": "2026-10-04T09:00:00Z",
    "lifecycles": [{"phase": "post-build"}],
    "tools": {
      "components": [
        {
          "type": "application",
          "name": "example-sbom-tool",
          "version": "0.1.0"
        }
      ]
    },
    "component": {
      "type": "application",
      "bom-ref": "app",
      "name": "example-web",
      "version": "2.3.0"
    }
  },
  "components": [
    {
      "type": "library",
      "bom-ref": "log4j-core",
      "manufacturer": {"name": "The Apache Software Foundation"},
      "group": "org.apache.logging.log4j",
      "name": "log4j-core",
      "version": "2.14.1",
      "purl": "pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1",
      "hashes": [
        {
          "alg": "SHA-1",
          "content": "9141212b8507ab50a45525b545b39d224614528b"
        },
        {
          "alg": "SHA-256",
          "content": "ade7402a70667a727635d5c4c29495f4ff96f061f12539763f6f123973b465b0"
        }
      ],
      "licenses": [{"license": {"id": "Apache-2.0"}}]
    }
  ],
  "dependencies": [{"ref": "app", "dependsOn": ["log4j-core"]}],
  "compositions": [{"aggregate": "incomplete", "dependencies": ["log4j-core"]}]
}
```

- `metadata.timestamp`가 SBOM 시각, `metadata.tools`가 생성 도구입니다. `metadata.lifecycles`에는 BOM의 데이터를 수명주기의 어느 단계에서 모았는지 적습니다 <cite data-ref="13"></cite>. 2026년 개정판의 생성 맥락에 맞춰 볼 수 있는 칸이고, 예시에는 빌드 뒤(`post-build`)라고 적었습니다.
- 구성요소마다 만든 조직, 이름, 버전, 식별자(`purl`), 해시, 라이선스를 붙였습니다. 만든 조직은 `manufacturer`에 적습니다. `supplier`라는 칸도 있지만, 여기에는 유통하거나 다시 묶어 낸 곳이 들어갈 수도 있습니다 <cite data-ref="13"></cite>.
- `dependencies`는 무엇이 무엇에 기대는지 적는 곳입니다. 예시에서는 `example-web`이 `log4j-core`에 기댑니다.
- `compositions`는 관계를 어디까지 다 적었는지 밝히는 칸입니다. log4j-core는 log4j-api에 기대는데 <cite data-ref="12"></cite> 예시에는 적지 않았습니다. 그래서 log4j-core의 의존 관계를 "다른 관계가 더 있다"는 뜻의 `incomplete`로 표시했습니다 <cite data-ref="13"></cite>. CycloneDX는 1.3에서 이 칸을 들이면서 NTIA의 "알려진 미지"를 넘어서는 완전성 표현이라고 소개했습니다 <cite data-ref="7"></cite>.

이 문서가 있으면 log4j-core 2.14.1이 들었는지는 purl 한 줄로 바로 확인됩니다. 하지만 이 목록이 실제로 배포된 파일과 같은지는 문서 어디에도 증명이 없습니다. 해시로 맞춰 보려면 받는 쪽이 실제 파일의 해시를 직접 계산해야 합니다.

## 어디서 시작한 건지

### 제조업의 부품 명세서(BOM)

SBOM은 이름 그대로 소프트웨어(Software)의 자재명세서(Bill of Materials)입니다. NTIA의 SBOM FAQ는 제조업의 자재명세서를 예로 듭니다. 자재명세서와 공급망 관리 원칙이 수십 년 동안 자동차, 식품, 제조업 전반을 바꿔 놓았고, 그 중심에는 공급망의 투명성과, 출처·품질·결함 대처법에 대한 지식이 있었다는 설명입니다. SBOM은 이미 검증된 그 원칙을 소프트웨어 개발에 들여오려는 시도라고 합니다 <cite data-ref="14"></cite>. 어떤 구성요소가 다른 구성요소를 품고 있으면 그 구성요소도 자기 SBOM을 가져야 하고, 이렇게 겹겹이 모인 SBOM은 제조업의 다단계 BOM과 같은 모양이 됩니다 <cite data-ref="14"></cite>.

### 처음엔 라이선스 관리였다 (저작권법)

지금 쓰이는 두 형식 가운데 먼저 나온 쪽은 SPDX이고, SPDX는 라이선스 문제에서 출발했습니다. 리눅스 재단은 2010년 8월 기업이 오픈소스 라이선스를 지키도록 돕는 오픈 컴플라이언스 프로그램을 시작했습니다. 그 발표문에서 SPDX 작업 그룹이 맡은 일은, 기업의 "bills of material"을 표준화해 제품에 들어간 오픈소스 구성요소를 쉽게 찾고 표시하게 하는 것이었습니다 <cite data-ref="9"></cite>. 이듬해 8월 SPDX 1.0을 내놓을 때도 같은 방향이었습니다. 소프트웨어 공급망에서 라이선스 정보를 주고받는 방식을 표준화해 오픈소스 라이선스 준수를 돕는 표준이라고 소개했습니다 <cite data-ref="15"></cite>.

NTIA에 따르면 금융권도 이르면 2013년부터 소프트웨어 공급망 투명성을 실험해 왔습니다 <cite data-ref="14"></cite>.

라이선스가 법률 문제가 되는 것은 저작권 때문입니다. 오픈소스는 소스 코드가 공개돼 있을 뿐, 여전히 저작권 같은 지식재산권의 보호를 받습니다. 라이선스는 저작권자가 사용자에게 지키라고 정한 조건이고, 이를 어기면 저작권 침해나 계약 위반으로 법적 책임을 질 수 있습니다 <cite data-ref="16"></cite>. 한국에서는 2009년 4월 22일 공포되고 7월 23일 시행된 저작권법 개정(법률 제9625호)으로 「컴퓨터프로그램 보호법」이 「저작권법」에 합쳐졌습니다. 이후 컴퓨터프로그램저작물도 일반 저작물과 같은 법률이 다룹니다 <cite data-ref="17"></cite>. 무엇을 가져다 썼는지 모르면 어떤 조건을 지켜야 하는지도 알 수 없습니다.

### 보안의 요구가 되다 (저작권법 + 정보통신망법)

같은 목록을 보안 제도로 끌어들이려 한 이른 시도 가운데 하나가 2014년 12월 4일 미국 하원에 제출된 「사이버 공급망 관리 및 투명성 법안」(H.R.5793)입니다. 법안은 예산관리국(OMB)에 연방 조달 지침을 만들라고 하면서 그 지침에 여러 계약 조항을 넣게 했는데, 그 가운데 두 조항이 SBOM과 닿아 있습니다. 하나는 제3자·오픈소스 구성요소(법안의 표현으로는 "바이너리 구성요소")가 든 소프트웨어를 살 때 구성요소마다의 포괄적인 목록, 곧 "bill of materials"를 기밀로 받는 조항입니다. 다른 하나는 납품 업체가 미국 국가취약점데이터베이스(NVD) 등에 오른 알려진 취약점이 그 제품에 없음을 확인하게 하는 조항입니다 <cite data-ref="18"></cite>. 법안은 제출된 날 위원회로 넘어간 뒤 더 진행되지 않았습니다 <cite data-ref="19"></cite> <cite data-ref="20"></cite>. 2010년의 SPDX가 이 목록으로 라이선스를 봤다면, 이 법안은 같은 목록으로 취약점을 보려 했습니다.

형식 쪽에서는 2018년 3월 CycloneDX 1.0이 보안을 앞세운 BOM 표준으로 나왔습니다 <cite data-ref="7"></cite>. 2021년 5월 미국 행정명령 14028, 같은 해 7월 NTIA 최소 요소가 뒤를 이었습니다 <cite data-ref="21"></cite> <cite data-ref="3"></cite>. 모두 Log4Shell이 공개된 2021년 12월보다 먼저입니다. 그러니 Log4Shell 때문에 SBOM이 보안 문서가 됐다고 말하기는 어렵습니다. 보안 문서로 자리를 잡아 가던 SBOM의 쓸모와 한계를 Log4Shell이 한꺼번에 드러냈다고 보는 편이 기록과 맞습니다.

한국 법으로 보면 라이선스 쪽은 저작권법의 몫입니다. 보안 쪽 법률 가운데 정보통신망법에서는 제45조가 정보통신서비스 제공자 등에게 정보통신망의 안정성과 정보의 신뢰성을 확보하기 위한 보호조치를 하라고 하고 <cite data-ref="22"></cite>, 현행 제48조의3이 정보통신서비스 제공자에게 침해사고를 알게 된 때부터 24시간 안에 신고하라고 합니다 <cite data-ref="23"></cite>. 두 조문은 무엇을 지키고 언제 알릴지를 정해 두었을 뿐, 지켜야 할 시스템에 어떤 소프트웨어 구성요소가 들었는지 적어 두라고 하지는 않습니다. 지금까지 공개된 정부 문서를 보면 구성요소 목록은 가이드라인, 고시, 로드맵, 종합대책에서 다뤄지고 있습니다 <cite data-ref="24"></cite> <cite data-ref="25"></cite> <cite data-ref="4"></cite> <cite data-ref="26"></cite>.

### 정의를 합의하다 (Software + BOM)

용어와 최소한의 약속은 NTIA가 꾸린 다자간 논의에서 정리됐습니다. NTIA는 2018년 소프트웨어 구성요소 투명성을 주제로 다자간 논의를 시작했고, 그해 7월 첫 공개회의를 열었습니다 <cite data-ref="3"></cite>. 참가자들은 무엇을 왜, 어떻게 투명하게 할지부터 정의했습니다. 공통으로 합의한 정의를 세웠고, "기준선(baseline)" SBOM이 중요하다고 강조했습니다. 의료기기 업계 전문가들은 일찍부터 나서 첫 SBOM 개념 증명(PoC)을 진행했습니다 <cite data-ref="2"></cite>.

2021년 최소 요소는 이 논의와는 별도의 절차로 만들어졌습니다. 행정명령으로 과제를 받은 NTIA는 다자간 논의에서 이해관계자들이 써 둔 내용을 바탕으로 초안을 잡았고, 2021년 6월 의견을 받은 뒤 최소 요소를 발표했습니다 <cite data-ref="3"></cite>.

## 제도가 되기까지

### SolarWinds와 행정명령 14028

2020년 12월 SolarWinds Orion을 거친 침해가 드러났습니다. FireEye가 12월 13일 공개한 분석에 따르면 공격자는 SolarWinds Orion 업데이트에 트로이 목마를 심어 SUNBURST라는 악성 코드를 퍼뜨렸습니다. 트로이 목마가 든 업데이트 여러 개가 2020년 3월부터 5월 사이에 디지털 서명까지 받은 채 SolarWinds 업데이트 웹사이트에 올라갔습니다 <cite data-ref="27"></cite>. CISA 경보 AA20-352A는 2020년 12월 17일 처음 게시된 뒤 여러 번 갱신됐습니다. 경보에 따르면 적어도 2020년 3월부터 미국 정부 기관과 핵심 기반시설, 민간 조직이 APT 행위자에게 침해당했고, 초기 침투 경로 가운데 하나가 SolarWinds Orion 제품의 공급망 침해였습니다 <cite data-ref="28"></cite>. MITRE ATT&CK는 이 사건을 캠페인 C0024로 정리해 T1195.002의 사례로 올려 두었습니다.

다섯 달 뒤인 2021년 5월 12일 행정명령 14028이 서명됐습니다. 행정명령은 상무부가 NIST를 통해 소프트웨어 공급망 보안 지침을 내게 하면서, 그 지침에 "구매자에게 제품마다 SBOM을 직접 제공하거나 공개 웹사이트에 게시하는 것"에 관한 기준을 넣으라고 했습니다. 상무부에는 60일 안에 SBOM 최소 요소를 발표하라고 했고, 예산관리국(OMB)에는 행정명령 이후에 조달하는 소프트웨어에 대해 기관들이 그 지침을 따르도록 조치하라고 했습니다 <cite data-ref="21"></cite>. 납품 업체에 SBOM 제출 의무를 곧바로 지운 것은 아니었습니다. 지침을 만들고, 기관이 그 지침을 따르게 하는 방식이었습니다.

OMB가 정한 이행 방식은 그사이 바뀌었습니다. 2022년 9월의 M-22-18은 기관이 소프트웨어를 쓰기 전에 생산자에게서 보안 개발 관행을 지켰다는 자체 증명을 받게 했고, SBOM은 소프트웨어의 중요도에 따라 또는 기관 판단으로 조달 요건에 넣을 수 있게 했습니다 <cite data-ref="29"></cite>. OMB는 2026년 1월 23일 M-26-05를 내고 이 M-22-18과 그 짝인 M-23-16을 폐지했습니다. M-22-18이 검증되지 않은 부담스러운 소프트웨어 회계 절차를 부과해, 실제 보안 투자보다 준수를 앞세웠다는 것이 폐지 이유였습니다. 이제 기관은 소프트웨어와 하드웨어의 전체 목록을 계속 유지하되, 보증 정책은 위험 판단에 맞춰 스스로 세웁니다. 원하면 소프트웨어 생산자가 요청에 따라 최신 SBOM을 내도록 계약 조건을 둘 수도 있습니다 <cite data-ref="30"></cite>. M-22-18 때도 지금도, 미국 연방 조달에서 SBOM은 모두에게 똑같이 지우는 의무가 아니라 기관이 골라 쓰는 조건입니다 <cite data-ref="29"></cite> <cite data-ref="30"></cite>.

### NTIA 최소 요소

NTIA는 2021년 7월 12일 그 최소 요소를 발표했습니다 <cite data-ref="3"></cite>. 앞에서 본 일곱 필드, 자동화 지원, 관행과 절차가 내용입니다. 문서는 이것이 지금 시점의 최소일 뿐이고 조직과 기관이 더 많이 요구할 수 있다고 분명히 적었습니다. 형식으로는 SPDX, CycloneDX, SWID 태그를 나란히 들었습니다 <cite data-ref="3"></cite>. 특정 형식을 고른 문서가 아니라, 어떤 형식으로 만들든 갖춰야 할 최소한을 정한 문서입니다.

### 의료기기 SBOM 의무화

법률이 SBOM 제출을 직접 요구한 분야로는 의료기기가 있습니다. 2022년 12월 29일 서명된 2023 통합세출법(Consolidated Appropriations Act, 2023)이 미국 연방 식품·의약품·화장품법(FD&C Act)에 524B조를 새로 넣었습니다 <cite data-ref="31"></cite>. 미국 법전에는 21 U.S.C. 360n-2로 실린 조항입니다. 이 조항에 따라 「사이버 기기」의 시판 전 신청서를 내는 스폰서는 상용, 오픈소스, 기성품 소프트웨어 구성요소를 포함한 SBOM을 제출해야 합니다. 사이버 기기란 스폰서가 검증·설치·승인한 소프트웨어를 포함하고, 인터넷에 연결할 수 있으며, 사이버보안 위협에 취약할 수 있는 기술적 특성을 지닌 기기를 말합니다 <cite data-ref="32"></cite>. 요건은 2023년 3월 29일부터 효력을 가졌습니다. 다만 FDA는 2023년 10월 1일 전까지는 이 요건만을 이유로 서류를 접수 거부(RTA)하는 일은 대체로 하지 않고, 보완 절차에서 신청자와 함께 다루겠다고 밝혔습니다 <cite data-ref="31"></cite>.

### EU 사이버 복원력법과 CISA 개정판

EU는 SBOM 작성을 아예 법률에 넣었습니다. 2024년 11월 20일 관보에 실린 사이버 복원력법(CRA)에 따라 디지털 요소를 가진 제품의 제조사는 제품의 취약점과 구성요소를 식별하고 문서로 남겨야 합니다. 여기에는 널리 쓰이는 기계 판독 형식으로 적어도 최상위 의존성까지 담은 SBOM 작성이 포함됩니다. 법은 관보 게재 20일 뒤 발효했고, 의무 대부분은 2027년 12월 11일부터 적용됩니다. 그보다 먼저 적용되는 조항 가운데 하나가 제14조의 보고 의무입니다. 실제로 악용된 취약점이나 제품 보안에 영향을 주는 중대 사고를 알게 되면 24시간 안에 조기 경보를 해야 하고, 이 조항은 2026년 9월 11일부터 적용되고 있습니다 <cite data-ref="33"></cite>. 제14조가 SBOM을 요구하지는 않습니다. 하지만 무엇이 들었는지 모르는 제조사가 24시간 안에 자기 제품이 영향을 받는지 판단하기는 어렵습니다. 보고 의무가 SBOM 준비를 앞당기는 압력으로 작용할 것으로 봅니다.

미국에서는 CISA가 2025년 8월 22일 최소 요소 개정 초안을 공개해 의견을 받았고, 2026년 7월 29일 13개국 기관과 함께 개정판을 냈습니다. 한국에서는 국가정보원 국가사이버안보센터와 한국인터넷진흥원(KISA)이 공동 작성 기관에 이름을 올렸습니다. 개정판은 모든 소프트웨어에 적용됩니다. 다만 AI 시스템이나 클라우드 환경의 서비스형 소프트웨어(SaaS)에는 요소가 더 필요할 수 있다고 적었습니다. AI용 요소는 개정판에 넣지 않고, CISA와 G7 파트너들이 2026년 5월 따로 낸 지침을 보라고 했습니다 <cite data-ref="5"></cite>. G7 사이버보안 실무그룹이 쓴 「Software Bill of Materials (SBOM) for Artificial Intelligence – Minimum Elements」입니다 <cite data-ref="34"></cite>.

## 한국은 어디까지 왔었나

### SW 공급망 보안 가이드라인 1.0

2024년 5월 과학기술정보통신부(한국인터넷진흥원), 국가정보원, 디지털플랫폼정부위원회가 함께 「소프트웨어(SW) 공급망 보안 가이드라인 1.0」을 냈습니다. KISA 배포 공지의 설명으로는, 퍼지고 있는 SW 공급망 사이버보안 위험과 "미국·유럽 등 해외 주요국의 SW 구성요소 명세서(SBOM) 제출 의무화 등"에 대응해 정부·공공기관·기업이 스스로 공급망 보안을 관리할 역량을 갖추게 하려고 만든 문서입니다. 공지에는 "업무에 참고하시기 바랍니다"라고 적혀 있습니다 <cite data-ref="24"></cite>. 지켜야 하는 규정이 아니라 참고하라는 지침입니다.

### SW 공급망 보안 로드맵

2026년 6월 24일 과학기술정보통신부와 국가정보원은 관계부처 합동 「AI 일상화 시대를 준비하는 SW 공급망 보안 강화 로드맵」을 공개했습니다. 전략은 셋으로, 공급망 위협 예방 역량 강화, 공급망 위협 신속 탐지·대응 체계 마련, 정책·제도적 기반 조성입니다 <cite data-ref="4"></cite>. SBOM은 세 전략 모두에 들어 있습니다. 예방 쪽에는 기업이 스스로 SW 구성요소를 SBOM으로 관리하게 하는 SBOM 기반 관리 모델 확산(2026년부터), SBOM의 정확도와 적용 범위를 검증하는 기술의 개발과 실증, SBOM에 담긴 취약점 같은 민감정보를 기업끼리 안전하게 주고받는 관리 방안 연구가 있습니다. 탐지·대응 쪽에는 공공분야에 조달되는 SW를 위한 SBOM 관리체계와 통합 관리 시스템 구축(2026년부터)이, 제도 쪽에는 공공분야 지침과 보안적합성 검증에 SBOM 제출을 넣는 일(2027년부터)이 잡혀 있습니다 <cite data-ref="4"></cite>.

### 의무인가 권고인가

아직은 대부분 권고이거나 "할 수 있다"에 머뭅니다. 공공 분야만큼은 SBOM 제출을 제도로 만드는 일정이 나와 있습니다.

정부는 2025년 10월 22일 관계부처 합동 「범부처 정보보호 종합대책」을 발표하면서, 공공분야에 쓰이는 IT 시스템·제품의 SW 구성요소(SBOM) 제출을 2027년까지 제도화하고 보안 문제가 발견된 IT 제품은 공공 조달 도입 제한을 추진한다고 밝혔습니다 <cite data-ref="26"></cite>. 공공분야 SBOM 제출을 어떻게 도입할지는 2026년 6월 로드맵에 나옵니다. 2026년부터는 해외 SBOM 요구사항과 표준화 동향을 고려해 공공분야 SBOM 항목을 최소한으로 뽑아 표준화하고, 국가·공공기관이 도입하는 SW 제품의 SBOM을 등록·관리하는 공공분야 SBOM 통합 관리 시스템을 만듭니다. 2027년부터는 보안기능 시험을 신청한 SW 제품으로 SBOM 생성·검증 체계를 실증하고, 공공 정보화사업의 보안 요구사항과 사이버보안 관련 지침에 SBOM 제출을 넣습니다. 공공분야에 도입되는 제품의 보안적합성 검증에서도 보안취약점 추적·관리를 위한 SBOM 제출과 '안전한 SW 개발 방법론' 준수 여부 등을 확인합니다. 공공분야 관리체계와 지침은 국가정보원과 행정안전부가, 보안적합성 검증 제도 개선은 국가정보원이 맡습니다 <cite data-ref="4"></cite>. 로드맵이 SBOM 제출의 수단으로 든 것은 지침 개정과 검증 제도 개선이고, 공공분야 SBOM에 들어갈 항목은 2026년부터 뽑아내는 과제로 잡혀 있습니다 <cite data-ref="4"></cite>.

의료기기는 조문만 나란히 놓아도 차이가 보입니다. 미국 법은 사이버 기기 신청자에게 SBOM을 제출하라고 합니다 <cite data-ref="32"></cite>. 식품의약품안전처가 2025년 4월 고시한 「디지털의료기기 전자적 침해행위 보안지침」 제16조는 다릅니다. 제조업자 등은 취약점 발견과 침해사고 대응에 소프트웨어 구성요소 명세서를 "활용할 수 있다", 의료서비스 제공자는 구매·설치 전에 이를 확인하는 것을 "고려할 수 있다"고 적혀 있습니다 <cite data-ref="25"></cite>.

| 지역·분야 | 요구하는 것 | 근거 | 시점 |
|---|---|---|---|
| 미국 연방 조달 | 기관이 원하면 계약으로 SBOM 요구 가능 | OMB M-26-05 <cite data-ref="30"></cite> | 2026년 1월 |
| 미국 의료기기 | 사이버 기기 시판 전 신청 시 SBOM 제출 | FD&C Act 524B조, 21 U.S.C. 360n-2 <cite data-ref="32"></cite> | 2023년 3월 |
| EU | 제조사의 SBOM 작성(최소 최상위 의존성) | 사이버 복원력법 <cite data-ref="33"></cite> | 2027년 12월 |
| 한국 공공 | SBOM 제출 제도화, 보안적합성 검증 연계 | 범부처 정보보호 종합대책 <cite data-ref="26"></cite>, SW 공급망 보안 강화 로드맵 <cite data-ref="4"></cite> | 2027년(계획) |
| 한국 의료기기 | 명세서 활용·확인을 "할 수 있다"로 규정 | 디지털의료기기 전자적 침해행위 보안지침 제16조 <cite data-ref="25"></cite> | 2025년 4월 |
| 한국 일반 | 참고용 가이드라인 | SW 공급망 보안 가이드라인 1.0 <cite data-ref="24"></cite> | 2024년 5월 |

법보다 거래 조건이 먼저 움직일 수도 있습니다. 미국 OMB는 기관이 원하면 SBOM을 계약 조건으로 요구할 수 있게 했고 <cite data-ref="30"></cite>, 한국에서는 SK텔레콤이 공급사의 SBOM 제출 요구사항과 허용 형식을 공개해 두었습니다 <cite data-ref="11"></cite>. 발주처가 계약서에 넣으면 공급사는 법이 없어도 SBOM을 만들어야 합니다.

### 한국의 사정

한국에는 금융 서비스를 쓰려면 PC에 먼저 깔아야 하는 보안 프로그램들이 있습니다. USENIX Security 2025에 실린 연구는 이 묶음을 KSA 2.0(Korea Security Applications 2.0)이라고 부릅니다. 연구에 따르면 KSA 2.0은 10년 넘게 한국 금융 서비스에서 의무로 쓰였고, 그 결과 전국 PC에 거의 다 깔려 있습니다 <cite data-ref="35"></cite>. 설문에 응한 400명을 보면 은행 서비스 이용자의 97%가 이 프로그램을 설치했지만, 59%는 이 프로그램이 무슨 일을 하는지 이해하지 못했습니다. 48명의 PC를 분석했더니 한 사람당 평균 9개가 깔려 있었고, 2022년이나 그 전에 나온 낡은 버전도 많았습니다. 연구를 시작한 계기는 2023년 북한이 이 프로그램을 악용한 실제 해킹 사건이었습니다 <cite data-ref="35"></cite>.

고치기도 지우기도 쉽지 않습니다. 연구에 따르면 KSA를 패치하려면 프로그램만이 아니라 서비스를 제공하는 웹사이트마다 JavaScript 코드까지 바꿔야 합니다 <cite data-ref="35"></cite>. 연구가 조사한 KSA 가운데 두 개를 빼면 모두 삭제할 때 자기가 설치한 루트 인증서를 지우지 않았습니다. 불완전한 삭제와 업데이트 없이 남은 낡은 버전이 겹쳐, 이용자의 86.5%는 삭제를 시도한 뒤에도 잠재적 보안 위험에 노출돼 있다는 것이 연구 결과입니다 <cite data-ref="35"></cite>.

정부는 2025년 10월 종합대책에서 금융·공공기관 등이 소비자에게 설치를 강요하는 보안 SW를 2026년부터 단계적으로 제한하고, 대신 다중 인증과 AI 기반 이상 탐지 같은 수단으로 보안을 강화하겠다고 했습니다 <cite data-ref="26"></cite>.

### 한국만의 문제일까

같은 연구는 이런 일이 한국에만 있지는 않다고 짚습니다. 문제가 될 수 있는 소프트웨어를 의무로 깔게 하려는 시도로 중국, 카자흐스탄, 러시아를 들었습니다 <cite data-ref="35"></cite>. 논문이 말하는 러시아 사례는 「주권 인터넷법」이고, 아래 표의 러시아 행은 그와 다른 조치입니다 <cite data-ref="35"></cite>.

사례를 모아 보면 두 갈래입니다. 하나는 정부가 나서서 이용자의 기기에 소프트웨어나 인증서를 깔게 했거나 깔게 하려 한 경우이고, 다른 하나는 은행 같은 기관이 자기 서비스를 쓰는 이용자에게 깔게 한 경우입니다.

#### 정부가 나선 경우

| 나라 | 설치하게 한 것 | 내세운 이유 | 그 뒤 |
|---|---|---|---|
| 중국(2009) | 중국에서 생산·판매하거나 수입해 파는 컴퓨터에 필터링 소프트웨어 「绿坝-花季护航(Green Dam Youth Escort)」 사전 설치 <cite data-ref="36"></cite> | 청소년을 음란물 같은 유해 정보에서 보호 <cite data-ref="36"></cite> | 웹사이트만 열어도 PC를 장악당하는 취약점이 보고됨 <cite data-ref="37"></cite>. 일반 PC 사전 설치는 연기하고 학교·PC방 설치는 계속한다고 발표 <cite data-ref="36"></cite>. USENIX 연구는 그해 의무를 거둬들였다고 기록 <cite data-ref="35"></cite> |
| 카자흐스탄(2019, 2020) | 모든 기기와 브라우저에 정부 루트 인증서 <cite data-ref="38"></cite> <cite data-ref="39"></cite> | "보안". 인터넷 사업자의 안내로는 사기·해킹·불법 콘텐츠 방지 <cite data-ref="38"></cite> | 정부가 "시범"이라 부른 HTTPS 감청에 쓰임 <cite data-ref="38"></cite>. 주요 브라우저가 이 인증서를 믿지 않도록 차단 <cite data-ref="40"></cite> <cite data-ref="41"></cite> <cite data-ref="39"></cite> |
| 인도(2025) | 모든 스마트폰에 사이버 보안 앱 「Sanchar Saathi」 사전 설치 <cite data-ref="42"></cite> | 모든 시민에게 사이버 보안 제공 <cite data-ref="42"></cite> | 2025년 12월 3일 제조사의 사전 설치 의무 철회 <cite data-ref="42"></cite> |
| 러시아(2025~) | 의무 사전 설치 프로그램 목록에 디지털 플랫폼 「Max」를 넣음. 2023년부터 목록에 있던 VK 메신저를 대신함 <cite data-ref="43"></cite> | 안전한 메신저, 정부·기업 디지털 서비스 이용 <cite data-ref="43"></cite> | 2025년 9월 1일부터 시행 <cite data-ref="43"></cite> |

중국 공업정보화부는 2009년 6월 30일 일반 PC 사전 설치를 미루면서도 학교와 PC방에는 계속 깔겠다고 했고 <cite data-ref="36"></cite>, USENIX 연구는 중국이 그해 보안 결함 때문에 의무를 거둬들였다고 적었습니다 <cite data-ref="35"></cite>. 인도는 제조사의 사전 설치 의무를 철회했고 <cite data-ref="42"></cite>, 카자흐스탄 인증서는 브라우저 회사들이 막았습니다 <cite data-ref="40"></cite> <cite data-ref="41"></cite> <cite data-ref="39"></cite>. 러시아는 2025년 9월 1일부터 시행에 들어갔습니다 <cite data-ref="43"></cite>. 중국에서는 미루기 전에 이미 깔린 것도 많았습니다. 공업정보화부 발표로는 2009년 5월 말 Green Dam이 학교 컴퓨터 261.8만 대, PC방 컴퓨터 469.92만 대에 깔려 있었습니다 <cite data-ref="36"></cite>.

#### 기관이 서비스 이용 조건으로 건 경우

| 나라 | 설치하게 한 것 | 내세운 이유 | 그 뒤 |
|---|---|---|---|
| 브라질(Banco do Brasil) | 이 은행의 PC 인터넷 뱅킹을 쓰는 고객에게 은행이 배포하는 보안 모듈 <cite data-ref="44"></cite> | 인터넷 뱅킹의 안전한 이용 <cite data-ref="44"></cite> | 2026년 4월 수정된 은행 안내에서도 설치 요구 <cite data-ref="44"></cite> |
| 한국 | 금융 서비스용 보안 프로그램 묶음(KSA 2.0) <cite data-ref="35"></cite> | 금융·공공 온라인 서비스 보안 <cite data-ref="35"></cite> | 2023년 북한이 악용 <cite data-ref="35"></cite>. 2026년부터 단계적 제한 추진 <cite data-ref="26"></cite> |

이쪽은 서비스를 쓰려면 깔아야 합니다. Banco do Brasil은 PC로 인터넷 뱅킹을 하려면 고객이 보안 모듈을 설치해야 한다고 안내하고 <cite data-ref="44"></cite>, 한국의 KSA도 금융 서비스에서 의무로 쓰였습니다. 다만 연구는 KSA가 이만큼 퍼진 데는 과거의 법령과 금융기관의 엄격한 요구가 함께 작용했다고 봅니다 <cite data-ref="35"></cite>. 한국은 정부와 기관이 함께 만든 경우에 가깝습니다 <cite data-ref="35"></cite> <cite data-ref="26"></cite>.

어느 갈래든 이용자가 고르지 않은 소프트웨어나 인증서를 넓게 깔게 하려 했습니다. 그렇게 깔린 것에 문제가 생기면 영향도 그만큼 넓게 번질 수 있습니다. 카자흐스탄 인증서는 브라우저 회사들이 막았고, Chrome 사용자는 따로 손쓸 일이 없었습니다 <cite data-ref="41"></cite>. KSA는 사정이 다릅니다. 브라우저 생태계에 속하지 않아 브라우저의 보호를 받지 못합니다 <cite data-ref="35"></cite>. 앞에서 본 패치와 삭제 문제까지 생각하면, KSA를 걷어내는 일은 설치된 PC를 하나씩 찾아 고치는 일이 될 것으로 봅니다. 게다가 한국은 이 프로그램이 쓰인 기간이 깁니다. 10년 넘게 금융 서비스의 이용 조건이었고, 그동안 한 사람의 PC에 여러 개가 쌓였습니다 <cite data-ref="35"></cite>.

공급사가 만든 SBOM은 그 프로그램 안에 무엇이 들었는지 알려 줍니다. 그 프로그램이 어느 PC에 몇 버전으로 깔려 있는지는 알려 주지 않습니다. 그건 쓰는 쪽이 따로 파악해야 합니다. 2023년 국가정보원과 영국 NCSC의 합동 권고문도 시스템 소유자에게 설치된 프로그램 목록에서 취약한 버전을 찾아 최신 버전으로 올리라고 권했습니다 <cite data-ref="45"></cite>. 이런 환경이라면 SBOM은 납품 서류로 끝나서는 안 되고, 어디에 몇 버전이 깔렸는지와 이어져 있어야 쓸모가 있습니다.

## 실제 공격 사례

### 3CX

2023년 3월 기업용 통신 소프트웨어 3CX의 데스크톱 앱이 악성 코드를 품은 채 배포됐습니다. 이 문제에는 CVE-2023-29059가 붙었습니다. 조사를 맡은 Mandiant에 따르면 공격자가 3CX 네트워크에 처음 들어온 길은 Trading Technologies 웹사이트에서 내려받은 악성 소프트웨어였습니다. Mandiant는 소프트웨어 공급망 공격이 또 다른 공급망 공격으로 이어진 것을 본 것은 이번이 처음이라고 했습니다 <cite data-ref="46"></cite>. 변조된 것은 금융 거래 소프트웨어 X_TRADER의 설치 파일이었고, 여기에는 Trading Technologies 명의의 인증서 서명이 붙어 있었습니다. X_TRADER는 2020년에 단종된 것으로 알려졌는데도 2022년에 여전히 정상 웹사이트에서 받을 수 있었습니다. Mandiant는 이 활동을 북한과 연계된 것으로 의심되는 UNC4736으로 추적했습니다 <cite data-ref="46"></cite>.

그다음 이야기는 3CX가 공개한 Mandiant 조사 결과에 있습니다. 2022년 한 직원이 개인 컴퓨터에 X_TRADER를 설치했고, Mandiant는 공격자가 그 컴퓨터에서 직원의 3CX 회사 계정 정보를 훔친 것으로 봤습니다. 3CX 내부에서 찾은 가장 이른 침해 흔적은, 직원 PC가 감염되고 이틀 뒤 그 계정으로 VPN에 접속한 기록이었습니다. 공격자는 계정 정보를 더 모으며 내부를 옮겨 다녔고, 결국 Windows와 macOS 빌드 환경을 둘 다 장악했습니다 <cite data-ref="47"></cite>. MITRE ATT&CK는 이 사건을 캠페인 C0057로 정리해 T1195.002의 사례로 올려 두었습니다.

### xz-utils

2024년 3월 29일 Andres Freund가 oss-security 메일링 리스트에 xz/liblzma에 백도어가 있다고 알렸습니다. Debian sid에서 ssh 로그인이 CPU를 많이 쓰고 valgrind 오류가 나는 이상한 증상을 쫓다가 찾아낸 것입니다 <cite data-ref="48"></cite>. 처음에는 Debian 패키지가 문제인 줄 알았지만, 백도어는 상위(upstream) 저장소와 배포용 압축 파일에 들어 있었습니다. 일부는 배포된 압축 파일에만 있었고, 5.6.0과 5.6.1의 압축 파일이 여기에 해당했습니다. OpenSSH는 liblzma를 직접 쓰지 않습니다. 그런데 Debian을 비롯한 여러 배포판이 systemd 알림을 위해 OpenSSH에 패치를 넣었고, 그 패치가 쓰는 libsystemd가 lzma에 기댔습니다. 백도어는 이 경로로 sshd까지 닿았습니다 <cite data-ref="48"></cite>. 취약점 번호는 CVE-2024-3094입니다. ATT&CK 기법 페이지에는 xz 사례가 올라 있지 않지만, 최종 사용자에게 닿기 전에 의존성을 조작했으니 T1195.001로 분류할 수 있다고 봅니다.

### MagicLine4NX

2023년 11월 23일 국가정보원과 영국 국가사이버보안센터(NCSC)가 합동 권고문을 냈습니다. 북한과 연계된 사이버 행위자들이 소프트웨어 공급망을 노리고 있다는 내용입니다 <cite data-ref="49"></cite> <cite data-ref="45"></cite>. 첫 번째 사례에서 공격자는 2023년 3월 보안 인증 프로그램과 망연계 시스템의 취약점을 차례로 이용해 한 기관의 내부망까지 들어갔습니다. 시작은 한 언론사 웹사이트였습니다. 공격자는 이 사이트를 장악해 기사에 악성 스크립트를 심고, 특정 IP 대역에서 접속할 때만 동작하게 했습니다. 취약한 보안 인증 프로그램 MagicLine4NX가 깔린 인터넷 PC에서 그 기사를 열면, MagicLine4NX가 악성 코드를 실행했습니다 <cite data-ref="45"></cite>. 다음에는 망연계 시스템의 제로데이 취약점으로 인터넷 쪽 서버에 들어갔고, 망연계 시스템의 데이터 동기화 기능을 이용해 업무망 서버로 악성 코드를 퍼뜨렸습니다. 업무망 PC에 심긴 악성 코드가 바깥 C2 서버로 신호를 보내려 하자, 이번에는 망연계 솔루션의 보안 정책이 이를 막았습니다 <cite data-ref="45"></cite>.

권고문은 이 사건을 한 공급망의 침해가 다른 공급망의 감염으로 이어진 표적 공격으로 정리했고, 취약한 버전이 MagicLine4NX 1.0.0.1부터 1.0.0.26까지라고 밝혔습니다 <cite data-ref="45"></cite>. 인터넷망과 업무망을 갈라 둔 환경이었는데, 공격자는 인터넷 PC에 깔린 보안 인증 프로그램과 두 망 사이에서 데이터를 동기화하는 시스템을 차례로 이용해 그 경계를 넘었습니다.

## 만약 SBOM이 있었다면

오른쪽 두 칸은 앞의 사건 기록을 보고 내린 판단입니다.

| 사건 | 들어온 길 | SBOM으로 할 수 있었던 것 | SBOM으로는 못 하는 것 |
|---|---|---|---|
| Log4Shell | 널리 쓰이고 다른 구성요소 안에 자주 묻히는 라이브러리의 취약점 <cite data-ref="1"></cite> | 어느 시스템에 log4j-core 몇 버전이 들었는지 찾기 | 생성 도구가 놓친 사본은 SBOM에도 없음 <cite data-ref="50"></cite> |
| SolarWinds | 서명된 정상 업데이트에 섞인 악성 코드 <cite data-ref="27"></cite> | 영향받는 Orion 버전이 깔린 곳 찾기 | 서명된 업데이트 안의 악성 코드 알아보기 |
| 3CX | 다른 회사 소프트웨어를 거친 빌드 환경 침해 <cite data-ref="46"></cite> <cite data-ref="47"></cite> | 설치된 3CX 버전으로 대응 범위 정하기 | 서명된 설치 파일이 악성이라는 사실, 직원 개인 PC에 깔린 단종 소프트웨어 |
| xz-utils | 배포용 압축 파일에 숨은 백도어 <cite data-ref="48"></cite> | 5.6.0·5.6.1이 깔린 시스템 찾기 | 백도어가 있다는 사실 |
| MagicLine4NX | 보안 인증 프로그램 취약점과 망연계 시스템 제로데이 <cite data-ref="45"></cite> | 기관 PC에 깔린 MagicLine4NX 버전 파악 | 공개되지 않은 망연계 시스템 제로데이 |

다섯 사건 모두에서 SBOM이 해 줄 수 있었던 일은 하나입니다. 사건이 알려진 다음 "우리도 해당되는가"에 빨리 답하는 것입니다. 사건이 알려지기 전에 침해를 먼저 찾아내는 일은 다섯 사건 어디에서도 SBOM이 한 일이 아니었습니다. xz-utils의 백도어도 목록이 아니라 이상하게 느려진 ssh 로그인과 valgrind 오류에서 드러났습니다 <cite data-ref="48"></cite>.

Log4j 때 CSRB가 만난 대표 단체들 가운데 SBOM으로 취약한 배포를 찾았다고 보고한 곳은 없었습니다. 위원회는 필드 설명이 제각각이고 버전 정보가 빠지며 받는 쪽에서 자동으로 처리하지 못한다는 한계를 예로 들었습니다. 그러면서도 권고 12에서는 소프트웨어 개발자가 SBOM을 만들어 소프트웨어와 함께 내놓으라고 했습니다 <cite data-ref="1"></cite>. 2026년 개정판은 받는 쪽이 SBOM 데이터가 정확하리라고 기대해도 된다고 쓰고 작성자 서명을 넣었지만, 정확성과 완전성을 확인하는 일은 최소 요소 밖에 남겨 두었습니다 <cite data-ref="5"></cite>. 또 SBOM은 취약한 구성요소가 들어 있다는 데까지만 말해 줍니다. 제품이 그 취약점의 영향을 실제로 받는지는 VEX 같은 별도 문서가 알려야 합니다. CISA의 정의로 VEX는 소프트웨어 제품이나 구성요소가 특정 취약점에 대해 어떤 상태인지 알리는 문서이고, 흔한 쓰임 하나가 영향을 받는지 아닌지 밝히는 것입니다 <cite data-ref="51"></cite>.

## 아직 해결하지 못한 미해결 문제

같은 대상을 넣어도 도구마다 다른 SBOM이 나옵니다 <cite data-ref="52"></cite>. 컨테이너 이미지 20개로 SBOM을 비교한 실증 연구를 보면, 운영체제 패키지(deb)의 식별자(PURL) 표기 차이 때문에 정규화하기 전에는 비교 지표가 매우 낮았고 정규화한 뒤에야 F1 점수가 0.98 이상으로 올라갔습니다 <cite data-ref="50"></cite>. 파이썬 쪽에서는 생성 도구가 구성요소와 의존성을 부정확하게 잡는 바람에, 그 SBOM을 받아 쓰는 취약점 탐지 도구의 결과까지 영향을 받았습니다 <cite data-ref="53"></cite>. 여러 도구의 결과를 합쳐 보는 연구에서는 Trivy와 GitHub Dependency Graph가 SPDX 필수·선택 필드의 59~61%를 비워 두었습니다 <cite data-ref="52"></cite>. 한국 로드맵도 SBOM의 정확도와 적용 범위를 검증하는 기술을 2026년부터 개발·실증할 과제로 잡았습니다 <cite data-ref="4"></cite>.

Java SBOM 25,882개를 해당 JAR 파일과 맞춰 본 연구에서는 7,907개가 직접 의존성을 밝히지 않았습니다. 빠진 의존성 가운데 4.97%는 취약한 것이었습니다 <cite data-ref="54"></cite>.

앞의 컨테이너 연구는 공유 라이브러리(.so)도 따로 들여다봤습니다. 패키지 관리자에 기대 만든 SBOM은 동적으로 불러오는 모듈 같은 파일 단위 구성요소를 자주 놓쳤습니다 <cite data-ref="50"></cite>. 2026년 개정판도 SBOM에 없는 구성요소를 찾는 수단으로 바이너리 분석 도구를 꼽았습니다 <cite data-ref="5"></cite>.

취약한 버전이 들어 있다고 해서 곧바로 위험하다는 뜻은 아닙니다. 영향 여부를 알리는 형식으로는 VEX가 있지만 <cite data-ref="51"></cite>, 국내 실증에서 세 기업이 만든 VEX 문서는 발견한 취약점을 모두 "조사 중(Under-Investigation)"으로 분류했습니다 <cite data-ref="55"></cite>. 형식은 갖췄지만 영향이 있는지 없는지에 대한 판단은 하나도 담기지 않았습니다.

SBOM은 공격자에게도 무엇을 노리면 되는지 알려 줄 수 있습니다. NTIA는 이론적으로는 그렇다고 인정하면서도, 방어하는 쪽이 얻는 이익이 훨씬 크고 공격자는 SBOM이 없어도 공격한다고 반박했습니다 <cite data-ref="14"></cite>. 기업과 규제 산업의 소프트웨어 공급사는 지식재산이나 취약점 정보 때문에 SBOM을 볼 수 있는 사람을 제한하고 싶어 합니다. 그래서 기밀을 지켜야 하는 SBOM은 지금 라이선스나 비밀유지계약 같은 계약 절차, 아니면 접근을 막아 둔 저장소를 통해 오갑니다 <cite data-ref="56"></cite>. 이런 방식으로는 규모를 키우기도, 회사끼리 호환되게 쓰기도 어렵습니다. 일부를 가린 SBOM을 호환되게 주고받으면서 그 무결성을 암호학적으로 감사할 수 있게 하는 방법은 아직 연구 단계입니다 <cite data-ref="56"></cite>. 한국 로드맵도 SBOM에 담긴 취약점 같은 민감정보를 기업끼리 안전하게 주고받는 관리 방안을 연구 과제로 올렸습니다 <cite data-ref="4"></cite>.

AI용 요소는 2026년 개정판에도 들어가지 않았습니다. 개정판은 AI 시스템과 SaaS에는 요소가 더 필요할 수 있다고 적었습니다 <cite data-ref="5"></cite>. 2026년 5월 나온 G7의 AI용 SBOM 최소 요소는 망라적이지 않고 의무도 아니며 새 요구사항이나 표준, 법을 만들지 않는다고 스스로 밝혔고, 기술 발전과 각국 법·정책에 맞춰 더 다듬을 여지도 남겨 두었습니다 <cite data-ref="34"></cite>. 클라우드에 대해서는 OMB가, 기관이 SBOM 계약 조건을 둔다면 클라우드 플랫폼에는 운영 중인 실행 환경의 SBOM을 요청하라고 적었습니다 <cite data-ref="30"></cite>.

한국은 일정은 나왔지만 세부 내용은 아직 만드는 중입니다. 정부는 공공분야 IT 시스템·제품의 SBOM 제출을 2027년까지 제도화하겠다고 했고 <cite data-ref="26"></cite>, 로드맵은 공공분야 지침과 보안적합성 검증에 SBOM 제출을 넣는 시점을 2027년으로 잡았습니다. 공공분야 SBOM에 어떤 항목을 적어야 할지는 2026년부터 뽑아내는 과제로 남아 있고, 민간 분야의 공급망 보안 검증은 2027년 자율 신청 시범 운영으로 시작합니다 <cite data-ref="4"></cite>.

<div class="remark" data-label="작성 도움" data-date="2026-10-04" markdown="1">
이 글은 AI(Claude Opus 5.5)의 도움을 받아 작성했습니다. 자료 조사와 초안 작성, 본문 주장과 참고자료 원문의 대조에 AI를 썼습니다.
</div>
