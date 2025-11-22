# Examples

이 디렉토리에는 GitHub Manager MCP Server를 다양한 방식으로 사용하는 예제가 포함되어 있습니다.

## rest_wrapper.py

REST API 래퍼 템플릿입니다. 이를 사용하면 MCP 프로토콜을 지원하지 않는 클라이언트(ChatGPT, Gemini 등)도 서버에 접근할 수 있습니다.

**주의**: 이것은 템플릿입니다. 실제로 작동하려면 MCP 클라이언트 라이브러리를 사용하여 SSE 연결을 구현해야 합니다.

### 사용 방법

```bash
# 1. MCP 서버를 SSE 모드로 시작
MCP_TRANSPORT=sse uv run github-manager-mcp

# 2. REST 래퍼 실행
python examples/rest_wrapper.py

# 3. REST API로 접근
curl http://localhost:9000/api/repositories?limit=5
```

### API 문서

서버 시작 후: http://localhost:9000/docs

## 완전한 구현을 위해

MCP 클라이언트 라이브러리 사용:
```bash
pip install mcp
```

자세한 내용은 `docs/connecting-llms.md`를 참조하세요.
