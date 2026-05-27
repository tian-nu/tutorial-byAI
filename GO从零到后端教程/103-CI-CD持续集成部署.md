# 第103章 · CI/CD持续集成部署

> "代码写好了、Docker镜像包好了——然后呢？每次改一行代码都手动build、test、push、deploy？别傻了。让机器替你做这些重复劳动。你只需要 `git push`，剩下的事交给CI/CD（持续集成与持续部署的自动化流水线，详见附录I）。本章用GitHub Actions教会你这个现代软件工程的必备技能。"

---

## 103.1 CI/CD是什么

### 先理解CI和CD

**CI（Continuous Integration，持续集成）**：
你把代码推到GitHub → 自动拉代码 → 自动编译 → 自动跑测试 → 自动代码检查。如果任何一步失败，你立刻收到通知。

目的：**尽早发现问题。** 你刚改了一行代码，5分钟后就知道它有没有破坏什么东西——而不是等到一个月后上线才发现。

**CD（Continuous Delivery/Deployment，持续交付/部署）**：
CI通过之后 → 自动构建Docker镜像 → 自动推送到镜像仓库 → 自动部署到测试/生产服务器。

目的：**自动化发布。** 代码合并到主分支后，不需要人为干预就能上线。

### 类比：餐厅的自动化厨房

| 步骤 | 传统方式 | CI/CD方式 |
|------|----------|-----------|
| 洗菜切菜 | 厨师手动 | 自动洗菜机+切菜机（CI） |
| 做菜 | 厨师凭经验 | 标准配方自动执行（CI） |
| 试吃 | 厨师自己尝 | 自动检测味道是否达标（CI测试） |
| 上菜 | 服务员端过去 | 自动传送带送到客人桌上（CD） |

你的角色从"洗菜切菜做菜试吃上菜全自己干"变成了"开发新菜品（写代码）→ 丢进自动化流水线 → 坐等上菜"。

### CI/CD流水线全景

```
git push ──>┌─────────────────────────────────────────────┐
             │  GitHub Actions / Jenkins / GitLab CI      │
             │                                              │
             │  1. Checkout 代码                            │
             │  2. 安装依赖（go mod download）               │
             │  3. 代码检查（go vet / golangci-lint）        │
             │  4. 单元测试（go test ./...）                 │
             │  5. 编译（go build）                          │
             │  ───────── CI完成 ─────────                  │
             │  6. 构建Docker镜像                            │
             │  7. 推送到镜像仓库                            │
             │  8. SSH到服务器，docker pull + docker run     │
             │  ───────── CD完成 ─────────                  │
             │                                              │
             └──────────────────────────────────────────────┘
```

---

## 103.2 GitHub Actions入门

### 核心概念

**Workflow（工作流）**：一个完整的自动化流程。定义在 `.github/workflows/` 目录下的YAML文件中。一个仓库可以有多个workflow（如 `ci.yml`、`deploy.yml`）。

**Job（任务）**：Workflow中的一组步骤，在同一个Runner上顺序执行。默认情况下多个Job并行运行，除非用 `needs` 指定依赖。

**Step（步骤）**：Job中的单个操作。可以是一条shell命令，也可以是一个Action（复用组件）。

**Event（事件）**：触发Workflow的条件——push、pull_request、schedule（定时）、手动触发等。

**Runner（运行器）**：执行Job的虚拟机。GitHub提供的Runner有 `ubuntu-latest`、`windows-latest`、`macos-latest`。

### 第一个Workflow

在仓库根目录创建 `.github/workflows/ci.yml`：

```yaml
name: CI

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  test-and-build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Go
        uses: actions/setup-go@v5
        with:
          go-version: "1.22"

      - name: Run tests
        run: go test ./... -v -cover

      - name: Run linter
        uses: golangci/golangci-lint-action@v4
        with:
          version: latest

      - name: Build
        run: go build -o myapp ./cmd/api/
```

**解释：**
- `on.push.branches`：当有人push到main或dev分支时触发
- `on.pull_request.branches`：当有人向main分支发起PR时也触发
- `uses: actions/checkout@v4`：GitHub官方Action，把代码拉下来
- `uses: actions/setup-go@v5`：安装Go环境
- `run: go test ./... -v -cover`：直接执行shell命令

---

## 103.3 实战：Go项目CI（lint + test + build）

一个完整的生产级CI Workflow：

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.22"
      - name: Run golangci-lint
        uses: golangci/golangci-lint-action@v4
        with:
          version: latest
          args: --timeout=5m

  test:
    needs: lint
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: testpass
          MYSQL_DATABASE: myapp_test
        ports:
          - 3306:3306
        options: >-
          --health-cmd="mysqladmin ping -h localhost"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd="redis-cli ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.22"
      - name: Run unit tests
        run: go test ./... -v -cover -coverprofile=coverage.out
      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: coverage.out

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.22"
      - name: Build
        run: go build -ldflags="-s -w" -o myapp ./cmd/api/
      - name: Upload binary
        uses: actions/upload-artifact@v4
        with:
          name: myapp-binary
          path: myapp
```

**关键点：**
- `needs: lint`、`needs: test`：lint通过后才跑test，test通过后才build——流水线串联
- `services`：GitHub Actions支持启动服务容器（数据库、缓存等），测试可以直接连这些容器
- `health-cmd`：和docker-compose的健康检查一样，确保服务真正就绪
- `upload-artifact`：把覆盖率报告和编译产物上传，供后续Job使用

---

## 103.4 实战：Go项目CD

CI通过后，自动构建Docker镜像、推送到仓库、部署到服务器。

```yaml
name: CD

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKER_USERNAME }}/myapp:latest
            ${{ secrets.DOCKER_USERNAME }}/myapp:${{ github.sha }}

      - name: Deploy to server
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            docker pull ${{ secrets.DOCKER_USERNAME }}/myapp:latest
            docker stop myapp || true
            docker rm myapp || true
            docker run -d \
              --name myapp \
              --restart always \
              -p 8080:8080 \
              -e DB_HOST=${{ secrets.DB_HOST }} \
              -e DB_PASSWORD=${{ secrets.DB_PASSWORD }} \
              -e REDIS_ADDR=${{ secrets.REDIS_ADDR }} \
              ${{ secrets.DOCKER_USERNAME }}/myapp:latest
            docker image prune -f
```

**关键点：**
- `${{ secrets.XXX }}`：从GitHub仓库的Settings → Secrets中读取。敏感信息（密码、SSH密钥）绝不硬编码。
- `${{ github.sha }}`：GitHub的内置变量，当前commit的哈希值。用作tag可以精确定位每次部署对应哪个commit。
- `|| true`：如果容器不存在，`docker stop`会报错。`|| true` 告诉Shell"即使这步失败也继续"。
- `docker image prune -f`：清理无用的旧镜像，防止服务器磁盘被撑满。

---

## 103.5 环境变量和Secrets管理

### 敏感信息绝不提交到Git！

```yaml
env:
  DB_PASSWORD: plaintext_password    # 绝对不要这样做！
```

GitHub仓库是公开的（或团队内部可见），任何提交到代码里的密码都可能泄露。

### GitHub Secrets正确用法

**设置：** GitHub仓库 → Settings → Secrets and variables → Actions → New repository secret

**使用：**
```yaml
- name: Deploy
  env:
    DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
  run: |
    echo "数据库密码已经安全注入到环境变量中"
    ./myapp
```

**GitHub不给显示Secrets的值**：一旦创建了Secret，它的值就再也看不到了（只能更新或删除）。Workflow执行时，Secret的值会被自动mask——即使你不小心把它的值打印到日志里，GitHub也会把它替换成 `***`。

### 分层管理

```
GitHub Secrets:
  ├── DOCKER_USERNAME          （构建用）
  ├── DOCKER_PASSWORD          （构建用）
  ├── SERVER_HOST              （部署用）
  ├── SERVER_USER              （部署用）
  ├── SERVER_SSH_KEY           （部署用——私钥！）
  ├── DB_PASSWORD              （运行时环境变量）
  ├── REDIS_PASSWORD           （运行时环境变量）
  └── JWT_SECRET               （运行时环境变量）
```

---

## 103.6 其他CI工具简介

### Jenkins

Jenkins是CI/CD界的"老祖宗"（2005年诞生）。Java写的，需要自己部署和运维。

**优点：** 插件生态极其丰富（几千个插件），完全可定制，适合大型企业
**缺点：** 部署和维护成本高，配置复杂（古老的Groovy语法），界面老气

**适不适合你：** 除非你的公司已经有Jenkins基础设施，否则对个人项目和中小团队来说太重了。

### GitLab CI

和GitLab深度集成，配置文件是 `.gitlab-ci.yml`。和GitHub Actions非常相似，但运行在GitLab自己的Runner上。

**优点：** 内置Docker Registry、内置Kubernetes集成
**缺点：** 和GitLab绑定

### 选择建议

| 场景 | 推荐 |
|------|------|
| 个人项目、GitHub上的开源项目 | GitHub Actions |
| 公司使用GitLab | GitLab CI |
| 大型企业、需要高度定制 | Jenkins |
| 不想维护CI服务器 | GitHub Actions / GitLab CI |

---

## 🤔 想多一点：CI/CD真的能完全自动化吗？

不完全。CD的最后一步——部署到生产环境——很多团队选择保留**人工审批**（"Continuous Delivery"而非"Continuous Deployment"）。

区别在于：
- **Continuous Delivery**：每次合并到main → 自动构建 → 自动测试 → **手动点击确认** → 自动部署到生产
- **Continuous Deployment**：每次合并到main → 自动构建 → 自动测试 → **自动部署到生产**（无需人工干预）

对于关键业务系统，保留一个人工确认的"安全阀门"是明智的。你可以在GitHub Actions中添加 `environment` 和审批规则来实现。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| CI | 持续集成：自动编译、测试、检查代码 |
| CD | 持续交付/部署：自动构建镜像、推送到仓库、部署 |
| Workflow | GitHub Actions的自动化流程，YAML定义 |
| Event | 触发条件：push/pull_request/schedule/manual |
| Job/Step | Job含多个Step，可并行或串行 |
| services | 在CI中启动数据库等依赖服务 |
| Secrets | 敏感信息的安全存储，`${{ secrets.XXX }}` |
| docker/build-push-action | 官方Action，构建和推送Docker镜像 |
| appleboy/ssh-action | 通过SSH在远程服务器执行命令 |
| Delivery vs Deployment | 前者有手动审批环节，后者全自动 |

> 🚀 下一章：第104章 · 云服务部署实战。CI/CD流水线搭好了，但"部署到服务器"——服务器在哪？怎么买？怎么配置？域名怎么绑？SSL证书怎么搞？下一章手把手带你走完从零到上线的全流程。

---
[← 上一章：102-Docker容器化.md](102-Docker容器化.md) | [下一章：104-云服务部署实战.md →](104-云服务部署实战.md)
