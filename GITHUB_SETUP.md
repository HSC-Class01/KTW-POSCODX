# GitHub 설정 순서

## 1. ZIP 업로드
ZIP을 풀고 모든 파일을 `KTW-POSCODX` repository의 main 브랜치에 업로드합니다.

## 2. Actions workflow 이동
ZIP에는 숨김폴더가 없기 때문에 `github_actions/deploy_and_update.yml`을 다음 경로로 이동/업로드해야 합니다.

`.github/workflows/deploy_and_update.yml`

GitHub 웹에서:
Add file → Create new file → 파일명에 `.github/workflows/deploy_and_update.yml`
→ `github_actions/deploy_and_update.yml`의 내용을 붙여넣고 commit.

## 3. DART API Key 등록
Settings → Secrets and variables → Actions → New repository secret

Name:
`DART_API_KEY`

Secret:
OpenDART에서 발급받은 40자리 인증키

## 4. Pages 활성화
Settings → Pages → Build and deployment → Source → GitHub Actions

## 5. 실행
Actions → DART update and GitHub Pages deploy → Run workflow

이후 매월 1일 자동 실행됩니다.
