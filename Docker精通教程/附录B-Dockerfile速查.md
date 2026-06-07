# 附录 B — Dockerfile 指令速查

> 按字母顺序列出所有 Dockerfile 指令，包含语法、说明、示例和注意事项。

---

## FROM

| 项目 | 内容 |
|------|------|
| **语法** | `FROM <镜像>[:<标签>] [AS <阶段名>]` |
| **说明** | 指定基础镜像。每个 Dockerfile 必须以 `FROM` 开头（`ARG` 除外）。多阶段构建中可以有多个 `FROM` |
| **示例** | `FROM node:20-alpine AS builder` |
| **注意事项** | 优先用 alpine 或 slim 版本缩小体积；锁定具体版本号，不要用 `latest`；`AS` 命名阶段便于后续引用 |

---

## RUN

| 项目 | 内容 |
|------|------|
| **语法** | `RUN <命令>`（shell 形式）或 `RUN ["可执行文件", "参数1", "参数2"]`（exec 形式） |
| **说明** | 在镜像构建时执行命令。每一条 `RUN` 创建一个新层 |
| **示例** | `RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*` |
| **注意事项** | 多条命令用 `&&` 连接成一条 `RUN`，减少镜像层数；清理包管理器缓存（`apt clean`、`rm -rf /var/lib/apt/lists/*`）；安装后立即删除临时文件 |

---

## CMD

| 项目 | 内容 |
|------|------|
| **语法** | `CMD ["可执行文件", "参数1", "参数2"]`（exec 形式，推荐）或 `CMD 命令 参数1`（shell 形式） |
| **说明** | 容器启动时的默认命令。如果 `docker run` 后面跟了命令，`CMD` 会被覆盖 |
| **示例** | `CMD ["node", "server.js"]` |
| **注意事项** | 推荐用 exec 形式（数组），避免 shell 解析问题；一个 Dockerfile 只有最后一个 `CMD` 生效；`CMD` 可被 `docker run` 后的命令覆盖 |

---

## ENTRYPOINT

| 项目 | 内容 |
|------|------|
| **语法** | `ENTRYPOINT ["可执行文件", "参数1", "参数2"]`（exec 形式）或 `ENTRYPOINT 命令 参数1`（shell 形式） |
| **说明** | 容器入口点。`docker run` 后面的命令作为参数追加到 `ENTRYPOINT` |
| **示例** | `ENTRYPOINT ["nginx"]` + `CMD ["-g", "daemon off;"]` |
| **注意事项** | `ENTRYPOINT` + `CMD` = 完整启动命令；`ENTRYPOINT` 不会被 `docker run` 后的命令覆盖（除非用 `--entrypoint` 强制覆盖）；适合做固定任务的容器 |

---

## COPY

| 项目 | 内容 |
|------|------|
| **语法** | `COPY [--chown=<用户>:<组>] <源路径> <目标路径>` |
| **说明** | 从构建上下文（宿主机）复制文件/目录到镜像。支持 `--from=<阶段名>` 从其他构建阶段复制 |
| **示例** | `COPY --chown=appuser:appgroup package.json ./` |
| **注意事项** | 源路径是相对于构建上下文的，不能访问 `../` 上级目录；`--chown` 改变文件所有权；`COPY --from=builder` 是多阶段构建的关键语法；如需自动解压 tar 用 `ADD` |

---

## ADD

| 项目 | 内容 |
|------|------|
| **语法** | `ADD [--chown=<用户>:<组>] <源> <目标路径>` |
| **说明** | 功能类似 `COPY`，但额外支持：① 源是 URL 时自动下载；② 源是 tar 时自动解压 |
| **示例** | `ADD https://example.com/archive.tar.gz /tmp/` |
| **注意事项** | 能用 `COPY` 就不用 `ADD`——`ADD` 的"魔法"行为（自动解压）可能导致非预期结果；下载远程文件推荐用 `RUN curl` 或 `RUN wget` 更可控 |

---

## WORKDIR

| 项目 | 内容 |
|------|------|
| **语法** | `WORKDIR <路径>` |
| **说明** | 设置工作目录。后续的 `RUN`、`CMD`、`ENTRYPOINT`、`COPY`、`ADD` 都在此目录下执行 |
| **示例** | `WORKDIR /app` |
| **注意事项** | 如果目录不存在，自动创建；用 `WORKDIR` 不要用 `RUN cd`——`RUN cd` 只在当前层生效，下一条 `RUN` 又回到原目录；可以用相对路径，会基于上一个 `WORKDIR` |

---

## ENV

| 项目 | 内容 |
|------|------|
| **语法** | `ENV <键>=<值>` 或 `ENV <键> <值>`（旧语法） |
| **说明** | 设置环境变量，在构建时和运行时都生效 |
| **示例** | `ENV NODE_ENV=production` |
| **注意事项** | 不要在 `ENV` 中存密钥——会被永久嵌入镜像层；运行时变量用 `ARG` 更安全；`ENV` 值在后续所有层中可用 |

---

## ARG

| 项目 | 内容 |
|------|------|
| **语法** | `ARG <变量名>[=<默认值>]` |
| **说明** | 定义构建时参数，只在构建阶段有效，不会进入最终镜像 |
| **示例** | `ARG VERSION=1.0` → `docker build --build-arg VERSION=2.0 .` |
| **注意事项** | `ARG` 值不会保留在最终镜像中（除非被 `ENV` 引用）；适合传递构建版本号、构建时间等；`ARG` 在 `FROM` 之前声明时，只在 `FROM` 行有效 |

---

## EXPOSE

| 项目 | 内容 |
|------|------|
| **语法** | `EXPOSE <端口>[/<协议>]` |
| **说明** | 声明容器运行时监听的端口。仅作文档用途，**不实际发布端口** |
| **示例** | `EXPOSE 3000` |
| **注意事项** | `EXPOSE` 只是声明，不会映射端口到宿主机——映射用 `docker run -p` 或 Compose 的 `ports:`；协议默认 TCP，UDP 需显式指定：`EXPOSE 53/udp` |

---

## USER

| 项目 | 内容 |
|------|------|
| **语法** | `USER <用户名>[:<用户组>]` 或 `USER <UID>[:<GID>]` |
| **说明** | 指定后续 `RUN`、`CMD`、`ENTRYPOINT` 以哪个用户身份运行。默认是 root |
| **示例** | `USER appuser` 或 `USER 1001:1001` |
| **注意事项** | 安全最佳实践：不要用 root 运行应用；`USER` 前要创建用户（`adduser`/`useradd`）；`COPY` 要在 `USER` 之前执行，且带 `--chown`；非 root 不能绑定 1024 以下端口 |

---

## HEALTHCHECK

| 项目 | 内容 |
|------|------|
| **语法** | `HEALTHCHECK [选项] CMD <命令>` 或 `HEALTHCHECK NONE`（禁用继承的健康检查） |
| **说明** | 定义容器健康检查规则。Docker 根据命令退出码判断容器是否健康（0=健康，非0=不健康） |
| **示例** | `HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD curl -f http://localhost/ \|\| exit 1` |
| **注意事项** | 检查命令必须轻量、快速、确定性；`--start-period` 给慢启动服务留缓冲期；连续失败 `retries` 次才标记 `unhealthy`；一个 Dockerfile 只能有一个 `HEALTHCHECK` |

---

## VOLUME

| 项目 | 内容 |
|------|------|
| **语法** | `VOLUME ["<路径1>", "<路径2>"]` 或 `VOLUME <路径>` |
| **说明** | 创建匿名数据卷挂载点，用于持久化数据或共享数据 |
| **示例** | `VOLUME ["/var/lib/mysql", "/var/log"]` |
| **注意事项** | 匿名卷在容器删除时不会自动删除（除非 `docker rm -v`）；`VOLUME` 在 Dockerfile 中声明后，该目录的后续修改都不会写入镜像层；数据库数据、日志等需要持久化的数据适合用 `VOLUME` |

---

## SHELL

| 项目 | 内容 |
|------|------|
| **语法** | `SHELL ["可执行文件", "参数"]` |
| **说明** | 覆盖 shell 形式的默认 shell（Linux 默认 `/bin/sh -c`，Windows 默认 `cmd /S /C`） |
| **示例** | `SHELL ["/bin/bash", "-c"]` |
| **注意事项** | 很少需要用到，除非 shell 形式命令需要 bash 特性；Windows 镜像可能需要 `SHELL ["powershell", "-Command"]` |

---

## STOPSIGNAL

| 项目 | 内容 |
|------|------|
| **语法** | `STOPSIGNAL <信号>` |
| **说明** | 指定 `docker stop` 发送的停止信号。默认是 `SIGTERM` |
| **示例** | `STOPSIGNAL SIGQUIT` |
| **注意事项** | 某些应用对 `SIGTERM` 不响应，需要换成 `SIGINT` 或 `SIGQUIT`；Nginx 推荐用 `SIGQUIT` 实现优雅关闭 |

---

## LABEL

| 项目 | 内容 |
|------|------|
| **语法** | `LABEL <键>=<值> <键>=<值>` |
| **说明** | 给镜像添加元数据标签，用于组织、过滤、文档 |
| **示例** | `LABEL maintainer="team@example.com" version="1.0"` |
| **注意事项** | 多条 `LABEL` 合成一条可减少镜像层数；标签可以用 `docker images --filter` 过滤 |

---

## ONBUILD

| 项目 | 内容 |
|------|------|
| **语法** | `ONBUILD <Dockerfile 指令>` |
| **说明** | 定义触发器指令。当此镜像作为另一个镜像的基础镜像时，`ONBUILD` 后的指令会在子镜像的 `FROM` 之后自动执行 |
| **示例** | `ONBUILD COPY . /app` |
| **注意事项** | 很少使用，容易产生非预期行为；适合做"父镜像"模板——如标准化的构建环境；`ONBUILD` 不会在自身构建时执行 |

---

## 附录小结

> 本附录涵盖了 Dockerfile 的全部 17 个指令（FROM、RUN、CMD、ENTRYPOINT、COPY、ADD、WORKDIR、ENV、ARG、EXPOSE、USER、HEALTHCHECK、VOLUME、SHELL、STOPSIGNAL、LABEL、ONBUILD）。每个指令都包含语法、实际示例和关键注意事项。建议结合第 10～14 章（Dockerfile 系列）深入学习。