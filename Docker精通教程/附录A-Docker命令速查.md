# 附录 A — Docker 命令速查

> 按场景分类的常用 Docker 命令速查表。覆盖镜像管理、容器管理、网络、数据卷、Compose、系统管理六大场景。

---

## 一、镜像管理

| 命令 | 用途 | 常用选项 | 示例 |
|------|------|---------|------|
| `docker pull` | 拉取镜像 | — | `docker pull nginx:1.27-alpine` |
| `docker build` | 构建镜像 | `-t` 标签, `-f` 指定 Dockerfile, `--no-cache` 不用缓存, `--pull` 拉最新基础镜像 | `docker build -t my-app:v1 .` |
| `docker images` | 列出本地镜像 | `-a` 全部（含中间层）, `--filter` 过滤, `--format` 格式化 | `docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"` |
| `docker tag` | 给镜像打标签 | — | `docker tag my-app:v1 my-app:latest` |
| `docker push` | 推送镜像到仓库 | — | `docker push myuser/my-app:v1` |
| `docker rmi` | 删除镜像 | `-f` 强制删除 | `docker rmi my-app:old` |
| `docker save` | 导出镜像为 tar | `-o` 输出文件 | `docker save -o my-app.tar my-app:v1` |
| `docker load` | 从 tar 导入镜像 | `-i` 输入文件 | `docker load -i my-app.tar` |
| `docker history` | 查看镜像层历史 | `--no-trunc` 不截断输出 | `docker history nginx:alpine` |
| `docker inspect` | 查看镜像详细信息 | `--format` 格式化 | `docker inspect --format='{{.Created}}' nginx:alpine` |
| `docker scout` | 扫描镜像漏洞 | `quickview` 概览, `cves` 详细漏洞 | `docker scout quickview nginx:latest` |
| `docker image prune` | 清理无用镜像 | `-a` 全部未使用, `-f` 不确认 | `docker image prune -a -f` |

---

## 二、容器管理

| 命令 | 用途 | 常用选项 | 示例 |
|------|------|---------|------|
| `docker run` | 创建并启动容器 | `-d` 后台, `-it` 交互, `--name` 命名, `--rm` 退出即删, `-p` 端口, `-v` 挂载, `-e` 环境变量, `--restart` 重启策略 | `docker run -d --name web -p 80:80 nginx:alpine` |
| `docker ps` | 列出运行中的容器 | `-a` 全部（含已停止）, `--filter` 过滤, `--format` 格式化 | `docker ps -a --filter "status=exited"` |
| `docker stop` | 停止容器 | `-t` 超时秒数 | `docker stop my-container` |
| `docker start` | 启动已停止的容器 | — | `docker start my-container` |
| `docker restart` | 重启容器 | `-t` 超时秒数 | `docker restart my-container` |
| `docker rm` | 删除容器 | `-f` 强制（运行中也可删）, `-v` 同时删匿名卷 | `docker rm -f my-container` |
| `docker exec` | 在运行中的容器执行命令 | `-it` 交互式 | `docker exec -it my-container sh` |
| `docker logs` | 查看容器日志 | `-f` 实时跟踪, `--tail` 最近 N 行, `--since` 从某时间开始 | `docker logs -f --tail 100 my-container` |
| `docker inspect` | 查看容器详情 | `--format` 格式化 | `docker inspect --format='{{.State.Status}}' my-container` |
| `docker cp` | 容器与宿主机间复制文件 | — | `docker cp my-container:/app/log.txt ./` |
| `docker top` | 查看容器内进程 | — | `docker top my-container` |
| `docker stats` | 查看容器资源使用 | `--no-stream` 只输出一次 | `docker stats --no-stream` |
| `docker port` | 查看端口映射 | — | `docker port my-container` |
| `docker diff` | 查看容器文件变更 | — | `docker diff my-container` |
| `docker commit` | 从容器创建镜像 | `-m` 提交说明 | `docker commit -m "snapshot" my-container my-snapshot` |
| `docker container prune` | 清理已停止的容器 | `-f` 不确认 | `docker container prune -f` |

---

## 三、网络管理

| 命令 | 用途 | 常用选项 | 示例 |
|------|------|---------|------|
| `docker network ls` | 列出网络 | `--filter` 过滤 | `docker network ls` |
| `docker network create` | 创建网络 | `--driver` 驱动, `--subnet` 子网 | `docker network create --driver bridge my-net` |
| `docker network inspect` | 查看网络详情 | — | `docker network inspect my-net` |
| `docker network connect` | 将容器连接到网络 | `--alias` 别名, `--ip` 指定 IP | `docker network connect my-net my-container` |
| `docker network disconnect` | 断开容器与网络 | — | `docker network disconnect my-net my-container` |
| `docker network rm` | 删除网络 | — | `docker network rm my-net` |
| `docker network prune` | 清理未使用的网络 | `-f` 不确认 | `docker network prune -f` |

---

## 四、数据卷管理

| 命令 | 用途 | 常用选项 | 示例 |
|------|------|---------|------|
| `docker volume ls` | 列出数据卷 | `--filter` 过滤 | `docker volume ls` |
| `docker volume create` | 创建数据卷 | `--driver` 驱动 | `docker volume create my-volume` |
| `docker volume inspect` | 查看数据卷详情 | — | `docker volume inspect my-volume` |
| `docker volume rm` | 删除数据卷 | — | `docker volume rm my-volume` |
| `docker volume prune` | 清理未使用的数据卷 | `-f` 不确认 | `docker volume prune -f` |

---

## 五、Docker Compose

| 命令 | 用途 | 常用选项 | 示例 |
|------|------|---------|------|
| `docker compose up` | 启动服务 | `-d` 后台, `--build` 先构建, `--force-recreate` 强制重建, `--remove-orphans` 删孤立容器 | `docker compose up -d` |
| `docker compose down` | 停止并删除服务 | `-v` 同时删数据卷, `--rmi` 同时删镜像 | `docker compose down -v` |
| `docker compose ps` | 查看服务状态 | `-a` 全部（含已停止） | `docker compose ps` |
| `docker compose logs` | 查看服务日志 | `-f` 实时跟踪, `--tail` 最近 N 行 | `docker compose logs -f --tail 50 web` |
| `docker compose exec` | 在服务容器中执行命令 | `-it` 交互式 | `docker compose exec web sh` |
| `docker compose build` | 构建服务镜像 | `--no-cache` 不用缓存, `--pull` 拉最新基础镜像 | `docker compose build --pull` |
| `docker compose pull` | 拉取服务镜像 | — | `docker compose pull` |
| `docker compose push` | 推送服务镜像 | — | `docker compose push` |
| `docker compose restart` | 重启服务 | — | `docker compose restart web` |
| `docker compose stop` | 停止服务 | — | `docker compose stop` |
| `docker compose start` | 启动已停止的服务 | — | `docker compose start` |
| `docker compose config` | 查看合并后的配置 | `--format` 输出格式 | `docker compose config` |
| `docker compose run` | 运行一次性命令 | `--rm` 退出即删 | `docker compose run --rm web npm test` |

---

## 六、系统管理

| 命令 | 用途 | 常用选项 | 示例 |
|------|------|---------|------|
| `docker version` | 查看 Docker 版本 | `--format` 格式化 | `docker version` |
| `docker info` | 查看系统信息 | `--format` 格式化 | `docker info --format '{{.ServerVersion}}'` |
| `docker system df` | 查看磁盘使用 | `-v` 详细输出 | `docker system df` |
| `docker system prune` | 清理所有未使用的资源 | `-a` 全量清理, `-f` 不确认, `--volumes` 含数据卷 | `docker system prune -a -f` |
| `docker events` | 监听 Docker 事件 | `--since` 从某时间开始, `--filter` 过滤 | `docker events --filter "event=die"` |
| `docker login` | 登录镜像仓库 | `-u` 用户名, `--password-stdin` 从标准输入读密码 | `echo "$TOKEN" \| docker login -u myuser --password-stdin` |
| `docker logout` | 登出镜像仓库 | — | `docker logout` |
| `docker context ls` | 列出 Docker 上下文 | — | `docker context ls` |

---

## 附录小结

> 本附录覆盖了 Docker 日常使用中最常用的 60+ 条命令，按场景分类便于快速定位。建议收藏本文，需要时 `Ctrl+F` 搜索场景关键词即可。