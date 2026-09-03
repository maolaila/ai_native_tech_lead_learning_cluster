# CI 失败报告（main 未更新）

- Workflow: https://github.com/maolaila/ai_native_tech_lead_learning_cluster/actions/runs/33722474778
- Commit: 13644b7474166ac91ffda2c3cd130cd074b1eed5
- 结论：至少一个发布门禁失败；main 快进步骤未执行。

## finalize.log 最后 200 行
```text
mini-commerce/infra/aws/terraform/versions.tf
[31m[31m╷[0m[0m
[31m│[0m [0m[1m[31mError: [0m[0m[1mInvalid character[0m
[31m│[0m [0m
[31m│[0m [0m[0m  on mini-commerce/infra/aws/terraform/main.tf line 15, in resource "aws_internet_gateway" "main":
[31m│[0m [0m  15: resource "aws_internet_gateway" "main" { vpc_id = aws_vpc.main.id[4m;[0m tags = { Name = local.name } }[0m
[31m│[0m [0m
[31m│[0m [0mThe ";" character is not valid. Use newlines to separate arguments and
[31m│[0m [0mblocks, and commas to separate items in collection values.
[31m╵[0m[0m
[0m[0m
[31m[31m╷[0m[0m
[31m│[0m [0m[1m[31mError: [0m[0m[1mInvalid single-argument block definition[0m
[31m│[0m [0m
[31m│[0m [0m[0m  on mini-commerce/infra/aws/terraform/main.tf line 15, in resource "aws_internet_gateway" "main":
[31m│[0m [0m  15: resource "aws_internet_gateway" "main" { vpc_id = aws_vpc.main.id[4m;[0m tags = { Name = local.name } }[0m
[31m│[0m [0m
[31m│[0m [0mA single-line block definition must end with a closing brace immediately
[31m│[0m [0mafter its single argument definition.
[31m╵[0m[0m
[0m[0m
[31m[31m╷[0m[0m
[31m│[0m [0m[1m[31mError: [0m[0m[1mInvalid character[0m
[31m│[0m [0m
[31m│[0m [0m[0m  on mini-commerce/infra/aws/terraform/outputs.tf line 2, in output "rds_endpoint":
[31m│[0m [0m   2: output "rds_endpoint" { value = aws_db_instance.postgres.address[4m;[0m sensitive = true }[0m
[31m│[0m [0m
[31m│[0m [0mThe ";" character is not valid. Use newlines to separate arguments and
[31m│[0m [0mblocks, and commas to separate items in collection values.
[31m╵[0m[0m
[0m[0m
[31m[31m╷[0m[0m
[31m│[0m [0m[1m[31mError: [0m[0m[1mInvalid single-argument block definition[0m
[31m│[0m [0m
[31m│[0m [0m[0m  on mini-commerce/infra/aws/terraform/outputs.tf line 2, in output "rds_endpoint":
[31m│[0m [0m   2: output "rds_endpoint" { value = aws_db_instance.postgres.address[4m;[0m sensitive = true }[0m
[31m│[0m [0m
[31m│[0m [0mA single-line block definition must end with a closing brace immediately
[31m│[0m [0mafter its single argument definition.
[31m╵[0m[0m
[0m[0m
[31m[31m╷[0m[0m
[31m│[0m [0m[1m[31mError: [0m[0m[1mInvalid character[0m
[31m│[0m [0m
[31m│[0m [0m[0m  on mini-commerce/infra/aws/terraform/variables.tf line 1, in variable "aws_region":
[31m│[0m [0m   1: variable "aws_region" { type = string[4m;[0m default = "ap-northeast-1" }[0m
[31m│[0m [0m
[31m│[0m [0mThe ";" character is not valid. Use newlines to separate arguments and
[31m│[0m [0mblocks, and commas to separate items in collection values.
[31m╵[0m[0m
[0m[0m
[31m[31m╷[0m[0m
[31m│[0m [0m[1m[31mError: [0m[0m[1mInvalid single-argument block definition[0m
[31m│[0m [0m
[31m│[0m [0m[0m  on mini-commerce/infra/aws/terraform/variables.tf line 1, in variable "aws_region":
[31m│[0m [0m   1: variable "aws_region" { type = string[4m;[0m default = "ap-northeast-1" }[0m
[31m│[0m [0m
[31m│[0m [0mA single-line block definition must end with a closing brace immediately
[31m│[0m [0mafter its single argument definition.
[31m╵[0m[0m
[0m[0m
{"status": "delivery-finalized", "counts": {"files": 375, "markdown": 163, "java": 123, "sql": 10, "python": 21, "yaml": 26}, "project": {"generatedAt": "2026-09-03T06:16:45.584459+00:00", "fileCount": 199, "javaMainFiles": 115, "javaTestFiles": 8, "migrations": ["V001__baseline.sql", "V002__operational_indexes.sql", "V003__refunds.sql"], "documentMappingEntries": 1281}, "aggregateSha256": "a2076198968117f3fd6b10bd9b4b1bf17d5db58339e57f48b629f512e917bee5"}
```

## generate.log 最后 200 行
```text
{"status": "generated", "project": "mini-commerce", "files": 304, "java": 120}
{"status": "final-fixes-applied", "files": 190, "java": 121}
{"status": "release-fixes-applied", "counts": {"files": 367, "markdown": 160, "java": 122, "sql": 10, "python": 21, "yaml": 25}, "aggregateSha256": "d58a42d496d9de0af8c97985e2c8579a92af8d9eb6061db2577dd32a8977be85"}
{"status": "completeness-fixes-v3-applied"}
{"status": "ci-and-doc-fixes-v5-applied"}
{"status": "mapping-refined", "entries": 1281}
```

## maven.log 最后 200 行
```text
[INFO] Scanning for projects...
[INFO] 
[INFO] ---------------------< com.example:mini-commerce >----------------------
[INFO] Building mini-commerce 1.0.0-SNAPSHOT
[INFO]   from pom.xml
[INFO] --------------------------------[ jar ]---------------------------------
[INFO] 
[INFO] --- jacoco:0.8.13:prepare-agent (default) @ mini-commerce ---
[INFO] argLine set to -javaagent:/home/runner/.m2/repository/org/jacoco/org.jacoco.agent/0.8.13/org.jacoco.agent-0.8.13-runtime.jar=destfile=/home/runner/work/ai_native_tech_lead_learning_cluster/ai_native_tech_lead_learning_cluster/mini-commerce/backend/target/jacoco.exec
[INFO] 
[INFO] --- resources:3.3.1:resources (default-resources) @ mini-commerce ---
[INFO] Copying 2 resources from src/main/resources to target/classes
[INFO] Copying 3 resources from src/main/resources to target/classes
[INFO] 
[INFO] --- compiler:3.14.1:compile (default-compile) @ mini-commerce ---
[INFO] Recompiling the module because of changed source code.
[INFO] Compiling 115 source files with javac [debug parameters release 21] to target/classes
[INFO] Some messages have been simplified; recompile with -Xdiags:verbose to get full output
[INFO] -------------------------------------------------------------
[ERROR] COMPILATION ERROR : 
[INFO] -------------------------------------------------------------
[ERROR] /home/runner/work/ai_native_tech_lead_learning_cluster/ai_native_tech_lead_learning_cluster/mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/ApiSecurityHandlers.java:[3,81] cannot find symbol
  symbol: class AccessDeniedHandler
[ERROR] /home/runner/work/ai_native_tech_lead_learning_cluster/ai_native_tech_lead_learning_cluster/mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java:[16,52] cannot find symbol
  symbol:   class PageableDefault
  location: class com.example.minicommerce.catalog.api.ProductController
[ERROR] /home/runner/work/ai_native_tech_lead_learning_cluster/ai_native_tech_lead_learning_cluster/mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderController.java:[3,739] cannot find symbol
  symbol:   class PageableDefault
  location: class com.example.minicommerce.order.api.OrderController
[ERROR] /home/runner/work/ai_native_tech_lead_learning_cluster/ai_native_tech_lead_learning_cluster/mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/ApiSecurityHandlers.java:[3,367] method does not override or implement a method from a supertype
[ERROR] /home/runner/work/ai_native_tech_lead_learning_cluster/ai_native_tech_lead_learning_cluster/mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/SecurityConfiguration.java:[4,424] incompatible types: com.example.minicommerce.shared.security.ApiSecurityHandlers cannot be converted to org.springframework.security.web.access.AccessDeniedHandler
[INFO] 5 errors 
[INFO] -------------------------------------------------------------
[INFO] ------------------------------------------------------------------------
[INFO] BUILD FAILURE
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  21.862 s
[INFO] Finished at: 2026-09-03T06:17:28Z
[INFO] ------------------------------------------------------------------------
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:3.14.1:compile (default-compile) on project mini-commerce: Compilation failure: Compilation failure: 
[ERROR] /home/runner/work/ai_native_tech_lead_learning_cluster/ai_native_tech_lead_learning_cluster/mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/ApiSecurityHandlers.java:[3,81] cannot find symbol
[ERROR]   symbol: class AccessDeniedHandler
[ERROR] /home/runner/work/ai_native_tech_lead_learning_cluster/ai_native_tech_lead_learning_cluster/mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java:[16,52] cannot find symbol
[ERROR]   symbol:   class PageableDefault
[ERROR]   location: class com.example.minicommerce.catalog.api.ProductController
[ERROR] /home/runner/work/ai_native_tech_lead_learning_cluster/ai_native_tech_lead_learning_cluster/mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderController.java:[3,739] cannot find symbol
[ERROR]   symbol:   class PageableDefault
[ERROR]   location: class com.example.minicommerce.order.api.OrderController
[ERROR] /home/runner/work/ai_native_tech_lead_learning_cluster/ai_native_tech_lead_learning_cluster/mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/ApiSecurityHandlers.java:[3,367] method does not override or implement a method from a supertype
[ERROR] /home/runner/work/ai_native_tech_lead_learning_cluster/ai_native_tech_lead_learning_cluster/mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/SecurityConfiguration.java:[4,424] incompatible types: com.example.minicommerce.shared.security.ApiSecurityHandlers cannot be converted to org.springframework.security.web.access.AccessDeniedHandler
[ERROR] -> [Help 1]
[ERROR] 
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
[ERROR] 
[ERROR] For more information about the errors and possible solutions, please read the following articles:
[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
```

## mcp.log 最后 200 行
```text
Obtaining file:///home/runner/work/ai_native_tech_lead_learning_cluster/ai_native_tech_lead_learning_cluster/mini-commerce/mcp-server
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Checking if build backend supports build_editable: started
  Checking if build backend supports build_editable: finished with status 'done'
  Getting requirements to build editable: started
  Getting requirements to build editable: finished with status 'done'
  Installing backend dependencies: started
  Installing backend dependencies: finished with status 'done'
  Preparing editable metadata (pyproject.toml): started
  Preparing editable metadata (pyproject.toml): finished with status 'done'
Collecting mcp==2.1.1 (from mini-commerce-mcp==1.0.0)
  Downloading mcp-2.1.1-py3-none-any.whl.metadata (7.8 kB)
Collecting psycopg<4,>=3.2 (from psycopg[binary]<4,>=3.2->mini-commerce-mcp==1.0.0)
  Downloading psycopg-3.3.5-py3-none-any.whl.metadata (4.3 kB)
Collecting pydantic<3,>=2.12 (from mini-commerce-mcp==1.0.0)
  Downloading pydantic-2.13.5-py3-none-any.whl.metadata (110 kB)
Collecting pytest<9,>=8.4 (from mini-commerce-mcp==1.0.0)
  Downloading pytest-8.4.2-py3-none-any.whl.metadata (7.7 kB)
Collecting anyio>=4.9 (from mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading anyio-4.15.0-py3-none-any.whl.metadata (4.7 kB)
Collecting httpx2>=2.5.0 (from mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading httpx2-2.12.0-py3-none-any.whl.metadata (9.5 kB)
Collecting jsonschema>=4.20.0 (from mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading jsonschema-4.26.0-py3-none-any.whl.metadata (7.6 kB)
Collecting mcp-types==2.1.1 (from mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading mcp_types-2.1.1-py3-none-any.whl.metadata (1.9 kB)
Collecting opentelemetry-api>=1.28.0 (from mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading opentelemetry_api-1.44.0-py3-none-any.whl.metadata (1.4 kB)
Collecting pyjwt>=2.10.1 (from pyjwt[crypto]>=2.10.1->mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading pyjwt-2.13.0-py3-none-any.whl.metadata (3.4 kB)
Collecting python-multipart>=0.0.9 (from mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading python_multipart-0.0.32-py3-none-any.whl.metadata (2.1 kB)
Collecting sse-starlette>=3.0.0 (from mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading sse_starlette-3.4.8-py3-none-any.whl.metadata (15 kB)
Collecting starlette>=0.27 (from mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading starlette-1.6.0-py3-none-any.whl.metadata (6.4 kB)
Collecting typing-extensions>=4.13.0 (from mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading typing_extensions-4.16.0-py3-none-any.whl.metadata (3.3 kB)
Collecting typing-inspection>=0.4.1 (from mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading typing_inspection-0.4.4-py3-none-any.whl.metadata (2.6 kB)
Collecting uvicorn>=0.31.1 (from mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading uvicorn-0.52.4-py3-none-any.whl.metadata (6.6 kB)
Collecting psycopg-binary==3.3.5 (from psycopg[binary]<4,>=3.2->mini-commerce-mcp==1.0.0)
  Downloading psycopg_binary-3.3.5-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (2.7 kB)
Collecting annotated-types>=0.6.0 (from pydantic<3,>=2.12->mini-commerce-mcp==1.0.0)
  Downloading annotated_types-0.8.0-py3-none-any.whl.metadata (15 kB)
Collecting pydantic-core==2.46.5 (from pydantic<3,>=2.12->mini-commerce-mcp==1.0.0)
  Downloading pydantic_core-2.46.5-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (6.6 kB)
Collecting iniconfig>=1 (from pytest<9,>=8.4->mini-commerce-mcp==1.0.0)
  Downloading iniconfig-2.3.0-py3-none-any.whl.metadata (2.5 kB)
Collecting packaging>=20 (from pytest<9,>=8.4->mini-commerce-mcp==1.0.0)
  Using cached packaging-26.3-py3-none-any.whl.metadata (3.5 kB)
Collecting pluggy<2,>=1.5 (from pytest<9,>=8.4->mini-commerce-mcp==1.0.0)
  Using cached pluggy-1.6.0-py3-none-any.whl.metadata (4.8 kB)
Collecting pygments>=2.7.2 (from pytest<9,>=8.4->mini-commerce-mcp==1.0.0)
  Downloading pygments-2.21.0-py3-none-any.whl.metadata (2.5 kB)
Collecting idna>=2.8 (from anyio>=4.9->mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading idna-3.19-py3-none-any.whl.metadata (9.2 kB)
Collecting httpcore2==2.12.0 (from httpx2>=2.5.0->mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading httpcore2-2.12.0-py3-none-any.whl.metadata (25 kB)
Collecting truststore>=0.10 (from httpx2>=2.5.0->mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading truststore-0.10.4-py3-none-any.whl.metadata (4.4 kB)
Collecting h11>=0.16 (from httpcore2==2.12.0->httpx2>=2.5.0->mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading h11-0.16.0-py3-none-any.whl.metadata (8.3 kB)
Collecting attrs>=22.2.0 (from jsonschema>=4.20.0->mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading attrs-26.1.0-py3-none-any.whl.metadata (8.8 kB)
Collecting jsonschema-specifications>=2023.03.6 (from jsonschema>=4.20.0->mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading jsonschema_specifications-2025.9.1-py3-none-any.whl.metadata (2.9 kB)
Collecting referencing>=0.28.4 (from jsonschema>=4.20.0->mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading referencing-0.37.0-py3-none-any.whl.metadata (2.8 kB)
Collecting rpds-py>=0.25.0 (from jsonschema>=4.20.0->mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading rpds_py-2026.6.3-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (4.1 kB)
Collecting cryptography>=3.4.0 (from pyjwt[crypto]>=2.10.1->mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading cryptography-50.0.1-cp311-abi3-manylinux_2_34_x86_64.whl.metadata (4.3 kB)
Collecting cffi>=2.0.0 (from cryptography>=3.4.0->pyjwt[crypto]>=2.10.1->mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading cffi-2.1.1-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (2.5 kB)
Collecting pycparser (from cffi>=2.0.0->cryptography>=3.4.0->pyjwt[crypto]>=2.10.1->mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading pycparser-3.0-py3-none-any.whl.metadata (8.2 kB)
Collecting click>=7.0 (from uvicorn>=0.31.1->mcp==2.1.1->mini-commerce-mcp==1.0.0)
  Downloading click-8.5.0-py3-none-any.whl.metadata (2.6 kB)
Downloading mcp-2.1.1-py3-none-any.whl (357 kB)
Downloading mcp_types-2.1.1-py3-none-any.whl (69 kB)
Downloading psycopg-3.3.5-py3-none-any.whl (213 kB)
Downloading psycopg_binary-3.3.5-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (5.2 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.2/5.2 MB 53.9 MB/s  0:00:00
Downloading pydantic-2.13.5-py3-none-any.whl (472 kB)
Downloading pydantic_core-2.46.5-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (2.1 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.1/2.1 MB 291.1 MB/s  0:00:00
Downloading pytest-8.4.2-py3-none-any.whl (365 kB)
Using cached pluggy-1.6.0-py3-none-any.whl (20 kB)
Downloading annotated_types-0.8.0-py3-none-any.whl (13 kB)
Downloading anyio-4.15.0-py3-none-any.whl (131 kB)
Downloading httpx2-2.12.0-py3-none-any.whl (95 kB)
Downloading httpcore2-2.12.0-py3-none-any.whl (83 kB)
Downloading h11-0.16.0-py3-none-any.whl (37 kB)
Downloading idna-3.19-py3-none-any.whl (68 kB)
Downloading iniconfig-2.3.0-py3-none-any.whl (7.5 kB)
Downloading jsonschema-4.26.0-py3-none-any.whl (90 kB)
Downloading attrs-26.1.0-py3-none-any.whl (67 kB)
Downloading jsonschema_specifications-2025.9.1-py3-none-any.whl (18 kB)
Downloading opentelemetry_api-1.44.0-py3-none-any.whl (60 kB)
Using cached packaging-26.3-py3-none-any.whl (129 kB)
Downloading pygments-2.21.0-py3-none-any.whl (1.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.3/1.3 MB 235.0 MB/s  0:00:00
Downloading pyjwt-2.13.0-py3-none-any.whl (31 kB)
Downloading cryptography-50.0.1-cp311-abi3-manylinux_2_34_x86_64.whl (4.7 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.7/4.7 MB 195.9 MB/s  0:00:00
Downloading cffi-2.1.1-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (221 kB)
Downloading python_multipart-0.0.32-py3-none-any.whl (30 kB)
Downloading referencing-0.37.0-py3-none-any.whl (26 kB)
Downloading rpds_py-2026.6.3-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (365 kB)
Downloading sse_starlette-3.4.8-py3-none-any.whl (16 kB)
Downloading starlette-1.6.0-py3-none-any.whl (75 kB)
Downloading truststore-0.10.4-py3-none-any.whl (18 kB)
Downloading typing_extensions-4.16.0-py3-none-any.whl (45 kB)
Downloading typing_inspection-0.4.4-py3-none-any.whl (14 kB)
Downloading uvicorn-0.52.4-py3-none-any.whl (79 kB)
Downloading click-8.5.0-py3-none-any.whl (125 kB)
Downloading pycparser-3.0-py3-none-any.whl (48 kB)
Building wheels for collected packages: mini-commerce-mcp
  Building editable for mini-commerce-mcp (pyproject.toml): started
  Building editable for mini-commerce-mcp (pyproject.toml): finished with status 'done'
  Created wheel for mini-commerce-mcp: filename=mini_commerce_mcp-1.0.0-py3-none-any.whl size=1537 sha256=14adc8455b06a7fd3dea4c43578da4feefa5f2bbe30e758b8bb1f8acc7e65683
  Stored in directory: /tmp/pip-ephem-wheel-cache-f4bm5nde/wheels/7e/28/d3/d833ac8e2df630274b8307af4e80eba1a5d4c2fd99b9061041
Successfully built mini-commerce-mcp
Installing collected packages: typing-extensions, truststore, rpds-py, python-multipart, pyjwt, pygments, pycparser, psycopg-binary, psycopg, pluggy, packaging, iniconfig, idna, h11, click, attrs, annotated-types, uvicorn, typing-inspection, referencing, pytest, pydantic-core, opentelemetry-api, httpcore2, cffi, anyio, starlette, pydantic, jsonschema-specifications, httpx2, cryptography, sse-starlette, mcp-types, jsonschema, mcp, mini-commerce-mcp

Successfully installed annotated-types-0.8.0 anyio-4.15.0 attrs-26.1.0 cffi-2.1.1 click-8.5.0 cryptography-50.0.1 h11-0.16.0 httpcore2-2.12.0 httpx2-2.12.0 idna-3.19 iniconfig-2.3.0 jsonschema-4.26.0 jsonschema-specifications-2025.9.1 mcp-2.1.1 mcp-types-2.1.1 mini-commerce-mcp-1.0.0 opentelemetry-api-1.44.0 packaging-26.3 pluggy-1.6.0 psycopg-3.3.5 psycopg-binary-3.3.5 pycparser-3.0 pydantic-2.13.5 pydantic-core-2.46.5 pygments-2.21.0 pyjwt-2.13.0 pytest-8.4.2 python-multipart-0.0.32 referencing-0.37.0 rpds-py-2026.6.3 sse-starlette-3.4.8 starlette-1.6.0 truststore-0.10.4 typing-extensions-4.16.0 typing-inspection-0.4.4 uvicorn-0.52.4
......                                                                   [100%]
6 passed in 0.15s
```

## static.log 最后 200 行
```text
Collecting PyYAML==6.0.2
  Downloading PyYAML-6.0.2-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (2.1 kB)
Downloading PyYAML-6.0.2-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (759 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 759.5/759.5 kB 12.9 MB/s  0:00:00
Installing collected packages: PyYAML
Successfully installed PyYAML-6.0.2
{"status": "valid", "project": "mini-commerce"}
{
  "references": 47,
  "errors": []
}
{
  "passed": true,
  "checks": [
    {
      "name": "创建订单请求不接收客户端总价",
      "passed": true,
      "evidence": "OrderDtos.CreateOrderRequest"
    },
    {
      "name": "库存使用数据库条件原子更新",
      "passed": true,
      "evidence": "InventoryRepository"
    },
    {
      "name": "事务 Outbox 存在",
      "passed": true,
      "evidence": "V001"
    },
    {
      "name": "支付跨幂等键有活跃支付唯一索引",
      "passed": true,
      "evidence": "V001"
    },
    {
      "name": "同一支付只有一个全额退款聚合",
      "passed": true,
      "evidence": "V003"
    },
    {
      "name": "MCP 拒绝写 SQL",
      "passed": true,
      "evidence": "security.py"
    },
    {
      "name": "MCP 测试命令使用固定白名单",
      "passed": true,
      "evidence": "tooling.py"
    }
  ]
}
valid-json mini-commerce/DELIVERY-MANIFEST.json
valid-json mini-commerce/infra/observability/grafana/dashboards/mini-commerce.json
valid-json mini-commerce/docs/generated/document-code-map.json
valid-json mini-commerce/docs/generated/source-catalog.json
valid-yaml mini-commerce/ai-engineering/rules/backend-rules.yml
valid-yaml mini-commerce/infra/observability/prometheus.yml
valid-yaml mini-commerce/infra/observability/tempo.yml
valid-yaml mini-commerce/infra/observability/otel-collector.yml
valid-yaml mini-commerce/infra/observability/alerts.yml
valid-yaml mini-commerce/infra/observability/grafana/provisioning/datasources/datasources.yml
valid-yaml mini-commerce/infra/observability/grafana/provisioning/dashboards/dashboards.yml
valid-yaml mini-commerce/backend/src/test/resources/application.yml
valid-yaml mini-commerce/backend/src/main/resources/application-test.yml
valid-yaml mini-commerce/backend/src/main/resources/application.yml
valid-yaml mini-commerce/compose.yaml
valid-yaml mini-commerce/api/openapi.yaml
valid-yaml mini-commerce/infra/k8s/secret.example.yaml
valid-yaml mini-commerce/infra/k8s/namespace.yaml
valid-yaml mini-commerce/infra/k8s/configmap.yaml
valid-yaml mini-commerce/infra/k8s/backend.yaml
```
