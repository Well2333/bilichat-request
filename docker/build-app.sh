#!/bin/bash

set -e

echo "==============================================="
echo "应用镜像构建脚本"
echo "==============================================="

# 代理设置 (如果需要) - Docker 构建时需要使用宿主机网络
# 获取宿主机IP (Linux)
HOST_IP=$(ip route get 1.1.1.1 | awk '{print $7; exit}' 2>/dev/null || echo "host.docker.internal")
export HTTP_PROXY=http://${HOST_IP}:7890
export HTTPS_PROXY=http://${HOST_IP}:7890

DOCKER_USERNAME=${DOCKER_USERNAME:-"well404"}
DEPS_HASH=$(sha256sum pyproject.toml | cut -d' ' -f1 | head -c 12)

echo "📦 Dependencies hash: ${DEPS_HASH}"
echo ""

# 检查运行时基础镜像是否存在
echo "🔍 检查运行时基础镜像..."
if docker images ${DOCKER_USERNAME}/bilichat-request:runtime-latest -q | grep -q .; then
    echo "✅ 发现运行时基础镜像: ${DOCKER_USERNAME}/bilichat-request:runtime-latest"
else
    echo "❌ 未找到运行时基础镜像！"
    echo "   请先运行: ./docker/build-runtime.sh"
    exit 1
fi
echo ""

# 构建应用镜像
echo "🏗️  构建应用镜像 (基于运行时基础镜像)..."
docker build -f docker/Dockerfile \
    -t ${DOCKER_USERNAME}/bilichat-request:latest \
    .

echo ""
echo "✅ 应用镜像构建完成！"
echo ""

# 显示构建结果对比
echo "📊 构建结果对比:"
echo ""
echo "运行时基础镜像:"
docker images ${DOCKER_USERNAME}/bilichat-request --filter "reference=*:runtime-*" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
echo ""
echo "应用镜像:"
docker images ${DOCKER_USERNAME}/bilichat-request --filter "reference=*:latest" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
echo ""

# 分析应用镜像的轻量化效果
echo "🔍 应用镜像层级分析 (仅应用层):"
docker history ${DOCKER_USERNAME}/bilichat-request:latest --format "table {{.ID}}\t{{.SIZE}}\t{{.CREATED_BY}}" --no-trunc | head -8
echo ""

echo "🎯 优化效果分析:"
RUNTIME_SIZE=$(docker images ${DOCKER_USERNAME}/bilichat-request:runtime-latest --format "{{.Size}}")
APP_SIZE=$(docker images ${DOCKER_USERNAME}/bilichat-request:latest --format "{{.Size}}")
echo "   📦 运行时基础镜像: ${RUNTIME_SIZE}"
echo "   📦 完整应用镜像:   ${APP_SIZE}"
echo "   ✅ 下次代码更新时，只需重建轻量的应用层"
echo "   ✅ 只有依赖变化时才重建重的运行时层"
echo ""

echo "🚀 测试运行:"
echo "   docker run --rm -p 40432:40432 ${DOCKER_USERNAME}/bilichat-request:latest -n bilichat-request-test"
echo ""

echo "🧹 清理旧镜像 (可选):"
echo "   docker image prune"
echo "   docker system prune"
echo ""

echo "🎉 构建完成！应用镜像已准备就绪"
