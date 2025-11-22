# Claude Code 프롬프트 가이드라인

이 문서는 Claude Code와 효과적으로 작업하기 위한 프롬프트 작성 모범 사례를 제공합니다.

## 목차

- [CLAUDE.md 파일 개요](#claudemd-파일-개요)
- [프롬프트 작성 모범 사례](#프롬프트-작성-모범-사례)
- [CLAUDE.md 파일 구조](#claudemd-파일-구조)
- [구체적인 프롬프트 작성법](#구체적인-프롬프트-작성법)
- [보안 모범 사례](#보안-모범-사례)
- [슬래시 커맨드 활용](#슬래시-커맨드-활용)
- [Skills 활용](#skills-활용)
- [추가 리소스](#추가-리소스)

---

## CLAUDE.md 파일 개요

### CLAUDE.md란?

`CLAUDE.md`는 Claude Code가 대화를 시작할 때 자동으로 컨텍스트로 읽어들이는 특별한 마크다운 파일입니다. 프로젝트별 지침, 규칙, 컨벤션을 Claude에게 제공하여 일관된 작업 품질을 유지할 수 있습니다.

### 주요 목적

CLAUDE.md는 다음과 같은 정보를 문서화하기에 이상적입니다:

- **공통 Bash 명령어** - 자주 사용하는 개발/빌드/테스트 명령어
- **핵심 파일 및 유틸리티 함수** - 프로젝트의 주요 파일 구조
- **코드 스타일 가이드라인** - 코딩 컨벤션 및 패턴
- **테스트 지침** - 테스트 작성 및 실행 방법
- **저장소 에티켓** - Git 워크플로우 및 커밋 규칙

---

## 프롬프트 작성 모범 사례

### 1. 구체적이고 명확하게 작성

❌ **나쁜 예:**
```
이 코드를 개선해주세요
```

✅ **좋은 예:**
```
이 함수의 성능을 개선해주세요. 특히:
- 반복문 대신 리스트 컴프리헨션 사용
- 불필요한 중첩 제거
- 타입 힌트 추가
- 100자 줄 길이 제한 준수
```

### 2. 컨텍스트 제공

항상 다음 정보를 포함하세요:
- 사용 중인 프레임워크/라이브러리
- 코딩 스타일 선호사항
- 제약사항 및 요구사항
- 프로젝트의 기존 패턴

### 3. 범위 명확히 정의

명확한 경계를 설정하여 범위 확대를 방지하고 중요한 시스템을 보호하세요.

✅ **좋은 예:**
```
src/api/users.py의 get_user 함수만 수정해주세요.
다른 파일은 건드리지 마세요.
```

### 4. 큰 작업은 체크리스트로 관리

여러 단계가 필요한 큰 작업의 경우, Claude가 마크다운 파일을 체크리스트 및 작업 스크래치패드로 사용하도록 하면 성능이 향상됩니다.

### 5. 예제 제공

Claude 4.x와 같은 고급 모델은 예제의 세부사항에 매우 주의를 기울입니다. 예제가 원하는 동작과 일치하고, 피하고 싶은 패턴을 최소화하도록 하세요.

---

## CLAUDE.md 파일 구조

### 기본 템플릿

```markdown
# CLAUDE.md

## 프로젝트 개요
[프로젝트의 간단한 설명과 목적을 2-3문장으로 작성]

## 기술 스택
- **언어**: [예: Python 3.11+, TypeScript 5.0+, Go 1.21+]
- **프레임워크**: [예: FastAPI, Next.js, Express]
- **주요 라이브러리**: [예: SQLAlchemy, Prisma, GORM]
- **개발 도구**: [예: pytest, jest, golangci-lint]

## 프로젝트 구조
[프로젝트의 주요 디렉터리 구조를 간단히 설명합니다.
각 디렉터리의 역할을 한 줄로 요약하세요.]

## 개발 명령어

### 설치
```bash
# 패키지 매니저에 따라 선택
npm install                # Node.js
pip install -e ".[dev]"    # Python
go mod download            # Go
```

### 실행
```bash
# 개발 서버 시작
npm run dev                # Node.js
python -m src.main         # Python
go run cmd/server/main.go  # Go
```

### 테스트
```bash
# 전체 테스트 실행
npm test                   # Node.js
pytest                     # Python
go test ./...              # Go

# 커버리지 포함
npm run test:coverage      # Node.js
pytest --cov=src           # Python
go test -cover ./...       # Go
```

### 코드 품질
```bash
# 린팅
npm run lint               # Node.js (ESLint)
ruff check src/            # Python (Ruff)
golangci-lint run          # Go

# 포맷팅
npm run format             # Node.js (Prettier)
black src/                 # Python (Black)
gofmt -w .                 # Go
```

## 코드 스타일

### Python 프로젝트 예시
- **줄 길이**: 100자
- **타입 힌트**: 필수
- **독스트링**: Google 스타일
- **임포트 순서**: 표준 라이브러리 → 서드파티 → 로컬

### JavaScript/TypeScript 프로젝트 예시
- **스타일 가이드**: Airbnb
- **들여쓰기**: 2 spaces
- **따옴표**: 싱글 쿼트 사용
- **세미콜론**: 항상 사용

### 공통
- 의미있는 변수명 사용
- 함수는 단일 책임 원칙 준수
- 주석은 "왜"를 설명 ("무엇"이 아님)

## 파일 경계

### 수정 가능
[Claude가 수정할 수 있는 파일/디렉터리 나열]
- 예: 소스 코드, 테스트, 문서, 스크립트 등

### 수정 금지
[절대 수정하면 안 되는 파일/디렉터리 나열]
- 환경 변수 파일 (.env)
- 의존성 잠금 파일 (package-lock.json, yarn.lock, uv.lock 등)
- Git 내부 파일 (.git/)
- 의존성 디렉터리 (node_modules/, venv/, vendor/ 등)
- 빌드 산출물 (dist/, build/ 등)

## 테스트 지침

- **커버리지 목표**: 최소 80%
- **테스트 구조**: Arrange-Act-Assert 패턴
- **네이밍**:
  - Python: `test_<function>_<scenario>`
  - JavaScript: `should <expected behavior> when <scenario>`
  - Go: `Test<Function>_<Scenario>`
- **모킹**: 외부 의존성은 항상 mock 처리
- **통합 테스트**: 별도 디렉터리 또는 표시

## Git 워크플로우

### 브랜치 전략
- `main`: 프로덕션 배포 브랜치
- `develop`: 개발 통합 브랜치
- `feature/*`: 새 기능 개발
- `bugfix/*`: 버그 수정
- `hotfix/*`: 긴급 수정

### 커밋 메시지 형식 (Conventional Commits)
```
<type>(<scope>): <subject>

<body>

<footer>
```

**타입:**
- `feat`: 새 기능
- `fix`: 버그 수정
- `refactor`: 리팩토링
- `docs`: 문서
- `test`: 테스트
- `chore`: 빌드/설정
- `perf`: 성능 개선
- `style`: 코드 스타일 (포맷팅)

**예시:**
```
feat(auth): add OAuth2 login support

Implement OAuth2 authentication flow using Google provider.
Includes token refresh and user profile retrieval.

Closes #123
```

## 환경 설정

### 필수 환경 변수
```bash
# API 설정
API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:pass@localhost/db

# 애플리케이션 설정
APP_ENV=development
LOG_LEVEL=info
```

### 선택 환경 변수
```bash
# 기능 플래그
FEATURE_NEW_UI=true

# 외부 서비스
REDIS_URL=redis://localhost:6379
SMTP_HOST=smtp.example.com
```

### .env.example 유지
실제 값이 아닌 예제 값만 포함하여 `.env.example`을 버전 관리에 포함하세요.
```
```

### 작성 팁

#### ✅ DO (해야 할 것)

- **간결하게 유지** - 짧고 선언적인 불릿 포인트 사용
- **명확한 구조** - 마크다운 헤딩(#, ##)으로 논리적 섹션 구분
- **구체적인 예제** - 코드베이스의 실제 예제 포함
- **중요한 정보 우선** - 가장 자주 사용되는 정보를 상단에 배치

#### ❌ DON'T (하지 말아야 할 것)

- **장황한 서술** - 긴 서사적 문단 지양
- **모든 것 문서화** - 노이즈를 유발하는 불필요한 정보 제외
- **주니어 개발자용 온보딩 문서 작성** - Claude를 위한 간결한 지침에 집중

### 기술 스택 작성 가이드라인

기술 스택 정보는 Claude가 프로젝트에 적합한 코드를 생성하는 데 매우 중요합니다.

#### 왜 중요한가?

Claude는 기술 스택 정보를 기반으로:
- 올바른 문법과 API 사용
- 프레임워크별 베스트 프랙티스 적용
- 적절한 라이브러리 import문 생성
- 버전별 차이점 고려 (예: Python 3.8 vs 3.12)

#### 포함해야 할 정보

**1. 언어 및 버전**
```markdown
- **언어**: Python 3.11+
```
- 최소 버전 명시 (`3.11+` 또는 `>= 3.11`)
- 정확한 버전이 중요한 경우 명시 (`3.11.5`)
- 버전별 주요 차이점 언급 (선택사항)

**2. 핵심 프레임워크**
```markdown
- **프레임워크**: FastAPI 0.104+, React 18.2
```
- 메인 프레임워크만 나열 (너무 많으면 노이즈)
- 버전 정보 포함 (breaking change가 있는 경우 필수)

**3. 주요 라이브러리**
```markdown
- **주요 라이브러리**:
  - 데이터베이스: SQLAlchemy 2.0, Alembic
  - 인증: PyJWT, passlib
  - HTTP: httpx, aiohttp
```
- 카테고리별로 그룹화하면 가독성 향상
- 자주 사용하는 것만 포함 (5-10개 이내)

**4. 개발 도구**
```markdown
- **개발 도구**: pytest, black (line-length: 100), ruff, mypy
```
- 코드 품질 도구 (린터, 포맷터)
- 테스트 프레임워크
- 중요한 설정 옵션 (예: 줄 길이)

#### 좋은 예 vs 나쁜 예

❌ **나쁜 예 - 너무 간략함**
```markdown
## 기술 스택
- Python
- FastAPI
```
> 문제: 버전 정보 없음, Claude가 어떤 버전의 문법을 사용해야 할지 모름

❌ **나쁜 예 - 너무 상세함**
```markdown
## 기술 스택
- Python 3.11.5
- FastAPI 0.104.1
- Pydantic 2.5.0
- uvicorn 0.24.0
- SQLAlchemy 2.0.23
- psycopg2-binary 2.9.9
- alembic 1.12.1
- python-dotenv 1.0.0
- PyJWT 2.8.0
- passlib 1.7.4
- bcrypt 4.1.1
- httpx 0.25.1
- aiohttp 3.9.0
- redis 5.0.1
- celery 5.3.4
- pytest 7.4.3
- pytest-asyncio 0.21.1
- black 23.11.0
- ruff 0.1.6
- mypy 1.7.0
```
> 문제: 너무 많은 정보, 핵심이 흐려짐, 유지보수 부담

✅ **좋은 예 - 적절한 균형**
```markdown
## 기술 스택

- **언어**: Python 3.11+ (타입 힌트 필수)
- **프레임워크**: FastAPI 0.104+
- **데이터베이스**:
  - ORM: SQLAlchemy 2.0 (async 모드)
  - 마이그레이션: Alembic
  - 드라이버: asyncpg (PostgreSQL)
- **인증**: JWT 기반 (PyJWT, passlib)
- **비동기 처리**: Celery + Redis
- **개발 도구**:
  - 테스트: pytest, pytest-asyncio
  - 린팅: ruff (line-length: 100)
  - 포맷팅: black (line-length: 100)
  - 타입 체크: mypy (strict mode)
```
> 장점: 핵심 정보만 포함, 카테고리별 정리, 중요한 설정 명시

#### 프론트엔드 예시

✅ **React 프로젝트**
```markdown
## 기술 스택

- **언어**: TypeScript 5.0+ (strict mode)
- **프레임워크**: React 18.2, Next.js 14
- **상태 관리**: Zustand (선호), React Query (서버 상태)
- **스타일링**:
  - CSS-in-JS: Emotion
  - 유틸리티: Tailwind CSS 3.x
- **폼 처리**: React Hook Form + Zod
- **테스트**:
  - 단위: Vitest
  - E2E: Playwright
- **린팅/포맷팅**: ESLint (Airbnb), Prettier
```

#### 중요한 컨벤션 추가

특정 라이브러리 사용 방식이 프로젝트마다 다를 수 있습니다:

```markdown
## 기술 스택

- **언어**: Python 3.11+
- **프레임워크**: Django 4.2
- **ORM**: Django ORM (QuerySet 체이닝 선호, raw SQL 금지)
- **폼**: Django Forms (FormView 사용, 함수형 뷰 지양)
- **템플릿**: Django Templates (Jinja2 사용 안 함)
```

이렇게 하면 Claude가 프로젝트의 특정 컨벤션을 따를 수 있습니다.

#### 버전 명시 전략

| 상황 | 명시 방법 | 예시 |
|------|----------|------|
| 최소 버전만 중요 | `+` 또는 `>=` | `Python 3.11+`, `React >= 18.0` |
| 메이저 버전 고정 | 메이저.마이너 | `Django 4.2`, `Next.js 14` |
| 정확한 버전 필요 | 전체 버전 | `Node.js 20.10.0` |
| 버전 범위 | 범위 표기 | `SQLAlchemy 2.0.x` |

---

## 구체적인 프롬프트 작성법

### 파일 수정 요청 시

```
src/api/users.py의 get_users 함수를 수정해주세요:
1. 페이지네이션 지원 추가 (limit, offset 파라미터)
2. 정렬 옵션 추가 (sort_by, order 파라미터)
3. 응답을 JSON으로 포맷팅 (users, total, page 정보 포함)
4. 타입 힌트 추가
5. 독스트링 업데이트
```

```
components/UserProfile.tsx 수정:
1. 프로필 이미지 lazy loading 적용
2. 에러 바운더리 추가
3. 로딩 상태 스켈레톤 UI로 개선
4. PropTypes → TypeScript 타입으로 변경
```

### 새 기능 추가 시

```
src/services/email.py에 새 함수 추가:
- 함수명: send_notification_email
- 기능: 사용자에게 알림 이메일 전송
- 파라미터:
  - user_email: str
  - subject: str
  - template_name: str
  - context: dict
- 반환값: bool (성공/실패)
- 에러 핸들링: SMTPException 캐치 및 로깅
- 기존 send_email 함수의 패턴 준수
```

```
새 API 엔드포인트 추가:
- 경로: POST /api/v1/webhooks/stripe
- 기능: Stripe 웹훅 처리
- 요청 바디: Stripe 이벤트 객체
- 응답: 200 OK 또는 400 Bad Request
- 보안: Stripe 시그니처 검증 필수
- 로깅: 모든 이벤트 기록
```

### 리팩토링 요청 시

```
src/utils/validators.py 리팩토링:
- 목적: 검증 로직 모듈화 및 재사용성 향상
- 변경사항:
  1. 각 검증 함수를 독립적인 validator로 분리
  2. 커스텀 예외 클래스 추가 (ValidationError)
  3. 데코레이터 패턴으로 검증 로직 적용 가능하게
  4. 단위 테스트 추가
- 유지사항:
  - 기존 함수 시그니처 변경 없음 (하위 호환성)
  - 에러 메시지 형식 유지
```

```
컴포넌트 리팩토링: src/components/Dashboard.jsx
- 큰 컴포넌트를 작은 컴포넌트로 분할:
  - DashboardHeader
  - DashboardStats
  - DashboardChart
  - DashboardActivity
- React hooks로 상태 관리 개선
- PropTypes 정의
- 성능 최적화 (useMemo, useCallback)
```

### 버그 수정 요청 시

```
버그 수정: src/auth/login.py의 authenticate_user 함수

증상:
- 비밀번호에 특수문자가 포함된 경우 인증 실패
- 로그: "Invalid password hash format"

예상 동작:
- 모든 특수문자를 올바르게 처리
- 성공 시 사용자 객체 반환

수정 방향:
- 비밀번호 해싱 전 이스케이프 처리 확인
- bcrypt 라이브러리 사용 방식 검토
- 단위 테스트 추가 (특수문자 케이스)
```

```
프론트엔드 버그 수정:

파일: components/SearchBar.jsx
문제: 검색 입력 시 한글 입력이 중복으로 처리됨
재현: 한글 타이핑 → 마지막 글자가 두 번 입력됨
원인: IME composition 이벤트 미처리

수정:
- onCompositionStart/End 이벤트 핸들러 추가
- composition 상태에서 onChange 무시
- 관련 이슈: #456
```

### 디버깅 요청 시

```
다음 에러를 디버깅해주세요:

에러 메시지:
```
TypeError: Cannot read property 'map' of undefined
at UserList.render (UserList.jsx:42)
```

컨텍스트:
- 컴포넌트: UserList
- 발생 시점: 페이지 첫 로드
- 예상: users 배열이 props로 전달되어야 함

확인 사항:
1. props 타입 검증
2. users의 초기값 설정
3. 로딩 상태 처리
4. 에러 바운더리 추가 권장
```

### 성능 최적화 요청 시

```
성능 최적화: src/api/search.py

현재 문제:
- 대용량 데이터 검색 시 응답 시간 5초 이상
- 메모리 사용량 과다 (500MB+)

목표:
- 응답 시간 1초 이하
- 메모리 사용량 100MB 이하

개선 방향:
1. 데이터베이스 쿼리 최적화 (인덱스 활용)
2. 페이지네이션 구현
3. 캐싱 레이어 추가 (Redis)
4. 불필요한 데이터 로딩 제거
5. 성능 측정 코드 추가
```

---

## 보안 모범 사례

### 중요 원칙

1. **AI 출력을 검증 전까지 신뢰하지 않기**
   - 생성된 코드를 항상 검토
   - 프로덕션 배포 전 테스트 필수

2. **프롬프트와 컨텍스트에서 시크릿 제외**
   - 프로덕션 시크릿이나 PII를 프롬프트에 붙여넣지 않기
   - `.env.example` 및 vault 사용
   - 예제에서 모의 데이터 사용

3. **최소 권한 원칙**
   - 필요한 최소한의 권한만 부여
   - API 토큰: 읽기 전용 vs 쓰기 권한 구분
   - 서비스 계정: 특정 작업에만 접근 가능하도록 제한

### 환경 변수 관리

```bash
# ✅ 좋은 예 - .env.example (예제 값만 포함)
API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
JWT_SECRET=your-secret-key-min-32-chars
STRIPE_API_KEY=sk_test_xxxxxxxxxxxxx

# ❌ 나쁜 예 - 실제 시크릿을 CLAUDE.md나 프롬프트에 포함
API_KEY=pk_live_51JxK2lS... (실제 프로덕션 키)
DATABASE_URL=postgresql://admin:P@ssw0rd!@prod.db.com/maindb
```

### 민감한 파일

다음 파일들은 절대 커밋하지 마세요:
- `.env` (실제 환경 변수)
- `credentials.json`
- `secrets.yaml`
- 개인 키 파일 (`*.key`, `*.pem`)

---

## 슬래시 커맨드 활용

### 커스텀 슬래시 커맨드

반복적인 워크플로우(디버깅 루프, 로그 분석 등)의 경우, `.claude/commands/` 폴더의 마크다운 파일에 프롬프트 템플릿을 저장하면 `/` 입력 시 슬래시 커맨드 메뉴에서 사용 가능합니다.

### 예제 구조

```
.claude/
└── commands/
    ├── review.md       # /review 커맨드
    ├── test.md         # /test 커맨드
    └── deploy.md       # /deploy 커맨드
```

### 커맨드 파일 예제 (.claude/commands/review.md)

```markdown
코드 리뷰를 수행해주세요:

1. 코드 스타일 검토 (프로젝트 스타일 가이드 기준)
2. 타입 안정성 확인 (타입 힌트, TypeScript 타입 등)
3. 에러 핸들링 적절성
4. 성능 이슈 (N+1 쿼리, 불필요한 렌더링 등)
5. 보안 취약점 (SQL injection, XSS 등)
6. 테스트 커버리지
7. 문서화 상태 (독스트링, JSDoc 등)

각 항목에 대해 구체적인 개선 제안을 제공해주세요.
```

### 추가 커맨드 예제

**.claude/commands/test.md**
```markdown
변경된 파일에 대한 테스트를 작성해주세요:

1. 단위 테스트 작성
2. 엣지 케이스 고려
3. 모킹 전략 적용
4. 테스트 커버리지 확인
5. 테스트 실행 및 결과 보고
```

**.claude/commands/optimize.md**
```markdown
다음 관점에서 코드를 최적화해주세요:

1. 성능: 시간 복잡도, 공간 복잡도
2. 가독성: 변수명, 함수 분리, 주석
3. 유지보수성: DRY, SOLID 원칙
4. 보안: 입력 검증, 인증/인가
5. 최적화 전후 비교 제공
```

**.claude/commands/explain.md**
```markdown
선택된 코드를 설명해주세요:

1. 전체 흐름 요약
2. 주요 로직 단계별 설명
3. 사용된 디자인 패턴
4. 잠재적 이슈 또는 개선점
5. 관련 문서 링크 (있다면)
```

### Git에 체크인

팀원들과 공유하기 위해 슬래시 커맨드를 Git에 커밋할 수 있습니다.

---

## Skills 활용

### Skills란?

**Skills**는 Claude Code의 모듈화된 기능 확장으로, 전문 지식을 발견 가능하고 조직화된 형태로 패키징합니다. 슬래시 커맨드와 달리 **Skills는 모델이 자동으로 호출**합니다—사용자의 요청과 Skill 설명을 기반으로 Claude가 자율적으로 활성화합니다.

### Skills vs 슬래시 커맨드

| 측면 | 슬래시 커맨드 | Skills |
|------|--------------|--------|
| **호출 방식** | 사용자가 수동으로 호출 (예: `/review`) | Claude가 컨텍스트 기반으로 자동 호출 |
| **파일 구조** | 단일 `.md` 파일 | `SKILL.md` + 지원 파일들이 있는 디렉터리 |
| **복잡도** | 간단한 단일 파일 프롬프트 | 여러 파일을 포함한 복잡한 워크플로우 |
| **사용 사례** | 빠른 유틸리티, 프로토타이핑 | 팀 협업, 포괄적인 워크플로우 |
| **공유** | 프로젝트별 또는 개인용 | 프로젝트, 개인, 플러그인 |
| **팀 접근** | 제한적 공유 | Git 통합 팀 공유 |
| **발견성** | 사용자가 명시적으로 알아야 함 | Claude가 컨텍스트 기반으로 발견 |

**언제 무엇을 사용할까?**

- **슬래시 커맨드 사용**: 빠른 자동화, 자주 사용하는 간단한 지침, 수동 제어가 필요한 즉각적인 유틸리티
- **Skills 사용**: 복잡한 다단계 워크플로우, 여러 파일이 필요한 기능, 팀과 공유할 역량, Claude가 자동 발견해야 하는 작업

### Skills 생성 방법

#### 1단계: Skill 디렉터리 구조 생성

Skills는 세 가지 위치에 저장됩니다:

```
개인 Skills:    ~/.claude/skills/<skill-name>/
프로젝트 Skills:  .claude/skills/<skill-name>/
플러그인 Skills:  플러그인을 통해 번들링
```

#### 2단계: YAML Frontmatter가 있는 SKILL.md 생성

모든 Skill은 다음 구조의 `SKILL.md` 파일이 필요합니다:

```yaml
---
name: skill-name
description: 이 스킬이 무엇을 하고 언제 사용하는지
allowed-tools: [optional-tool1, optional-tool2]
---

# Skill 설명

상세한 설명과 문서를 여기에 작성...
```

**YAML Frontmatter 필드**:
- `name`: 필수. 소문자, 숫자, 하이픈만 사용. 최대 64자.
- `description`: 필수. Claude가 언제 활성화할지 결정하는 중요한 정보. 기능과 트리거 용어 모두 포함.
- `allowed-tools`: 선택사항. Skill 활성화 시 Claude가 접근할 수 있는 도구 제한 (읽기 전용 또는 보안 민감 워크플로우에 유용).

#### 3단계: 지원 파일 추가 (선택사항)

`SKILL.md`와 함께 추가 리소스 구성:

```
.claude/skills/skill-name/
├── SKILL.md                    # 메인 스킬 정의
├── reference.md                # 참조 문서
├── examples.md                 # 사용 예제
├── scripts/
│   ├── helper-script.sh
│   ├── data-processor.py
│   └── template-generator.ts
└── templates/
    ├── template1.txt
    └── template2.txt
```

Claude는 필요할 때만 이 파일들을 점진적으로 읽습니다.

### Skills 작성 모범 사례

#### 1. Skills는 집중적으로 유지

- 각 Skill은 하나의 특정 기능에 집중
- 광범위한 카테고리 지양, 좁은 범위 유지
- 예: "GitHub 자동화"가 아닌 "PR 코드 리뷰어"

#### 2. 구체적이고 실행 가능한 설명 작성

이것이 Claude가 적절한 시점에 Skill을 발견하는 핵심입니다:

✅ **좋은 설명**:
```yaml
description: |
  버그, 성능 문제, 베스트 프랙티스를 위해 풀 리퀘스트 코드를 검토합니다.
  코드 변경 분석, 풀 리퀘스트 검토, 구현 품질 평가 시 사용합니다.
```

❌ **나쁜 설명**:
```yaml
description: 코드 리뷰 도움
```

포함할 내용:
- Skill이 무엇을 하는지
- 사용자가 언급할 구체적인 트리거 용어
- 예상되는 결과

#### 3. 재사용성을 고려한 설계

- 다른 팀원들도 유용하게 사용할 수 있는 Skills 생성
- 명확하지 않은 워크플로우는 자세히 문서화
- 지원 문서에 예제 포함

#### 4. 필요시 도구 접근 제어 사용

```yaml
---
name: read-only-analyzer
description: 변경 없이 코드와 문서를 분석합니다
allowed-tools: [Read, Grep, WebSearch]
---
```

읽기 전용 작업이나 보안이 중요한 워크플로우에 유용합니다.

#### 5. 스크립트를 논리적으로 구성

- 실행 가능한 코드는 `scripts/` 디렉터리 사용
- 보일러플레이트 콘텐츠는 `templates/` 사용
- `examples.md`에 사용 예제 제공

### Skills 예제

#### 예제 1: 코드 리뷰어 Skill

**파일 구조**:
```
.claude/skills/code-reviewer/
├── SKILL.md
├── review-criteria.md
└── templates/
    └── review-template.md
```

**SKILL.md**:
```yaml
---
name: code-reviewer
description: |
  코드 품질, 보안 문제, 성능 문제, 프로젝트 표준 준수를 위해
  코드를 검토합니다. 코드 변경 분석, 코드 리뷰 제공, 품질 검증 시 사용합니다.
allowed-tools: [Read, Grep, Bash]
---

# 코드 리뷰어

프로젝트를 위한 포괄적인 코드 리뷰 기능입니다.

## 기능

- 버그 및 이슈에 대한 코드 변경 분석
- 테스트 커버리지 확인
- 보안 취약점 검토
- 성능 영향 검증
- 코딩 표준 준수 확인

## 사용법

검토할 코드를 설명하면 상세한 피드백을 제공합니다.

## 분석 기준

상세한 검토 체크리스트는 `review-criteria.md`를 참조하세요.
```

**review-criteria.md**:
```markdown
# 코드 리뷰 기준

## 보안
- 하드코딩된 시크릿 또는 자격 증명 없음
- 적절한 입력 검증
- SQL 인젝션 방지
- 인증/인가 검사

## 성능
- 데이터베이스 쿼리 최적화
- 메모리 누수 또는 비효율적 알고리즘
- 캐싱 기회
- 부하 처리

## 코드 품질
- 프로젝트 스타일 가이드 준수
- 타입 안정성 준수
- 문서화 완성도
- 테스트 커버리지 (최소 80%)
```

#### 예제 2: API 문서 생성기 Skill

**파일 구조**:
```
.claude/skills/api-doc-generator/
├── SKILL.md
├── examples.md
└── templates/
    ├── endpoint-doc.md
    ├── parameter-table.md
    └── example-curl.txt
```

**SKILL.md**:
```yaml
---
name: api-doc-generator
description: |
  엔드포인트 명세, 파라미터, 요청/응답 예제, 에러 처리를 포함한
  포괄적인 API 문서를 코드에서 생성합니다. API 문서 작성,
  엔드포인트 문서화, API 레퍼런스 업데이트 시 사용합니다.
allowed-tools: [Read, Grep, Bash]
---

# API 문서 생성기

코드베이스에서 전문적인 API 문서를 자동 생성합니다.

## 기능

- 엔드포인트 정의 및 파라미터 추출
- 요청/응답 예제 생성
- 에러 코드 및 메시지 문서화
- 타입과 설명이 포함된 파라미터 테이블 생성
- 사용 예제 작성

## 문서화 스타일

일관된 형식 사용:
- 파라미터용 마크다운 테이블
- 언어 지정이 있는 코드 블록
- 명확한 섹션 계층
- 예제 curl 명령어

템플릿은 `templates/`, 출력 샘플은 `examples.md`를 참조하세요.
```

#### 예제 3: 보안 감사 Skill

**SKILL.md**:
```yaml
---
name: security-auditor
description: |
  인젝션 공격, 인증 문제, 노출된 자격 증명, 안전하지 않은 의존성을 포함한
  보안 취약점을 감사합니다. 보안 검토 수행, 취약점 확인,
  코드 변경의 보안 영향 분석 시 사용합니다.
allowed-tools: [Read, Grep, Bash]
---

# 보안 감사자

포괄적인 보안 취약점 탐지 및 분석입니다.

## 보안 검사 항목

- SQL/명령 인젝션 취약점
- 크로스사이트 스크립팅(XSS) 위험
- 인증/인가 우회
- 하드코딩된 시크릿/자격 증명
- 안전하지 않은 역직렬화
- 안전하지 않은 암호화
- 의존성 취약점
- CORS 설정 오류

## 사용법

특정 코드나 파일의 보안 감사를 요청하면, 심각도 수준과
개선 가이드와 함께 잠재적 취약점을 식별합니다.
```

### Skills 디버깅

Claude가 Skill을 활성화하지 않으면 다음을 확인하세요:

1. **설명 구체성**
   - 기능과 사용 트리거 모두 포함
   - 모호한 설명 지양
   - 예: "로그 처리"가 아닌 "에러 로그 추출 및 분석"

2. **파일 위치**
   - `SKILL.md`가 `.claude/skills/<skill-name>/SKILL.md`에 있는지 확인
   - 또는 개인 Skills의 경우 `~/.claude/skills/<skill-name>/SKILL.md`
   - 디렉터리 구조가 올바른지 확인

3. **YAML 문법**
   - `---` 구분자가 있는 유효한 frontmatter 확인
   - 들여쓰기 확인 (탭이 아닌 2 스페이스)
   - 필수 필드 검증: `name`과 `description`

4. **디버그 모드**
   ```bash
   claude --debug
   ```
   스킬 로딩 및 활성화 로그에서 에러 확인

### 프로젝트에 Skills 적용하기

프로젝트에서 Skills를 효과적으로 사용하려면:

1. **프로젝트 Skills 디렉터리 생성**
   ```bash
   mkdir -p .claude/skills
   ```

2. **팀 워크플로우 식별**
   - 반복적인 복잡한 작업은?
   - 여러 파일/스크립트가 필요한 작업은?
   - 팀원들이 자주 요청하는 작업은?

3. **Skills부터 시작하기**
   - 코드 리뷰 프로세스
   - 보안 감사
   - 문서 생성
   - 테스트 자동화

4. **Git에 커밋**
   ```bash
   git add .claude/skills
   git commit -m "feat: add team skills for code review and documentation"
   ```

5. **팀과 테스트**
   - 동료들이 Skills를 사용하도록 요청
   - Claude가 적절한 시점에 활성화하는지 모니터링
   - 실제 사용 경험을 바탕으로 설명 개선

---

## 추가 리소스

### 공식 문서
- [Claude Code Best Practices (Anthropic)](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Prompting Best Practices (Claude Docs)](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)
- [Claude Prompt Engineering Blog](https://www.claude.com/blog/best-practices-for-prompt-engineering)

### 커뮤니티 리소스
- [CLAUDE.md Best Practices (Arize)](https://arize.com/blog/claude-md-best-practices-learned-from-optimizing-claude-code-with-prompt-learning/)
- [My Claude Code Usage Best Practices](https://nikiforovall.blog/productivity/2025/06/13/claude-code-rules.html)
- [How to Write Better Prompts for Claude Code](https://claudelog.com/faqs/how-to-write-better-prompts-for-claude-code/)
- [What is CLAUDE.md in Claude Code](https://claudelog.com/faqs/what-is-claude-md/)
- [CLAUDE.md Templates (GitHub)](https://github.com/ruvnet/claude-flow/wiki/CLAUDE-MD-Templates)
- [Awesome Claude Code (GitHub)](https://github.com/hesreallyhim/awesome-claude-code)

### 가이드 및 튜토리얼
- [Cooking with Claude Code: The Complete Guide](https://www.siddharthbharath.com/claude-code-the-complete-guide/)
- [Claude Code CLI Cheatsheet (Shipyard)](https://shipyard.build/blog/claude-code-cheat-sheet/)
- [How I Use Claude Code (Builder.io)](https://www.builder.io/blog/claude-code)
- [Step-by-Step Guide: Prepare Your Codebase for Claude Code](https://medium.com/@dan.avila7/step-by-step-guide-prepare-your-codebase-for-claude-code-3e14262566e9)

---

## 요약

효과적인 Claude Code 사용을 위한 핵심 원칙:

1. **구체성이 핵심** - 명확하고 상세한 지침 제공
2. **CLAUDE.md 활용** - 프로젝트 컨텍스트를 지속적으로 유지
3. **범위 명확히** - 작업 경계를 명확히 정의
4. **보안 우선** - 시크릿 제외, 최소 권한 원칙
5. **예제 제공** - 구체적인 코드 예제로 의도 전달
6. **간결하게 유지** - 불필요한 정보 제외, 핵심에 집중

Claude Code와의 협업은 명확한 커뮤니케이션에서 시작됩니다. 이 가이드라인을 따라 더 효율적이고 생산적인 개발 경험을 만들어보세요.
