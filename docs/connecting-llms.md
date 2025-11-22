# 다른 LLM에서 MCP 서버 연결하기

## 서버 시작

### SSE 모드로 시작 (네트워크 접근 가능)

```bash
# 기본 포트 8000으로 시작
./start_sse.sh

# 또는 커스텀 포트
./start_sse.sh --port 3000

# 또는 직접 실행
MCP_TRANSPORT=sse MCP_PORT=8000 uv run github-manager-mcp
```

서버 URL: **http://localhost:8000/sse**

## 연결 방법

### 1. MCP 클라이언트 사용

MCP 프로토콜을 지원하는 클라이언트 (Python 예시):

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import httpx

async def connect_to_mcp_server():
    """SSE 방식으로 MCP 서버에 연결"""

    # SSE 엔드포인트로 연결
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "GET",
            "http://localhost:8000/sse",
            headers={"Accept": "text/event-stream"}
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    # MCP 메시지 처리
                    message = json.loads(line[6:])
                    print(message)

# 또는 MCP SDK 사용
from mcp import ClientSession
from mcp.client.sse import sse_client

async with sse_client("http://localhost:8000/sse") as (read, write):
    async with ClientSession(read, write) as session:
        # Initialize
        await session.initialize()

        # List tools
        tools = await session.list_tools()
        print("Available tools:", tools)

        # Call tool
        result = await session.call_tool(
            "list_repositories",
            {"username": "KoreanLeeChangHyun", "limit": 5}
        )
        print(result)
```

### 2. HTTP REST API로 래핑

다른 LLM(ChatGPT, Gemini 등)이 사용하려면 REST API 래퍼 필요:

```python
# rest_wrapper.py
from fastapi import FastAPI, HTTPException
from mcp.client.sse import sse_client
from mcp import ClientSession
import uvicorn

app = FastAPI()

# MCP 클라이언트 세션 (글로벌)
mcp_session = None

@app.on_event("startup")
async def startup():
    """MCP 서버에 연결"""
    global mcp_session
    async with sse_client("http://localhost:8000/sse") as (read, write):
        mcp_session = ClientSession(read, write)
        await mcp_session.initialize()

@app.get("/api/repositories")
async def list_repositories(username: str = None, limit: int = 10):
    """저장소 목록 조회 (REST API)"""
    try:
        result = await mcp_session.call_tool(
            "list_repositories",
            {"username": username, "limit": limit}
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/repositories")
async def create_repository(name: str, description: str = "", private: bool = False):
    """저장소 생성"""
    result = await mcp_session.call_tool(
        "create_repository",
        {"name": name, "description": description, "private": private}
    )
    return {"success": True, "data": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
```

이제 REST API로 접근 가능:
```bash
# ChatGPT, Gemini 등에서 사용 가능
curl http://localhost:9000/api/repositories?username=KoreanLeeChangHyun&limit=5
```

### 3. OpenAI Function Calling 형식으로 변환

ChatGPT가 사용할 수 있는 Function Calling 형식:

```python
# openai_adapter.py
from openai import OpenAI
import requests

# MCP 도구를 OpenAI Function 형식으로 변환
def mcp_tool_to_openai_function(tool_name, description, parameters):
    return {
        "type": "function",
        "function": {
            "name": tool_name,
            "description": description,
            "parameters": parameters
        }
    }

# MCP 서버 호출 함수
async def call_mcp_tool(tool_name, arguments):
    # REST 래퍼를 통해 MCP 서버 호출
    response = requests.post(
        "http://localhost:9000/api/call-tool",
        json={"tool": tool_name, "arguments": arguments}
    )
    return response.json()

# OpenAI 클라이언트 설정
client = OpenAI()

# MCP 도구들을 OpenAI Function으로 등록
tools = [
    mcp_tool_to_openai_function(
        "list_repositories",
        "GitHub 저장소 목록 조회",
        {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "limit": {"type": "integer"}
            }
        }
    ),
    # ... 다른 도구들
]

# ChatGPT 사용
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "내 GitHub 저장소 목록 보여줘"}],
    tools=tools
)

# Function call 처리
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        result = await call_mcp_tool(
            tool_call.function.name,
            json.loads(tool_call.function.arguments)
        )
        print(result)
```

### 4. 직접 HTTP 요청

MCP 프로토콜 없이 직접 사용하려면 SSE 엔드포인트로 요청:

```bash
# SSE 스트림 연결
curl -N -H "Accept: text/event-stream" http://localhost:8000/sse
```

하지만 이 방식은 MCP 프로토콜을 구현해야 하므로 복잡합니다.

## 추천 방식

### ChatGPT, Gemini 등 외부 LLM
1. **REST API 래퍼 사용** (가장 간단)
   - `rest_wrapper.py` 실행
   - REST API로 접근

2. **OpenAI Function Calling** (ChatGPT)
   - Function 형식으로 변환
   - GPT-4 등에서 사용

### Claude Code 등 MCP 지원 클라이언트
- **STDIO 모드** (기본)
  - 로컬에서만 사용
  - 설정 간단

- **SSE 모드** (네트워크)
  - 원격 접근 가능
  - 여러 클라이언트 연결 가능

## 서버 모드 비교

| 모드 | 포트 | 네트워크 접근 | 용도 |
|------|------|---------------|------|
| **STDIO** | 없음 | 불가능 | Claude Code 로컬 전용 |
| **SSE** | 8000 | 가능 | 네트워크 환경, 여러 클라이언트 |

## 보안 고려사항

SSE 모드로 실행 시:
1. **방화벽 설정**: 필요한 경우 포트 제한
2. **인증 추가**: 프로덕션에서는 API 키 또는 OAuth 필요
3. **HTTPS**: 실제 배포 시 TLS 사용
4. **환경 변수**: `.env` 파일 보호 (`.gitignore`에 포함됨)

```bash
# 로컬에서만 접근 가능하게
MCP_HOST=127.0.0.1 MCP_PORT=8000 uv run github-manager-mcp

# 모든 네트워크에서 접근 가능 (주의!)
MCP_HOST=0.0.0.0 MCP_PORT=8000 uv run github-manager-mcp
```

## 예제 프로젝트

`examples/` 디렉토리에 다음 예제들이 있습니다:
- `rest_wrapper.py`: REST API 래퍼
- `openai_adapter.py`: OpenAI Function Calling 어댑터
- `mcp_client.py`: Python MCP 클라이언트 예제
