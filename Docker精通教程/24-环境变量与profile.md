# 24 — 环境变量与 profile

> - 对应文档版本：Docker精通教程 outline v1
> - 适用环境：任何已安装 Docker + Docker Compose 的系统
> - 读者角色：已掌握 Compose 基本操作，需要管理多环境配置的开发者
> - 预计耗时：新手 30 分钟 / 熟手 15 分钟
> - 前置教程：第 23 章（Compose 常用命令）
> - 可视化：无

---

## 我在做什么？

到目前为止，你的 compose.yml 里所有的配置都是写死的：密码写死、端口写死、环境名写死。但真实项目需要一个 compose.yml 同时适配开发、测试、生产三个环境——同一个 compose.yml，不同环境用不同的密码、端口、调试选项。

这一章讲两个核心能力：
1. **环境变量**：用 `.env` 文件 + `${VARIABLE}` 语法，让 compose.yml 的参数可配置
2. **profiles**：用 `profiles` 字段，按场景选择性启动服务（比如开发时启动调试工具，生产时启动监控服务）

学完这一章，你能：
- 用 `.env` 文件管理环境变量，不让密码进 compose.yml
- 用 `${VARIABLE:-默认值}` 实现变量替换和默认值
- 用 `profiles` 按场景选择性启动服务
- 实现"开发环境"和"生产环境"两套配置

---

## 一、`.env` 文件：环境变量的家

### 问题：密码写在 compose.yml 里

```yaml
# ❌ 密码硬编码在 compose.yml 里
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: MySecretPass123   # 密码明文！
```

这个 compose.yml 如果提交到 Git，任何人（包括后来的同事、GitHub 上的路人）都能看到你的数据库密码。即使你改了密码后提交，Git 历史里仍然保留着旧密码。

### 解决：`.env` 文件

Compose 会自动读取 compose.yml 所在目录的 `.env` 文件。你可以把密码和环境相关的配置放在 `.env` 里，然后在 compose.yml 里用 `${VARIABLE}` 引用。

**步骤 1：创建 `.env` 文件**

```bash
# .env
MYSQL_ROOT_PASSWORD=your_root_password_here
MYSQL_DATABASE=myapp
MYSQL_USER=myapp
MYSQL_PASSWORD=your_db_password_here
WORDPRESS_DB_PASSWORD=your_wp_password_here
WEB_PORT=8080
```

**步骤 2：在 compose.yml 里引用**

```yaml
# compose.yml
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}

  wordpress:
    image: wordpress:latest
    ports:
      - "${WEB_PORT}:80"
    environment:
      WORDPRESS_DB_PASSWORD: ${WORDPRESS_DB_PASSWORD}
```

**步骤 3：`.env` 加入 `.gitignore`**

```bash
# .gitignore
.env
```

**绝对不要把 `.env` 提交到 Git！** 它包含敏感信息，应该只存在于你的本地机器和服务器上。

### 项目的完整文件结构

```
my-app/
├── compose.yml
├── .env                 # 不在 Git 里！
├── .env.example         # 提交到 Git：模板文件，不含真实密码
├── .gitignore           # 包含 .env
└── Dockerfile
```

`.env.example` 是给团队看的模板：

```bash
# .env.example — 复制为 .env 后填入真实值
MYSQL_ROOT_PASSWORD=your_root_password_here
MYSQL_DATABASE=myapp
MYSQL_USER=myapp
MYSQL_PASSWORD=your_db_password_here
WORDPRESS_DB_PASSWORD=your_wp_password_here
WEB_PORT=8080
```

---

## 二、`${VARIABLE}` 变量替换

### 基本语法

```yaml
services:
  web:
    ports:
      - "${WEB_PORT}:80"           # 用 .env 里的 WEB_PORT 值
```

### 设置默认值：`${VARIABLE:-默认值}`

```yaml
services:
  web:
    ports:
      - "${WEB_PORT:-8080}:80"     # 如果 WEB_PORT 没设置，用 8080
```

这个语法非常实用：你可以在 `.env` 里不写 `WEB_PORT`，Compose 会自动用 8080。只有当你需要改端口时，才在 `.env` 里加上 `WEB_PORT=9090`。

```yaml
# 更多默认值示例
environment:
  NODE_ENV: ${NODE_ENV:-production}
  LOG_LEVEL: ${LOG_LEVEL:-info}
  DB_HOST: ${DB_HOST:-db}
  REDIS_URL: ${REDIS_URL:-redis://cache:6379}
```

### 必须设定（没有默认值）：`${VARIABLE:?错误信息}`

```yaml
environment:
  MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:?请设置 MYSQL_ROOT_PASSWORD}
```

如果 `.env` 里没有 `MYSQL_ROOT_PASSWORD`，Compose 会报错并显示"请设置 MYSQL_ROOT_PASSWORD"。这比静默地用空值安全得多。

### 变量替换可以用在任何地方

```yaml
services:
  web:
    image: ${DOCKER_REGISTRY:-docker.io}/myapp:${APP_VERSION:-latest}
    ports:
      - "${WEB_PORT:-8080}:${APP_PORT:-3000}"
    environment:
      - NODE_ENV=${NODE_ENV:-production}
    volumes:
      - ${DATA_DIR:-./data}:/app/data
    restart: ${RESTART_POLICY:-unless-stopped}
```

> **想多一点**：变量替换 + 默认值的组合，让 compose.yml 做到了"开箱即用，但可配置"。新同事 clone 项目后，不需要创建 `.env` 文件，直接 `docker compose up` 就能跑起来——因为每个变量都有默认值。当他需要定制时（比如改端口），才创建 `.env` 并覆盖。这比"要么必须写 `.env`（新同事不知道写什么），要么全部写死（改端口要改 compose.yml）"优雅得多。

---

## 三、profiles：按场景启动服务

### 问题：不是所有服务都需要一直启动

假设你的 compose.yml 有 5 个服务：

```
web       — Web 应用（随时需要）
db        — 数据库（随时需要）
cache     — 缓存（随时需要）
phpmyadmin — 数据库管理工具（偶尔需要）
debugger  — 调试工具（开发时需要，生产不需要）
```

你希望：
- 正常运行：启动 web + db + cache
- 调试时：启动 web + db + cache + phpmyadmin + debugger
- 生产时：启动 web + db + cache（不启动调试工具）

### 解决：`profiles`

```yaml
services:
  web:
    build: .
    # 没有 profiles → 始终启动

  db:
    image: mysql:8.0
    # 没有 profiles → 始终启动

  cache:
    image: redis:7-alpine
    # 没有 profiles → 始终启动

  phpmyadmin:
    image: phpmyadmin:latest
    ports:
      - "8081:80"
    profiles:
      - debug       # 只有 --profile debug 时才启动

  debugger:
    build: ./debug-tools
    profiles:
      - debug       # 只有 --profile debug 时才启动
      - dev         # 或 --profile dev 时启动
```

### 使用

```bash
# 正常启动（只启动 web + db + cache）
docker compose up -d

# 调试模式（启动 web + db + cache + phpmyadmin + debugger）
docker compose --profile debug up -d

# 也可以同时激活多个 profile
docker compose --profile debug --profile monitoring up -d
```

### 一个服务可以属于多个 profile

```yaml
services:
  adminer:
    image: adminer:latest
    profiles:
      - debug
      - dev
      - tools
    # 三种 profile 任意一个激活时都启动
```

### 实战：开发环境 vs 生产环境

```yaml
# compose.yml
services:
  # ===== 核心服务（始终启动） =====
  web:
    build:
      context: .
      target: ${BUILD_TARGET:-production}   # 多阶段构建，开发用 dev 阶段
    ports:
      - "${WEB_PORT:-8080}:3000"
    environment:
      NODE_ENV: ${NODE_ENV:-production}
    volumes:
      - ./src:/app/src       # 开发时热更新（生产环境不需要但留着也没事）
    depends_on:
      db:
        condition: service_healthy

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
    volumes:
      - mysql-data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ===== 开发工具（profile: dev） =====
  phpmyadmin:
    image: phpmyadmin:latest
    ports:
      - "8081:80"
    environment:
      PMA_HOST: db
    profiles:
      - dev

  # ===== 调试工具（profile: dev） =====
  node-debug:
    image: node:20-alpine
    command: ["node", "--inspect=0.0.0.0:9229", "/app/server.js"]
    working_dir: /app
    volumes:
      - ./src:/app/src
    ports:
      - "9229:9229"
    profiles:
      - dev

  # ===== 生产监控（profile: prod） =====
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    profiles:
      - prod

  # ===== 日志收集（profile: prod） =====
  fluentd:
    image: fluent/fluentd:latest
    volumes:
      - ./fluentd.conf:/fluentd/etc/fluentd.conf
    profiles:
      - prod

volumes:
  mysql-data:
```

使用：

```bash
# 开发环境启动（核心服务 + 开发工具）
docker compose --profile dev up -d

# 生产环境启动（核心服务 + 监控）
docker compose --profile prod up -d

# 最小启动（只有核心服务）
docker compose up -d
```

> 这样，**同一个 compose.yml 适配了所有环境**。开发、测试、生产用同一个配置文件，差异只在 profile 和 `.env`。

---

## 四、环境变量的优先级

当同一个变量在多个地方定义时，Compose 的优先级从高到低：

```
1. docker compose run -e 或 docker compose --env-file 指定的值
2. Shell 环境变量（export VAR=value）
3. .env 文件里的值
4. compose.yml 里 ${VAR:-默认值} 的默认值
```

### 举例

```bash
# .env 里写了：
WEB_PORT=8080

# Shell 环境变量：
export WEB_PORT=9090

# compose.yml 里：
# ports: "${WEB_PORT:-3000}:80"
```

最终 `WEB_PORT` 的值是 `9090`（Shell 环境变量覆盖了 `.env` 文件）。

> 这个优先级机制意味着：你可以在 CI/CD 流水线里通过 Shell 环境变量注入配置，而不需要修改 `.env` 文件或 compose.yml。

---

## 五、指定其他 `.env` 文件

默认情况下，Compose 读取 compose.yml 所在目录的 `.env` 文件。如果你想用别的文件：

```bash
# 用 .env.production 替代 .env
docker compose --env-file .env.production up -d

# 用 .env.staging
docker compose --env-file .env.staging up -d
```

这让你可以轻松切换环境：

```bash
# 开发
docker compose --env-file .env.dev up -d

# 测试
docker compose --env-file .env.test up -d

# 生产
docker compose --env-file .env.prod up -d
```

---

## 六、我做得对不对？

### 验证方法

```bash
# 1. 创建 .env 文件
cat > .env << 'EOF'
MYSQL_ROOT_PASSWORD=test123
WEB_PORT=9090
NODE_ENV=development
EOF

# 2. 创建最小 compose.yml 测试变量替换
cat > compose.yml << 'EOF'
services:
  web:
    image: nginx:alpine
    ports:
      - "${WEB_PORT:-8080}:80"
    environment:
      NODE_ENV: ${NODE_ENV:-production}
EOF

# 3. 验证变量被替换了
docker compose config
# 输出中应该看到：
#   ports:
#     - "9090:80"
#   environment:
#     NODE_ENV: development

# 4. 测试默认值（删除 .env 里的某个变量）
# 注释掉 .env 里的 WEB_PORT
# 重新运行 docker compose config
# 应该看到 "8080:80"（用了默认值）

# 5. 测试 profiles
cat > compose.yml << 'EOF'
services:
  web:
    image: nginx:alpine
  debug:
    image: alpine:latest
    command: echo "debug mode"
    profiles:
      - dev
EOF

# 不带 profile
docker compose up -d
docker compose ps
# 预期：只有 web 服务

# 带 profile
docker compose --profile dev up -d
docker compose ps
# 预期：web + debug 两个服务

# 6. 清理
docker compose down
```

---

## 七、不对怎么办？

### 常见错误 1：`.env` 文件提交到 Git

```bash
git add .env
git commit -m "add env file"
git push
# 密码泄露了！
```

❌ 原因：`.gitignore` 里没有 `.env`。

✅ 解决：

```bash
# 确保 .gitignore 包含 .env
echo ".env" >> .gitignore

# 如果已经提交了，从 Git 历史中移除
git rm --cached .env
git commit -m "remove .env from git tracking"

# 如果已经 push 到远程，需要改密码！Git 历史无法真正删除
```

> **安全红线**：一旦 `.env` 被 push 到远程仓库，里面的密码就视为已泄露。即使你 `git rm` 了，Git 历史里仍然保留着。**立刻修改所有涉及的密码**，然后才处理 Git 历史。

### 常见错误 2：变量名在 `.env` 和 compose.yml 里拼写不一致

```bash
# .env 里
MYSQL_ROOT_PASSWORD=test123

# compose.yml 里
environment:
  MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASWORD}  # 少了一个 S！
```

❌ 原因：拼写错误。Compose 不会报错——它会把 `${MYSQL_ROOT_PASWORD}` 当作一个未定义的变量，替换为空字符串。

✅ 排查：

```bash
docker compose config
# 输出中检查 MYSQL_ROOT_PASSWORD 的值是否为空
```

### 常见错误 3：`.env` 放在错误的目录

```
my-app/
├── src/
│   └── .env        # ❌ 错误！不在 compose.yml 同级目录
├── compose.yml
```

✅ 正确位置：

```
my-app/
├── .env            # ✅ 和 compose.yml 同级
├── compose.yml
```

### 常见错误 4：`profiles` 写错，服务没启动

```bash
docker compose --profile debu up -d
# 拼写错误：debu 而不是 debug
# 服务没启动，也不报错
```

❌ 原因：`--profile` 的值和 compose.yml 里定义的 `profiles` 不匹配。Compose 不会报错，只是静默地不启动那些服务。

✅ 排查：

```bash
docker compose config --services
# 列出所有服务名，对照你的 compose.yml 检查哪些服务有 profiles

docker compose --profile debug config --services
# 带 profile 时列出会启动的服务
```

### 常见错误 5：`.env` 文件里的值有空格

```bash
# .env
WEB_PORT = 8080      # ❌ 等号两边有空格
```

```bash
docker compose config
# 错误：WEB_PORT 的值变成了 " 8080"（带空格）
```

✅ 正确：

```bash
# .env
WEB_PORT=8080        # ✅ 等号两边不能有空格
```

`.env` 文件的格式是 `KEY=VALUE`，等号两边不能有空格。这和 Shell 变量赋值一样。

### 常见错误 6：在所有服务上都加了 `profiles`，忘了核心服务

```yaml
# ❌ 错误：所有服务都有 profiles
services:
  web:
    profiles:
      - prod       # 不加 --profile prod 就不启动 web

  db:
    profiles:
      - prod       # 不加 --profile prod 就不启动 db
```

结果：`docker compose up` 什么都不启动，因为所有服务都有 profile 限制。

✅ 正确：核心服务不加 `profiles`，只有可选服务加。

---

## 八、术语解释

| 术语 | 解释 |
|------|------|
| **`.env`** *此术语见附录C* | Docker Compose 自动读取的环境变量文件。放在 compose.yml 同级目录，用于存储密码、端口等环境相关配置 |
| **变量替换** *此术语见附录C* | 在 compose.yml 里用 `${VARIABLE}` 引用 `.env` 或 Shell 环境变量的值。`${VAR:-默认值}` 提供默认值 |
| **profiles** *此术语见附录C* | Compose 的按场景启动机制。给服务打上 profile 标签，用 `--profile` 参数选择性启动 |
| **`.gitignore`** | Git 的忽略文件列表。`.env` 必须加入，防止密码泄露 |

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| `.env` 文件 | 存放环境变量，Compose 自动读取 | 绝对不能提交到 Git；和 compose.yml 同级目录 |
| 变量替换 | `${VARIABLE}` | 可出现在 compose.yml 任何位置 |
| 默认值 | `${VAR:-默认值}` | 没设变量时用默认值，做到"开箱即用" |
| 必须设定 | `${VAR:?错误信息}` | 变量没设时报错，比静默空值安全 |
| 优先级 | Shell 环境变量 > `.env` > 默认值 | CI/CD 可通过 Shell 变量注入配置 |
| profiles | `profiles: - dev` | 按场景选择性启动服务 |
| 启动 profile | `docker compose --profile dev up` | 不指定则只启动无 profile 的服务 |
| 多 profile | `docker compose --profile dev --profile debug up` | 一个服务可以属于多个 profile |
| 指定 .env 文件 | `docker compose --env-file .env.prod up` | 切换环境配置 |
| 安全实践 | `.env.example` 模板文件 | 提交模板，不提交真实配置 |

---

> **[可暂停点 5/8]**：第五篇结束。重启验证命令：
>
> ```bash
> docker compose version
> # 确认 Docker Compose 可用
>
> docker compose ps
> # 查看当前是否有正在运行的 Compose 项目
>
> # 如果之前有 WordPress 项目，验证它还在运行：
> cd ~/wordpress-demo && docker compose ps
> # 如果停止了，重新启动：
> cd ~/wordpress-demo && docker compose up -d
> ```

---

## 本篇最可能出错的地方及原因

### 1. `.env` 文件提交到 Git

**这是安全层面最高频的错误。** 习惯了 `git add .` 和 `git commit -a`，`.env` 文件就被带上去了。一旦 push 到 GitHub，密码就暴露了。

**预防**：项目初始化时就创建 `.gitignore`，第一行写 `.env`。同时创建 `.env.example` 作为模板提交。

**如果已经泄露**：立刻改密码，然后再处理 Git 历史。Git 历史无法真正删除（即使 force push，GitHub 的缓存和 fork 的仓库里可能还有）。

### 2. 变量名拼写错误

`.env` 里写 `MYSQL_ROOT_PASSWORD`，compose.yml 里写 `${MYSQL_ROOT_PASWORD}`（少了一个 S）。Compose 不会报错，只是把未定义变量替换为空字符串。MySQL 密码变成空的，容器启动失败——但错误信息不会告诉你"密码没设"，而是 `Access denied for user 'root'@'localhost'`。

**排查**：`docker compose config` 输出完整配置，逐行检查变量值是否和预期一致。

### 3. `profiles` 的静默行为

`docker compose --profile typo up`（拼写错误）不会报错，只是静默地不启动带 profile 的服务。你以为启动了调试工具，实际上没有。

**排查**：`docker compose ps` 永远是你最好的朋友。启动后立刻检查，确认所有该启动的服务都在。

### 4. `.env` 文件格式错误

`.env` 文件不是随便写的。等号两边不能有空格，值如果有空格需要引号，注释用 `#`。格式错误可能导致变量值不是你预期的。

```bash
# ❌ 错误
WEB_PORT = 8080          # 有空格
DATABASE_URL=mysql://user:pass@host/db  # pass 里的特殊字符没引号

# ✅ 正确
WEB_PORT=8080
DATABASE_URL="mysql://user:p@ss@host/db"
```

### 5. 混淆 `profiles` 和 `depends_on`

`profiles` 控制"哪些服务启动"，`depends_on` 控制"启动顺序"。它们不是互斥的——你可以同时用。一个带 profile 的服务仍然可以有 `depends_on`：

```yaml
phpmyadmin:
  profiles:
    - dev
  depends_on:
    - db         # 当 --profile dev 启动时，先启 db 再启 phpmyadmin
```

但注意：`depends_on` 里引用的服务（如 `db`）不能有 profiles 限制，否则 `db` 没启动，`phpmyadmin` 的依赖就永远满足不了。