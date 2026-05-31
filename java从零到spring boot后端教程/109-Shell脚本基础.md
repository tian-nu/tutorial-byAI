# 109-Shell脚本基础

> 💡 每天凌晨3点，你都要手动SSH登录服务器，把昨天的日志压缩、备份到另一个目录、再删除7天前的旧备份。这件事你做了三天就疯了。如果能写一个文件，里面写好这串命令，然后一条命令执行它——这就是 Shell 脚本。本章教你写出能自己跑的运维脚本，让你从"手工劳动者"升级为"自动化工程师"。

---

## 本章目标
- 创建并运行一个 Shell 脚本
- 使用变量、条件判断、循环
- 理解 `$1`、`$?`、`$#` 等特殊变量
- 写出一个实用的启动/停止脚本模板
- 理解 `crontab` 定时任务

---

## 109.1 第一个脚本

### 你在做什么？
创建一个脚本，自动输出一句话并显示当前时间。

### 创建脚本文件

```bash
vim hello.sh
```

内容：

```bash
#!/bin/bash
echo "Hello, this script runs at: $(date)"
echo "Current user: $(whoami)"
echo "Current directory: $(pwd)"
```

### 赋予执行权限并运行

```bash
chmod +x hello.sh
./hello.sh
```

### 关键解释

| 行 | 含义 |
|----|------|
| `#!/bin/bash` | Shebang——告诉系统用哪个解释器执行这个脚本。必须有，且必须在第一行。 |
| `echo` | 输出文本到终端 |
| `$(命令)` | 命令替换——先执行括号里的命令，把输出放到这个位置 |
| `./hello.sh` | 执行当前目录下的脚本（不能用 `hello.sh`，因为当前目录不在 PATH 中） |

### 验证方法

运行后应看到类似输出：

```
Hello, this script runs at: Wed May 29 10:30:00 CST 2026
Current user: ubuntu
Current directory: /home/ubuntu
```

---

## 109.2 变量

```bash
#!/bin/bash

# 定义变量（等号两边不能有空格！）
APP_NAME="my-spring-app"
APP_PORT=8080

echo "Starting $APP_NAME on port $APP_PORT"

# 只读变量
readonly APP_NAME

# 删除变量
unset APP_PORT
```

### 常见错误

❌ **错误写法**：
```bash
APP_NAME = "my-app"     # 等号两边有空格，会报错
$APP_NAME="my-app"      # 变量名前不能加$
```

✅ **正确写法**：
```bash
APP_NAME="my-app"       # 定义时不用$
echo "$APP_NAME"        # 使用时加$
```

---

## 109.3 用户输入与特殊变量

```bash
#!/bin/bash

echo "Script name: $0"
echo "First argument: $1"
echo "Second argument: $2"
echo "Total arguments: $#"
echo "All arguments: $@"
```

运行：

```bash
./args.sh hello world 123
```

输出：

```
Script name: ./args.sh
First argument: hello
Second argument: world
Total arguments: 3
All arguments: hello world 123
```

### 特殊变量速查表

| 变量 | 含义 |
|------|------|
| `$0` | 脚本自身的名字 |
| `$1` ~ `$9` | 第1到第9个参数 |
| `$#` | 参数个数 |
| `$@` | 所有参数（每个作为独立字符串） |
| `$*` | 所有参数（合并为一个字符串） |
| `$?` | 上一条命令的退出状态码（0=成功） |
| `$$` | 当前 Shell 的 PID |

---

## 109.4 条件判断

### if 语句

```bash
#!/bin/bash

if [ "$1" = "start" ]; then
    echo "Starting application..."
elif [ "$1" = "stop" ]; then
    echo "Stopping application..."
else
    echo "Usage: $0 {start|stop}"
    exit 1
fi
```

> ⚠️ `[` 和 `]` 两边的空格不能省略！`[ "$1" = "start" ]` 是对的，`["$1" = "start"]` 是错的。

### 常用条件判断

```bash
# 字符串比较
[ "$a" = "$b" ]        # 相等
[ "$a" != "$b" ]       # 不等
[ -z "$a" ]            # 字符串为空
[ -n "$a" ]            # 字符串非空

# 数字比较
[ "$a" -eq "$b" ]      # 等于
[ "$a" -ne "$b" ]      # 不等于
[ "$a" -gt "$b" ]      # 大于
[ "$a" -lt "$b" ]      # 小于

# 文件判断
[ -f "app.jar" ]       # 是普通文件
[ -d "/opt/app" ]      # 是目录
[ -x "start.sh" ]      # 可执行
[ -e "config.yml" ]    # 存在（文件或目录）
```

### 验证方法

```bash
./control.sh start    # 应输出 "Starting application..."
./control.sh stop     # 应输出 "Stopping application..."
./control.sh restart  # 应输出用法提示并退出
echo $?               # 应输出 1（exit 1 的结果）
```

---

## 109.5 循环

```bash
#!/bin/bash

# for 循环：批量处理
echo "=== 批量创建目录 ==="
for dir in dev test prod; do
    mkdir -p "/opt/config/$dir"
    echo "Created /opt/config/$dir"
done

# while 循环：等待条件
echo "=== 等待应用启动 ==="
RETRY=0
MAX_RETRY=30
while [ $RETRY -lt $MAX_RETRY ]; do
    if curl -s http://localhost:8080/health > /dev/null; then
        echo "Application is up!"
        break
    fi
    echo "Waiting... ($RETRY/$MAX_RETRY)"
    sleep 2
    RETRY=$((RETRY + 1))
done
```

---

## 109.6 实战：Spring Boot 启动脚本

这是一个真实可用的模板，可以直接放到你的项目里：

```bash
#!/bin/bash

JAR_FILE="app.jar"
LOG_FILE="logs/app.log"
PID_FILE="app.pid"
PROFILE="${1:-prod}"           # 默认 prod 环境
JVM_OPTS="-Xms256m -Xmx512m"

start() {
    if [ -f "$PID_FILE" ]; then
        echo "Application is already running (PID: $(cat $PID_FILE))"
        return 1
    fi

    mkdir -p logs
    nohup java $JVM_OPTS -jar $JAR_FILE --spring.profiles.active=$PROFILE \
        > $LOG_FILE 2>&1 &
    echo $! > $PID_FILE
    echo "Started with PID $(cat $PID_FILE)"
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Application is not running"
        return 1
    fi

    PID=$(cat $PID_FILE)
    echo "Stopping PID $PID..."
    kill $PID
    sleep 5

    if kill -0 $PID 2>/dev/null; then
        echo "Force killing..."
        kill -9 $PID
    fi

    rm -f $PID_FILE
    echo "Stopped"
}

restart() {
    stop
    sleep 2
    start
}

status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat $PID_FILE)
        if kill -0 $PID 2>/dev/null; then
            echo "Application is running (PID: $PID)"
            return 0
        fi
    fi
    echo "Application is not running"
    return 1
}

case "$2" in
    start)   start ;;
    stop)    stop ;;
    restart) restart ;;
    status)  status ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
```

### 使用方式

```bash
chmod +x app.sh
./app.sh start        # 启动（默认 prod 环境）
./app.sh start dev    # 启动 dev 环境
./app.sh status       # 查看状态
./app.sh stop         # 停止
./app.sh restart      # 重启
```

### 脚本解析

| 部分 | 说明 |
|------|------|
| `nohup ... &` | 后台运行，关闭终端不停止 |
| `$!` | 上一条后台命令的 PID |
| `2>&1` | 将标准错误重定向到标准输出 |
| `kill -0` | 不发送信号，只检查进程是否存在 |
| `${1:-prod}` | 第一个参数，未提供时默认为 `prod` |

---

## 109.7 crontab——定时任务

让脚本按计划自动执行。

### 基本用法

```bash
crontab -e          # 编辑当前用户的定时任务
crontab -l          # 列出当前用户的定时任务
```

### 格式

```
分 时 日 月 星期 命令
```

### 示例

```bash
# 每天凌晨3点备份日志
0 3 * * * /opt/app/backup.sh >> /var/log/backup.log 2>&1

# 每隔5分钟检查应用是否存活
*/5 * * * * /opt/app/healthcheck.sh

# 每周一早上8点重启
0 8 * * 1 /opt/app/app.sh restart

# 每月1号凌晨2点清理日志
0 2 1 * * find /opt/app/logs -name "*.log" -mtime +30 -delete
```

### 验证方法

添加一条测试任务：

```bash
crontab -e
# 添加：
* * * * * echo "Cron test at $(date)" >> /tmp/cron_test.log
```

等一分钟后检查：

```bash
cat /tmp/cron_test.log
```

---

## 109.8 完成效果

学完本章，你应该能：
1. 创建、赋权并运行 `.sh` 脚本
2. 使用变量、`if`、`for`/`while` 编写逻辑
3. 写出一个标准的 Spring Boot 启停脚本
4. 用 `crontab` 设置定时任务

---

## 小结

| 知识点 | 核心内容 |
|--------|----------|
| 脚本开头 | `#!/bin/bash` |
| 变量 | `NAME="value"`，用 `$NAME` 或 `${NAME}` |
| 命令替换 | `$(command)` |
| 特殊变量 | `$0`, `$1`, `$#`, `$@`, `$?` |
| 条件判断 | `if [ 条件 ]; then ... fi` |
| 循环 | `for ... in ...` / `while [ 条件 ]` |
| 后台运行 | `nohup ... &` |
| 定时任务 | `crontab -e`，格式 `分 时 日 月 周` |

---

## 自测题

1. 写一条命令：定义一个变量 `PORT=9090`，然后用 `echo` 输出 "Server is listening on port 9090"。
2. `$?` 的含义是什么？什么时候它的值是 0？
3. 你想让脚本 `/opt/cleanup.sh` 每天凌晨 2:30 执行，crontab 怎么写？

<details>
<summary>点击查看答案</summary>

1. 
```bash
PORT=9090
echo "Server is listening on port $PORT"
```

2. `$?` 是上一条命令的退出状态码。当上一条命令执行**成功**时值为 0，非 0 表示某种错误。
3. `30 2 * * * /opt/cleanup.sh`
</details>