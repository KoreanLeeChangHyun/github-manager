#!/usr/bin/env python3
"""MCP 서버 통신 방식 데모"""

import json
import sys

# 이것이 MCP 서버가 하는 일입니다
def mcp_server_demo():
    """
    MCP 서버는 이렇게 작동합니다:
    1. stdin(표준 입력)에서 요청을 읽음
    2. 처리 후 stdout(표준 출력)으로 응답
    """

    # stdin에서 한 줄 읽기 (Claude Code가 보낸 요청)
    request = input()

    # JSON으로 파싱
    data = json.loads(request)

    # 도구 실행 (여기서는 간단한 예시)
    if data.get("method") == "tools/call":
        tool_name = data["params"]["name"]

        response = {
            "jsonrpc": "2.0",
            "id": data["id"],
            "result": {
                "content": [{
                    "type": "text",
                    "text": f"도구 '{tool_name}'를 실행했습니다!"
                }]
            }
        }

    # stdout으로 응답 출력 (Claude Code가 읽음)
    print(json.dumps(response))

if __name__ == "__main__":
    # 실제 MCP 서버는 무한 루프로 계속 대기합니다
    # mcp.run()이 하는 일이 바로 이것입니다
    print("# MCP 서버 데모 - stdin/stdout 통신", file=sys.stderr)
    print("# 요청 예시를 stdin으로 보내세요:", file=sys.stderr)
    print('# echo \'{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list_repositories"}}\' | python test_mcp.py', file=sys.stderr)
    print("", file=sys.stderr)

    mcp_server_demo()
