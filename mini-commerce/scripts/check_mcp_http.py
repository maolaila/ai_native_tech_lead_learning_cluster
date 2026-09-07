"""从宿主机验证 MCP HTTP 认证与协议握手，只接受本地地址。"""
import json
import os
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

url = os.getenv('MCP_URL', 'http://127.0.0.1:18081/mcp')
assert urlparse(url).hostname in {'localhost','127.0.0.1','::1'}
body = json.dumps({'jsonrpc':'2.0','id':1,'method':'initialize',
    'params':{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'pre-study-smoke','version':'1'}}}).encode()
headers = {'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
try:
    urlopen(Request(url, data=body, headers=headers), timeout=10)
except HTTPError as error:
    assert error.code == 401, error.code
else:
    raise AssertionError('MCP accepted anonymous access')
headers['Authorization'] = 'Bearer ' + os.getenv('MCP_STATIC_TOKEN','local-mcp-readonly-token')
with urlopen(Request(url, data=body, headers=headers), timeout=10) as response:
    result = json.loads(response.read())
assert 'result' in result and 'serverInfo' in result['result'], result
print('MCP anonymous rejection and authenticated initialize verified')
