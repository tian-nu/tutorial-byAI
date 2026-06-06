# 第100章 · Shell脚本基础

> "你在终端里敲的每一条命令都是可以'录下来'的。把一堆命令写到一个文件里，然后一次性执行——这就是Shell脚本。学会了它，部署代码、备份数据库、监控服务，全都可以自动化。本章从变量、条件、循环讲到函数，最后用两个实战脚本收尾。"

---

## 100.1 什么是Shell脚本

### 类比：做饭的菜单

你点外卖时，外卖小哥只需要送一份饭。但如果要开一个餐厅，你不可能每来一个客人就从头教厨师怎么做菜——你需要**菜谱**。

Shell脚本就是命令行操作的"菜谱"：把一系列命令按顺序写好，存到一个文件里，需要的时候 `bash 文件名` 一键执行。

### Shell vs Shell脚本

**Shell**（壳）是用户和操作系统内核之间的翻译官。你输入命令 → Shell解释 → 内核执行。常见的Shell有：
- `bash`（Bourne Again Shell）：Linux默认，最常用
- `zsh`（Z Shell）：macOS默认，功能更强
- `sh`：最原始的Shell，功能最少

**Shell脚本**就是一个以 `#!/bin/bash` 开头的文本文件，里面写着你平时在终端敲的命令。

### 第一个脚本：hello.sh

```bash
#!/bin/bash

echo "Hello, 后端工程师!"
echo "今天是 $(date)"
echo "当前目录是 $(pwd)"
```

执行方式：
```bash
chmod +x hello.sh            # 添加执行权限
./hello.sh                   # 运行
```

或者：
```bash
bash hello.sh                # 不需要执行权限，直接用bash解释器运行
```

输出：
```
Hello, 后端工程师!
今天是 Sat May 18 10:30:00 CST 2026
当前目录是 /home/alice
```

### `#!/bin/bash` 是什么

第一行的 `#!` 叫**shebang**（发音：shé-bàng）。它告诉系统："用哪个解释器来执行这个脚本"。

```bash
#!/bin/bash          # 用bash执行
#!/bin/sh            # 用sh执行
#!/usr/bin/env bash  # 自动找到bash的位置（更可移植）
#!/usr/bin/env python3  # 用Python执行
```

没有shebang也行，但系统会用当前Shell执行，可能导致兼容性问题（比如你在zsh里写了bash特有的语法）。

### 🤔 想多一点：Shell脚本是不是编程？

很多人觉得Shell脚本"不是真正的编程"——这不对。Shell脚本有变量、条件判断、循环、函数、输入输出，是一门完整的编程语言。它只是语法比Python更紧凑（也更魔幻），而且不用编译就能执行。

Shell脚本最适合的场景是**运维自动化**：你不可能每次部署都手动敲20条命令，但写一个脚本就能一劳永逸。

---

## 100.2 变量

### 定义变量

```bash
name="Alice"           # 等号两边不能有空格！
age=25
PI=3.14159
```

**注意！等号两边绝对不能有空格！** 这是初学者最容易犯的错误：
```bash
name = "Alice"   # 错误！bash会把name当成命令执行！
name="Alice"     # 正确
```

### 引用变量

```bash
name="Alice"
echo $name        # 输出：Alice
echo ${name}      # 输出：Alice（花括号更安全）
echo "Hello, ${name}!"   # 输出：Hello, Alice!
echo "Hello, $name!"     # 也可以，但不推荐
```

**花括号的好处**：
```bash
echo "${name}Smith"    # 输出：AliceSmith（明确区分变量名和文本）
echo "$nameSmith"      # 输出：空（bash认为变量叫nameSmith，不存在）
```

### 只读变量和删除变量

```bash
readonly PI=3.14159
PI=3.14          # 错误！./script: line X: PI: readonly variable

greeting="hello"
unset greeting    # 删除变量
echo $greeting    # 输出：空
```

### 特殊变量（非常重要！）

这些是脚本运行时自动设置的变量：

| 变量 | 含义 | 示例（`./deploy.sh myapp v2.0`） |
|------|------|----------------------------------|
| `$0` | 脚本本身的名称 | `./deploy.sh` |
| `$1` | 第一个参数 | `myapp` |
| `$2` | 第二个参数 | `v2.0` |
| `$#` | 参数个数 | `2` |
| `$@` | 所有参数（作为独立字符串） | `myapp v2.0` |
| `$*` | 所有参数（作为一个字符串） | `myapp v2.0` |
| `$?` | 上一条命令的退出状态码 | `0`（成功）或非`0`（失败） |
| `$$` | 当前脚本的进程ID | `12345` |
| `$!` | 最后一个后台进程的PID | `12346` |

**$? 的使用**：
```bash
grep "error" app.log
if [ $? -eq 0 ]; then
    echo "找到了错误"
else
    echo "没有错误"
fi
```

### 命令替换

把命令的输出赋值给变量：

```bash
current_dir=$(pwd)          # 推荐写法
current_dir=`pwd`           # 老式写法（反引号），不推荐
now=$(date "+%Y-%m-%d %H:%M:%S")
file_count=$(ls | wc -l)
free_mem=$(free -h | grep Mem | awk '{print $4}')
```

---

## 100.3 条件判断

### if/elif/else

```bash
if [ 条件 ]; then
    命令
elif [ 条件 ]; then
    命令
else
    命令
fi
```

**注意：** `[` 后面和 `]` 前面必须有空格！`if [` 和 `]`都是命令，空格缺失会导致语法错误。

### test命令和 [ ] 

`[ ]` 本质上是 `test` 命令的别名。以下三条等价：
```bash
test -f config.yaml
[ -f config.yaml ]
if [ -f config.yaml ]; then echo "存在"; fi
```

### 数值比较

```bash
num=10

if [ $num -eq 10 ]; then echo "等于10"; fi
if [ $num -ne 20 ]; then echo "不等于20"; fi
if [ $num -gt 5 ];  then echo "大于5"; fi
if [ $num -lt 20 ]; then echo "小于20"; fi
if [ $num -ge 10 ]; then echo "大于等于10"; fi
if [ $num -le 10 ]; then echo "小于等于10"; fi
```

| 操作符 | 含义 |
|--------|------|
| `-eq` | equal（等于） |
| `-ne` | not equal（不等于） |
| `-gt` | greater than（大于） |
| `-lt` | less than（小于） |
| `-ge` | greater or equal（大于等于） |
| `-le` | less or equal（小于等于） |

### 字符串比较

```bash
name="Alice"

if [ "$name" = "Alice" ];  then echo "是Alice"; fi
if [ "$name" != "Bob" ];   then echo "不是Bob"; fi
if [ -z "$name" ];         then echo "字符串为空"; fi     # -z=zero length
if [ -n "$name" ];         then echo "字符串非空"; fi     # -n=non-zero length
```

### 文件判断

```bash
if [ -f "config.yaml" ];  then echo "文件存在且是普通文件"; fi
if [ -d "/etc/nginx" ];   then echo "目录存在"; fi
if [ -r "app.log" ];      then echo "文件可读"; fi
if [ -w "app.log" ];      then echo "文件可写"; fi
if [ -x "myapp" ];        then echo "文件可执行"; fi
if [ -s "app.log" ];      then echo "文件非空"; fi
if [ -e "anything" ];     then echo "文件/目录存在"; fi    # -e=exists
```

### 逻辑运算符

```bash
if [ $age -gt 18 ] && [ $age -lt 60 ]; then echo "上班年龄"; fi
if [ $age -gt 18 ] || [ "$name" = "Alice" ]; then echo "命中"; fi
if ! [ -f "config.yaml" ]; then echo "配置文件不存在"; fi
```

也可以用 `-a`（and）和 `-o`（or），但不推荐（可读性差）：
```bash
if [ $age -gt 18 -a $age -lt 60 ]; then echo "上班年龄"; fi
```

### 双括号 [[ ]]（bash特有，推荐）

`[[ ]]` 比 `[ ]` 更强大、更安全：
- 支持 `&&` 和 `||` 运算符
- 支持正则匹配 `=~`
- 不需要给变量加双引号防分词

```bash
if [[ $num -gt 5 && $num -lt 20 ]]; then
    echo "在5到20之间"
fi

if [[ "$filename" =~ \.txt$ ]]; then
    echo "这是一个.txt文件"
fi
```

### 实战：部署前检查脚本片段

```bash
if [ ! -f "myapp" ]; then
    echo "错误：编译产物 myapp 不存在！请先执行 go build"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "错误：环境变量文件 .env 不存在！"
    exit 1
fi

echo "所有检查通过，开始部署..."
```

---

## 100.4 循环

### for循环（最常用）

**遍历列表：**
```bash
for name in Alice Bob Charlie; do
    echo "Hello, $name!"
done
```

**遍历数字范围：**
```bash
for i in {1..5}; do
    echo "第 $i 次尝试"
done
```

**遍历目录中的文件：**
```bash
for file in /var/log/*.log; do
    echo "处理文件: $file"
    wc -l "$file"
done
```

**C风格for循环：**
```bash
for ((i=1; i<=5; i++)); do
    echo "i = $i"
done
```

### while循环

```bash
count=1
while [ $count -le 5 ]; do
    echo "计数: $count"
    count=$((count + 1))
done
```

**实用：等待服务启动**
```bash
echo "等待MySQL启动..."
while ! mysqladmin ping -h localhost --silent; do
    echo "MySQL还没就绪，等2秒..."
    sleep 2
done
echo "MySQL已就绪！"
```

### until循环

`until` 是 `while` 的反面——条件为**假**时继续循环：

```bash
count=1
until [ $count -gt 5 ]; do
    echo "计数: $count"
    count=$((count + 1))
done
```

### break和continue

```bash
for i in {1..10}; do
    if [ $i -eq 5 ]; then
        echo "找到5了，退出！"
        break
    fi
    if [ $((i % 2)) -eq 0 ]; then
        echo "$i 是偶数，跳过"
        continue
    fi
    echo "处理奇数: $i"
done
```

---

## 100.5 函数

### 定义函数

```bash
function_name() {
    命令
}
```

或（function关键字可选）：
```bash
function function_name {
    命令
}
```

### 参数和返回值

**函数的参数**通过 `$1`、`$2` 获取（和脚本参数一样）：

```bash
greet() {
    echo "Hello, $1! 你今年 $2 岁。"
}

greet "Alice" 25
```

输出：`Hello, Alice! 你今年 25 岁。`

**返回值**有两种方式：

方式一：`return` 返回数字（0-255），通过 `$?` 获取：
```bash
is_even() {
    if [ $(($1 % 2)) -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

is_even 10
if [ $? -eq 0 ]; then echo "偶数"; fi
```

方式二：`echo` 返回字符串（更常用）：
```bash
get_config() {
    grep "^$1=" .env | cut -d'=' -f2
}

db_host=$(get_config "DB_HOST")
echo "数据库地址: $db_host"
```

### 局部变量

函数内用 `local` 声明局部变量，避免污染全局命名空间：

```bash
process_file() {
    local filename=$1
    local line_count=$(wc -l < "$filename")
    echo "$filename 有 $line_count 行"
}
```

### 算术运算

```bash
a=10
b=3

sum=$((a + b))
diff=$((a - b))
prod=$((a * b))
quot=$((a / b))
mod=$((a % b))
power=$((a ** b))        # 10的3次方

count=$((count + 1))     # 自增
```

---

## 100.6 实战脚本：Go项目自动部署

一个完整的自动部署脚本，涵盖：拉代码 → 编译 → 备份旧版本 → 启动新版本 → 健康检查。

```bash
#!/usr/bin/env bash

set -e

APP_NAME="myapi"
APP_DIR="/opt/$APP_NAME"
REPO_URL="git@github.com:myteam/myapi.git"
BRANCH="main"
BACKUP_DIR="/opt/backups"
HEALTH_URL="http://localhost:8080/health"
MAX_WAIT=30

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

if [ ! -d "$APP_DIR" ]; then
    log "首次部署，克隆仓库..."
    git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"

log "拉取最新代码..."
git fetch origin
git reset --hard "origin/$BRANCH"

log "编译项目..."
go build -o "${APP_NAME}_new" ./cmd/api/

log "备份旧版本..."
mkdir -p "$BACKUP_DIR"
if [ -f "$APP_NAME" ]; then
    cp "$APP_NAME" "$BACKUP_DIR/${APP_NAME}_$(date '+%Y%m%d_%H%M%S')"
fi

log "替换二进制文件..."
mv "${APP_NAME}_new" "$APP_NAME"

log "重启服务..."
sudo systemctl restart "$APP_NAME"

log "等待服务启动..."
for i in $(seq 1 $MAX_WAIT); do
    if curl -s "$HEALTH_URL" > /dev/null 2>&1; then
        log "部署成功！健康检查通过。"
        exit 0
    fi
    sleep 1
done

log "部署失败！健康检查超时。回滚..."
if [ -f "$BACKUP_DIR"/* ]; then
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/${APP_NAME}_* | head -1)
    cp "$LATEST_BACKUP" "$APP_NAME"
    sudo systemctl restart "$APP_NAME"
    log "已回滚到上一版本。"
fi
exit 1
```

**逐段解释：**

1. `set -e`：任何命令失败（退出码非0），脚本立即退出。避免了"第一步失败了第二步还继续跑"的危险。
2. 先定义变量：方便修改配置，不用在脚本里到处找硬编码。
3. `log` 函数：统一日志格式，每条日志带时间戳。
4. 首次部署检查：如果目录不存在就 `git clone`。
5. `reset --hard`：抛弃所有本地修改，强制对齐远程分支。生产环境部署脚本就该这样——本地不能有任何"手动改过的痕迹"。
6. 先编译到 `_new` 文件，再 `mv` 替换——保证了"原子性替换"。
7. 备份旧版本：万一新版本有问题还能回滚。
8. 健康检查循环：最多等30秒，每秒检查一次。通过了就成功，超时就回滚。

---

## 100.7 实战脚本：数据库定时备份

每天凌晨3点自动备份MySQL，压缩后用 `scp` 传到远程备份服务器。

```bash
#!/usr/bin/env bash

set -e

DB_USER="root"
DB_PASSWORD="${DB_BACKUP_PASSWORD}"
DB_NAME="myapp"
BACKUP_DIR="/opt/backups/mysql"
REMOTE_USER="backup"
REMOTE_HOST="backup.example.com"
REMOTE_DIR="/data/backups/mysql"
RETENTION_DAYS=30

TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BACKUP_FILE="${DB_NAME}_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

mysqldump -u"$DB_USER" -p"$DB_PASSWORD" --single-transaction --routines --triggers "$DB_NAME" | gzip > "$BACKUP_DIR/$BACKUP_FILE"

if [ ! -s "$BACKUP_DIR/$BACKUP_FILE" ]; then
    echo "备份失败：备份文件为空！"
    exit 1
fi

scp "$BACKUP_DIR/$BACKUP_FILE" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/"

find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "备份成功：$BACKUP_FILE（大小：$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)）"
```

**要点解释：**

- `--single-transaction`：对于InnoDB表，在一个事务中完成备份，保证数据一致性，不锁表。
- `--routines --triggers`：连存储过程和触发器一起备份。
- `-s` 检查文件是否非空：如果数据库宕机导致备份为空，及时报错。
- `find ... -mtime +30 -delete`：删除30天前的旧备份，防止磁盘被撑爆。

**配合crontab实现定时执行：**
```bash
crontab -e
```

添加一行：
```
0 3 * * * /opt/scripts/backup_db.sh >> /var/log/backup.log 2>&1
```

含义：每天凌晨3:00执行备份脚本，日志输出到 `/var/log/backup.log`。

### Crontab格式速查

```
*    *    *    *    *    要执行的命令
┬    ┬    ┬    ┬    ┬
│    │    │    │    └─── 星期（0-7，0和7都是周日）
│    │    │    └──────── 月份（1-12）
│    │    └───────────── 日期（1-31）
│    └────────────────── 小时（0-23）
└─────────────────────── 分钟（0-59）
```

常见示例：
```
0 3 * * *          # 每天凌晨3点
*/5 * * * *        # 每5分钟
0 9 * * 1-5        # 工作日早上9点
0 0 1 * *          # 每月1号零点
```

### 🤔 想多一点：为什么要 `set -e`？

默认情况下，Shell脚本里一条命令失败了，脚本会继续往下执行。这在大多数运维场景下是灾难性的：

```bash
cd /opt/myapp          # 如果cd失败了...
rm -rf *               # ...这一步就会在当前目录执行！
```

`set -e` 让脚本在第一条失败的命令处立即退出。但同时，你需要在预期可能失败的地方主动处理：`grep` 没有匹配时退出码也是1（不算真正的错误），此时可以写成 `grep "pattern" file || true`。

其他有用的 `set` 选项：
- `set -u`：引用未定义变量时报错（防止拼写错误）
- `set -x`：执行每条命令前打印它（调试神器）
- `set -o pipefail`：管道中任意一个命令失败，整个管道算失败

组合到一起：
```bash
set -euo pipefail
```

这是我个人几乎每个脚本开头的标配。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| Shell脚本 | 把终端命令写成文件，批量自动化执行 |
| shebang | `#!/bin/bash` 指定解释器 |
| 变量 | 等号两边不能有空格，用 `$var` 或 `${var}` 引用 |
| 特殊变量 | $0脚本名、$1~$n参数、$?退出码、$#参数个数 |
| 条件判断 | `if [ 条件 ]; then ... fi`，空格不能少 |
| test/[ ] | 数值-eq/-gt、字符串=/!=/-z、文件-f/-d/-r |
| [[ ]] | bash增强版，支持&&、\|\|、正则匹配 |
| for循环 | `for i in list; do ... done`，最常用 |
| while循环 | `while [ 条件 ]; do ... done` |
| 函数 | `func() { ... }`，参数用$1/$2，返回用return或echo |
| set -e | 命令失败立即退出，防止灾难性连锁错误 |
| 部署脚本 | git pull → build → backup → restart → health check → rollback |
| 备份脚本 | mysqldump → gzip → scp → 清理过期备份 |
| crontab | 定时任务：分 时 日 月 周 命令 |

> 🚀 下一章：第101章 · Git版本控制。脚本帮你自动部署了，但代码的版本谁来管？谁改了什么、什么时候改的、怎么回退？你需要学会用Git——程序员的"时间机器"。

---
[← 上一章：99-Linux必备知识.md](99-Linux必备知识/) | [下一章：101-Git版本控制.md →](101-Git版本控制/)
