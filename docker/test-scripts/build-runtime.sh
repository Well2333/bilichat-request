#!/bin/bash

set -e

echo "==============================================="
echo "运行时基础镜像构建脚本"
echo "==============================================="

# 代理设置 - Docker 构建时需要使用宿主机网络
# 获取宿主机IP (Linux)
HOST_IP=$(ip route get 1.1.1.1 | awk '{print $7; exit}' 2>/dev/null || echo "host.docker.internal")
export HTTP_PROXY=http://${HOST_IP}:7890
export HTTPS_PROXY=http://${HOST_IP}:7890

DOCKER_USERNAME=${DOCKER_USERNAME:-"well404"}
DEPS_HASH=$(sha256sum pyproject.toml | cut -d' ' -f1 | head -c 12)

echo "🌐 使用代理: ${HTTP_PROXY}"
echo "📦 Dependencies hash (from pyproject.toml): ${DEPS_HASH}"

# 检查代理是否可达
echo ""
echo "🔍 检查代理连通性..."
if curl -s --connect-timeout 3 --proxy ${HTTP_PROXY} http://httpbin.org/ip >/dev/null 2>&1; then
    echo "✅ 代理连接正常"
elif curl -s --connect-timeout 3 http://httpbin.org/ip >/dev/null 2>&1; then
    echo "⚠️  代理不可达，将尝试直连"
    export HTTP_PROXY=""
    export HTTPS_PROXY=""
else
    echo "❌ 网络连接异常"
    echo "   建议检查网络或代理设置"
fi
echo ""

# 构建运行时基础镜像
echo "🏗️  构建运行时基础镜像..."
docker build -f docker/Dockerfile.runtime \
    --build-arg HTTP_PROXY=${HTTP_PROXY} \
    --build-arg HTTPS_PROXY=${HTTPS_PROXY} \
    -t ${DOCKER_USERNAME}/bilichat-request:runtime-latest \
    -t ${DOCKER_USERNAME}/bilichat-request:runtime-${DEPS_HASH} \
    .

echo ""
echo "✅ 运行时基础镜像构建完成！"
echo ""

# 显示构建结果
echo "📊 构建结果:"
echo ""
docker images ${DOCKER_USERNAME}/bilichat-request --filter "reference=*:runtime-*" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
echo ""

echo "🔍 镜像层级分析:"
docker history ${DOCKER_USERNAME}/bilichat-request:runtime-latest --format "table {{.ID}}\t{{.SIZE}}\t{{.CREATED_BY}}" --no-trunc | head -10
echo ""

echo "🏷️  生成的标签:"
echo "   🔧 ${DOCKER_USERNAME}/bilichat-request:runtime-latest"
echo "   🔧 ${DOCKER_USERNAME}/bilichat-request:runtime-${DEPS_HASH}"
echo ""

echo "⚠️  注意："
echo "   这是内部运行时基础镜像，包含:"
echo "   - Python 3.12 环境"
echo "   - 系统依赖 (wget, curl, build-essential)"  
echo "   - Python 依赖 (从 pyproject.toml)"
echo "   - Playwright Firefox"
echo "   - 字体文件"
echo ""
echo "   请不要直接运行此镜像，它仅用于构建应用镜像"
echo ""

echo "🚀 下一步："
echo "   运行 ./docker/build-app.sh 构建完整应用镜像"
