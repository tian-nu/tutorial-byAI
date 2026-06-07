# 附录 C — 常见错误排查

> 按场景分类的 Docker 常见错误排查指南。包含 20 条高频错误，每条给出错误现象、原因分析、排查命令和解决方案。

---

## 一、安装问题

### 1. Docker Desktop 启动失败

| 项目 | 内容 |
|------|------|
| **错误现象** | Docker Desktop 启动后卡在 "Docker Engine starting..."，或直接报错退出 |
| **原因** | ① Windows：WSL 2 未安装或版本太旧；② Hyper-V 未启用；③ 虚拟化在 BIOS 中被禁用 |
| **排查命令** | `wsl --version`（Windows），`systemctl status docker`（Linux） |
| **解决方案** | Windows：`wsl --install` 安装 WSL 2；在 BIOS 中启用 Intel VT-x / AMD-V；Linux：`sudo systemctl start docker`，检查 `journalctl -u docker` 日志 |

### 2. `docker: command not found`

| 项目 | 内容 |
|------|------|
| **错误现象** | 终端输入 `docker` 提示 `command not found` |
| **原因** | Docker 未安装，或安装后未将当前用户加入 `docker` 组 |
| **排查命令** | `which docker`、`systemctl status docker` |
| **解决方案** | 安装 Docker；加入 docker 组：`sudo usermod -aG docker $USER`，然后**重新登录**（必须重新登录才生效） |

### 3. `permission denied` 使用 Docker 命令

| 项目 | 内容 |
|------|------|
| **错误现象** | `Got permission denied while trying to connect to the Docker daemon socket` |
| **原因** | 当前用户不在 `docker` 组中，没有权限访问 `/var/run/docker.sock` |
| **排查命令** | `groups`（查看当前用户组） |
| **解决方案** | `sudo usermod -aG docker $USER`，然后**登出再登入**。不要用 `sudo chmod 777 /var/run/docker.sock`——这是安全漏洞 |

---

## 二、构建问题

### 4. Dockerfile 构建报 `COPY failed: file not found`

| 项目 | 内容 |
|------|------|
| **错误现象** | `COPY failed: file not found in build context or excluded by .dockerignore` |
| **原因** | ① 源文件路径写错；② 文件在 `.dockerignore` 中被排除；③ 路径是相对路径但不是相对于构建上下文 |
| **排查命令** | `ls -la` 确认文件存在；`cat .dockerignore` 检查排除规则 |
| **解决方案** | 确认 `COPY` 的源路径是相对于构建上下文（`docker build` 的 `context` 目录）；检查 `.dockerignore` 是否误排除了目标文件 |

### 5. 构建报 `exec format error`

| 项目 | 内容 |
|------|------|
| **错误现象** | `standard_init_linux.go:228: exec user process caused: exec format error` |
| **原因** | 在 ARM 架构（如 Apple Silicon Mac）上构建的镜像，部署到 x86 服务器上运行，或反之 |
| **排查命令** | `uname -m` 查看架构；`docker inspect` 查看镜像架构 |
| **解决方案** | 用 `docker build --platform linux/amd64` 指定目标平台；或用 Buildx 多平台构建：`docker buildx build --platform linux/amd64,linux/arm64` |

### 6. 构建报 `no space left on device`

| 项目 | 内容 |
|------|------|
| **错误现象** | 构建过程中报 `no space left on device` 或 `write /var/lib/docker/...: no space left on device` |
| **原因** | 宿主机磁盘空间不足，或 Docker 的 overlay2 存储空间耗尽 |
| **排查命令** | `df -h` 查看磁盘；`docker system df` 查看 Docker 占用 |
| **解决方案** | `docker system prune -a -f` 清理无用镜像和容器；`docker volume prune -f` 清理无用数据卷；考虑增加磁盘空间 |

### 7. 构建非常慢，每次都下载全部依赖

| 项目 | 内容 |
|------|------|
| **错误现象** | 每次 `docker build` 都要重新下载依赖，即使没改 `package.json` |
| **原因** | Dockerfile 中 `COPY . .` 在 `RUN npm install` 之前，代码变更导致依赖缓存失效 |
| **排查命令** | 检查 Dockerfile 中 `COPY` 和 `RUN` 的顺序 |
| **解决方案** | 调整顺序：先 `COPY package.json` → `RUN npm install` → 再 `COPY . .`。把不常变的层放前面 |

---

## 三、运行问题

### 8. 容器启动后立即退出

| 项目 | 内容 |
|------|------|
| **错误现象** | `docker ps` 看不到容器，`docker ps -a` 显示 `Exited (0)` 或 `Exited (1)` |
| **原因** | ① 容器内 PID 1 进程执行完毕退出；② 启动命令错误；③ 缺少必要的环境变量或配置 |
| **排查命令** | `docker logs <容器名>` 查看退出前的输出；`docker inspect <容器名> --format='{{.State.ExitCode}}'` |
| **解决方案** | 确保 `CMD` 或 `ENTRYPOINT` 启动的是一个前台持续运行的进程；检查 `docker logs` 的报错信息 |

### 9. 容器报 `Connection refused` 但 `docker ps` 显示 Up

| 项目 | 内容 |
|------|------|
| **错误现象** | 容器在运行，但连接端口报 `Connection refused` |
| **原因** | ① 服务只监听 `127.0.0.1` 而不是 `0.0.0.0`；② 服务还在初始化（如 MySQL 首次启动）；③ 端口映射错误 |
| **排查命令** | `docker exec <容器名> netstat -tlnp` 查看容器内端口监听；`docker port <容器名>` 查看端口映射 |
| **解决方案** | 确认服务监听 `0.0.0.0`；给数据库等慢启动服务加 `HEALTHCHECK`；确认 Compose 中 `depends_on` 用了 `condition: service_healthy` |

### 10. 容器被 OOM Kill（退出码 137）

| 项目 | 内容 |
|------|------|
| **错误现象** | `docker ps -a` 显示 `Exited (137)` |
| **原因** | 容器内存使用超过 `--memory` 限制，或被宿主机 OOM Killer 杀死 |
| **排查命令** | `docker inspect <容器名> --format='{{.State.OOMKilled}}'`；`dmesg \| grep -i oom` 查看系统日志 |
| **解决方案** | 增加 `--memory` 限制值；优化应用内存使用；Java 应用配合 `-XX:MaxRAMPercentage`；检查 `docker stats` 确认实际内存使用 |

### 11. 容器内 `apt-get` 或 `apk` 报网络错误

| 项目 | 内容 |
|------|------|
| **错误现象** | `Could not resolve 'archive.ubuntu.com'` 或 `temporary failure resolving` |
| **原因** | 容器 DNS 配置问题，无法解析外部域名 |
| **排查命令** | `docker exec <容器名> cat /etc/resolv.conf`；`docker exec <容器名> ping 8.8.8.8`（测试网络连通性） |
| **解决方案** | 检查 `/etc/docker/daemon.json` 的 `dns` 配置；重启 Docker：`sudo systemctl restart docker`；确认宿主机 DNS 正常 |

---

## 四、网络问题

### 12. 容器之间无法通过容器名通信

| 项目 | 内容 |
|------|------|
| **错误现象** | `ping: bad address 'my-container'` |
| **原因** | 容器不在同一个 Docker 网络（bridge）中；或用的是默认 bridge 网络（不支持 DNS 解析） |
| **排查命令** | `docker network inspect <网络名>` 查看网络中的容器列表 |
| **解决方案** | 创建自定义网络：`docker network create my-net`；把容器都加入同一个网络：`docker network connect my-net <容器名>`；Compose 中容器默认在同一网络，不需要额外配置 |

### 13. 端口映射不生效

| 项目 | 内容 |
|------|------|
| **错误现象** | `curl http://localhost:8080` 无响应 |
| **原因** | ① 端口映射写错（`-p 80:80` 但服务监听 3000）；② 宿主机端口被占用；③ 防火墙阻止 |
| **排查命令** | `docker port <容器名>` 查看映射；`sudo lsof -i :8080` 查看端口占用；`sudo ufw status` 或 `sudo firewall-cmd --list-ports` 查看防火墙 |
| **解决方案** | 确认 `-p 宿主机端口:容器端口` 中容器端口对应服务监听端口；换一个宿主机端口；开放防火墙端口 |

### 14. Compose 中 `depends_on` 不等待服务就绪

| 项目 | 内容 |
|------|------|
| **错误现象** | `app` 容器启动后报数据库连接失败，但 `db` 容器也在运行 |
| **原因** | `depends_on` 默认只等容器启动（`Up`），不等服务就绪（`healthy`） |
| **排查命令** | `docker compose ps` 查看服务状态 |
| **解决方案** | 给数据库加 `healthcheck`，然后用 `depends_on: db: condition: service_healthy` |

---

## 五、数据卷问题

### 15. 数据卷挂载后容器内文件消失

| 项目 | 内容 |
|------|------|
| **错误现象** | 挂载 volume 或 bind mount 后，容器内原来的文件不见了 |
| **原因** | Docker 挂载的行为是"覆盖"——挂载目标路径的内容被宿主机目录/卷内容替换 |
| **排查命令** | `docker inspect <容器名> --format='{{json .Mounts}}'` 查看挂载配置 |
| **解决方案** | 用匿名卷保护：`- /app/node_modules`（匿名卷不会被 bind mount 覆盖）；首次启动前确保数据卷已初始化 |

### 16. Bind mount 在 Windows/macOS 上性能极差

| 项目 | 内容 |
|------|------|
| **错误现象** | 容器内文件读写极慢，`npm install` 要几分钟 |
| **原因** | Docker Desktop 在 Windows/macOS 上通过虚拟化层访问宿主机文件系统，bind mount 性能天然差 |
| **排查命令** | `docker exec <容器名> time ls -la /app` 测试文件操作速度 |
| **解决方案** | 只挂载必要的子目录（如 `./src:/app/src`），不要挂载整个项目；用 `docker compose watch`（Compose v2.22+）替代 bind mount；考虑用 Dev Containers |

### 17. `docker compose down -v` 误删了重要数据

| 项目 | 内容 |
|------|------|
| **错误现象** | 执行 `docker compose down -v` 后，数据库数据丢失 |
| **原因** | `-v` 参数删除所有关联的匿名卷和命名卷 |
| **排查命令** | 无（数据已删除，无法恢复） |
| **解决方案** | 命名卷在 `compose.yml` 中声明 `external: true` 避免被删除；养成备份习惯；确认数据卷有备份后再执行 `-v`；`docker compose down` 不加 `-v` 不会删除数据卷 |

---

## 六、Compose 问题

### 18. `docker compose up` 报 `service "xxx" has no healthcheck configured`

| 项目 | 内容 |
|------|------|
| **错误现象** | `service "db" has no healthcheck configured` |
| **原因** | `depends_on` 中用了 `condition: service_healthy`，但目标服务没有定义 `healthcheck` |
| **排查命令** | 检查 `compose.yml` 中目标服务的配置 |
| **解决方案** | 给目标服务添加 `healthcheck:` 配置；或者去掉 `condition: service_healthy` 改用默认的 `depends_on` |

### 19. Compose 环境变量不生效

| 项目 | 内容 |
|------|------|
| **错误现象** | 容器内 `echo $MY_VAR` 为空或不是预期值 |
| **原因** | ① `.env` 文件不在 `compose.yml` 同级目录；② 变量名拼写错误；③ shell 环境中同名变量覆盖了 `.env` 的值 |
| **排查命令** | `docker compose config` 查看合并后的完整配置（包含变量值） |
| **解决方案** | 确认 `.env` 文件在 `compose.yml` 同级目录；确认变量名一致；用 `docker compose config` 验证 |

### 20. `docker compose pull` 不更新镜像（提示 Skipped）

| 项目 | 内容 |
|------|------|
| **错误现象** | `Skipped - No image tag specified, pull skipped` |
| **原因** | `compose.yml` 中服务用的是 `build:` 而不是 `image:`，`pull` 只能拉取 `image:` 指定的镜像 |
| **排查命令** | 检查 `compose.yml` 中服务用的是 `build` 还是 `image` |
| **解决方案** | 服务器上的 `compose.yml` 用 `image:` 指定镜像；本地开发用 `docker-compose.override.yml` 覆盖为 `build:` |

---

## 附录小结

> 本附录覆盖了 Docker 使用中最常见的 20 个问题，按场景（安装、构建、运行、网络、数据卷、Compose）分类。每个问题包含：错误现象 → 原因分析 → 排查命令 → 解决方案。遇到问题时，先按场景定位，再按排查命令确认，最后按解决方案修复。
>
> **排查通用原则**：
> 1. 先看日志：`docker logs <容器名>` 或 `docker compose logs`
> 2. 再看状态：`docker ps -a` 和 `docker inspect`
> 3. 再看配置：`docker compose config` 和 `docker inspect --format`
> 4. 最后看系统：`docker system df` 和 `docker info`