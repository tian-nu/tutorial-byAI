# 15 — Volume 数据持久化

> - 对应文档版本：Docker精通教程 outline v1
> - 适用环境：任何已安装 Docker 的系统
> - 读者角色：已掌握容器基本操作，需要让容器数据"活过"容器删除的开发者
> - 预计耗时：新手 40 分钟 / 熟手 15 分钟
> - 前置教程：第 6 章（容器生命周期）
> - 可视化：无

---

## 我在做什么？

你现在能启动容器、进入容器、在里面装软件跑程序了。但你有没有想过一个问题：

> 你在容器里写的数据，删了容器之后还在吗？

答案让人不安：**不在。**

Docker 容器的设计哲学是"用完即弃"。容器删除时，它在运行时产生的所有文件（数据库内容、日志、用户上传的图片、配置文件……）全部跟着消失。就像你在酒店房间里写了一本小说，退房时保洁阿姨把它当垃圾扔了。

这一章教你用 **Volume** *此术语见附录C* 把数据"存进保险箱"。容器可以随便删，数据永远在。

学完这一章，你能：
- 理解为什么容器默认不持久化数据
- 用 bind mount 把宿主机目录挂进容器
- 用 named volume 让 Docker 替你管理数据
- 给 MySQL 容器配上持久化存储，删了容器数据也不丢
- 查看、清理 Docker 管理的卷

---

## 一、容器的"健忘症"：数据为什么没了？

### 先做一个残酷实验

```bash
# 1. 启动一个容器，在里面创建一个文件
docker run --name demo-container alpine:latest sh -c "echo '珍贵数据' > /data.txt && cat /data.txt"
# 输出：珍贵数据
```

数据写好了，容器也退出了。删掉它，再起一个新的：

```bash
# 2. 删除容器
docker rm demo-container

# 3. 用同样的镜像启动一个新容器，尝试读取
docker run --rm alpine:latest cat /data.txt
# 输出：cat: can't open '/data.txt': No such file or directory
```

文件没了。这叫什么？这叫**容器的存储层是临时的**。

### 想多一点：为什么 Docker 要这么设计？

镜像的每一层是只读的。容器启动时，Docker 在上面加了一层**可写层**（也叫容器层）。你所有的修改——创建文件、安装软件、改配置——全在这一层。

这层是"一次性"的。容器删除，这层就没了。

这难道不是设计缺陷吗？不，这是**刻意设计**。Docker 希望你：
- 容器本身不承载状态
- 数据存到专门的持久化存储里
- 容器可以随时销毁、重建、横向扩展

如果你把重要的东西写在容器可写层，然后 `docker rm` 了——这不是 Docker 的 bug，是你没做Volume。

---

## 二、Volume 的两个流派

Docker 有两种方式让你持久化数据：

| 类型 | 谁管理 | 存放位置 | 典型场景 |
|------|--------|---------|---------|
| **bind mount** *此术语见附录C* | 你手动指定宿主机路径 | 宿主机任意目录 | 开发时挂载代码目录，实时修改 |
| **named volume** *此术语见附录C* | Docker 管理 | `/var/lib/docker/volumes/` | 生产环境数据库、重要数据 |

### 比喻帮你记住

- **bind mount**：你在墙（宿主机文件系统）上钉一个书架，容器可以往上面放书。书架位置由你决定。
- **named volume**：你租了一个银行保险箱（Docker 管理的存储空间），你把东西放进去，Docker 帮你保管。你不知道保险箱具体位置，也不在乎。

---

## 三、`-v` 语法（快速上手，但不够明确）

### bind mount 用 `-v`

```bash
# 语法：-v 宿主机绝对路径:容器内路径
docker run -v /home/user/myapp:/app nginx
#          ──────┬──────  ─┬─
#          宿主机目录    容器内目录
```

```bash
# 实战：把当前目录挂进容器的 /data
mkdir -p /tmp/demo-host
echo "宿主机的文件" > /tmp/demo-host/host.txt

docker run --rm -v /tmp/demo-host:/container-data alpine:latest cat /container-data/host.txt
# 输出：宿主机的文件
```

容器里面读到的 `/container-data/host.txt`，实际上是宿主机 `/tmp/demo-host/host.txt`。你改宿主机文件，容器里立刻能看到；容器里改文件，宿主机也立刻能看到。

### named volume 用 `-v`

```bash
# 语法：-v 卷名:容器内路径（卷名不以 / 开头）
docker run -v mydata:/app/data alpine:latest
#          ──┬──
#          卷名（不是路径！）
```

Docker 会：
1. 检查有没有叫 `mydata` 的 volume
2. 没有就自动创建一个
3. 把它挂载到容器的 `/app/data` 路径

### `-v` 的三种面孔总结

```bash
# 1. bind mount（宿主机路径:容器路径）
docker run -v /home/jack/code:/app myimage

# 2. named volume（卷名:容器路径）
docker run -v myvolume:/app myimage

# 3. 匿名 volume（只写容器路径，Docker 自动生成卷名）
docker run -v /app/data myimage
```

第 3 种不推荐——你连卷名都不知道，以后怎么找？

---

## 四、`--mount` 语法（推荐）

`-v` 最大的问题是什么？看命令行很难分辨这是 bind mount 还是 named volume。而且 bind mount 路径写错 Docker 不会报错——它默默给你建个空目录。

`--mount` *此术语见附录C* 语法更啰嗦，但更安全、更明确：

```bash
# --mount 语法
docker run --mount type=bind,source=/host/path,target=/container/path myimage

# 对应的 -v 写法
docker run -v /host/path:/container/path myimage
```

### bind mount 用 `--mount`

```bash
# bind mount：必须指定 type=bind
docker run --rm \
  --mount type=bind,source=/tmp/demo-host,target=/container-data \
  alpine:latest cat /container-data/host.txt
```

如果 `source` 路径不存在，`--mount` **会报错**而不是悄悄建目录——这就是为什么推荐它。

### named volume 用 `--mount`

```bash
# named volume：type=volume
docker run --rm \
  --mount type=volume,source=mydata,target=/app/data \
  alpine:latest sh -c "echo '持久化数据' > /app/data/note.txt"
```

如果卷 `mydata` 不存在，Docker 会自动创建它（named volume 的便利性保留）。

### `-v` vs `--mount` 对比决策表

| 场景 | 用哪个 | 原因 |
|------|--------|------|
| 快速测试、临时挂载 | `-v` | 少打字 |
| 生产部署、脚本 | `--mount` | 明确类型，路径不存在时报错 |
| bind mount 且宿主机目录可能未创建 | `--mount` | `-v` 会偷偷建空目录 |
| 团队共享脚本 | `--mount` | 可读性更好 |

---

## 五、实战：MySQL 数据持久化

这是你入门 Volume 最重要的一节。我们做一个"狠心"的实验：

### 步骤 1：创建 named volume

```bash
docker volume create mysql-data
# 输出：mysql-data
```

### 步骤 2：启动带 Volume 的 MySQL 容器

```bash
docker run -d \
  --name mysql-persistent \
  -e MYSQL_ROOT_PASSWORD=your_root_password_here \
  --mount type=volume,source=mysql-data,target=/var/lib/mysql \
  mysql:8.0
```

> `MYSQL_ROOT_PASSWORD` 是必须的环境变量。生产环境请用真实强密码，不要照抄示例。

### 步骤 3：进入容器，建库建表，插入数据

```bash
# 进入容器
docker exec -it mysql-persistent bash

# 在容器内连接 MySQL
mysql -uroot -pyour_root_password_here
```

在 MySQL 客户端里执行：

```sql
-- 创建数据库
CREATE DATABASE docker_demo;

-- 切换到 docker_demo
USE docker_demo;

-- 创建表
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入一条测试数据
INSERT INTO users (name) VALUES ('张三');

-- 确认数据已写入
SELECT * FROM users;
-- +----+--------+---------------------+
-- | id | name   | created_at          |
-- +----+--------+---------------------+
-- |  1 | 张三   | 202X-XX-XX XX:XX:XX |
-- +----+--------+---------------------+

-- 退出 MySQL
EXIT;
```

```bash
# 退出容器
exit
```

### 步骤 4：狠心删除容器

```bash
docker rm -f mysql-persistent
# 容器被强制删除！
```

先别慌。容器是删了，但 volume 还在：

```bash
docker volume ls
# DRIVER    VOLUME NAME
# local     mysql-data    ← 还在！
```

### 步骤 5：用同一个 Volume 启动新容器

```bash
docker run -d \
  --name mysql-new \
  -e MYSQL_ROOT_PASSWORD=your_root_password_here \
  --mount type=volume,source=mysql-data,target=/var/lib/mysql \
  mysql:8.0
```

### 步骤 6：验证数据还在

```bash
docker exec -it mysql-new bash

# 进入 MySQL
mysql -uroot -pyour_root_password_here

USE docker_demo;
SELECT * FROM users;
# +----+--------+---------------------+
# | id | name   | created_at          |
# +----+--------+---------------------+
# |  1 | 张三   | 202X-XX-XX XX:XX:XX |
# +----+--------+---------------------+
#                     ↑ 数据还在！
```

你的数据活过了容器的"死亡"。这就是 Volume 的核心价值。

---

## 六、管理 Volume

### 查看所有卷

```bash
docker volume ls
# DRIVER    VOLUME NAME
# local     mysql-data
# local     mydata
```

### 查看卷的详细信息

```bash
docker volume inspect mysql-data
```

输出类似：

```json
[
    {
        "CreatedAt": "202X-XX-XXTXX:XX:XX+08:00",
        "Driver": "local",
        "Labels": null,
        "Mountpoint": "/var/lib/docker/volumes/mysql-data/_data",
        "Name": "mysql-data",
        "Options": null,
        "Scope": "local"
    }
]
```

`Mountpoint` 就是数据在宿主机上的实际路径。在 Linux 上你可以直接 `sudo ls` 看里面的文件。

> Windows 用户注意：Docker Desktop 在 Windows 上通过一个轻量级 Linux VM 运行 Docker。`Mountpoint` 指向 VM 内部路径，你无法在 Windows 资源管理器直接访问。但你可以通过容器来读写这些数据。

### 删除指定卷

```bash
# 警告：数据不可恢复！确保不再需要
docker volume rm mydata
```

如果卷正被某个容器使用，Docker 会拒绝删除：

```bash
docker volume rm mysql-data
# Error response from daemon: remove mysql-data: volume is in use
```

### 清理所有未使用的卷

```bash
# 删除所有没有被任何容器引用的 volume
docker volume prune
```

Docker 会提示确认：

```
WARNING! This will remove all local volumes not used by at least one container.
Are you sure you want to continue? [y/N] y
```

### 删除容器时顺便删 Volume

```bash
# -v 参数：删除容器时，同时删除它独占的匿名 volume
docker rm -v my-container
```

> ⚠️ 这对 named volume 无效——named volume 不会被自动删除，这是保护机制。

---

## 七、常见错误

### 错误 1：bind mount 路径写错，不报错

```bash
# ❌ 把 /home/user/appp 写成了 /home/user/appp（多了一个 p）
docker run -v /home/user/appp:/app myimage
```

用 `-v` 时，宿主机路径不存在，Docker 会**默默创建一个空目录**。容器启动正常，但里面空空如也。你盯着代码半小时才发现路径多打了一个字母。

✅ 用 `--mount` 避免：

```bash
# ✅ --mount 在路径不存在时直接报错
docker run --mount type=bind,source=/home/user/appp,target=/app myimage
# docker: Error response from daemon: invalid mount config for type "bind":
# bind source path does not exist: /home/user/appp
```

### 错误 2：Windows 路径格式问题

```powershell
# ❌ 错误：Windows 路径用反斜杠
docker run -v C:\Users\jack\code:/app myimage

# ❌ 错误：路径中有空格但不加引号
docker run -v C:\Users\jack\my code:/app myimage
```

✅ 正确做法：

```powershell
# ✅ Windows 路径必须用正斜杠 / 且不加 C: 后的反斜杠
docker run -v C:/Users/jack/code:/app myimage

# ✅ 路径含空格时用双引号包裹整个 -v 参数
docker run -v "C:/Users/jack/my code:/app" myimage

# ✅ 使用 --mount 语法更清晰
docker run --mount "type=bind,source=C:/Users/jack/code,target=/app" myimage
```

### 错误 3：容器内路径被 Volume 覆盖后，原有文件"消失"

```bash
# MySQL 镜像的 /var/lib/mysql 本来有初始数据
# 挂一个空 volume 上去后，原有文件被"遮盖"了
docker run -v empty-vol:/var/lib/mysql mysql:8.0
# MySQL 启动失败！因为 /var/lib/mysql 变成空的
```

❌ 原因：Volume 的挂载逻辑是**替换**，不是**合并**。你把一个空卷挂到一个本来有文件的目录上，那些原有文件就被"遮住"了。

✅ 解决方案：第一次挂载时，Docker 会把容器内目标路径的现有内容**复制到空 volume**（仅限 named volume，bind mount 不会）。所以：

```bash
# ✅ 第一次用 named volume 挂 MySQL 的数据目录是可以的
docker run -v mysql-data:/var/lib/mysql mysql:8.0
# Docker 会把 MySQL 镜像里 /var/lib/mysql 的初始数据复制到 mysql-data 卷
# 然后 MySQL 正常启动
```

这个"自动复制"行为只发生在**容器首次启动**且 **named volume 是空的**的时候。bind mount 永远不会复制。

### 错误 4：修改了宿主机文件，容器里没变化——然后发现挂错目录了

```bash
# 你改了 /host/app/config.yml
# 但实际挂载的是 /host/app-old/config.yml
# → 容器里当然没变化
```

✅ 排查方法：

```bash
# 查看容器的挂载详情
docker inspect 容器名 | grep -A 10 Mounts

# 或更精确
docker inspect -f '{{ json .Mounts }}' 容器名 | python3 -m json.tool
```

---

## 八、我做得对不对？

### 验证方法

```bash
# 1. 确认 volume 存在
docker volume ls | grep mysql-data

# 2. 查看 volume 详情
docker volume inspect mysql-data

# 3. 确认容器正在使用该 volume
docker inspect mysql-new -f '{{ json .Mounts }}' | python3 -m json.tool

# 4. 在容器内写入新数据
docker exec mysql-new mysql -uroot -pyour_root_password_here -e \
  "INSERT INTO docker_demo.users (name) VALUES ('李四'); SELECT * FROM docker_demo.users;"

# 5. 删容器，重建，查数据
docker rm -f mysql-new
docker run -d --name mysql-v3 \
  -e MYSQL_ROOT_PASSWORD=your_root_password_here \
  --mount type=volume,source=mysql-data,target=/var/lib/mysql \
  mysql:8.0

docker exec mysql-v3 mysql -uroot -pyour_root_password_here -e \
  "SELECT * FROM docker_demo.users;"
# 预期：张三和李四都在
```

---

## 本章小结

| 本章学了什么 | 对应命令/概念 | 注意事项 |
|-------------|-------------|---------|
| 容器数据为什么丢失 | 可写层是临时的，容器删除即丢失 | 不是 bug，是设计哲学 |
| bind mount | `-v /host/path:/container/path` | 宿主机目录 ↔ 容器目录实时同步 |
| named volume | `-v myvol:/path` | Docker 管理，位置在 `/var/lib/docker/volumes/` |
| `--mount` 语法（推荐） | `--mount type=bind,source=...,target=...` | 路径不存在时报错，比 `-v` 安全 |
| 创建 volume | `docker volume create 卷名` | 提前创建好，挂在容器时路径不会弄错 |
| 查看 volume | `docker volume ls` / `docker volume inspect` | inspect 可看 Mountpoint 实际路径 |
| 清理 volume | `docker volume prune` / `docker volume rm` | prune 删所有未使用的，rm 删指定 |
| MySQL 持久化实战 | 完整创建→写数据→删容器→重建→读数据 | 这是验证 Volume 价值的最佳方式 |
| Windows 路径 | 用正斜杠 `/`，空格加引号 | C:/Users/xxx，不是 C:\Users\xxx |
| bind mount 路径写错 | `-v` 不报错，`--mount` 报错 | 排查时用 `docker inspect` 看 Mounts |

---

## 本篇最可能出错的地方及原因

### 1. bind mount 路径写错，Docker 悄悄建空目录

这是 `-v` 最大的坑。因为 Docker 把不存在的宿主机路径当作"你想让我帮你建个目录"，所以它不会报错。容器启动正常，但里面没有你要的数据。《Docker 官方文档》也建议用 `--mount` 来避免这个问题。**口诀：bind mount 用 `--mount`。**

### 2. 把 MySQL 的 `/var/lib/mysql` 挂到空 bind mount 目录

```bash
# ❌ 如果 /tmp/empty-dir 是空的
docker run -v /tmp/empty-dir:/var/lib/mysql mysql:8.0
# MySQL 启动失败：/var/lib/mysql 里没有初始数据
```

bind mount 不会把容器内原有数据复制到宿主机目录。而 named volume 在第一次挂载且卷为空时**会复制**。这就是为什么生产环境数据库必须用 named volume。

### 3. 用 `docker rm` 忘加 `-v`，匿名 volume 堆积

你反复 `docker run -v /app/data myimage`（只指定容器内路径，不指定卷名），就创建了大量匿名 volume。每个都是随机名字，清理起来很麻烦。**定期执行 `docker volume prune`。**

### 4. Windows 和 macOS 上的 bind mount 性能差异

在 macOS 上，`osxfs` 文件共享的性能不如 Linux。大吞吐量场景（如挂载代码目录跑 Node.js 的 `node_modules`）会明显变慢。解决方案：把 `node_modules` 独立为一个 named volume，代码目录用 bind mount。

### 5. 容器被删除后 volume 还在，你以为数据丢了

`docker rm -f 容器名` 之后 `docker volume ls` 看到卷还在，以为：  "数据没丢，但我怎么访问？" 其实只要启动一个新容器挂载同一个 volume 即可。Volume 的生命周期独立于容器。