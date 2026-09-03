from __future__ import annotations
import os
from pydantic import AnyHttpUrl
from mcp.server import MCPServer
from mcp.server.auth.provider import AccessToken,TokenVerifier
from mcp.server.auth.settings import AuthSettings
from . import tooling

class StaticTokenVerifier(TokenVerifier):
    """仅用于本地学习。生产应验证企业 IdP 的 JWT 或调用 RFC 7662 introspection。"""
    async def verify_token(self,token:str)->AccessToken|None:
        expected=os.getenv("MCP_STATIC_TOKEN")
        if expected and token==expected:return AccessToken(token=token,client_id="local-learning-client",scopes=["commerce:read","tests:run"],subject="learner")
        return None

def build_server()->MCPServer:
    transport=os.getenv("MCP_TRANSPORT","stdio")
    kwargs={}
    if transport=="streamable-http":
        public=os.getenv("MCP_PUBLIC_URL","http://127.0.0.1:8081/mcp")
        kwargs={"token_verifier":StaticTokenVerifier(),"auth":AuthSettings(issuer_url=AnyHttpUrl("https://local-idp.invalid"),resource_server_url=AnyHttpUrl(public),required_scopes=["commerce:read"])}
    mcp=MCPServer("Mini Commerce Engineering Knowledge",**kwargs)
    @mcp.tool()
    def search_learning_docs(query:str,limit:int=8)->dict:return tooling.search_docs(query,limit)
    @mcp.tool()
    def get_database_schema()->dict:return tooling.database_schema()
    @mcp.tool()
    def explain_readonly_query(sql:str)->dict:return tooling.explain_readonly(sql)
    @mcp.tool()
    def read_runbook(path:str)->dict:return tooling.read_runbook(path)
    @mcp.tool()
    def list_test_suites()->dict:return {"status":"ok","data":sorted(tooling.SUITES)}
    @mcp.tool()
    def run_test_suite(name:str)->dict:return tooling.run_suite(name)
    return mcp

def main()->None:
    mcp=build_server();transport=os.getenv("MCP_TRANSPORT","stdio")
    if transport=="streamable-http":mcp.run(transport="streamable-http",host=os.getenv("MCP_HOST","127.0.0.1"),port=int(os.getenv("MCP_PORT","8081")),json_response=True,stateless_http=True)
    else:mcp.run(transport="stdio")

if __name__=="__main__":main()
