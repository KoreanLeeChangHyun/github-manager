# MCP 서버 아키텍처 설명

## 작동 방식

### 1. Claude Code가 서버 시작
```bash
# Claude Code가 내부적으로 실행하는 명령
uv run github-manager-mcp
```

### 2. 서버 프로세스 생성
```
프로세스 ID: 12345
stdin  (입력 파이프)  ← Claude Code가 여기로 요청 전송
stdout (출력 파이프)  → Claude Code가 여기서 응답 수신
stderr (에러 로그)
```

### 3. 통신 예시

#### Claude Code → MCP 서버 (stdin)
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "list_repositories",
    "arguments": {
      "username": "KoreanLeeChangHyun",
      "limit": 10
    }
  }
}
```

#### MCP 서버 → Claude Code (stdout)
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "1. KoreanLeeChangHyun/github-manager\n   Description: FastMCP server..."
      }
    ]
  }
}
```

## 구성 요소

### server.py (메인 서버)
```python
from fastmcp import FastMCP

# MCP 서버 인스턴스 생성
mcp = FastMCP("GitHub Manager")

# 도구 등록
@mcp.tool()
def list_repositories(...):
    # GitHub API 호출
    return "저장소 목록..."

# STDIO로 서버 실행
def main():
    mcp.run()  # ← 여기서 stdin/stdout 대기
```

### FastMCP의 mcp.run()이 하는 일
1. **stdin 대기**: JSON-RPC 요청 수신 대기
2. **요청 파싱**: JSON 메시지 해석
3. **도구 실행**: 해당하는 `@mcp.tool()` 함수 호출
4. **결과 반환**: stdout으로 JSON 응답 전송
5. **반복**: 프로세스가 종료될 때까지 1-4 반복

## 왜 포트가 필요 없는가?

### HTTP 서버 (포트 필요)
```
여러 클라이언트 → 네트워크 → 포트 8000 → 서버
                                   ↓
                              멀티스레드 처리
```

### STDIO 서버 (포트 불필요)
```
단일 클라이언트 (Claude Code)
    ↓
프로세스 직접 실행
    ↓
stdin/stdout 파이프 (1:1 연결)
    ↓
MCP 서버 프로세스
```

- **1:1 전용 통신**: Claude Code가 서버 프로세스를 직접 소유
- **로컬 통신**: 네트워크 통신 없음
- **프로세스 간 통신 (IPC)**: 파이프를 통한 직접 데이터 전송

## Claude Code 설정 파일 (mcp.json)

```json
{
  "mcpServers": {
    "github-manager": {
      "command": "uv",              // 실행할 명령
      "args": [                     // 명령 인자
        "--directory", "/home/deus/github",
        "run", "github-manager-mcp"
      ],
      "env": {                      // 환경 변수
        "GITHUB_TOKEN": "...",
        "GITHUB_USERNAME": "..."
      }
    }
  }
}
```

Claude Code는 이 설정을 읽고:
1. `uv --directory /home/deus/github run github-manager-mcp` 실행
2. 환경 변수 전달
3. stdin/stdout 파이프 연결
4. JSON-RPC 메시지 송수신

## 비교: 웹서버 vs MCP 서버

### 웹 서버 (Flask, FastAPI 등)
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/repositories")
def list_repos():
    return {"repos": [...]}

# HTTP 서버 시작 - 포트 필요!
uvicorn.run(app, host="0.0.0.0", port=8000)
```

### MCP 서버 (FastMCP)
```python
from fastmcp import FastMCP

mcp = FastMCP("GitHub Manager")

@mcp.tool()
def list_repositories():
    return "repos..."

# STDIO 서버 - 포트 불필요!
mcp.run()
```

## 실행 흐름

```
사용자가 Claude Code에 "내 저장소 목록 보여줘" 요청
    ↓
Claude Code가 github-manager MCP 서버에 요청 필요 판단
    ↓
mcp.json 읽어서 서버 실행 (이미 실행 중이면 재사용)
    ↓
stdin으로 JSON-RPC 요청 전송:
{
  "method": "tools/call",
  "params": {"name": "list_repositories", ...}
}
    ↓
MCP 서버가 요청 수신 및 처리
    ↓
GitHub API 호출 (PyGithub 사용)
    ↓
결과를 JSON으로 stdout에 출력
    ↓
Claude Code가 stdout에서 응답 읽기
    ↓
사용자에게 결과 표시
```

## 정리

- **포트 없음**: 네트워크 서버가 아니라 로컬 프로세스
- **통신 방식**: stdin/stdout 파이프 (표준 입출력)
- **연결 방식**: Claude Code가 프로세스를 직접 실행 및 관리
- **프로토콜**: JSON-RPC over STDIO
- **장점**:
  - 설정 간단 (포트 충돌 없음)
  - 보안 (로컬만 접근 가능)
  - 빠름 (네트워크 오버헤드 없음)
