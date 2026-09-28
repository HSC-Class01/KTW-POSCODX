# POSCO DX DART Financial Analysis Agent

포스코DX의 DART 정기보고서(사업보고서/반기보고서/분기보고서)를 수집하고 주요 재무수치와 재무비율을 계산하여 GitHub Pages 대시보드로 보여주는 프로젝트입니다.

Repository: https://github.com/HSC-Class01/KTW-POSCODX.git

## 데이터 범위
- 목표 시작연도: 2010
- 보고서: 사업보고서, 반기보고서, 1분기보고서, 3분기보고서
- 2015년 이후: OpenDART 재무제표 API를 통한 자동 수치 수집
- 2010~2014년: OpenDART 공시검색 API로 정기보고서 접수정보를 수집하고, 별도 레거시 원문 파서/수동 보정 영역을 유지
- 회사: 포스코DX (DART/영문 DART 회사코드 022100; OpenDART API에서는 8자리 corp_code가 필요)

## 주요 재무수치
- 매출액
- 영업이익
- 당기순이익
- 자산총계
- 부채총계
- 자본총계
- 유동자산
- 유동부채
- 현금및현금성자산
- 영업활동현금흐름

## 재무비율
- 영업이익률
- 순이익률
- ROA
- ROE
- 부채비율
- 자기자본비율
- 유동비율
- 매출액 증가율
- 영업이익 증가율
- 당기순이익 증가율
- 총자산회전율

## API 설정
1. OpenDART에서 API 인증키를 발급합니다.
2. GitHub Repository → Settings → Secrets and variables → Actions → New repository secret
3. 이름: `DART_API_KEY`
4. 값: 발급받은 40자리 API key
5. 로컬에서는 `.env` 파일 대신 환경변수 `DART_API_KEY`를 사용하세요.

API key를 소스코드, CSV, README에 직접 입력하지 마세요.

## 로컬 실행
```bash
python -m pip install -r requirements.txt
export DART_API_KEY="YOUR_KEY"
python src/update_data.py
python src/analyze.py
```

Windows PowerShell:
```powershell
$env:DART_API_KEY="YOUR_KEY"
python src/update_data.py
python src/analyze.py
```

대시보드:
`dashboard/index.html`을 브라우저에서 열거나 GitHub Pages로 배포합니다.

## GitHub Actions 설치
ZIP에는 숨김파일을 넣지 않았습니다. 따라서 `github_actions/deploy_and_update.yml`을 아래 경로로 GitHub에 업로드하세요.

`.github/workflows/deploy_and_update.yml`

그 후 GitHub Actions가
1. 매월 1일 03:00 UTC에 DART 데이터를 업데이트
2. 데이터 분석
3. 변경사항을 main에 커밋
4. GitHub Pages를 재배포
하도록 동작합니다.

GitHub Pages 설정:
Settings → Pages → Build and deployment → Source: GitHub Actions

## 주의
GitHub Pages는 공개 웹사이트이므로 API key와 개인정보/비공개 원문을 대시보드에 넣지 마세요.
