# OpenDART API Key 안내

1. OpenDART 접속: https://opendart.fss.or.kr/
2. 회원가입/로그인 후 API 인증키 발급 메뉴에서 인증키를 발급합니다.
3. 발급받은 40자리 키를 GitHub에 직접 코드로 넣지 않습니다.
4. Repository → Settings → Secrets and variables → Actions → New repository secret
5. Secret name: DART_API_KEY
6. Secret value: 발급받은 API key

로컬 실행:
- macOS/Linux: `export DART_API_KEY="발급키"`
- PowerShell: `$env:DART_API_KEY="발급키"`

참고: OpenDART API는 `crtfc_key`, `corp_code`, `bsns_year`, `reprt_code`, `fs_div` 등을 이용해 재무자료를 조회합니다.
