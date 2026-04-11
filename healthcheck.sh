#!/bin/sh
# ============================================
# DeepResearch 健康检查脚本
# ============================================
# 用于 Podman/Docker 健康检查
# 检查 API 服务是否正常响应

API_HOST=${API_HOST:-localhost}
API_PORT=${API_PORT:-8000}

curl --fail http://${API_HOST}:${API_PORT}/api/v1/health
exit $?
