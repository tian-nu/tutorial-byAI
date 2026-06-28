# 附录C：HTTP状态码对照表

> 状态码首位定义类别：`1xx` 信息、`2xx` 成功、`3xx` 重定向、`4xx` 客户端错误、`5xx` 服务端错误。表格中 ⭐ 标记为重点展开状态码。

---

## C.1 1xx — 信息响应（Informational）

| 状态码 | 名称 | 含义 | 排错提示 |
|:---:|------|------|------|
| 100 | Continue | 客户端应继续发送请求体 | 服务器已收到请求头，等待body |
| 101 | Switching Protocols | 协议切换（如 WebSocket 握手） | 检查 `Upgrade` 头是否正确 |
| 102 | Processing | WebDAV：服务器正在处理，尚未完成 | 轮询等待完成 |
| 103 | Early Hints | 在最终响应前预发送 `Link` 头 | 浏览器预加载优化，非必要 |

---

## C.2 2xx — 成功响应（Success）⭐

| 状态码 | 名称 | 含义 | 排错提示 |
|:---:|------|------|------|
| ⭐ **200** | OK | 请求成功，返回所请求数据 | 最通用成功状态。GET 返回资源、POST 返回处理结果 |
| 201 | Created | 资源已创建（常用于 POST 请求后返回新资源URL） | 应在 `Location` 头中返回新资源URI |
| 202 | Accepted | 请求已接受但尚未处理（异步任务） | 通常用于批量/异步处理，客户端需轮询或通过Webhook获取结果 |
| 203 | Non-Authoritative Information | 返回的元信息来自缓存/代理，非原始服务器 | 内容可能不是最新，需确认缓存策略 |
| 204 | No Content | 成功但无响应体（保存/删除后常见） | DELETE请求常见返回，前端不应刷新页面内容 |
| 205 | Reset Content | 要求客户端重置表单 | 清除用户输入 |
| 206 | Partial Content | 返回部分内容（断点续传/视频拖动） | 检查 `Range` 和 `Content-Range` 头 |

---

## C.3 3xx — 重定向（Redirection）⭐

| 状态码 | 名称 | 含义 | 排错提示 |
|:---:|------|------|------|
| ⭐ **301** | Moved Permanently | 永久重定向，浏览器会缓存，下次直接跳新URL | 已迁移的URL返回301；注意浏览器会硬缓存，调试时需清缓存或开无痕模式 |
| ⭐ **302** | Found（原Moved Temporarily） | 临时重定向，浏览器不缓存 | 常见于登录后跳转；搜索引擎继续索引原URL |
| 303 | See Other | 响应在另一个URI（GET方法获取） | POST 后重定向到结果页（PRG模式） |
| ⭐ **304** | Not Modified | 资源未修改，使用本地缓存 | 由 `If-Modified-Since` / `If-None-Match` 触发，不传body，节省带宽 |
| 307 | Temporary Redirect | 临时重定向，且**必须保持原方法**（POST不变为GET） | 与302的关键区别：不改变请求方法 |
| 308 | Permanent Redirect | 永久重定向，且**必须保持原方法** | 与301的关键区别：不改变请求方法 |

> **301 vs 302 排错要点**：浏览器301缓存很难清除。调错URL时请用**浏览器无痕模式**，或 `curl -v` 直接查看。

---

## C.4 4xx — 客户端错误（Client Error）⭐

| 状态码 | 名称 | 含义 | 排错提示 |
|:---:|------|------|------|
| ⭐ **400** | Bad Request | 请求格式错误/参数不合法 | 检查JSON格式、参数类型、必填字段；常见于 API 调用时 body 不对 |
| ⭐ **401** | Unauthorized | 需要认证（未登录/Token过期） | 检查 `Authorization` 头、Token 是否过期、Cookie 中 session 是否存在 |
| 402 | Payment Required | 保留供未来使用（付费内容） | 极少出现 |
| ⭐ **403** | Forbidden | 已认证但没有权限访问 | 与401区别：身份已知但无权限；检查角色/权限配置、CORS策略 |
| ⭐ **404** | Not Found | 资源不存在（URL写错/资源已删除） | 最常见的排错入口：检查URL拼写、路由配置、动态路由参数 |
| ⭐ **405** | Method Not Allowed | HTTP方法不支持（如只允许GET却用了POST） | 检查 `Allow` 响应头看支持哪些方法；常见于 REST API 路由配置错误 |
| 406 | Not Acceptable | 客户端要求的格式服务器无法提供 | 检查 `Accept` 请求头是否合理 |
| 408 | Request Timeout | 客户端发送请求超时，服务器主动断开 | 提升客户端超时阈值或检查网络延迟 |
| 409 | Conflict | 资源冲突（并发编辑/重复创建） | 常见于 PUT 更新同一资源；实现乐观锁（ETag/版本号） |
| 410 | Gone | 资源永久删除，不会再恢复 | 比404更确定，搜索引擎会删除索引 |
| 411 | Length Required | 缺少 `Content-Length` 头 | 补充 Content-Length 头 |
| 413 | Payload Too Large | 请求体过大 | 增大服务器 `client_max_body_size`（Nginx）/ 检查上传限制 |
| 414 | URI Too Long | URL 过长 | GET请求参数过多，改用POST；避免嵌套超深的路由 |
| 415 | Unsupported Media Type | `Content-Type` 不支持 | 检查是否为 `application/json` / `multipart/form-data` |
| 422 | Unprocessable Entity | 语义错误（格式正确但业务逻辑不通过） | 多见于表单验证失败，检查返回的错误详情 |
| 429 | Too Many Requests | 请求频率超限（触发限流） | 检查 `Retry-After` 头，降低请求频率，使用指数退避重试 |

---

## C.5 5xx — 服务端错误（Server Error）⭐

| 状态码 | 名称 | 含义 | 排错提示 |
|:---:|------|------|------|
| ⭐ **500** | Internal Server Error | 服务器内部错误（通用） | 查服务端日志！通常由未捕获异常、配置错误、依赖服务不可用引起 |
| 501 | Not Implemented | 服务器不支持该功能 | 检查反向代理是否正确转发；API 版本是否匹配 |
| ⭐ **502** | Bad Gateway | 网关/代理收到后端无效响应 | 检查上游服务是否运行；Nginx 到应用服务是否通；应用是否崩了 |
| ⭐ **503** | Service Unavailable | 服务暂时不可用（过载/维护） | 检查 `Retry-After` 头；排查是否触发熔断；服务器是否被打满 |
| ⭐ **504** | Gateway Timeout | 网关等待上游响应超时 | 增 `proxy_read_timeout`（Nginx）；检查上游处理耗时（慢SQL/死循环） |
| 505 | HTTP Version Not Supported | 不支持的HTTP版本 | 极少见，检查客户端HTTP版本设置 |

---

## C.6 常见排错流程速查

| 看到的状态码 | 第一反应 |
|:---:|------|
| 200 | 正常 |
| 301/302 | 清浏览器缓存或用 `curl -v` 查看跳转链 |
| 304 | 正常缓存行为，不是错误 |
| 400 | 检查请求参数格式 |
| 401 | 检查Token/登录状态 |
| 403 | 检查权限和CORS |
| 404 | 检查URL和资源是否存在 |
| 405 | 检查HTTP方法和路由配置 |
| 500 | **查服务器日志！** |
| 502 | 检查上游服务是否运行 |
| 503 | 检查服务器负载和熔断状态 |
| 504 | 检查上下游超时配置 |