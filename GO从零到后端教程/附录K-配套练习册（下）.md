# 附录K：配套练习册（下）—— 第50~115章

> **使用说明**：每章 3~5 道练习，分为「基础练习」与「挑战练习」两级。基础练习检验是否掌握核心知识点；挑战练习（⭐）要求综合运用并独立排查问题。每道题标注预计耗时。参考答案见 **附录P-练习参考答案（下）**。

---

## 第50章 · 数据库基础

### K-50-1 MySQL 安装验证（基础，10min）
在本地完成 MySQL 8.0+ 安装后，执行以下验证步骤并将输出截图保存：
```sql
SELECT VERSION();
SHOW DATABASES;
```
**期望结果**：输出 `8.0.x` 版本号，列出 `information_schema`、`mysql`、`performance_schema`、`sys` 四个系统库。

### K-50-2 创建第一个数据库和表（基础，10min）
编写 SQL，完成：
1. 创建数据库 `practice_db`，字符集 `utf8mb4`，排序规则 `utf8mb4_unicode_ci`
2. 创建表 `users`，包含字段：
   - `id` INT 自增主键
   - `username` VARCHAR(50) NOT NULL
   - `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
3. 插入一条测试数据并查询

### K-50-3 数据库配置排查 ⭐（挑战，20min）
场景：执行 `mysql -u root -p` 报错 `Can't connect to MySQL server on 'localhost' (10061)`。请写出至少 3 种可能原因及对应的解决步骤。

---

## 第51章 · SQL 基础 DDL/DML

### K-51-1 学生表 DDL + DML（基础，15min）
```sql
-- 请写出完整的建表语句
-- 表名：students
-- 字段：id(自增主键)、name(VARCHAR(20), NOT NULL)、age(TINYINT)、gender(ENUM:'M','F')、score(DECIMAL(4,1))
-- 要求：age 默认为 18，score 范围 0~100
```
建表后插入 5 条数据（包含你自己的信息），执行 `SELECT * FROM students` 并截图。

### K-51-2 商品表 CRUD（基础，15min）
```sql
-- 表名：products
-- 字段：id(自增主键)、name(VARCHAR(100))、price(DECIMAL(10,2))、stock(INT DEFAULT 0)
```
执行以下操作：
1. 批量插入 3 条商品
2. 将第二条商品价格上调 10%
3. 删除库存为 0 的商品
4. 查询价格在 50~200 之间的商品

### K-51-3 批量数据生成 ⭐（挑战，30min）
使用一条 INSERT 语句插入 100 条学生记录（可借助存储过程或脚本）。要求 name 格式为 `student_001` ~ `student_100`，score 为 40~100 随机数。**写出完整 SQL**。

---

## 第52章 · SQL 查询

### K-52-1 组合查询（基础，15min）
基于第51章 `students` 表（至少 10 条数据），写出以下查询：
1. 查询 score >= 60 且 gender = 'F' 的学生，按 score 降序排列，取前 3 名
2. 查询 age 在 20~25 之间的学生，按 age 升序、score 降序排列
3. 查询 name 中包含 "张" 的学生

### K-52-2 模糊搜索与分页（基础，15min）
基于 `products` 表（至少 20 条数据），写出：
```sql
-- 1. 搜索商品名包含"手机"的商品，按价格降序，分页每页 5 条，取第 2 页
-- 期望结果格式：列出第 6~10 条匹配商品
-- 2. 统计各类价格区间的商品数量（0~99、100~499、500~999、1000+）
```

### K-52-3 复杂报表查询 ⭐（挑战，30min）
基于 `students` 表（至少 50 条数据），写出 SQL：
1. 查询各性别（M/F）的平均分、最高分、最低分、及格率（score≥60）
2. 查询每个年龄段的平均分（按 18~20、21~23、24+ 分组）
3. 找出 score 比自己年龄相同同学平均分高出 20 分以上的学生

**期望输出示例**：
```
gender | avg_score | max_score | min_score | pass_rate
M      | 72.3      | 98.5      | 35.0      | 0.78
F      | 68.1      | 95.0      | 40.0      | 0.71
```

---

## 第53章 · JOIN

### K-53-1 用户+订单关联查询（基础，20min）
```sql
-- 已有表
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    city VARCHAR(20)
);
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```
要求：
1. 插入至少 5 个用户和 10 条订单（保证有用户无订单、有用户多条订单）
2. 用 INNER JOIN 查询每个用户的总消费金额
3. 用 LEFT JOIN 查询所有用户及其订单数（无订单显示 0）
4. 找出从未下过订单的用户

### K-53-2 LEFT JOIN vs INNER JOIN 区别（基础，10min）
构造两条 SQL（LEFT JOIN 和 INNER JOIN），展示在「某用户无订单」场景下二者结果有何不同。**写出数据、SQL 和对比结论**。

### K-53-3 多表关联报表 ⭐（挑战，30min）
```sql
-- 新增表
CREATE TABLE order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
```
要求：
1. 插入数据构造多商品订单
2. 查询每个用户消费最高的订单详情（用户姓名、订单ID、订单总金额、商品明细）
3. 查询购买过「同一商品 2 次以上」的用户列表

---

## 第54章 · 表设计

### K-54-1 电商系统表结构设计（基础，30min）
设计一套简化电商表结构，至少包含：用户（users）、商品（products）、订单（orders）、订单明细（order_items）。写出完整 DDL，包含：
- 所有字段及类型
- 主键、外键约束
- 必要的索引建议（用注释标注）

### K-54-2 范式判断（基础，15min）
判断以下表是否符合 3NF，如不符合请拆解至 3NF：
```sql
-- 表：employee_orders
-- 字段：order_id, employee_id, employee_name, department, dept_location, product, quantity, price
```
**输出要求**：列出存在的传递依赖和部分依赖，给出拆分后的表结构 DDL。

### K-54-3 反范式设计场景 ⭐（挑战，20min）
场景：一个日活百万的电商首页，需要展示「热销商品排行（商品名 + 销量 + 当前价格）」。每次请求都 JOIN 三张表查询，响应超过 500ms。请设计一个反范式方案，写出新表 DDL 和数据同步策略（用文字描述或伪代码）。

---

## 第55章 · 索引

### K-55-1 EXPLAIN 分析练习（基础，20min）
基于第54章 `orders` 表（至少 10000 条数据），执行以下查询的 EXPLAIN：
```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 5 AND created_at > '2024-01-01';
```
1. 记录未建索引时的 `type`、`rows`、`Extra`
2. 分别添加单列索引 `idx_user_id`、`idx_created_at`，再次 EXPLAIN
3. 添加联合索引 `idx_user_created (user_id, created_at)`，再次 EXPLAIN
4. 对比三次结果，写出最优索引选择及理由

### K-55-2 设计最优索引组合（基础，20min）
```sql
-- 表：logs (id, user_id, action, target_type, target_id, created_at, ip)
-- 高频查询：
--   1. WHERE user_id = ? AND created_at BETWEEN ? AND ?
--   2. WHERE action = ? AND target_type = ?
--   3. WHERE user_id = ? AND action = ? ORDER BY created_at DESC
--   4. WHERE target_type = ? AND target_id = ?
```
请为每种查询设计最优索引，并说明哪些可以合并为联合索引。

### K-55-3 索引失效场景 ⭐（挑战，25min）
构造至少 5 种导致索引失效的 SQL 示例（函数包裹、类型隐式转换、LIKE 前缀通配等），每种附 EXPLAIN 结果对比和修正后的 SQL。

---

## 第56章 · 事务

### K-56-1 转账事务实现（基础，20min）
```sql
-- 表：accounts (id, owner, balance DECIMAL(12,2))
-- 约束：balance >= 0，不允许透支
```
用事务实现转账：从 A 账户转 200 元到 B 账户。要求：
1. 开启事务
2. 检查 A 余额是否充足（不足则回滚）
3. 扣款、加款
4. 提交
写出完整 SQL（含 `START TRANSACTION`、`COMMIT`、`ROLLBACK`）。

### K-56-2 隔离级别实验（基础，20min）
在两个数据库会话中，分别设置 `READ UNCOMMITTED` 和 `REPEATABLE READ` 隔离级别，复现「脏读」和「不可重复读」现象。**记录每一步的 SQL 和结果**。

### K-56-3 事务并发问题 ⭐（挑战，25min）
模拟以下场景并给出解决方案：
1. **丢失更新**：两个事务同时读取 balance=1000，各自加 100 后写回，最终 balance=1100（正确应为 1200）
2. 使用 `SELECT ... FOR UPDATE` 修复，写出完整 SQL

---

## 第57章 · 锁

### K-57-1 模拟死锁（基础，20min）
构造两个事务互相等待对方锁资源的场景。写出完整步骤 SQL（含事务时序标注），并用 `SHOW ENGINE INNODB STATUS` 查看死锁日志。

### K-57-2 乐观锁 vs 悲观锁（基础，25min）
基于 `accounts` 表，分别用乐观锁（version 字段）和悲观锁（`SELECT ... FOR UPDATE`）实现扣款操作。写出对比代码（Go 伪代码或 SQL），分析各自适用场景。

### K-57-3 高并发扣库存 ⭐（挑战，35min）
场景：秒杀活动，库存 100 件，1000 人同时抢购。设计表结构和扣库存逻辑，保证不超卖且性能可接受。写出：
1. 表 DDL
2. 扣库存 SQL / Go 伪代码
3. 为什么不用简单的 `UPDATE ... WHERE stock > 0` 加事务

---

## 第58章 · 优化

### K-58-1 慢查询分析（基础，20min）
开启 MySQL 慢查询日志（`long_query_time = 0.1`），执行以下操作：
1. 向 `logs` 表插入 10 万条数据（可用存储过程）
2. 执行全表扫描查询：`SELECT * FROM logs WHERE ip LIKE '192.168.%'`
3. 查看慢查询日志，找到该条记录
4. 为 `ip` 列添加索引，再次执行，对比耗时

### K-58-2 SQL 改写优化（基础，20min）
将以下低效 SQL 改写为高效版本，用 EXPLAIN 对比：
```sql
-- 原始 SQL（假设 orders 有 100 万行）：
SELECT * FROM orders WHERE YEAR(created_at) = 2024 AND MONTH(created_at) = 6;

SELECT o.*, u.name FROM orders o
LEFT JOIN users u ON u.id = o.user_id
WHERE o.amount > (SELECT AVG(amount) FROM orders);
```
给出改写后的 SQL 和 EXPLAIN 对比。

### K-58-3 综合优化方案 ⭐（挑战，35min）
场景：报表页面需要展示「2024年每月销售额 Top 10 商品」，当前查询耗时 30s。请设计完整的优化方案，包括：
1. 表结构调整（如需要汇总表）
2. 索引设计
3. 查询改写
4. 缓存策略
写出完整 DDL、SQL 和优化思路说明。

---

## 第59章 · Go + MySQL (GORM)

### K-59-1 GORM CRUD 实现（基础，30min）
用 Go + GORM 实现以下功能，写出完整可运行代码：
```go
// 数据结构
type Article struct {
    ID        uint   `gorm:"primaryKey"`
    Title     string `gorm:"size:200;not null"`
    Content   string `gorm:"type:text"`
    Author    string `gorm:"size:50"`
    ViewCount int    `gorm:"default:0"`
    CreatedAt time.Time
}

// 要求实现：
// 1. 自动迁移建表
// 2. Create：插入 3 篇文章
// 3. Read：查询作者为"张三"的所有文章，按 ViewCount 降序
// 4. Update：给所有 ViewCount < 10 的文章增加 5 次浏览
// 5. Delete：软删除作者为"李四"的文章（需添加 DeletedAt 字段）
```
**期望输出**：Go 程序运行截图，展示数据库变更内容。

### K-59-2 连接池配置（基础，15min）
写出 GORM 连接 MySQL 的完整配置代码，包含：
```go
// 要求配置项：
// - MaxOpenConns: 100
// - MaxIdleConns: 10
// - ConnMaxLifetime: 1 小时
// - ConnMaxIdleTime: 10 分钟
```
并写出如何用 `DB.Stats()` 验证连接池配置已生效。

### K-59-3 事务 + 批量操作 ⭐（挑战，30min）
用 GORM 事务实现：批量导入 CSV 格式的文章数据（至少 100 条），要求：
1. 每条记录先检查 title 是否重复（重复则跳过并记录日志）
2. 全部成功则提交，任意一条解析失败则回滚整批
3. 使用 `SavePoint` 实现部分回滚能力

---

## 第60章 · Redis 基础

### K-60-1 Redis 安装与基本操作（基础，15min）
完成 Redis 安装后，在 `redis-cli` 中执行：
```bash
SET user:1 '{"name":"Alice","age":25}'
GET user:1
EXPIRE user:1 60
TTL user:1
INCR visit_count
INCRBY visit_count 10
```
**期望结果**：每条命令的输出截图。

### K-60-2 五种数据类型练习（基础，20min）
分别用 Redis 的 String、Hash、List、Set、SortedSet 实现以下场景：
- String：缓存文章内容（key=`article:1`，值=文章JSON）
- Hash：存储用户信息（key=`user:100`，字段 name/email/age）
- List：最近浏览记录（key=`history:user:1`，保留最近 20 条）
- Set：文章标签（key=`tags:article:1`，标签去重）
- SortedSet：文章排行榜（key=`rank:articles`，按浏览量排序）
写出所有命令和验证命令。

### K-60-3 缓存穿透/击穿/雪崩 ⭐（挑战，30min）
请设计并实现以下三种场景的解决方案（用文字描述 + Go 伪代码）：
1. **缓存穿透**：大量请求查询不存在的 key（如 id=-1）
2. **缓存击穿**：热点 key 过期瞬间大量请求打到 DB
3. **缓存雪崩**：大量 key 同时过期

要求每种方案至少给出一种具体解决策略，并说明优缺点。

---

## 第61章 · Redis 进阶

### K-61-1 分布式锁实现（基础，25min）
用 Go + Redis 实现一个分布式锁，要求：
```go
// 接口：
type RedisLock interface {
    Lock(key string, ttl time.Duration) (bool, error)
    Unlock(key string) error
}
```
要求：
1. 使用 `SET NX EX` 实现加锁
2. Unlock 时用 Lua 脚本验证 value 归属，防止误删
3. 写出完整 Go 代码

### K-61-2 分布式锁防误删 ⭐（挑战，30min）
在 K-61-1 基础上，增加以下能力：
1. **锁续期**（WatchDog）：业务执行时间不确定时自动续期
2. **可重入锁**：同一线程/协程可多次获取同一把锁
3. 写出测试代码：模拟 10 个并发协程争抢同一把锁

---

## 第62章 · Redis 实战

### K-62-1 排行榜系统（基础，25min）
用 Redis SortedSet 实现一个「文章热度排行榜」：
1. 设计 key 结构和 score 计算规则（浏览 1 分、点赞 3 分、评论 5 分）
2. 写出更新分数的命令/代码
3. 查询 Top 10 和某篇文章的排名

### K-62-2 消息队列模拟 ⭐（挑战，25min）
只用 Redis List（`LPUSH` / `BRPOP`）模拟一个简单的消息队列，实现：
1. 生产者向队列投递任务（JSON 格式）
2. 消费者阻塞等待并处理任务
3. 处理失败时重新放回队列（`RPOPLPUSH` 到备份队列）

---

## 第63章 · Go + Redis

### K-63-1 缓存旁路模式实现（基础，30min）
用 Go + go-redis 实现 Cache-Aside 模式：
```go
// 函数签名：
func GetArticle(ctx context.Context, id int64) (*Article, error)
func UpdateArticle(ctx context.Context, art *Article) error
```
要求：
1. 读：先查 Redis，命中返回；未命中查 MySQL，回写 Redis（TTL=10min）
2. 写：先更新 MySQL，再删除 Redis 缓存
3. 处理 Redis 不可用时的降级（直接查 MySQL）

### K-63-2 防缓存击穿 ⭐（挑战，35min）
在 K-63-1 基础上，增加防缓存击穿能力（使用 `singleflight` 或手动实现），确保热点 key 过期时只有一个请求穿透到 MySQL。写出核心代码和并发测试。

---

## 第65章 · RESTful API

### K-65-1 设计 RESTful API 文档（基础，30min）
为一个「博客系统」设计完整的 RESTful API，包含以下资源：
- 文章（articles）：CRUD + 列表分页 + 按标签筛选
- 评论（comments）：对文章的评论 CRUD
- 用户（users）：注册、登录、个人资料

**输出要求**：写出每个接口的 Method、URL、Request Body（示例 JSON）、Response Body（示例 JSON）、HTTP Status Code。

### K-65-2 RESTful 命名审查（基础，15min）
以下 API 设计是否符合 RESTful 规范？不符合的请改正：
```
POST   /api/createArticle
GET    /api/getArticles?page=1&size=10
POST   /api/articles/123/delete
GET    /api/articlesByUser?userId=5
PUT    /api/articles/updateTitle/123
```

### K-65-3 API 版本管理策略 ⭐（挑战，20min）
为一个已有 3 个版本（v1/v2/v3）的 API 设计版本管理策略。要求覆盖：
1. URL 路径版本 vs Header 版本，选择一种并说明理由
2. 旧版本废弃（Deprecation）流程
3. v2 接口修改字段名时如何兼容 v1 客户端

---

## 第66章 · Gin 框架

### K-66-1 Gin Hello World（基础，10min）
搭建一个 Gin 项目，实现：
```go
// GET /ping → {"message": "pong"}
// GET /hello?name=世界 → {"message": "你好, 世界"}
```
写出完整 `main.go`，能在浏览器验证。

### K-66-2 Gin 路由分组（基础，15min）
将以下路由组织为 Gin 路由组：
```
GET    /api/v1/users
GET    /api/v1/users/:id
POST   /api/v1/users
PUT    /api/v1/users/:id
DELETE /api/v1/users/:id
GET    /api/v1/articles
GET    /api/v1/articles/:id
```

### K-66-3 优雅关停 ⭐（挑战，20min）
为 Gin 服务器实现优雅关停（Graceful Shutdown）：收到 SIGINT/SIGTERM 信号后，不再接受新请求，等待现有请求处理完成（最多 5 秒超时），然后退出。

---

## 第67章 · Gin 路由

### K-67-1 RESTful 风格路由设计（基础，20min）
为一个「任务管理系统」设计完整的 Gin 路由，资源为 tasks：
```
GET    /api/v1/tasks          # 列表，支持 ?status=&priority=&page=&size=
POST   /api/v1/tasks          # 创建
GET    /api/v1/tasks/:id      # 详情
PUT    /api/v1/tasks/:id      # 更新
DELETE /api/v1/tasks/:id      # 删除
PATCH  /api/v1/tasks/:id/status   # 更新状态
```
写出 Gin 路由注册代码。

### K-67-2 路由优先级与冲突（基础，10min）
以下路由注册是否有问题？如有，如何修正？
```go
r.GET("/users/:id", handleUser)
r.GET("/users/me", handleMe)
r.GET("/users/:id/articles/:aid", handleArticle)
r.GET("/users/:id/posts/:pid", handlePost)
```

### K-67-3 动态路由中间件 ⭐（挑战，25min）
实现一个路由中间件，根据请求路径自动选择不同的限流策略：`/api/v1/write/*` 限流 10 req/s，`/api/v1/read/*` 限流 100 req/s。

---

## 第68章 · Gin 请求参数绑定

### K-68-1 各种参数绑定方式练习（基础，30min）
实现以下所有参数绑定方式，并写测试 curl 命令：
```go
// 1. Query 参数：GET /search?keyword=golang&page=2&size=10
// 2. Path 参数：GET /users/123/articles/456
// 3. Form 参数：POST /login （application/x-www-form-urlencoded）
// 4. JSON Body：POST /articles （application/json）
// 5. Header 绑定：从 Header 获取 X-Request-ID
// 6. 文件上传：POST /upload （multipart/form-data）
```
每种给出 Go 代码和 curl 验证命令。

### K-68-2 自定义绑定验证器 ⭐（挑战，25min）
为 Gin 实现一个自定义验证器 `valid_date`，校验参数字符串是否为合法日期（格式 `YYYY-MM-DD`，且不能是未来日期），集成到 binding tag 中使用。

---

## 第69章 · Gin 中间件

### K-69-1 自定义日志中间件（基础，25min）
实现一个日志中间件，记录：
- 请求方法、路径、Query 参数
- 响应状态码
- 请求耗时（毫秒）
- 客户端 IP

输出格式（结构化）：
```json
{"method":"GET","path":"/api/v1/users","status":200,"latency_ms":12,"ip":"127.0.0.1"}
```

### K-69-2 限流中间件（基础，25min）
用 `time.Ticker` 或 `rate.Limiter` 实现一个简单的令牌桶限流中间件：全局 50 req/s。写出完整代码和测试方法。

### K-69-3 中间件链执行顺序 ⭐（挑战，20min）
现有 4 个中间件：A（日志）、B（认证）、C（限流）、D（恢复 panic）。请画出它们的执行洋葱模型，并说明：
1. 推荐的注册顺序及理由
2. 如果 C 拒绝请求，A 是否还会记录日志？为什么？

---

## 第70章 · Gin 响应

### K-70-1 统一响应格式封装（基础，25min）
设计并实现统一的 API 响应结构：
```json
{
  "code": 0,
  "message": "success",
  "data": { ... },
  "request_id": "uuid"
}
```
要求：
1. 定义 `Response` 结构体
2. 封装 `Success(c, data)`、`Error(c, code, message)`、`ErrorWithStatus(c, httpStatus, code, message)`
3. code=0 表示成功，非 0 表示错误
4. 自动注入 request_id

### K-70-2 响应格式版本兼容 ⭐（挑战，30min）
场景：API v1 返回格式为 `{"data": ..., "msg": "..."}`，v2 改为 `{"code": 0, "data": ..., "message": "..."}`。设计一个向后兼容方案，让 v1 客户端无感知升级。写出核心设计思路和代码。

---

## 第71章 · 参数校验

### K-71-1 自定义校验规则（基础，25min）
用 `go-playground/validator` 实现以下自定义校验规则：
```go
type RegisterReq struct {
    Username string `validate:"required,min=3,max=20,alphanum"`
    Password string `validate:"required,min=8,password_strength"`
    Phone    string `validate:"required,phone_cn"`
    Age      int    `validate:"gte=0,lte=150"`
    Email    string `validate:"required,email"`
}
```
实现 `password_strength`（至少含大写、小写、数字）和 `phone_cn`（中国大陆手机号）两个自定义校验。

### K-71-2 多语言校验错误 ⭐（挑战，30min）
在 K-71-1 基础上，实现校验错误信息的中英文切换（通过请求头 `Accept-Language: zh-CN` 或 `en-US` 控制）。给出核心代码设计。

---

## 第72章 · 项目结构

### K-72-1 搭建标准三层架构骨架（基础，35min）
按以下结构搭建一个 Go Web 项目骨架：
```
project/
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── handler/      # HTTP 处理层
│   ├── service/      # 业务逻辑层
│   ├── repository/   # 数据访问层
│   ├── model/        # 数据模型
│   ├── middleware/   # 中间件
│   └── router/       # 路由注册
├── pkg/
│   ├── response/     # 统一响应
│   └── errcode/      # 错误码
├── config/
│   └── config.yaml
├── go.mod
└── Makefile
```
要求：每层至少有一个示例文件，`main.go` 能成功启动 Gin 服务。

### K-72-2 依赖注入实践 ⭐（挑战，30min）
用 `wire`（Google Wire）为三层架构实现依赖注入。写出：
1. `wire.go` 定义 Provider Set
2. `wire_gen.go` 生成后的代码
3. `main.go` 如何使用注入后的对象

---

## 第73章 · 日志

### K-73-1 结构化日志配置（基础，20min）
使用 `zap` 或 `logrus` 配置结构化日志：
1. 开发环境：console 格式，DEBUG 级别，带颜色
2. 生产环境：JSON 格式，INFO 级别，输出到文件（按天切割）
3. 每条日志自动附带 `service_name` 和 `version` 字段

写出配置代码。

### K-73-2 链路追踪日志 ⭐（挑战，25min）
在 Gin 中间件中注入 `trace_id`，并确保同一次请求的所有日志自动携带该 `trace_id`（使用 `context.Context` 传递）。写出核心代码。

---

## 第74章 · 错误码

### K-74-1 统一错误码体系设计（基础，20min）
设计一套错误码体系：
- 分段：通用(10000~19999)、用户(20000~29999)、文章(30000~39999)
- 每种错误包含：错误码、HTTP 状态码、中英文消息
- 定义至少 10 个错误码

用 Go 代码定义（`const` 或 `enum`），并实现 `Error()` 接口。

### K-74-2 错误码与 i18n ⭐（挑战，25min）
在 K-74-1 基础上，实现错误消息国际化（中/英文），通过请求头切换。写出代码结构和示例。

---

## 第75章 · Swagger

### K-75-1 API 文档生成（基础，25min）
为一个已有 Gin 项目集成 Swagger（`swaggo/swag`），要求：
1. 添加必要的注释（`@title`、`@description`、`@version` 等）
2. 为一个 CRUD 接口添加完整的 Swagger 注解
3. 生成文档并能在浏览器访问 `/swagger/index.html`

### K-75-2 Swagger + 自动化 ⭐（挑战，20min）
在 Makefile 中添加 `swagger` 目标，自动执行 `swag init` 并将生成内容纳入 CI 检查（文档与代码不一致时报错）。

---

## 第76章 · CORS

### K-76-1 跨域配置（基础，15min）
为 Gin 项目配置 CORS 中间件（`gin-contrib/cors`），要求：
1. 允许 `http://localhost:3000` 和 `https://yourdomain.com` 跨域
2. 允许 `GET`、`POST`、`PUT`、`DELETE`、`OPTIONS`
3. 允许携带 Cookie（`credentials: true`）
4. 预检请求缓存 12 小时

### K-76-2 CORS 安全分析 ⭐（挑战，15min）
如果 CORS 配置为 `AllowOrigins: ["*"]` 且 `AllowCredentials: true`，会出现什么问题？请写出具体的安全风险和一个攻击示例。如何正确配置？

---

## 第77章 · 认证基础

### K-77-1 bcrypt 密码哈希（基础，20min）
用 Go `golang.org/x/crypto/bcrypt` 实现：
```go
func HashPassword(password string) (string, error)
func CheckPassword(hashed, password string) bool
```
要求：
1. 使用默认 cost（10）
2. 编写测试：同一密码两次哈希结果应不同，但验证均通过
3. 测试 cost 对性能的影响（cost=10 vs cost=14 的耗时对比）

### K-77-2 密码策略校验 ⭐（挑战，20min）
实现密码强度校验器（不依赖 validate tag）：
- 长度 >= 8 且 <= 128
- 必须包含大写、小写、数字、特殊字符（至少 3 类）
- 不能包含常见弱密码（如 `password123`、`admin123`，维护一个黑名单文件）
写出完整代码和黑名单文件格式。

---

## 第78章 · Session 认证

### K-78-1 Session 认证实现（基础，30min）
用 Gin + Redis 实现 Session 认证：
1. 登录接口：验证账号密码，生成 session_id，存入 Redis（TTL=24h），Set-Cookie
2. 认证中间件：从 Cookie 取出 session_id，查 Redis 获取用户信息，注入 context
3. 登出接口：删除 Redis 中的 session
4. 使用 `github.com/gin-contrib/sessions` 或自行实现

### K-78-2 Session 安全加固 ⭐（挑战，25min）
在 K-78-1 基础上：
1. 登录后生成新的 session_id（防 Session Fixation）
2. 敏感操作（修改密码、绑定手机）要求二次验证 session
3. Cookie 设置 `HttpOnly`、`Secure`、`SameSite=Lax`

---

## 第79章 · JWT

### K-79-1 JWT 签发与验证（基础，30min）
用 `golang-jwt/jwt` 实现：
```go
// 签发
func GenerateToken(userID int64, username string) (accessToken, refreshToken string, err error)
// 验证
func ParseToken(tokenString string) (*Claims, error)
```
要求：
1. Access Token 有效期 15 分钟，Refresh Token 有效期 7 天
2. Claims 包含 `user_id`、`username`、`iss`、`exp`、`iat`
3. 签名算法使用 HS256
4. 写出 3 个测试用例：正常 token、过期 token、伪造 token

### K-79-2 Refresh Token 刷新（基础，20min）
实现 `/api/v1/auth/refresh` 接口：
1. 接收 Refresh Token
2. 验证 Refresh Token 是否有效、是否在 Redis 白名单中
3. 签发新的 Access Token + Refresh Token（旧 Refresh Token 加入黑名单或删除）
4. 要求 Refresh Token 只能使用一次（防重放攻击）

### K-79-3 JWT 无感刷新 ⭐（挑战，30min）
设计并实现前端无感刷新 Token 的方案：
1. 写出完整的中间件逻辑（检测 Access Token 即将过期时自动刷新）
2. 处理并发请求同时刷新 Token 的竞态问题
3. 写出前后端协作的完整流程（文字描述 + Go 核心代码）

---

## 第80章 · OAuth 2.0

### K-80-1 OAuth 流程描述（基础，20min）
用你自己的话描述 OAuth 2.0 授权码流程（Authorization Code Flow），必须包含：
1. 涉及的四个角色
2. 每一步的 HTTP 请求/响应
3. 为什么需要授权码这一步（而不是直接返回 Access Token）

输出格式：文字描述 + 时序图（用 Mermaid 或 ASCII Art）。

### K-80-2 OAuth 三方登录集成 ⭐（挑战，35min）
用 Go 实现 GitHub OAuth 登录：
1. 引导用户跳转 GitHub 授权页
2. 回调处理：用 code 换 access_token，再用 access_token 获取用户信息
3. 本地创建/绑定用户，返回 JWT
写出核心 Handler 代码和 OAuth 配置。

---

## 第81章 · RBAC

### K-81-1 设计角色权限表（基础，25min）
设计 RBAC（基于角色的访问控制）表结构：
```sql
-- 至少包含：
-- users、roles、permissions、user_roles、role_permissions 五张表
```
要求：
1. 写出完整 DDL（含外键、唯一索引）
2. 预置三个角色：admin、editor、viewer
3. 预置权限：user:read、user:write、article:read、article:write、article:delete
4. 为每个角色分配权限

### K-81-2 权限中间件实现（基础，25min）
基于 K-81-1 的表结构，实现 Gin 中间件：
```go
func RequirePermission(perm string) gin.HandlerFunc
```
要求：
1. 从 context 获取当前用户（由认证中间件注入）
2. 查询用户拥有的权限（优先查 Redis 缓存）
3. 无权限时返回 403

### K-81-3 权限缓存刷新 ⭐（挑战，25min）
当管理员修改用户角色后，如何确保权限缓存立即失效？设计并实现一种方案（如版本号、Pub/Sub、延迟双删等），写出核心代码。

---

## 第82章 · Web 安全

### K-82-1 SQL 注入攻击模拟与防护（基础，20min）
以下代码存在 SQL 注入漏洞：
```go
query := "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
```
1. 构造一个恶意输入，绕过密码验证登录
2. 写出使用参数化查询修复后的代码
3. 用 GORM 写出安全等价写法，说明 GORM 如何防注入

### K-82-2 XSS 攻击模拟与防护（基础，20min）
1. 构造一个 XSS payload，提交后能在其他用户页面执行 `alert(document.cookie)`
2. 写出 HTML 转义函数（Go 代码）
3. 设置 Content-Security-Policy 响应头

### K-82-3 CSRF 攻击模拟与防护（基础，15min）
1. 描述 CSRF 攻击的完整流程
2. 用 Gin 实现 CSRF Token 防护（生成 token、验证 token）
3. SameSite Cookie 属性如何辅助防御 CSRF？

### K-82-4 综合安全扫描 ⭐（挑战，30min）
编写一个简单的安全扫描脚本（Go 代码），对本地 API 进行自动化检查：
1. SQL 注入检测（发送特殊 payload 观察响应）
2. 未授权访问检测（不带 token 访问需要认证的接口）
3. 敏感信息泄露检测（响应中是否包含 stack trace、数据库错误等）

---

## 第83章 · 加密

### K-83-1 AES 加解密实现（基础，25min）
用 Go `crypto/aes` 实现 AES-256-GCM 加解密：
```go
func Encrypt(plaintext []byte, key []byte) ([]byte, error)
func Decrypt(ciphertext []byte, key []byte) ([]byte, error)
```
要求：
1. 每次加密生成随机 nonce（12 字节），拼接在密文前
2. 写出测试：加密后解密与原值一致；不同 nonce 产生不同密文
3. 密钥管理：建议如何安全存储密钥

### K-83-2 敏感字段加密 ⭐（挑战，25min）
为数据库中的「手机号」和「身份证号」字段实现透明加解密：
1. 定义一个加密标记类型（如 `EncryptedString`），实现 `Scan` 和 `Value` 接口
2. 写入 DB 时自动加密，读取时自动解密
3. 支持密钥轮换（旧数据用旧密钥解密，新数据用新密钥加密）

---

## 第84章 · HTTPS/TLS

### K-84-1 TLS 握手描述（基础，20min）
用你自己的话描述 TLS 1.3 握手过程，必须回答：
1. Client Hello 包含哪些关键信息？
2. Server Hello 选择了什么？
3. 对称密钥是如何协商出来的？（不需要说数学细节）
4. TLS 1.3 比 1.2 快在哪？（减少了几次 RTT）

输出格式：文字描述 + 简易流程图。

### K-84-2 自签名证书配置 ⭐（挑战，25min）
1. 用 `openssl` 生成自签名证书
2. 配置 Gin 服务启用 HTTPS
3. 同时支持 HTTP（80）自动跳转 HTTPS（443）
4. 写出完整操作命令和 Go 代码

---

## 第85章 · 消息队列基础

### K-85-1 MQ 场景选择题（基础，15min）

判断以下场景是否适合使用消息队列，并说明理由：
- A）用户注册后发送欢迎邮件
- B）用户查询自己的订单详情（需要实时返回）
- C）秒杀活动中的下单请求削峰
- D）每日凌晨生成经营报表
- E）两个微服务之间的同步 RPC 调用

### K-85-2 MQ 选型对比（基础，15min）
从以下维度对比 RabbitMQ 和 Kafka：
- 消息可靠性（是否可能丢消息）
- 吞吐量
- 消息顺序保证
- 消息回溯能力
- 适用场景

输出表格格式。

---

## 第86章 · RabbitMQ 基础

### K-86-1 Hello World 模式（基础，20min）
用 Go + `amqp` 实现 RabbitMQ 的 Hello World 模式（一个生产者 + 一个消费者），写出完整可运行代码。

### K-86-2 Work Queue 模式（基础，20min）
在 K-86-1 基础上改为 Work Queue（多个消费者竞争消费），要求：
1. 设置 `prefetch=1`（公平调度）
2. 消息确认（Manual Ack）
3. 消息持久化（队列和消息都持久化）

---

## 第87章 · RabbitMQ 进阶

### K-87-1 Publish/Subscribe 模式（基础，20min）
用 fanout 交换机实现发布/订阅模式：一个生产者发送日志，两个消费者各自接收全部日志。

### K-87-2 Routing 模式（基础，20min）
用 direct 交换机实现路由模式：日志级别分为 info、warn、error，不同消费者订阅不同级别。

### K-87-3 Topics 模式（基础，20min）
用 topic 交换机实现主题模式：
- `order.*` 匹配所有订单相关消息
- `*.error` 匹配所有错误级别消息
- `order.create.#` 匹配订单创建及子操作

### K-87-4 死信队列 ⭐（挑战，30min）
实现一个带死信队列的订单超时处理系统：
1. 创建订单时发送消息到延迟队列（用 TTL + 死信交换机实现）
2. 订单超时（30 分钟）后消息进入死信队列
3. 消费者处理死信队列中的超时订单（关闭订单、恢复库存）
写出完整 Go 代码。

---

## 第88章 · Kafka 基础

### K-88-1 Topic/Partition 设计（基础，20min）
为「电商订单系统」设计 Kafka Topic 和 Partition 方案：
```
需求：
- 订单创建、支付、发货、完成事件需要顺序消费
- 日均订单量 100 万
- 需要保留 7 天数据用于回溯
```
写出：
1. Topic 命名规范
2. Partition 数量及分区策略（如何保证同一订单的事件进入同一分区）
3. 保留策略配置

### K-88-2 Go 连接 Kafka（基础，25min）
用 `sarama` 或 `confluent-kafka-go` 实现：
```go
// 生产者：发送订单事件
func ProduceOrderEvent(orderID string, eventType string, data []byte) error
// 消费者：消费并打印事件
func ConsumeOrderEvents(topic string) error
```

---

## 第89章 · Kafka 进阶

### K-89-1 消费者组协调（基础，20min）
解释 Kafka 消费者组的工作原理：
1. 一个 Topic 3 个 Partition，消费者组中有 2 个消费者，Partition 如何分配？
2. 如果第 3 个消费者加入，会发生什么？
3. 消费者宕机后，Partition 如何重新分配？

### K-89-2 Exactly-Once 语义实现 ⭐（挑战，35min）
用 Kafka 事务实现「订单创建 → 扣库存 → 发送通知」的 Exactly-Once 语义。要求写出：
1. 生产者事务代码（Go）
2. 消费者隔离级别配置
3. 幂等性如何保证

---

## 第90章 · Go + 消息队列

### K-90-1 Go 连接 RabbitMQ 异步任务（基础，30min）
实现一个异步邮件发送系统：
1. HTTP 接口接收发送请求，将任务投递到 RabbitMQ
2. 后台 Worker 从队列消费任务，模拟发送邮件（打印日志即可）
3. 前端查询发送状态（用 Redis 存储状态）
写出完整代码。

### K-90-2 消息可靠性保障 ⭐（挑战，35min）
在 K-90-1 基础上实现消息可靠性：
1. 生产者确认（Publisher Confirm）
2. 消费者手动 ACK + 重试机制（最多 3 次，失败后入死信队列）
3. 消息幂等性（基于 message_id 防重复消费）

---

## 第91章 · 设计模式

### K-91-1 五种设计模式 Go 实现（基础，45min）
用 Go 实现以下五种设计模式，每种附简短说明和示例调用：
1. **单例模式**（Singleton）：`sync.Once` 实现
2. **工厂模式**（Factory）：根据类型创建不同支付方式
3. **策略模式**（Strategy）：多种排序算法可切换
4. **观察者模式**（Observer）：事件发布/订阅
5. **装饰器模式**（Decorator）：为 HTTP Handler 添加日志/计时功能

### K-91-2 设计模式实战重构 ⭐（挑战，35min）
以下代码存在什么问题？用合适的设计模式重构：
```go
func ProcessNotification(notifyType string, userID int, content string) error {
    if notifyType == "email" {
        // 发送邮件...80 行代码
    } else if notifyType == "sms" {
        // 发送短信...60 行代码
    } else if notifyType == "push" {
        // 推送通知...50 行代码
    } else if notifyType == "wechat" {
        // 微信通知...70 行代码
    }
    return nil
}
```
写出重构后的代码，说明使用了哪种模式及理由。

---

## 第92章 · SOLID 原则

### K-92-1 判断违反哪个原则（基础，20min）
判断以下代码分别违反了 SOLID 中哪个原则，并改正：
```go
// 代码 A：一个 struct 负责连接数据库、处理业务逻辑、渲染 HTML
type ReportService struct { ... }

// 代码 B：子类无法替换父类
type Bird struct{}
func (b Bird) Fly() {}
type Penguin struct{ Bird }
// Penguin 不能飞，但继承了 Fly()

// 代码 C：修改支付逻辑需要改核心类
type Payment struct{}
func (p Payment) Pay(method string) {
    if method == "alipay" { ... }
    else if method == "wechat" { ... }
}
```

### K-92-2 SOLID 综合重构 ⭐（挑战，35min）
一个用户注册模块需要：保存用户 → 发送验证邮件 → 记录审计日志 → 赠送注册积分。
当前所有逻辑耦合在一个 `Register` 函数中。请按 SOLID 原则重构，分别践行 SRP、OCP、DIP，写出重构后的代码。

---

## 第93章 · 微服务

### K-93-1 设计微服务拆分方案（基础，30min）
为一个「电商平台」设计微服务拆分方案，业务包含：
- 用户管理（注册、登录、个人资料）
- 商品管理（发布、编辑、上下架）
- 订单管理（创建、支付、退款）
- 库存管理（入库、出库、盘点）
- 物流管理（发货、跟踪、签收）
- 营销（优惠券、秒杀、推荐）

回答：
1. 哪些应该拆为独立微服务？拆分边界在哪？
2. 每个微服务的数据存储策略（独立数据库 or 共享？）
3. 画出服务间调用关系图

### K-93-2 分布式事务方案 ⭐（挑战，30min）
场景：下单需要调用订单服务（创建订单）+ 库存服务（扣库存）+ 积分服务（增加积分）。请设计一种分布式事务方案（如 Saga、TCC、本地消息表），写出：
1. 方案选择及理由
2. 正常流程的伪代码
3. 失败回滚流程的伪代码

---

## 第94章 · 微服务通信

### K-94-1 gRPC Hello World（基础，30min）
用 Go 实现一个 gRPC 服务：
```protobuf
service Greeter {
    rpc SayHello (HelloRequest) returns (HelloReply);
}
message HelloRequest {
    string name = 1;
}
message HelloReply {
    string message = 1;
}
```
要求：
1. 编写 `.proto` 文件，生成 Go 代码
2. 实现服务端
3. 实现客户端并调用
4. 写出完整操作步骤（protoc 命令等）

### K-94-2 gRPC 流式调用 ⭐（挑战，30min）
在 K-94-1 基础上，增加服务端流式 RPC：
```protobuf
rpc ListOrders (OrderFilter) returns (stream Order);
```
客户端发送查询条件，服务端分批返回订单（每批 10 条，模拟大数据量场景）。

---

## 第95章 · 分布式理论

### K-95-1 CAP 定理解释题（基础，15min）
分别举出以下三种系统各一个真实例子，并说明在 CAP 中牺牲了哪个：
1. CP 系统（牺牲可用性）
2. AP 系统（牺牲一致性）
3. CA 系统（为什么在分布式系统中不可能真正 CA？）

### K-95-2 分布式一致性场景 ⭐（挑战，25min）
场景：分布式缓存集群（3 个节点），用户修改了个人信息。
1. 如何保证各节点数据最终一致？
2. 如果用户修改后立刻查询，如何避免读到旧数据？
给出至少两种方案及对比。

---

## 第96章 · 负载均衡

### K-96-1 Nginx 配置负载均衡（基础，25min）
编写 Nginx 配置，实现：
1. 上游 3 个 Go 服务实例（`localhost:8081`、`8082`、`8083`）
2. 负载均衡算法：最少连接（least_conn）
3. 健康检查：每 5 秒检查一次，失败 2 次后摘除，成功 2 次后恢复
4. 配置限流：每个 IP 每秒最多 10 个请求

写出完整 `nginx.conf` 片段。如果是 Nginx Plus 的功能请标注。

### K-96-2 四层 vs 七层负载均衡 ⭐（挑战，20min）
用 Nginx 分别配置：
1. 四层（stream）负载均衡：转发 MySQL 连接（3306）到两个 MySQL 实例
2. 七层（http）负载均衡：根据 URL 路径 `/api/v1/users` 和 `/api/v1/orders` 转发到不同服务集群

写出完整配置，并说明两种方式的适用场景。

---

## 第97章 · 高并发

### K-97-1 限流算法实现（令牌桶）（基础，30min）
用 Go 实现令牌桶限流算法：
```go
type TokenBucket struct {
    rate       float64 // 每秒生成令牌数
    capacity   int64   // 桶容量
    tokens     int64   // 当前令牌数
    lastRefill time.Time
    mu         sync.Mutex
}
func (tb *TokenBucket) Allow() bool
```
要求：
1. 不使用第三方库，纯 Go 实现
2. 写出测试：验证精确限流效果（1000 个请求，限制 100/s，统计通过的请求数）

### K-97-2 滑动窗口限流 ⭐（挑战，30min）
实现滑动窗口限流，并与令牌桶对比：
1. 基于 Redis ZSet 实现（滑动窗口日志）
2. 基于内存实现（Go 语言，`[]time.Time` 滑动）
3. 对比内存 vs Redis 实现的优缺点

---

## 第98章 · 系统设计

### K-98-1 短链接系统设计（基础，35min）
设计一个短链接系统（类似 t.cn），要求：
1. 功能：长链转短链、短链跳转、访问统计
2. 写出核心表结构 DDL
3. 写出短链生成算法（哈希 or 自增 ID + Base62）
4. 画出核心流程图（跳转流程）
5. 估算：日生成 100 万条短链，存储和 QPS 需求

### K-98-2 高并发短链 ⭐（挑战，30min）
在 K-98-1 基础上，解决以下问题：
1. **分布式 ID 生成**：多实例部署时如何保证短链不冲突？
2. **缓存策略**：如何缓存热点短链的跳转映射？
3. **跳转链路**：301 还是 302？为什么？

---

## 第99章 · Linux

### K-99-1 常用命令实操（基础，25min）
在 Linux 环境（或 WSL）中完成以下操作并截图：
```bash
# 1. 查找 /var/log 下大于 100MB 的文件
# 2. 统计一个日志文件中 "ERROR" 出现的次数
# 3. 查看端口 8080 被哪个进程占用
# 4. 后台启动一个进程，并使其在终端关闭后继续运行
# 5. 查找所有 .go 文件中包含 "TODO" 的行
# 6. 实时监控某个日志文件的新增内容
```
每道题写出一条命令。

### K-99-2 Shell 一行命令 ⭐（挑战，15min）
用一行 Shell 命令完成：
1. 统计 Nginx 访问日志中访问量 Top 10 的 IP
2. 将当前目录下所有 `.txt` 文件中的 "foo" 替换为 "bar"
3. 找出两个文件中不同的行（`diff` 替代方案：部分行相似但格式不同）

---

## 第100章 · Shell

### K-100-1 自动化部署脚本（基础，30min）
编写一个 Shell 脚本 `deploy.sh`，实现以下功能：
```bash
#!/bin/bash
# 1. 拉取最新代码（git pull）
# 2. 编译 Go 项目（go build）
# 3. 停止旧进程（kill）
# 4. 备份旧二进制文件（带时间戳）
# 5. 启动新进程（nohup）
# 6. 健康检查（curl 检查新进程是否正常）
# 7. 健康检查失败则回滚到旧版本
```
要求：每步有 echo 输出，失败时退出并提示。

### K-100-2 多环境部署脚本 ⭐（挑战，25min）
在 K-100-1 基础上，支持多环境部署：
```bash
./deploy.sh --env=dev     # 开发环境
./deploy.sh --env=staging # 预发布
./deploy.sh --env=prod    # 生产（需二次确认）
```
要求：
1. 每个环境读取不同的 `.env` 文件
2. 生产环境部署前需要人工输入 "yes" 确认
3. 部署后记录版本号和部署时间到日志文件

---

## 第101章 · Git

### K-101-1 分支操作练习（基础，20min）
在实际 Git 仓库中完成以下操作（可用本地练习仓库）：
```bash
# 1. 从 main 分支创建 feature/login 分支并切换
# 2. 在 feature/login 上提交 2 个 commit
# 3. 切回 main，创建 hotfix/urgent 分支，提交 1 个 commit
# 4. 将 hotfix/urgent 合并到 main（fast-forward）
# 5. 将 feature/login rebase 到最新的 main 上
# 6. 解决 rebase 过程中的冲突（假设 README.md 有冲突）
```
记录每一步使用的命令。

### K-101-2 冲突解决练习（基础，15min）
构造一个 Git 合并冲突场景并解决：
1. 两个分支同时修改同一个文件的同一行
2. `git merge` 时出现冲突
3. 解决冲突并完成合并
4. 用 `git merge --abort` 放弃合并，改用 `git rebase` 重新操作
记录完整命令和冲突标记内容。

### K-101-3 Git 工作流 ⭐（挑战，20min）
设计一个 5 人团队的 Git 工作流（如 GitFlow 或 GitHub Flow），画出分支模型图，写出：
1. 哪些分支是长期分支
2. feature、hotfix、release 分支的生命周期
3. 合并策略（merge commit vs squash vs rebase）
4. Code Review 如何集成到流程中

---

## 第102章 · Docker

### K-102-1 Dockerfile 编写（基础，25min）
为一个 Go Web 项目编写生产级 Dockerfile，要求：
1. 多阶段构建（编译阶段 + 运行阶段）
2. 运行阶段使用 `alpine` 基础镜像
3. 使用非 root 用户运行
4. 处理时区（Asia/Shanghai）
5. 健康检查（HEALTHCHECK）
6. 写出构建和运行命令

### K-102-2 docker-compose 编排（基础，25min）
编写 `docker-compose.yml`，编排以下服务：
- Go Web 应用（你的项目）
- MySQL 8.0（初始化 SQL 脚本）
- Redis 7
- Nginx（反向代理到 Go 应用）

要求：
1. 服务间网络隔离（自定义 network）
2. 数据持久化（volumes）
3. 健康检查依赖（depends_on + condition）
4. 环境变量通过 `.env` 文件注入

### K-102-3 镜像优化 ⭐（挑战，25min）
一个 Go 应用的 Docker 镜像大小为 800MB，请分析原因并优化至 20MB 以内。写出：
1. 镜像分层分析命令
2. 优化后的 Dockerfile
3. 优化前后大小对比

---

## 第103章 · CI/CD

### K-103-1 GitHub Actions 配置（基础，30min）
为一个 Go 项目编写 GitHub Actions 工作流 `.github/workflows/ci.yml`：
1. 触发条件：push 到 main、PR 到 main
2. 运行环境：ubuntu-latest
3. 步骤：
   - Checkout 代码
   - 安装 Go 1.22
   - 运行 `go vet`
   - 运行 `go test -race -coverprofile=coverage.out`
   - 上传覆盖率报告
   - 运行 `golangci-lint`

### K-103-2 自动化部署流水线 ⭐（挑战，30min）
在 K-103-1 基础上，扩展为完整 CI/CD 流水线：
1. 测试通过后，构建 Docker 镜像并推送到 Docker Hub / 私有 Registry
2. SSH 到服务器，拉取新镜像并重启容器
3. 部署后自动执行冒烟测试（curl 关键接口）
4. 失败时自动回滚到上一个镜像版本
写出完整 workflow 文件。

---

## 第104章 · 部署

### K-104-1 完整部署流程（基础，35min）
将你的 Go Web 项目部署到一台 Linux 服务器（可用虚拟机），完整流程：
1. 服务器环境准备（安装 Go、MySQL、Redis、Nginx）
2. 配置 systemd 服务（`/etc/systemd/system/myapp.service`）
3. 配置 Nginx 反向代理 + HTTPS
4. 配置 MySQL 和 Redis
5. 启动服务并验证
写出所有配置文件和命令。

### K-104-2 零停机部署 ⭐（挑战，30min）
设计并实现零停机部署方案（滚动更新）：
1. 使用 Nginx upstream 多实例
2. 部署新版本时：启动新实例 → 健康检查 → 加入 upstream → 摘除旧实例 → 停止旧实例
3. 写出 Shell 脚本或 docker-compose 配置

---

## 第105章 · 监控

### K-105-1 Prometheus + Grafana 基础（基础，30min）
为 Go Web 项目接入 Prometheus 监控：
1. 使用 `prometheus/client_golang` 暴露 `/metrics` 端点
2. 至少实现以下指标：
   - HTTP 请求总数（Counter，按 method/path/status 分组）
   - HTTP 请求延迟（Histogram）
   - 活跃连接数（Gauge）
3. 配置 Prometheus 抓取 + Grafana 仪表盘
4. 写出 `prometheus.yml` 配置和 Grafana 面板 JSON

### K-105-2 告警规则配置 ⭐（挑战，25min）
配置 Prometheus 告警规则 + Alertmanager：
1. 错误率 > 5% 告警
2. P99 延迟 > 1s 告警
3. 服务宕机告警（up == 0）
4. 写出 `alert.rules.yml` 和 Alertmanager 配置

---

## 第106章 · 单元测试

### K-106-1 表格驱动测试（基础，25min）
为以下函数编写表格驱动测试：
```go
func CalculateDiscount(amount float64, userLevel string) float64 {
    switch userLevel {
    case "vip":
        return amount * 0.8
    case "svip":
        return amount * 0.7
    case "normal":
        if amount >= 100 {
            return amount * 0.95
        }
        return amount
    default:
        return amount
    }
}
```
要求：
1. 覆盖正常、边界、异常输入
2. 每个 case 有 `name` 字段说明场景
3. 使用 `t.Run` 运行子测试

### K-106-2 测试覆盖率 ⭐（挑战，20min）
为第59章或第63章的代码编写单元测试，要求：
1. 覆盖率达到 80% 以上
2. 运行 `go test -coverprofile=coverage.out` 后使用 `go tool cover -html` 查看
3. 截图覆盖率报告，标注未覆盖的分支并解释原因

---

## 第107章 · Mock

### K-107-1 使用 testify 编写 mock 测试（基础，30min）
为以下接口编写 mock 测试：
```go
type UserRepository interface {
    GetByID(ctx context.Context, id int64) (*User, error)
    Create(ctx context.Context, user *User) error
}
type UserService struct {
    repo UserRepository
}
func (s *UserService) GetUserWithGreeting(ctx context.Context, id int64) (string, error) {
    user, err := s.repo.GetByID(ctx, id)
    if err != nil {
        return "", err
    }
    return "Hello, " + user.Name, nil
}
```
要求：
1. 使用 `testify/mock` 创建 `MockUserRepository`
2. 测试正常返回和 repo 报错两种情况
3. 验证 mock 的 `GetByID` 确实被调用了一次

### K-107-2 时间 Mock ⭐（挑战，25min）
场景：`UserService` 中有一个方法判断用户是否在活动期内（需要比较当前时间）。写出不使用真实时间的测试方案（至少两种方法），并实现其中一种。

---

## 第108章 · 集成测试

### K-108-1 HTTP 接口集成测试（基础，30min）
为第66章 Gin 项目的 CRUD 接口编写集成测试：
```go
// 使用 httptest.NewServer 启动测试服务器
// 测试以下场景：
// 1. POST /api/v1/users — 创建用户，断言返回 201 和正确的 JSON
// 2. GET /api/v1/users/:id — 查询刚创建的用户，断言返回 200
// 3. PUT /api/v1/users/:id — 更新用户名，断言返回 200
// 4. DELETE /api/v1/users/:id — 删除用户，断言返回 204
// 5. GET /api/v1/users/:id — 再次查询，断言返回 404
```
要求：使用 `testify/assert`，测试之间隔离（每个测试创建独立的用户）。

### K-108-2 数据库集成测试 ⭐（挑战，30min）
编写涉及真实数据库的集成测试：
1. 使用 `testcontainers-go` 启动 MySQL 容器
2. 自动运行 migrations
3. 测试 DAO 层（repository）的 CRUD 操作
4. 测试完成后自动清理容器
写出完整代码和 `go test` 命令。

---

## 第109章 · 性能测试

### K-109-1 Benchmark + pprof 分析（基础，30min）
为以下场景编写 benchmark 并分析：
```go
// 场景 A：字符串拼接（+ vs strings.Builder vs fmt.Sprintf）
// 场景 B：JSON 序列化（encoding/json vs jsoniter）
// 场景 C：切片预分配容量 vs 动态扩容
```
要求：
1. 每种场景写 2~3 种实现方式的 benchmark
2. 运行 `go test -bench=. -benchmem`
3. 对结果进行分析，说明哪个最优及原因

### K-109-2 pprof 性能排查 ⭐（挑战，35min）
构造一个有性能问题的 Go 程序（如内存泄漏、CPU 热点），使用 pprof 分析：
1. 运行程序并采集 CPU profile 和 heap profile
2. 使用 `go tool pprof` 定位热点函数
3. 使用火焰图辅助分析
4. 修复性能问题并验证
写出完整步骤和关键截图说明。

---

## 第110章 · 项目 Todo API

### K-110-P1 为 Todo API 增加优先级字段（基础，30min）
为 Todo API 项目增加以下功能：
1. Todo 表新增 `priority` 字段（TINYINT，1=低、2=中、3=高）
2. 创建 Todo 时可指定优先级（不指定默认为 2）
3. 列表接口支持按优先级筛选：`GET /api/v1/todos?priority=3`
4. 列表接口支持按优先级排序：`GET /api/v1/todos?sort_by=priority&order=desc`

写出完整 migration SQL、模型修改和 handler 修改。

### K-110-P2 批量操作扩展 ⭐（挑战，35min）
为 Todo API 增加批量操作：
1. `PATCH /api/v1/todos/batch` — 批量更新状态（传入 id 列表和新状态）
2. `DELETE /api/v1/todos/batch` — 批量删除
3. 使用事务保证批量操作的原子性
4. 返回每个 id 的操作结果（成功/失败，失败时注明原因）

---

## 第111章 · 项目博客系统

### K-111-P1 为博客系统增加标签功能（基础，35min）
为博客系统增加标签功能：
1. 设计文章-标签的多对多关系（articles ←→ article_tags ←→ tags）
2. 创建文章时可同时设置标签
3. 文章详情中返回标签列表
4. 实现「按标签筛选文章」：`GET /api/v1/articles?tag=golang`
5. 实现「热门标签」接口：返回使用最多的 10 个标签及文章数

写出 DDL、模型、接口和核心逻辑。

### K-111-P2 文章全文搜索 ⭐（挑战，40min）
为博客系统增加全文搜索功能：
1. 使用 MySQL FULLTEXT 索引或 Elasticsearch
2. 搜索接口：`GET /api/v1/articles/search?q=关键词&page=1&size=10`
3. 搜索结果高亮关键词
4. 考虑搜索性能优化策略

---

## 第112章 · 项目电商系统

### K-112-P1 为电商系统增加优惠券功能（基础，40min）
为电商系统增加优惠券功能：
1. 设计优惠券表（类型：满减/折扣、门槛金额、面值、有效期、库存）
2. 用户领券接口：`POST /api/v1/coupons/:id/claim`
3. 下单时使用优惠券：传入优惠券 ID，校验规则，计算优惠后价格
4. 优惠券使用后标记已用，不可重复使用
5. 查询用户可用优惠券列表

写出 DDL、完整接口代码和核心校验逻辑。

### K-112-P2 秒杀活动 ⭐（挑战，45min）
为电商系统增加秒杀功能：
1. 设计秒杀活动表和秒杀商品表
2. 秒杀开始前显示倒计时和活动预告
3. 秒杀接口需要解决超卖问题（结合 Redis 预减库存 + 异步下单）
4. 秒杀结束后恢复原价
5. 考虑限流策略（同一用户 1 秒内只能请求 1 次）

写出完整设计思路、核心代码和压测方案。

---

## 第113章 · 项目即时通讯

### K-113-P1 为 IM 系统增加消息已读/未读功能（基础，35min）
为即时通讯系统增加消息已读/未读功能：
1. 设计消息已读记录表
2. 单聊和群聊的已读判断逻辑
3. 前端查询未读消息数
4. 标记消息为已读（单条/批量）
5. 群聊中显示「N 人已读」

写出 DDL、核心代码和 WebSocket 消息格式定义。

### K-113-P2 消息撤回功能 ⭐（挑战，35min）
为 IM 系统增加消息撤回功能：
1. 撤回时间限制（2 分钟内）
2. 撤回后发送系统消息通知对方
3. 已读的消息撤回后显示「对方撤回了一条消息」
4. 未读的消息撤回后从聊天记录中移除痕迹

写出完整实现方案和核心代码。

---

## 第114章 · 项目后台管理系统

### K-114-P1 为后台系统增加数据导出功能（基础，35min）
为后台管理系统增加数据导出功能：
1. 用户列表导出为 Excel（`excelize` 库）
2. 订单列表导出为 CSV
3. 导出接口支持时间范围筛选
4. 大文件导出使用异步任务（请求返回任务 ID，轮询下载链接）
5. 导出文件保留 24 小时后自动清理

写出核心代码和异步任务的实现方案。

### K-114-P2 操作审计日志 ⭐（挑战，35min）
为后台管理系统增加完整的操作审计日志：
1. 记录所有管理员的增删改操作（操作人、时间、IP、操作类型、操作对象、修改前后对比）
2. 审计日志不可删除（软删除除外）
3. 支持按操作人、操作类型、时间范围搜索
4. 敏感操作（如修改权限）发送告警通知

写出 DDL、中间件或 AOP 实现方案。

---

## 第115章 · 项目微服务网关

### K-115-P1 为网关增加 API 编排功能（基础，40min）
为微服务网关增加简单的 API 编排功能：
1. 定义一个「复合接口」，由多个下游接口聚合而成
2. 支持并行调用和串行调用
3. 支持结果合并（例如 `/api/v1/user-profile` 聚合用户信息 + 最近订单 + 积分余额）
4. 任一子调用失败时的容错策略（返回部分数据 or 整体失败）

写出核心配置结构和编排引擎代码。

### K-115-P2 全链路灰度发布 ⭐（挑战，45min）
为微服务网关增加全链路灰度发布能力：
1. 根据请求头 `X-Version` 将请求路由到灰度服务实例
2. 灰度标识在微服务调用链中透传（Context 传递）
3. 支持按比例分流（10% 流量进灰度）
4. 灰度实例连接灰度数据库（而不是正式数据库）

写出设计思路、核心代码和配置示例。

---

## 参考答案索引

| 章节 | 题号 | 参考答案位置 |
|------|------|-------------|
| 第50章 | K-50-1 ~ K-50-3 | 见附录L §L.50 |
| 第51章 | K-51-1 ~ K-51-3 | 见附录L §L.51 |
| 第52章 | K-52-1 ~ K-52-3 | 见附录L §L.52 |
| 第53章 | K-53-1 ~ K-53-3 | 见附录L §L.53 |
| 第54章 | K-54-1 ~ K-54-3 | 见附录L §L.54 |
| 第55章 | K-55-1 ~ K-55-3 | 见附录L §L.55 |
| 第56章 | K-56-1 ~ K-56-3 | 见附录L §L.56 |
| 第57章 | K-57-1 ~ K-57-3 | 见附录L §L.57 |
| 第58章 | K-58-1 ~ K-58-3 | 见附录L §L.58 |
| 第59章 | K-59-1 ~ K-59-3 | 见附录L §L.59 |
| 第60章 | K-60-1 ~ K-60-3 | 见附录L §L.60 |
| 第61章 | K-61-1 ~ K-61-2 | 见附录L §L.61 |
| 第62章 | K-62-1 ~ K-62-2 | 见附录L §L.62 |
| 第63章 | K-63-1 ~ K-63-2 | 见附录L §L.63 |
| 第64章 | — | （本章无练习，参考第60-63章） |
| 第65章 | K-65-1 ~ K-65-3 | 见附录L §L.65 |
| 第66章 | K-66-1 ~ K-66-3 | 见附录L §L.66 |
| 第67章 | K-67-1 ~ K-67-3 | 见附录L §L.67 |
| 第68章 | K-68-1 ~ K-68-2 | 见附录L §L.68 |
| 第69章 | K-69-1 ~ K-69-3 | 见附录L §L.69 |
| 第70章 | K-70-1 ~ K-70-2 | 见附录L §L.70 |
| 第71章 | K-71-1 ~ K-71-2 | 见附录L §L.71 |
| 第72章 | K-72-1 ~ K-72-2 | 见附录L §L.72 |
| 第73章 | K-73-1 ~ K-73-2 | 见附录L §L.73 |
| 第74章 | K-74-1 ~ K-74-2 | 见附录L §L.74 |
| 第75章 | K-75-1 ~ K-75-2 | 见附录L §L.75 |
| 第76章 | K-76-1 ~ K-76-2 | 见附录L §L.76 |
| 第77章 | K-77-1 ~ K-77-2 | 见附录L §L.77 |
| 第78章 | K-78-1 ~ K-78-2 | 见附录L §L.78 |
| 第79章 | K-79-1 ~ K-79-3 | 见附录L §L.79 |
| 第80章 | K-80-1 ~ K-80-2 | 见附录L §L.80 |
| 第81章 | K-81-1 ~ K-81-3 | 见附录L §L.81 |
| 第82章 | K-82-1 ~ K-82-4 | 见附录L §L.82 |
| 第83章 | K-83-1 ~ K-83-2 | 见附录L §L.83 |
| 第84章 | K-84-1 ~ K-84-2 | 见附录L §L.84 |
| 第85章 | K-85-1 ~ K-85-2 | 见附录L §L.85 |
| 第86章 | K-86-1 ~ K-86-2 | 见附录L §L.86 |
| 第87章 | K-87-1 ~ K-87-4 | 见附录L §L.87 |
| 第88章 | K-88-1 ~ K-88-2 | 见附录L §L.88 |
| 第89章 | K-89-1 ~ K-89-2 | 见附录L §L.89 |
| 第90章 | K-90-1 ~ K-90-2 | 见附录L §L.90 |
| 第91章 | K-91-1 ~ K-91-2 | 见附录L §L.91 |
| 第92章 | K-92-1 ~ K-92-2 | 见附录L §L.92 |
| 第93章 | K-93-1 ~ K-93-2 | 见附录L §L.93 |
| 第94章 | K-94-1 ~ K-94-2 | 见附录L §L.94 |
| 第95章 | K-95-1 ~ K-95-2 | 见附录L §L.95 |
| 第96章 | K-96-1 ~ K-96-2 | 见附录L §L.96 |
| 第97章 | K-97-1 ~ K-97-2 | 见附录L §L.97 |
| 第98章 | K-98-1 ~ K-98-2 | 见附录L §L.98 |
| 第99章 | K-99-1 ~ K-99-2 | 见附录L §L.99 |
| 第100章 | K-100-1 ~ K-100-2 | 见附录L §L.100 |
| 第101章 | K-101-1 ~ K-101-3 | 见附录L §L.101 |
| 第102章 | K-102-1 ~ K-102-3 | 见附录L §L.102 |
| 第103章 | K-103-1 ~ K-103-2 | 见附录L §L.103 |
| 第104章 | K-104-1 ~ K-104-2 | 见附录L §L.104 |
| 第105章 | K-105-1 ~ K-105-2 | 见附录L §L.105 |
| 第106章 | K-106-1 ~ K-106-2 | 见附录L §L.106 |
| 第107章 | K-107-1 ~ K-107-2 | 见附录L §L.107 |
| 第108章 | K-108-1 ~ K-108-2 | 见附录L §L.108 |
| 第109章 | K-109-1 ~ K-109-2 | 见附录L §L.109 |
| 第110章 | K-110-P1 ~ K-110-P2 | 见附录L §L.110 |
| 第111章 | K-111-P1 ~ K-111-P2 | 见附录L §L.111 |
| 第112章 | K-112-P1 ~ K-112-P2 | 见附录L §L.112 |
| 第113章 | K-113-P1 ~ K-113-P2 | 见附录L §L.113 |
| 第114章 | K-114-P1 ~ K-114-P2 | 见附录L §L.114 |
| 第115章 | K-115-P1 ~ K-115-P2 | 见附录L §L.115 |

> **说明**：参考答案见「附录L：配套练习册参考答案（下）」。建议独立完成练习后再查阅答案。标注 ⭐ 的挑战题答案包含详细思路解析。