#!/bin/bash

if ! command -v java &> /dev/null; then
  echo "❌ 未检测到 Java，请安装 Java 并配置好环境变量。"
  exit 1
fi

JAR_NAME="demo-0.0.1-SNAPSHOT.jar"
PORT=8080

echo "🔨 编译项目..."
mvn clean package

if [ ! -f target/$JAR_NAME ]; then
  echo "❌ 找不到 JAR 文件 target/$JAR_NAME，请先运行 'mvn clean package'"
  exit 1
fi

# 查找占用端口的进程 ID
PID=$(lsof -ti tcp:$PORT)

if [ -n "$PID" ]; then
  echo "发现占用端口 $PORT 的进程，PID=$PID，准备杀死..."
  kill -9 $PID
  echo "已杀死进程 $PID"
else
  echo "端口 $PORT 未被占用"
fi

# 启动jar包
echo "启动 $JAR_NAME ..."
nohup java -jar target/$JAR_NAME > app.log 2>&1 &
PID=$!
sleep 1
if ps -p $PID > /dev/null; then
  echo "✅ 应用已成功启动，PID=$PID，查看日志：tail -f app.log"
else
  echo "❌ 应用启动失败，请检查 app.log 日志"
fi