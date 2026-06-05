# 全局术语索引

> 本文件为系列教程的全局术语索引，按字母顺序排列。每个教程新增术语时同步更新此文件。

| 术语 | 简要解释 | 出处教程 | 是否项目特有 |
|------|----------|----------|-------------|
| Bearer | OAuth 2.0 规范中的 token 类型。意思是"持票人"——谁持有 token，谁就是对应的用户。请求时放在 HTTP Header 里：`Authorization: Bearer <token>`。 | 15-用户登录+JWT认证 | 否（OAuth 2.0 标准） |
| Header | JWT 的第一部分，描述签名算法和 token 类型。就像手环上写的"材质说明"。 | 15-用户登录+JWT认证 | 否（JWT 标准） |
| HS256 | HMAC-SHA256，JWT 最常用的签名算法。对称加密——签发和验证用同一把密钥。 | 15-用户登录+JWT认证 | 否（密码学） |
| HTTPException | FastAPI 内置异常类，用于返回 HTTP 错误状态码（如 401 未授权）。 | 14-用户注册、15-用户登录+JWT认证 | 否（FastAPI 术语） |
| httpOnly cookie | 一种浏览器 cookie 属性。设置了 `httpOnly` 后，JavaScript 代码无法读取，只能由浏览器自动携带。防 XSS 偷 token 的重要手段。 | 15-用户登录+JWT认证 | 否（Web 安全） |
| iat | issued at，JWT 标准字段，token 的签发时间（Unix 时间戳）。 | 15-用户登录+JWT认证 | 否（JWT 标准） |
| jwt.io | JWT 官方提供的在线调试工具。可以粘贴 token 在线解码 Header 和 Payload，验证签名。仅用于学习和调试，不要粘贴生产环境 token。 | 15-用户登录+JWT认证 | 否（工具网站） |
| JWT | JSON Web Token，"游乐园手环"——登录后服务端给你的一个凭证，之后每次请求出示它就行，不用再传密码。由三部分组成：Header.Payload.Signature。 | 15-用户登录+JWT认证 | 否（通用标准） |
| JWTError | `python-jose` 库中的异常类。当 token 无效、过期、签名不匹配时抛出。 | 15-用户登录+JWT认证 | 否（python-jose 术语） |
| Payload | JWT 的第二部分，存放实际数据（用户 ID、用户名、过期时间等）。是 Base64 编码，不是加密，任何人都能解码看到内容。 | 15-用户登录+JWT认证 | 否（JWT 标准） |
| SECRET_KEY | JWT 签名用的密钥。服务端用它来签发和验证 token。必须保密，泄露后任何人都能伪造 token。生产环境建议用环境变量存储。 | 15-用户登录+JWT认证 | 否（安全概念） |
| Signature | JWT 的第三部分，签名。用 Header + Payload + 密钥通过 HMAC-SHA256 算出来的。防篡改的核心——你改了 Payload，签名就对不上。 | 15-用户登录+JWT认证 | 否（JWT 标准） |
| sub | subject，JWT 标准字段，表示"主题"——通常放用户 ID。解码出 `sub` 就知道 token 属于哪个用户。 | 15-用户登录+JWT认证 | 否（JWT 标准） |
| XSS | Cross-Site Scripting，跨站脚本攻击。攻击者注入恶意 JavaScript 代码，可以读取 localStorage 里的 token。这就是为什么 token 不能存 localStorage。 | 15-用户登录+JWT认证 | 否（Web 安全） |
| exp | expiration，JWT 标准字段，token 的有效截止时间。过了这个时间，token 自动失效。默认为 30 分钟。 | 15-用户登录+JWT认证 | 否（JWT 标准） |
| token | 令牌、凭证。JWT 是一种 token。拿到了 token 就相当于拿到了"我是 XXX 用户"的证明。 | 15-用户登录+JWT认证 | 否（通用概念） |
| 中间件 | 在请求到达接口函数之前/之后执行的函数，对所有请求生效。快递站安检机的比喻。 | 08-中间件 | 否（通用 Web 概念） |
| 限流 | 限制客户端在单位时间内的请求次数，防攻击/防过载。 | 08-中间件 | 否（通用概念） |
| 依赖注入 | 接口声明自己需要什么，框架自动传入。与中间件区别：按需注入而非全局生效。 | 08-中间件、16-权限保护 | 否（设计模式） |
| 429 状态码 | "Too Many Requests"，HTTP 状态码，用于限流场景。 | 08-中间件 | 否（HTTP 标准） |
| 洋葱模型 | 描述中间件执行顺序的比喻：请求从外到内，响应从内到外。 | 08-中间件 | 否（通用概念） |
| 数据库 | 持久化存储数据的容器，类比 Excel 文件。程序重启后数据不丢。 | 09-数据库入门 | 否（通用概念） |
| SQLite | 轻量级嵌入式数据库，零配置，一个文件即整个数据库，Python 自带。 | 09-数据库入门 | 否（通用数据库） |
| 表 | 数据库中一类数据的集合，类比 Excel 的一个 Sheet。 | 09-数据库入门 | 否（通用概念） |
| 行 | 表中的一条记录，类比 Excel 的一行。 | 09-数据库入门 | 否（通用概念） |
| 列 | 表中的一个属性字段，类比 Excel 的一列。 | 09-数据库入门 | 否（通用概念） |
| CREATE TABLE | SQL 建表语句，定义表结构和列类型。 | 09-数据库入门 | 否（SQL 标准） |
| INSERT INTO | SQL 插入语句，向表中新增一行数据。 | 09-数据库入门 | 否（SQL 标准） |
| SELECT | SQL 查询语句，从表中读取数据。 | 09-数据库入门 | 否（SQL 标准） |
| 游标 | Python 中执行 SQL 语句的"光标"，通过 conn.cursor() 创建。 | 09-数据库入门 | 否（Python DB-API） |
| 提交 | 将修改保存到硬盘的操作，Python 中需手动 conn.commit()。 | 09-数据库入门 | 否（数据库通用） |
| 持久化 | 数据保存到硬盘，程序关闭后不丢失，与"内存存储"相对。 | 09-数据库入门 | 否（通用概念） |
| ORM | 对象关系映射：用 Python 对象操作数据，自动翻译成 SQL。比喻为"翻译官"。 | 12-后端连数据库 | 否（通用概念） |
| SQLAlchemy | Python 最流行的 ORM 库，负责 Python 对象与数据库之间的翻译。 | 12-后端连数据库 | 是（选型） |
| engine | SQLAlchemy 核心组件，负责与数据库建立连接、管理连接池。比喻为"电话"。 | 12-后端连数据库 | 否（SQLAlchemy 术语） |
| Session | SQLAlchemy 中与数据库交互的"工作单元"，查询、增删改都在其中进行。比喻为"临时工位"。 | 12-后端连数据库 | 否（SQLAlchemy 术语） |
| relationship | SQLAlchemy 中定义对象间关联的方法，不改变表结构，只影响 Python 对象行为。 | 12-后端连数据库 | 否（SQLAlchemy 术语） |
| back_populates | relationship 参数，用于建立双向导航。两个关联类的值必须互相匹配。 | 12-后端连数据库 | 否（SQLAlchemy 术语） |
| commit | 提交事务：把待办操作真正写入数据库。不 commit 数据就丢了。 | 12-后端连数据库 | 否（数据库通用概念） |
| 外键（Foreign Key） | 数据库概念：一张表的列指向另一张表的主键，建立表间关联。身份证号校验器的比喻。 | 10-建表、12-后端连数据库 | 否（数据库通用概念） |
| 数据完整性（Data Integrity） | 数据在存储后仍然准确、一致、没有逻辑矛盾。外键约束是保证手段之一。 | 10-建表 | 否（数据库通用概念） |
| 建表语句（CREATE TABLE） | SQL 中创建新表的命令，定义表结构（列名、类型、约束）。 | 10-建表 | 否（SQL 标准） |
| 表关系（Table Relationship） | 表与表之间通过外键建立的联系，如一对多（一个用户→多篇文章）。 | 10-建表 | 否（数据库通用概念） |
| 密码哈希（Password Hash） | 把密码原文通过数学算法变成"乱码"，无法反推。数据库存哈希不存明文。 | 10-建表 | 否（安全通用概念） |
| 主键（Primary Key） | 表中每行数据的唯一标识，如身份证号。SQLite 中用 INTEGER PRIMARY KEY。 | 10-建表 | 否（数据库通用概念） |
| SQLite | 零配置轻量数据库，数据存为单个 .db 文件，无需安装服务器。 | 12-后端连数据库 | 是（选型） |
| 持久化 | 把数据存到硬盘上，程序重启后数据还在。 | 12-后端连数据库、13-博客接口升级 | 否（通用概念） |
| query | SQLAlchemy ORM 的查询入口，`db.query(Model)` 表示查询某个模型对应的表。 | 13-博客接口升级 | 否（SQLAlchemy 术语） |
| filter | SQLAlchemy 查询中的过滤条件，只保留满足条件的行。 | 13-博客接口升级 | 否（SQLAlchemy 术语） |
| add | 把新建的 ORM 对象添加到数据库会话，准备插入。需配合 commit 才真正写入。 | 13-博客接口升级 | 否（SQLAlchemy 术语） |
| refresh | 从数据库重新读取对象数据，用于获取数据库自动生成的字段（如自增 ID）。 | 13-博客接口升级 | 否（SQLAlchemy 术语） |
| delete | 标记一个 ORM 对象为删除，需调用 commit 才真正从数据库删掉。 | 13-博客接口升级 | 否（SQLAlchemy 术语） |
| UPDATE | SQL 中用来修改已有数据的语句，不加 WHERE 会修改全表。 | 11-SQL 增删改查实战 | 否（SQL 标准） |
| DELETE | SQL 中用来删除数据的语句，不加 WHERE 会清空整张表。 | 11-SQL 增删改查实战 | 否（SQL 标准） |
| WHERE | SQL 中的条件过滤子句，指定操作哪些行。UPDATE/DELETE 不加 WHERE 等于灾难。 | 11-SQL 增删改查实战 | 否（SQL 标准） |
| ORDER BY | SQL 中的排序子句，ASC 升序，DESC 降序。排序是临时的，不改变数据存储。 | 11-SQL 增删改查实战 | 否（SQL 标准） |
| JOIN | SQL 中的联表查询，将多张表按关联条件拼接后一起查询。 | 11-SQL 增删改查实战 | 否（SQL 标准） |
| 联表查询 | JOIN 的中文翻译，将多张表的数据按关联条件合并查询。 | 11-SQL 增删改查实战 | 否（数据库通用概念） |
| 聚合函数 | 将多行数据压缩为一个值的函数，如 COUNT(*), SUM(), AVG()。 | 11-SQL 增删改查实战 | 否（数据库通用概念） |
| LIMIT | SQL 中限制返回行数的子句，LIMIT 5 表示只返回前 5 行。 | 11-SQL 增删改查实战 | 否（SQL 标准） |
| OAuth2PasswordBearer | FastAPI 内置的"门禁刷卡器"，从请求的 `Authorization` 头中提取 Bearer token。`tokenUrl` 参数告诉客户端去哪里登录拿 token。 | 16-权限保护 | 否（FastAPI 术语） |
| 401 Unauthorized | HTTP 状态码，表示"未授权"——客户端没有提供有效的身份凭证。 | 16-权限保护 | 否（HTTP 标准） |
| Authorization Header | HTTP 请求头，格式为 `Authorization: Bearer <token>`，用来携带身份凭证。 | 16-权限保护 | 否（HTTP 标准） |
| Bearer Token | "持有者令牌"：谁持有这个 token，谁就有相应的权限。Bearer 的意思是"出示即认可"。 | 16-权限保护 | 否（HTTP 标准） |
| JWTError | `python-jose` 库的异常，表示 JWT 解码失败（签名不对、过期、格式错误等）。 | 16-权限保护 | 否（python-jose 术语） |
| sub（subject） | JWT 标准字段之一，表示"主题"——token 代表谁，通常放用户名或用户 ID。 | 16-权限保护 | 否（JWT 标准） |
| 403 Forbidden | HTTP 状态码，表示"服务器知道你是谁，但你不被允许执行这个操作"。与 401 的区别：401 是"不知道你是谁"，403 是"知道你是谁但不让你做"。 | 17-文章归属 | 否（HTTP 标准） |
| 所有权检查 | Ownership Check：在操作资源之前，检查当前用户是否是该资源的拥有者（作者/创建者）。是则放行，否则拒绝。 | 17-文章归属 | 否（安全通用概念） |
| RBAC | Role-Based Access Control：基于角色的访问控制。不直接给人分配权限，而是给角色分配权限，再把人分配到角色。 | 17-文章归属 | 否（安全通用概念） |
| check_owner(obj, current_user) | 本教程封装的所有权检查函数，检查 `obj.author_id` 是否等于 `current_user.id`，不匹配则抛出 403。可复用于任何有 `author_id` 属性的对象。 | 17-文章归属 | 是（项目特有） |
| echo | SQLAlchemy `create_engine` 的参数。设为 `True` 后，每次数据库查询都会在终端打印 SQL 语句和参数。后端开发的"透视镜"。上线前必须关掉。 | 19-一对多关系深入 | 否（SQLAlchemy 术语） |
| joinedload | SQLAlchemy 的预加载策略之一。用 `LEFT OUTER JOIN` 一次性把主表和关联表的数据都查出来，1 次查询搞定。适合"多对一"（如查文章带作者）。 | 19-一对多关系深入 | 否（SQLAlchemy 术语） |
| LEFT OUTER JOIN | SQL 的一种 JOIN 类型。以左表为主，右表有匹配就填上，没有匹配就填 NULL。保证左表数据不丢失。`joinedload` 默认使用这种 JOIN。 | 19-一对多关系深入 | 否（SQL 标准） |
| N+1 问题 | N+1 Problem：查 N 条主记录，然后每条主记录触发一次关联查询，总共 N+1 次查询。典型的性能陷阱。就像先拿名单，然后给每个人打电话问电话号码。 | 19-一对多关系深入 | 否（数据库通用概念） |
| 孤儿记录 | Orphan Record：数据库中存在但无法通过正常关联路径访问到的记录。比如 `post_id` 为 NULL 的评论——它属于哪篇文章？不知道。通常由忘记设置外键字段导致。 | 18-评论功能 | 否（数据库通用概念） |
| 结果集膨胀 | Result Set Bloat：一对多关系用 JOIN 时，主表数据在每行 JOIN 结果中重复，导致传输数据量增大。就像把同一篇文章复制了 N 遍（每条评论复制一遍）。 | 19-一对多关系深入 | 否（数据库通用概念） |
| 懒加载 | Lazy Loading：SQLAlchemy 默认行为——你不访问关联属性（如 `post.comments`），就不去数据库查。第一次访问时才查。好处是省查询，坏处是可能造成 N+1 问题。 | 18-评论功能、19-一对多关系深入 | 否（SQLAlchemy 术语） |
| 嵌套返回 | Nested Response：把关联数据（如评论）嵌在主数据（如文章）的 JSON 里一起返回，而不是让客户端发两次请求。就像快递包裹里附带清单。 | 18-评论功能 | 否（API 设计概念） |
| selectinload | SQLAlchemy 的预加载策略之一。先查主表，再用 `WHERE id IN (...)` 一次性查所有关联数据，2 次查询搞定。适合"一对多"（如查文章带评论列表），避免 JOIN 结果集膨胀。 | 19-一对多关系深入 | 否（SQLAlchemy 术语） |
| 测试金字塔 | Test Pyramid：测试分层模型，底层单元测试（多、快），中层集成测试（中），顶层 E2E 测试（少、慢）。指导写测试时的比例分配。 | 24-为什么要写测试 | 否（测试通用概念） |
| 单元测试 | Unit Test：测试单个函数/方法的逻辑，不涉及外部依赖（数据库、网络等）。快、多、稳定。 | 24-为什么要写测试 | 否（测试通用概念） |
| 集成测试 | Integration Test：测试多个模块协作的完整链路，如发 HTTP 请求 → 路由 → 数据库 → 返回响应。 | 24-为什么要写测试 | 否（测试通用概念） |
| E2E 测试 | End-to-End Test：端到端测试，模拟真实用户操作整个应用。最慢，最接近真实场景。 | 24-为什么要写测试 | 否（测试通用概念） |
| pytest | Python 最流行的测试框架。自动发现 `test_*.py` 文件中的 `test_*` 函数，运行并输出结果。支持丰富的插件生态。 | 24-为什么要写测试 | 否（测试框架） |
| httpx | 支持异步的 Python HTTP 客户端库。在 FastAPI 测试中用于向应用发 HTTP 请求，与 TestClient 配合使用。 | 24-为什么要写测试 | 否（Python 库） |
| TestClient | FastAPI 自带的测试客户端。不需要启动真实服务器，在内存中直接与 FastAPI app 交互。 | 24-为什么要写测试 | 否（FastAPI 术语） |
| 断言（assertion） | 程序中的"我认为某件事一定为真"的声明。`assert a == b` 表示断言 a 等于 b，不成立则 `AssertionError`，测试失败。 | 24-为什么要写测试 | 否（编程通用概念） |
| fixture | pytest 的核心机制，`@pytest.fixture` 装饰的函数。测试前自动准备环境（setup），测试后自动清理（teardown）。比喻：每次考试前自动发空白试卷。 | 25-为博客API写测试 | 否（pytest 术语） |
| conftest.py | pytest 的特殊文件名，放在测试目录下。pytest 自动加载其中的 fixture，同目录的所有测试文件共享。 | 25-为博客API写测试 | 否（pytest 术语） |
| dependency_overrides | FastAPI 的依赖替换机制。`app.dependency_overrides[原依赖] = 新依赖`，常用于测试中把数据库连接替换为测试数据库。 | 25-为博客API写测试 | 否（FastAPI 术语） |
| 测试数据库 | Test Database：独立于开发数据库的数据库文件（如 `test_blog.db`）。测试数据写入这里，不影响开发数据。 | 25-为博客API写测试 | 否（测试通用概念） |
| 覆盖率（Code Coverage） | 衡量"测试代码执行了多少行业务代码"的指标。80%+ 及格，90%+ 良好。`pytest-cov` 可统计。 | 25-为博客API写测试 | 否（测试通用概念） |
| pytest-cov | pytest 的覆盖率插件。`pip install pytest-cov` 安装后，用 `--cov=包名` 参数自动统计代码覆盖率。 | 25-为博客API写测试 | 否（pytest 插件） |