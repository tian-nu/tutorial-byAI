# 33 — MongoDB 入门

> - 对应文档版本：本篇为数据库精通教程第七篇第 4 章
> - 适用环境：MongoDB 7.0+，mongosh 命令行工具
> - 读者角色：已学完第 1-2 篇 MySQL 基础，首次接触文档数据库的开发者
> - 预计耗时：新手 90 分钟 / 熟手 40 分钟
> - 前置教程：第 1-2 篇（MySQL 基础）
> - 可视化：无

---

## 本章假设你已掌握 MySQL 基础（第 1-5 篇）

---

## 从 MySQL 到 MongoDB 的思维转换

在 MySQL 中，你写数据的流程是：

```
1. 先想好表结构（Schema）
2. CREATE TABLE 定义列名和类型
3. INSERT INTO 按列插入数据
4. 要改结构？ALTER TABLE（可能锁表）
```

在 MongoDB 中，流程变成了：

```
1. 直接插入 JSON 文档
2. 没有预先定义的 Schema
3. 同一个 Collection 里的文档可以有不同的字段
4. 想加字段？直接插入新字段就行，不需要 ALTER 任何东西
```

**一句话**：MySQL 是"先盖房子再住人"，MongoDB 是"住进去再慢慢装修"。

**MongoDB** *此术语见附录E* 是一个**文档数据库**，它把数据存成 **BSON**（Binary JSON）格式的文档。如果你会 JSON，你基本就会 MongoDB。

---

## 我在做什么？

前面两章你学了 Redis 这个"内存字典"，现在来认识 NoSQL 世界的另一个重要成员——MongoDB。和 Redis 不同，MongoDB 是**磁盘存储**的，可以处理大量数据，而且支持复杂的查询和聚合。

这一章我们走一条"从 MySQL 思维迁移到 MongoDB 思维"的路线：
1. 先把 MySQL 的概念映射到 MongoDB
2. CRUD 操作——和 SQL 对照着学
3. 聚合管道——MongoDB 的"GROUP BY 升级版"
4. 索引——和 MySQL 有相似也有不同

学完这一章，你能说出 3 个"选 MongoDB 不选 MySQL"的场景，并且能独立完成 MongoDB 的 CRUD 和基本聚合操作。

---

## 一、安装与连接

```bash
# Windows（Docker 推荐）
docker run --name mongo-local -p 27017:27017 -d mongo:7

# macOS
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0

# Linux (Ubuntu)
# 参考官方文档：https://www.mongodb.com/docs/manual/installation/
```

连接：
```bash
# 命令行连接（mongosh）
mongosh
# 或通过 Docker
docker exec -it mongo-local mongosh

# 图形化工具：MongoDB Compass
# 下载：https://www.mongodb.com/products/compass
# 连接字符串：mongodb://localhost:27017
```

---

## 二、核心概念映射

把 MySQL 的概念"翻译"成 MongoDB，是上手最快的方式。

| MySQL | MongoDB | 说明 |
|-------|---------|------|
| Database（数据库） | Database（数据库） | 概念相同，存放集合 |
| Table（表） | **Collection（集合）** | 存文档的地方，但不需要定义 Schema |
| Row（行） | **Document（文档）** | 一条 JSON 记录 |
| Column（列） | **Field（字段）** | 文档里的 key |
| Primary Key（主键） | `_id`（默认主键） | MongoDB 自动生成 `ObjectId` |
| Index（索引） | Index（索引） | 概念相同，语法不同 |
| JOIN | `$lookup`（聚合操作） | 不推荐频繁 JOIN，用嵌入式文档代替 |
| GROUP BY | `$group`（聚合管道） | 聚合管道能力强得多 |

### 文档示例

```javascript
// MySQL 中的一行：
// | id | name  | age | tags          | address.city |
// |----|-------|-----|---------------|-------------|
// | 1  | 张三  | 25  | ["技术","阅读"] | 北京         |

// MongoDB 中的同一个文档：
{
  "_id": ObjectId("667a1b2c3d4e5f6a7b8c9d0e"),
  "name": "张三",
  "age": 25,
  "tags": ["技术", "阅读"],
  "address": {
    "city": "北京",
    "district": "海淀区"
  },
  "created_at": ISODate("2026-01-01T08:00:00Z")
}
```

**关键差异**：
- `_id` 是 ObjectId 类型（12 字节，自动生成，全局唯一）
- 日期用 `ISODate` 而不是 `DATETIME`
- 数组和嵌套文档直接内嵌，不需要关联表

---

## 三、CRUD 操作：与 MySQL 对照

### 3.1 创建（Create）

```javascript
// === 切换到数据库（不存在就自动创建） ===
use my_shop

// === 插入单条文档 ===
// MySQL: INSERT INTO users (name, age, city) VALUES ('张三', 25, '北京');
db.users.insertOne({
  name: "张三",
  age: 25,
  city: "北京",
  tags: ["技术", "阅读"]
})

// === 插入多条文档 ===
db.users.insertMany([
  { name: "李四", age: 30, city: "上海", tags: ["管理"] },
  { name: "王五", age: 22, city: "北京", tags: ["技术", "设计"] },
  { name: "赵六", age: 28, city: "深圳", tags: ["销售"] }
])

// === 查看插入结果 ===
db.users.find()
```

**注意**：MongoDB 不需要 `CREATE TABLE`。`db.users.insertOne()` 第一次执行时，`users` 集合自动创建。

### 3.2 查询（Read）

```javascript
// === 查询所有 ===
// MySQL: SELECT * FROM users;
db.users.find()

// === 精确匹配 ===
// MySQL: SELECT * FROM users WHERE age = 25;
db.users.find({ age: 25 })

// === 比较运算符 ===
// MySQL: SELECT * FROM users WHERE age > 25;
db.users.find({ age: { $gt: 25 } })      // $gt = greater than

// MySQL: SELECT * FROM users WHERE age >= 25;
db.users.find({ age: { $gte: 25 } })     // $gte = greater than or equal

// MySQL: SELECT * FROM users WHERE age < 30;
db.users.find({ age: { $lt: 30 } })      // $lt = less than

// MySQL: SELECT * FROM users WHERE age <= 30;
db.users.find({ age: { $lte: 30 } })     // $lte = less than or equal

// MySQL: SELECT * FROM users WHERE age != 25;
db.users.find({ age: { $ne: 25 } })      // $ne = not equal

// === 范围查询 ===
// MySQL: SELECT * FROM users WHERE age BETWEEN 22 AND 28;
db.users.find({ age: { $gte: 22, $lte: 28 } })

// === AND 逻辑 ===
// MySQL: SELECT * FROM users WHERE age > 22 AND city = '北京';
db.users.find({ age: { $gt: 22 }, city: "北京" })

// === OR 逻辑 ===
// MySQL: SELECT * FROM users WHERE age = 25 OR age = 30;
db.users.find({ $or: [{ age: 25 }, { age: 30 }] })

// === IN 查询 ===
// MySQL: SELECT * FROM users WHERE city IN ('北京', '上海');
db.users.find({ city: { $in: ["北京", "上海"] } })

// === 数组查询 ===
// 查询 tags 包含"技术"的文档
db.users.find({ tags: "技术" })

// 查询 tags 同时包含"技术"和"设计"的文档
db.users.find({ tags: { $all: ["技术", "设计"] } })

// === 嵌套文档查询 ===
// 假如有 address: { city: "北京", district: "海淀区" }
db.users.find({ "address.city": "北京" })  // 点号访问嵌套字段

// === 投影（只返回特定字段） ===
// MySQL: SELECT name, age FROM users;
db.users.find({}, { name: 1, age: 1, _id: 0 })
// 1 = 包含，0 = 排除。_id 默认返回，要排除需显式 _id: 0

// === 排序 ===
// MySQL: SELECT * FROM users ORDER BY age DESC;
db.users.find().sort({ age: -1 })   // 1 = 升序，-1 = 降序

// === 分页 ===
// MySQL: SELECT * FROM users LIMIT 2 OFFSET 0;
db.users.find().limit(2).skip(0)

// === 计数 ===
// MySQL: SELECT COUNT(*) FROM users;
db.users.countDocuments({})
db.users.countDocuments({ age: { $gt: 25 } })

// === 去重 ===
// MySQL: SELECT DISTINCT city FROM users;
db.users.distinct("city")
```

### 3.3 更新（Update）

```javascript
// === 更新单条 ===
// MySQL: UPDATE users SET age = 26 WHERE name = '张三';
db.users.updateOne(
  { name: "张三" },                    // 过滤条件
  { $set: { age: 26 } }               // 更新操作
)

// === 更新多条 ===
// MySQL: UPDATE users SET city = '北京' WHERE age < 25;
db.users.updateMany(
  { age: { $lt: 25 } },
  { $set: { city: "北京" } }
)

// === 常用更新操作符 ===
// $set：设置字段
// $unset：删除字段
db.users.updateOne({ name: "张三" }, { $unset: { tags: "" } })

// $inc：数值自增
db.users.updateOne({ name: "张三" }, { $inc: { age: 1 } })

// $push：向数组追加元素
db.users.updateOne({ name: "张三" }, { $push: { tags: "运动" } })

// $pull：从数组移除元素
db.users.updateOne({ name: "张三" }, { $pull: { tags: "运动" } })

// $rename：重命名字段
db.users.updateMany({}, { $rename: { "city": "location" } })

// === 更新或插入（Upsert） ===
// 如果存在就更新，不存在就插入
db.users.updateOne(
  { name: "新用户" },
  { $set: { age: 20, city: "杭州" } },
  { upsert: true }                     // 关键参数
)
```

### 3.4 删除（Delete）

```javascript
// === 删除单条 ===
// MySQL: DELETE FROM users WHERE name = '张三' LIMIT 1;
db.users.deleteOne({ name: "张三" })

// === 删除多条 ===
// MySQL: DELETE FROM users WHERE age < 25;
db.users.deleteMany({ age: { $lt: 25 } })

// === 删除所有文档（保留集合） ===
db.users.deleteMany({})

// === 删除集合（包括索引） ===
db.users.drop()
```

### 3.5 对比运算符速查

| MySQL 运算符 | MongoDB 运算符 | 示例 |
|-------------|---------------|------|
| `=` | 直接写值 | `{ age: 25 }` |
| `>` | `$gt` | `{ age: { $gt: 25 } }` |
| `>=` | `$gte` | `{ age: { $gte: 25 } }` |
| `<` | `$lt` | `{ age: { $lt: 30 } }` |
| `<=` | `$lte` | `{ age: { $lte: 30 } }` |
| `!=` | `$ne` | `{ age: { $ne: 25 } }` |
| `IN` | `$in` | `{ city: { $in: ["北京","上海"] } }` |
| `NOT IN` | `$nin` | `{ city: { $nin: ["北京"] } }` |
| `AND` | 逗号分隔 | `{ age: 25, city: "北京" }` |
| `OR` | `$or` | `{ $or: [{age:25}, {age:30}] }` |
| `LIKE` | 正则 `$regex` | `{ name: { $regex: /张/ } }` |

---

## 四、聚合管道：MongoDB 的 GROUP BY 升级版

**聚合管道（Aggregation Pipeline）** *此术语见附录E* 是 MongoDB 最强大的功能之一。你可以把它理解为"数据通过一系列加工步骤，每步处理后再传给下一步"。

```
集合 → [$match] → [$group] → [$sort] → [$project] → 结果
       筛选        分组聚合     排序        投影
```

### 4.1 基础聚合

```javascript
// 准备数据：订单表
db.orders.insertMany([
  { customer: "张三", product: "手机", amount: 5000, status: "已完成", date: ISODate("2026-01-01") },
  { customer: "张三", product: "耳机", amount: 300, status: "已完成", date: ISODate("2026-01-02") },
  { customer: "李四", product: "电脑", amount: 8000, status: "已完成", date: ISODate("2026-01-01") },
  { customer: "李四", product: "键盘", amount: 500, status: "取消", date: ISODate("2026-01-03") },
  { customer: "王五", product: "手机", amount: 5000, status: "已完成", date: ISODate("2026-01-02") },
  { customer: "王五", product: "鼠标", amount: 200, status: "已完成", date: ISODate("2026-01-03") },
])

// === 聚合：统计每个客户的消费总额 ===
// MySQL 等价：
// SELECT customer, SUM(amount) AS total_amount
// FROM orders
// WHERE status = '已完成'
// GROUP BY customer
// ORDER BY total_amount DESC

db.orders.aggregate([
  // 阶段 1：$match — 筛选已完成的订单
  { $match: { status: "已完成" } },
  
  // 阶段 2：$group — 按客户分组，计算总额
  { $group: {
      _id: "$customer",              // 分组字段（$customer 表示引用 customer 字段）
      total_amount: { $sum: "$amount" },
      order_count: { $sum: 1 },       // 计数
      avg_amount: { $avg: "$amount" } // 平均
  }},
  
  // 阶段 3：$sort — 按总额降序
  { $sort: { total_amount: -1 } },
  
  // 阶段 4：$project — 重命名和格式化输出
  { $project: {
      _id: 0,
      customer: "$_id",
      total_amount: 1,
      order_count: 1,
      avg_amount: { $round: ["$avg_amount", 2] }
  }}
])
```

输出：
```json
[
  { "customer": "张三", "total_amount": 5300, "order_count": 2, "avg_amount": 2650 },
  { "customer": "王五", "total_amount": 5200, "order_count": 2, "avg_amount": 2600 },
  { "customer": "李四", "total_amount": 8000, "order_count": 1, "avg_amount": 8000 }
]
```

### 4.2 常用聚合操作符

```javascript
// === 聚合操作符速查 ===

// 分组操作符
{ $sum: "$amount" }       // 求和
{ $avg: "$amount" }       // 平均
{ $min: "$amount" }       // 最小
{ $max: "$amount" }       // 最大
{ $first: "$amount" }     // 每组第一个
{ $last: "$amount" }      // 每组最后一个
{ $push: "$product" }     // 把值放入数组
{ $addToSet: "$product" } // 把值放入数组（去重）

// === $unwind：展开数组 ===
// 文档 tags: ["技术", "阅读", "运动"]
// $unwind 后变成 3 个文档，每个 tags 字段只有一个值
db.users.aggregate([
  { $unwind: "$tags" },
  { $group: { _id: "$tags", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])

// === $lookup：关联查询（类似 JOIN） ===
db.orders.aggregate([
  { $lookup: {
      from: "users",               // 关联的集合
      localField: "customer",      // orders 的字段
      foreignField: "name",        // users 的字段
      as: "user_info"              // 结果放入的字段名
  }}
])
// 注意：MongoDB 不推荐频繁 $lookup，如果经常需要关联，考虑嵌入式文档
```

---

## 五、索引

MongoDB 的索引和 MySQL 类似，但语法不同。

```javascript
// === 单字段索引 ===
db.users.createIndex({ name: 1 })            // 1 = 升序，-1 = 降序

// === 复合索引 ===
db.users.createIndex({ city: 1, age: -1 })

// === 唯一索引 ===
db.users.createIndex({ email: 1 }, { unique: true })

// === 文本索引（全文搜索） ===
db.articles.createIndex({ title: "text", body: "text" })
db.articles.find({ $text: { $search: "MongoDB 教程" } })

// === 查看索引 ===
db.users.getIndexes()

// === 删除索引 ===
db.users.dropIndex("name_1")   // 按索引名删除
db.users.dropIndexes()         // 删除所有索引（除了 _id）

// === 查看查询是否用了索引 ===
db.users.find({ name: "张三" }).explain("executionStats")
// 看 winningPlan 和 executionTimeMillis
```

---

## 六、适用场景：什么时候选 MongoDB？

### 选 MongoDB 不选 MySQL 的场景

| 场景 | 为什么选 MongoDB | MongoDB 的哪个特性 |
|------|-----------------|-------------------|
| **数据结构不确定或频繁变化** | 不需要 ALTER TABLE，直接存 | 无 Schema 约束 |
| **日志/事件数据** | 大量写入，结构可能不同，很少需要关联 | 高写入性能 + 灵活文档 |
| **用户画像/个性化配置** | 每个用户字段不同，嵌入式文档天然适合 | 嵌套文档 |
| **IoT 数据** | 设备上报的数据格式可能不同，数据量大 | 灵活文档 + 水平扩展 |
| **内容管理系统（CMS）** | 文章/产品/评论，结构多样，嵌套合理 | 文档模型 + 聚合管道 |
| **原型快速开发** | 不用先设计表结构，改需求也快 | 无 Schema |

### 不选 MongoDB 的场景

| 场景 | 为什么不选 MongoDB | 推荐 |
|------|-------------------|------|
| 需要复杂事务（多表 ACID） | MongoDB 4.0+ 支持事务但不如 MySQL 成熟 | MySQL/PostgreSQL |
| 需要大量 JOIN | MongoDB 的 JOIN 是弱项 | MySQL/PostgreSQL |
| 数据之间有严格的关联关系 | 文档模型不适合高度关联的数据 | MySQL/PostgreSQL |
| 需要强一致性的金融数据 | 金融场景对事务要求极高 | PostgreSQL/Oracle |

---

## 七、验证方法

### 验证 1：在 mongosh 中完成完整 CRUD

```javascript
// 1. 创建集合并插入数据
db.products.insertMany([
  { name: "iPhone", category: "手机", price: 6999, stock: 100 },
  { name: "MacBook", category: "电脑", price: 12999, stock: 50 },
  { name: "AirPods", category: "耳机", price: 1999, stock: 200 }
])

// 2. 查询：价格 > 2000 的商品
db.products.find({ price: { $gt: 2000 } })

// 3. 更新：iPhone 涨价 500
db.products.updateOne({ name: "iPhone" }, { $inc: { price: 500 } })

// 4. 聚合：按分类统计商品数量和平均价格
db.products.aggregate([
  { $group: { _id: "$category", count: { $sum: 1 }, avg_price: { $avg: "$price" } } },
  { $sort: { avg_price: -1 } }
])

// 5. 删除
db.products.deleteOne({ name: "AirPods" })
```

### 验证 2：说出 3 个选 MongoDB 不选 MySQL 的场景

1. ___
2. ___
3. ___

---

## 八、常见错误

### 错误 1：把 MongoDB 当 MySQL 用（疯狂 JOIN）

**现象**：在 MongoDB 里频繁使用 `$lookup` 做关联查询，性能很差。

❌ MongoDB 的优势在于嵌入式文档。如果数据经常需要关联查询，应该考虑：
- 把关联数据嵌入到同一个文档里
- 或者干脆用 MySQL/PostgreSQL

```javascript
// ❌ 不推荐：用户和订单分两个集合，频繁 $lookup
db.orders.aggregate([
  { $lookup: { from: "users", localField: "user_id", foreignField: "_id", as: "user" } }
])

// ✅ 推荐：如果用户信息不常变，嵌入到订单里
{
  _id: ObjectId("..."),
  product: "手机",
  amount: 5000,
  user: { name: "张三", city: "北京" }  // 嵌入
}
```

### 错误 2：文档嵌套过深

**现象**：文档嵌套 5-6 层，查询和更新都很痛苦。

```javascript
// ❌ 太深了
{
  level1: {
    level2: {
      level3: {
        level4: {
          level5: { value: "很难维护" }
        }
      }
    }
  }
}
```

✅ 一般不超过 3 层嵌套。如果嵌套很深，说明可能需要拆分成多个集合。

### 错误 3：不建索引

**现象**：MongoDB 看起来很快，因为没建索引时数据量小。数据量大了以后，全表扫描让查询变慢。

✅ 和 MySQL 一样，MongoDB 也需要建索引。特别是 `_id` 以外的查询字段。

```javascript
// 检查慢查询
db.setProfilingLevel(1, { slowms: 100 })  // 记录超过 100ms 的查询
db.system.profile.find().sort({ ts: -1 }).limit(5)
```

### 错误 4：以为 MongoDB 不支持事务

**现象**：MongoDB 4.0 之前确实不支持多文档事务，但现在支持了。

```javascript
// MongoDB 4.0+ 多文档事务
const session = db.getMongo().startSession()
session.startTransaction()

try {
  session.getDatabase("my_shop").users.updateOne(
    { name: "张三" },
    { $inc: { balance: -100 } }
  )
  session.getDatabase("my_shop").users.updateOne(
    { name: "李四" },
    { $inc: { balance: 100 } }
  )
  session.commitTransaction()
} catch (error) {
  session.abortTransaction()
} finally {
  session.endSession()
}
```

✅ 但要注意：MongoDB 的事务性能不如 MySQL/PostgreSQL，不要在高并发场景频繁使用。

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| 核心概念映射 | Database/Collection/Document/Field | Table→Collection, Row→Document, Column→Field |
| 插入 | `insertOne()`, `insertMany()` | 自动创建集合，不需要 CREATE TABLE |
| 查询 | `find()`, `$gt/$lt/$in/$or/$and` | 比较运算符以 $ 开头 |
| 更新 | `updateOne()`, `updateMany()`, `$set/$inc/$push/$pull` | upsert 选项实现"存在则更新，不存在则插入" |
| 删除 | `deleteOne()`, `deleteMany()`, `drop()` | 删除文档 vs 删除集合 |
| 聚合管道 | `aggregate()`, `$match/$group/$sort/$project` | 数据流经多个阶段，每个阶段加工后传给下一步 |
| 关联查询 | `$lookup` | 不推荐频繁使用，考虑嵌入式文档 |
| 数组展开 | `$unwind` | 一个文档变多个，用于统计 |
| 索引 | `createIndex()`, `getIndexes()`, `explain()` | 和 MySQL 一样需要建索引 |
| 文本索引 | `createIndex({field: "text"})`, `$text: {$search: "..."}` | 内置全文搜索 |
| 事务 | `startSession()`, `startTransaction()` | 4.0+ 支持，但性能不如 MySQL |
| 适用场景 | 日志、IoT、CMS、用户画像、快速原型 | 不适合需要大量 JOIN 或强事务的场景 |
| 文档嵌套 | 嵌入式文档 vs 引用 | 不超过 3 层，经常 JOIN 就嵌入 |

---

## 最可能出错的地方及原因

1. **把 MongoDB 当 MySQL 用**：频繁 `$lookup` 做 JOIN，性能很差，原因是 MySQL 思维惯性——"数据应该分表存"，但 MongoDB 的设计哲学是"把相关数据嵌入在一起"。
2. **文档嵌套过深**：嵌套 5-6 层，查询和更新语法复杂且容易出错，原因是没有规划好文档结构，把所有东西都塞进一个文档。
3. **不建索引导致全表扫描**：MongoDB 的灵活性让开发者忽视了索引的重要性，和 MySQL 一样，数据量大后全表扫描性能极差。
4. **比较运算符忘记 $ 前缀**：写 `{ age: { gt: 25 } }` 而不是 `{ age: { $gt: 25 } }`，原因是 MongoDB 的查询语法和 SQL 差异大，需要时间适应。
5. **聚合管道概念不熟**：把 `$match/$group/$sort` 顺序写错，比如 `$sort` 放在 `$group` 前面导致排序无效，原因是不理解管道是"顺序执行"的。