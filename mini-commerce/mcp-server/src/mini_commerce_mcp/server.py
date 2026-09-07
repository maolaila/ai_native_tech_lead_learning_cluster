"""MCP 协议适配层。HTTP 模式必须配置 Token；测试执行只允许本地 stdio 显式开启。"""
from __future__ import annotations

import hmac
import os
from pydantic import AnyHttpUrl
from mcp.server import MCPServer
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from . import tooling


class StaticTokenVerifier(TokenVerifier):
    """仅用于本地学习。生产需要真正的身份提供方与按用户授权，不是共享固定 Token。"""
    async def verify_token(self, token: str) -> AccessToken | None:
        expected = os.getenv("MCP_STATIC_TOKEN")
        if expected and hmac.compare_digest(token, expected):
            return AccessToken(token=token, client_id="local-learning-client",
                               scopes=["commerce:read"], subject="learner")
        return None


def build_server() -> MCPServer:
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    kwargs = {}
    if transport == "streamable-http":
        if not os.getenv("MCP_STATIC_TOKEN"):
            raise ValueError("MCP_STATIC_TOKEN is required for HTTP mode")
        public = os.getenv("MCP_PUBLIC_URL", "http://127.0.0.1:8081/mcp")
        kwargs = {"token_verifier": StaticTokenVerifier(), "auth": AuthSettings(
            issuer_url=AnyHttpUrl("https://local-idp.invalid"),
            resource_server_url=AnyHttpUrl(public), required_scopes=["commerce:read"])}
    server = MCPServer("Mini Commerce Engineering Knowledge", **kwargs)

    @server.tool()
    def search_learning_docs(query: str, limit: int = 8) -> dict:
        return tooling.search_docs(query, limit)

    @server.tool()
    def get_database_schema() -> dict:
        return tooling.database_schema()

    @server.tool()
    def explain_readonly_query(sql: str) -> dict:
        return tooling.explain_readonly(sql)

    @server.tool()
    def read_runbook(path: str) -> dict:
        return tooling.read_runbook(path)

    @server.tool()
    def list_test_suites() -> dict:
        return {"status": "ok", "data": sorted(tooling.SUITES),
                "executionEnabled": tooling.execution_enabled()}

    @server.tool()
    def run_test_suite(name: str) -> dict:
        return tooling.run_suite(name)

    return server


def main() -> None:
    server = build_server()
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        server.run(transport="streamable-http", host=os.getenv("MCP_HOST", "127.0.0.1"),
                   port=int(os.getenv("MCP_PORT", "8081")), json_response=True, stateless_http=True)
    else:
        server.run(transport="stdio")


if __name__ == "__main__":
    main()
