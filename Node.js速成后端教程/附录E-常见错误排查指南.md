# 附录E：常见错误排查指南

> 本附录按章节编号索引，收录教程中所有标注的常见错误，以及额外收录的部署阶段常见错误。每个错误包含：错误信息 → 可能原因 → 解决方案。

---

## 第 01 章：环境搭建

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E01-1 | `node: command not found` | Node.js 未安装或未添加到 PATH | 重新安装 Node.js（从 [nodejs.org](https://nodejs.org) 下载 LTS 版本），安装时勾选"Add to PATH" |
| E01-2 | `npm: command not found` | npm 随 Node.js 一起安装，同上 | 同上 |
| E01-3 | `node -v` 显示的版本 < 18 | 安装了旧版本 | 下载 Node.js 18 LTS 重新安装，或用 nvm 切换版本 |

---

## 第 02 章：你的第一个后端程序

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E02-1 | `Cannot find module 'express'` | 未安装 express | 在项目目录下运行 `npm install express` |
| E02-2 | `Error: listen EADDRINUSE :::3000` | 端口 3000 已被占用（可能另一个终端还在运行旧服务器） | 关闭占用端口的进程：`npx kill-port 3000`，或改用其他端口 |
| E02-3 | `npm start` 报 `missing script: start` | `package.json` 中没有 `"start"` 脚本 | 在 `scripts` 中添加 `"start": "node server.js"` |
| E02-4 | `document is not defined` | 在 Node.js 中使用了浏览器 API（如 `document`、`window`） | Node.js 是服务器环境，没有 DOM。去掉浏览器专属代码 |

---

## 第 03 章：请求与响应

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E03-1 | Thunder Client 请求后一直转圈 | 服务器未启动，或 URL 拼写错误 | 确认 `npm run dev` 正在运行，检查 URL 是否正确（`http://localhost:3000`） |
| E03-2 | `Cannot GET /api/articles` | 路由未定义 | 确认 `server.js` 中已挂载该路由，或检查路由文件路径是否正确 |

---

## 第 04 章：模块系统

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E04-1 | `Cannot find module './routes/articles'` | 文件路径错误或文件不存在 | 检查文件是否存在，`require` 路径是否正确（相对路径从当前文件算起） |
| E04-2 | `xxx is not a function` | 导入方式与导出方式不匹配 | 确认 `module.exports` 导出的是什么（对象/函数/值），`require` 时用对应的方式接收 |
| E04-3 | `require` 路径大小写不一致 | Windows 不区分大小写但 Linux/Mac 区分 | 始终用与文件名完全一致的大小写（建议全部小写） |

---

## 第 05 章：路由

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E05-1 | POST 请求返回 404 | 路由定义用的是 GET 方法 | 检查 `router.get` 和 `router.post` 是否正确 |
| E05-2 | `req.params.id` 是 `undefined` | URL 中没有定义路由参数 | 路由路径应写成 `/articles/:id`，不是 `/articles/id` |

---

## 第 06 章：中间件

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E06-1 | 请求一直转圈，最终超时 | 中间件中忘了调用 `next()` | 在中间件函数末尾添加 `next()` |
| E06-2 | `req.body` 是 `undefined` | 未配置 `express.json()` 中间件 | 在路由之前添加 `app.use(express.json())` |
| E06-3 | `Cannot find module 'morgan'` | 未安装 morgan | `npm install morgan` |
| E06-4 | `Cannot find module 'cors'` | 未安装 cors | `npm install cors` |

---

## 第 07 章：请求与响应深入

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E07-1 | POST 请求 `req.body` 为空对象 `{}` | 请求头 `Content-Type` 未设置或设置错误 | 设置 `Content-Type: application/json` |
| E07-2 | `req.body` 是 `undefined` | `express.json()` 放在路由之后 | 中间件顺序：`app.use(express.json())` 必须在路由之前 |

---

## 第 08 章：返回 JSON 与统一错误处理

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E08-1 | `AppError is not defined` | 忘了 `require('../utils/AppError')` | 在路由文件顶部添加 `const AppError = require('../utils/AppError')` |
| E08-2 | 错误处理中间件没有执行 | 错误处理中间件没有 4 个参数 | Express 通过参数数量识别错误处理中间件：必须是 `(err, req, res, next)` |
| E08-3 | 404 兜底没有生效 | 404 兜底放在路由之前 | 404 兜底必须放在所有路由之后 |
| E08-4 | Express 默认 HTML 错误页出现 | 全局错误处理中间件未挂载或参数数量不对 | 确认 `app.use(errorHandler)` 在 404 兜底之后，且 `errorHandler` 有 4 个参数 |

---

## 第 09 章：博客文章 CRUD（内存版）

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E09-1 | POST 创建文章后 `id` 不存在 | 忘了用 `crypto.randomUUID()` 生成 ID | 在创建时添加 `id: crypto.randomUUID()` |
| E09-2 | PUT 更新文章后旧数据还在 | 用了 `articles.push()` 而不是找到原对象修改 | 用 `findIndex` 找到索引，然后 `articles[index] = { ...articles[index], ...updateData }` |
| E09-3 | 重启服务器后文章消失 | 数据存在内存中（数组），重启即丢失 | 这是正常的——内存存储的致命缺陷，第 14 章会升级为数据库存储 |

---

## 第 10 章：异步编程（一）

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E10-1 | Promise 结果是 `Promise { <pending> }` | 忘了 `await` 或 `.then()` | 添加 `await` 或使用 `.then()` 处理 Promise |
| E10-2 | `UnhandledPromiseRejection` 警告 | Promise 被拒绝但没有 `.catch()` 处理 | 添加 `.catch()` 或在 `async` 函数中用 `try/catch` 包裹 |
| E10-3 | 回调地狱——代码缩进超过 5 层 | 嵌套了太多回调函数 | 改用 Promise 链或 async/await |

---

## 第 11 章：异步编程（二）

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E11-1 | `SyntaxError: await is only valid in async functions` | 在非 async 函数中使用了 `await` | 将外层函数标记为 `async`，或使用 `.then()` |
| E11-2 | `ENOENT: no such file or directory` | 文件路径不存在 | 检查文件路径是否正确，使用 `path.join()` 而非手动拼接 |
| E11-3 | `fs.writeFileSync` 报 `EACCES` | 没有写入权限 | 检查目标目录是否存在且有写入权限 |

---

## 第 12 章：数据库入门

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E12-1 | `Cannot find module 'better-sqlite3'` | 未安装 better-sqlite3 | `npm install better-sqlite3` |
| E12-2 | `node-gyp` 编译错误（Windows） | 缺少 C++ 构建工具 | 用管理员身份运行 `npm install --global windows-build-tools`，或改用 `sql.js`（纯 JS 备选） |
| E12-3 | 数据库文件 `blog.db` 找不到 | 工作目录不对 | 确认 `node` 命令在 `blog-backend/` 目录下执行 |

---

## 第 13 章：建表

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E13-1 | `SQLITE_ERROR: table users already exists` | 表已存在，但没使用 `IF NOT EXISTS` | 建表语句加 `CREATE TABLE IF NOT EXISTS` |
| E13-2 | `SQLITE_CONSTRAINT: FOREIGN KEY constraint failed` | 外键约束失败——插入的数据引用了不存在的父记录 | 确认父表中的 ID 存在后再插入子记录，或开启 `PRAGMA foreign_keys = ON` |
| E13-3 | 外键约束不生效 | SQLite 默认不开启外键约束 | 每次连接数据库后执行 `db.pragma('foreign_keys = ON')` |

---

## 第 14 章：SQL 增删改查实战

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E14-1 | `db.prepare is not a function` | `db` 对象不是 `better-sqlite3` 的 Database 实例 | 确认 `require` 路径正确，`const { db } = require('../database/db')` |
| E14-2 | `stmt.get is not a function` | 忘了在 `db.prepare()` 后调用 `.get()` | `db.prepare(sql).get(params)` 而不是 `db.prepare(sql)` |
| E14-3 | UPDATE 把所有行都改了 | 忘了 `WHERE` 子句 | 永远给 UPDATE 加 WHERE 条件 |
| E14-4 | DELETE 把所有行都删了 | 忘了 `WHERE` 子句 | 永远给 DELETE 加 WHERE 条件 |
| E14-5 | SQL 注入漏洞 | 用字符串拼接构造 SQL | 使用参数化查询：`db.prepare('SELECT ... WHERE id = ?').get(id)` |

---

## 第 15 章：后端连接数据库

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E15-1 | `Cannot find module '../database/db'` | 文件路径拼写错误或文件不存在 | 确认 `database/db.js` 已创建，`require` 路径正确 |
| E15-2 | 路由中 `db` 是 `undefined` | `database/db.js` 中 `module.exports` 没导出 `db` | 确认 `module.exports = { db, initDatabase }` |
| E15-3 | `npm run dev` 启动后 GET /api/articles 返回空数组 | 测试数据未插入 | 运行 `node database/seed.js` |
| E15-4 | 多次 `require` 后 `db` 不是同一个对象 | 不同路径 `require` 导致缓存 key 不同 | 确保所有地方都用相同的路径 `require('../database/db')` |

---

## 第 16 章：博客接口升级

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E16-1 | `changes` 为 0，但文章确实存在 | `WHERE` 条件不匹配（如 ID 类型不匹配） | 确认 `req.params.id` 用 `parseInt()` 转为数字 |
| E16-2 | `lastInsertRowid` 不是预期的值 | 事务中多次插入，只返回最后一次的 ID | 每次 INSERT 后立即保存 `result.lastInsertRowid` |

---

## 第 17 章：用户注册与密码哈希

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E17-1 | `Cannot find module 'bcrypt'` | bcrypt 编译失败，模块未安装 | 改用 `npm install bcryptjs`，代码中 `require('bcryptjs')` |
| E17-2 | `bcrypt.hash is not a function` | 忘了 `require('bcryptjs')` 或拼写错误 | 确认文件顶部有 `const bcrypt = require('bcryptjs')` |
| E17-3 | 注册成功但数据库中 `password_hash` 是 `[object Promise]` | 忘了 `await`——`bcrypt.hash()` 返回 Promise | 改为 `const password_hash = await bcrypt.hash(password, 10)` |
| E17-4 | `Cannot read properties of undefined` | 注册接口返回 500，忘了 `async` | 处理函数改为 `async (req, res) => { ... }` |
| E17-5 | `SQLITE_CONSTRAINT: UNIQUE constraint failed` | 用户名或邮箱重复，但错误处理没生效 | 在 INSERT 之前先检查是否存在 |
| E17-6 | 注册成功但响应里包含 `password_hash` | 用了 `SELECT *` | 改为 `SELECT id, username, email, created_at` 明确列出列 |
| E17-7 | `UNIQUE constraint failed: users.email` 但没有前置检查 | 数据库报错后才知重复，用户体验差 | 在 INSERT 前先用 SELECT 检查邮箱唯一性，返回友好的 409 错误 |

---

## 第 18 章：用户登录与 JWT 认证

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E18-1 | `Cannot find module 'jsonwebtoken'` | 没安装 jsonwebtoken | `npm install jsonwebtoken` |
| E18-2 | `JWT_SECRET is not defined` / `secretOrPrivateKey must have a value` | 没创建 `.env` 文件，或 dotenv 没加载 | 创建 `.env` 文件，确保 `server.js` 顶部有 `require('dotenv').config()` |
| E18-3 | `secretOrPrivateKey must have a value`（即使有 .env） | dotenv 加载顺序错误 | 把 `require('dotenv').config()` 移到 `server.js` 最顶部 |
| E18-4 | 登录始终返回 401 "邮箱或密码错误" | 用户是 seed 脚本创建的，`password_hash` 是 `'hash_placeholder'` | 通过注册接口创建新用户再登录 |
| E18-5 | 登录成功但没有 token 返回 | 忘了 `jwt.sign()` 或拼写错误 | 确认代码中有 `const token = jwt.sign(...)` |
| E18-6 | `bcrypt.compare is not a function` | 忘了 `require('bcryptjs')` 或拼写错误 | 确认文件顶部有 `const bcrypt = require('bcryptjs')` |
| E18-7 | `bcrypt.compare` 报 `data and hash arguments required` | `user.password_hash` 是 `undefined`——用户不存在或 SELECT 没查 `password_hash` | 确认 SELECT 语句包含 `password_hash` 列 |
| E18-8 | `.env` 文件被提交到 Git | 忘了在 `.gitignore` 中加 `.env` | 立即 `git rm --cached .env`，添加 `.env` 到 `.gitignore`，重新提交 |

---

## 第 19 章：权限保护

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E19-1 | `Cannot find module '../middleware/auth'` | 文件路径错误或文件不存在 | 确认 `middleware/auth.js` 已创建 |
| E19-2 | `authenticate is not a function` | 导入方式不对——`auth.js` 导出的是 `{ authenticate }` 对象 | 使用解构导入：`const { authenticate } = require('../middleware/auth')` |
| E19-3 | 带 token 请求仍返回 401 | `Authorization` 头格式不对——忘了 `Bearer ` 前缀或空格 | 格式应为 `Bearer eyJ...`（注意 `Bearer` 后面有一个空格） |
| E19-4 | `jwt.verify` 报 `JsonWebTokenError` | token 被篡改或签名不匹配 | 检查 `JWT_SECRET` 是否正确，token 是否被截断 |
| E19-5 | `jwt.verify` 报 `TokenExpiredError` | token 已过期 | 重新登录获取新 token，或调整 `expiresIn` 参数 |

---

## 第 20 章：文章归属

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E20-1 | 用户可以修改别人的文章 | 未检查 `author_id === req.user.userId` | 在 PUT 和 DELETE 路由中添加归属检查：`if (article.author_id !== req.user.userId) throw new AppError('无权限', 403)` |
| E20-2 | `req.user` 是 `undefined` | 忘了在路由上挂载 `authenticate` 中间件 | 在路由第二个参数加上 `authenticate`：`router.put('/:id', authenticate, (req, res) => ...)` |

---

## 第 21 章：评论功能

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E21-1 | `SQLITE_CONSTRAINT: FOREIGN KEY constraint failed` 插入评论时 | `article_id` 引用不存在的文章 | 在插入评论前检查文章是否存在 |
| E21-2 | 删除文章后评论还在 | 未设置级联删除或未手动删除评论 | 在 `schema.js` 建表时添加 `ON DELETE CASCADE`，或删除文章前先删除其评论 |
| E21-3 | `comment_count` 始终为 0 | 用了 INNER JOIN 而非 LEFT JOIN | 改为 LEFT JOIN——没有评论的文章也应该返回，`comment_count` 为 0 |

---

## 第 22 章：分页

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E22-1 | `page` 为负数时返回空数组 | 未对负数页码做修正 | 添加 `if (page < 1) page = 1` |
| E22-2 | `limit` 为 0 或负数时 SQL 报错 | LIMIT 不能为 0 或负数 | 添加 `if (limit < 1) limit = 1` |
| E22-3 | 用户传 `limit=999999` 导致全表扫描 | 未限制最大 limit | 添加 `if (limit > 100) limit = 100` |
| E22-4 | `totalPages` 计算错误 | 整数除法没有向上取整 | 使用 `Math.ceil(total / limit)` |

---

## 第 23 章：搜索

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E23-1 | 搜索中文返回空结果 | SQLite 的 LIKE 对中文大小写敏感，且不支持全文搜索 | 确认 SQLite 版本支持 UTF-8，或用 `LIKE` 而非 `FULLTEXT` |
| E23-2 | 搜索词为空字符串时 `LIKE '%%'` 匹配所有行 | 未过滤空搜索词 | 添加 `if (search) { ... WHERE ... LIKE ... }` 条件判断 |
| E23-3 | 搜索词含特殊字符（`%`、`_`）导致意外结果 | `%` 和 `_` 是 LIKE 的通配符 | 对搜索词中的通配符做转义：`search.replace(/[%_]/g, '\\$&')` |

---

## 第 24 章：文件上传

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E24-1 | `Cannot find module 'multer'` | 未安装 multer | `npm install multer` |
| E24-2 | `req.file` 是 `undefined` | 表单字段名与 `upload.single('image')` 中的字段名不一致 | 确认前端上传的字段名是 `image` |
| E24-3 | 上传文件成功但 `GET /uploads/xxx.jpg` 返回 404 | 未配置 `express.static` 或路径不对 | 在 `server.js` 中添加 `app.use('/uploads', express.static(path.join(__dirname, 'uploads')))` |
| E24-4 | 上传超大文件成功（应该被拒绝） | 未设置 `limits.fileSize` | multer 默认没有文件大小限制，必须设置 `limits: { fileSize: 5 * 1024 * 1024 }` |
| E24-5 | `uploads/` 目录不存在 | 未创建 uploads 目录 | 创建目录：`mkdir uploads`，或在 multer 配置中自动创建 |
| E24-6 | `LIMIT_FILE_SIZE` 错误返回 500 而非 413 | 未在 multer 错误处理中区分错误码 | 在 `upload.single()` 的回调中检查 `err.code === 'LIMIT_FILE_SIZE'` |
| E24-7 | `uploads/` 目录被提交到 Git | 未加入 `.gitignore` | 在 `.gitignore` 中添加 `uploads/` |

---

## 第 25-26 章：测试

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E25-1 | `Cannot find module 'jest'` | 未安装 Jest | `npm install --save-dev jest` |
| E25-2 | `Cannot find module 'supertest'` | 未安装 supertest | `npm install --save-dev supertest` |
| E25-3 | `npm test` 报 `Your test suite must contain at least one test` | 测试文件为空或没有 `it()`/`test()` 调用 | 确认测试文件中至少有一个 `it(...)` 或 `test(...)` |
| E25-4 | `request(app)` 导致端口 3000 被占用 | 误解 supertest 工作原理（它在内存中运行，不需要端口） | 确保 `server.js` 中 `app.listen` 只在直接运行时执行：`if (require.main === module) { app.listen(...) }` |
| E25-5 | `SQLITE_BUSY: database is locked` | 多个测试同时写入 SQLite | 在 `jest` 命令加 `--runInBand` 串行执行测试 |
| E25-6 | `TypeError: app.address is not a function` | `server.js` 没有导出 `app` | 在 `server.js` 末尾添加 `module.exports = app` |
| E25-7 | 测试数据污染了开发数据库 | 测试使用了同一个 `blog.db` | 创建独立的测试数据库（`test.db`），在 `tests/setup.js` 中配置 |

---

## 部署阶段：常见错误

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E-DEPLOY-1 | `pm2: command not found` | PM2 未安装或未全局安装 | `npm install -g pm2` |
| E-DEPLOY-2 | `nginx: command not found` | Nginx 未安装 | `sudo apt install nginx`（Ubuntu）或 `brew install nginx`（macOS） |
| E-DEPLOY-3 | `502 Bad Gateway`（Nginx 反向代理） | Express 服务未启动或端口不对 | 检查 `pm2 status`确认服务运行，检查 Nginx 配置中的 `proxy_pass` 端口 |
| E-DEPLOY-4 | `docker: command not found` | Docker 未安装 | 安装 Docker Desktop 或 Docker Engine |
| E-DEPLOY-5 | `docker build` 报 `COPY failed: file not found` | Dockerfile 中 `COPY` 路径不对 | 检查 `COPY` 指令的源路径相对于 Dockerfile 所在目录 |
| E-DEPLOY-6 | `docker-compose: command not found` | Docker Compose 未安装 | 新版 Docker Desktop 自带，旧版需单独安装 `docker-compose` |
| E-DEPLOY-7 | 容器内 `blog.db` 数据丢失 | 数据库文件未做数据卷挂载 | 在 `docker-compose.yml` 中添加 `volumes: - ./blog.db:/app/blog.db` |
| E-DEPLOY-8 | HTTPS 证书过期 | Let's Encrypt 证书未自动续期 | 配置 certbot 自动续期：`certbot renew --dry-run` |
| E-DEPLOY-9 | 环境变量在生产环境未生效 | 服务器上未创建 `.env` 文件 | 在服务器上创建 `.env` 文件，或用 PM2 的 `ecosystem.config.js` 注入环境变量 |
| E-DEPLOY-10 | `Error: Cannot find module 'bcrypt'`（生产环境） | 生产环境缺少编译工具 | 改用 `bcryptjs`，或在 Dockerfile 中安装编译依赖 |

---

## 通用错误

| # | 错误信息 | 可能原因 | 解决方案 |
|---|----------|----------|----------|
| E-GEN-1 | `Error: Cannot find module 'xxx'` | 模块未安装或路径拼写错误 | 检查 `require` 路径是否正确，运行 `npm install xxx` 安装缺失模块 |
| E-GEN-2 | `TypeError: xxx is not a function` | 导入方式与导出方式不匹配 | 检查 `module.exports` 导出的是什么，`require` 时用对应的方式 |
| E-GEN-3 | `SyntaxError: Unexpected token` | 语法错误（缺括号、逗号、引号等） | 检查报错行附近的代码，常见：缺 `)`、`}`、`,` |
| E-GEN-4 | 修改代码后不生效 | nodemon 未检测到文件变化，或缓存问题 | 重启 `npm run dev`，或检查 nodemon 配置 |
| E-GEN-5 | `npm install` 报 `EACCES` 权限错误（Linux/macOS） | 使用了 `sudo npm install` 导致权限混乱 | 不要用 `sudo`，改用 nvm 管理 Node.js 版本 |

---

> **更新记录**：2026-06-12 初始版本，收录 60+ 条常见错误，涵盖教程第 01-31 章所有标注的错误及部署阶段常见错误。