# 系统接口

## GET /version

获取系统版本信息

### API 输入

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| 无 | - | - | 无需参数 |

```bash
curl -X GET "http://localhost:40432/bilichatapi/version" \
  -H "Authorization: Bearer <your_token>"
```

### API 输出

| 字段名 | 类型 | 说明 |
|--------|------|------|
| version | string | 包版本号 |
| bilichat_min_version | string | 最低支持的bilichat版本 |
| package | string | 包名 |
| datetime | string | 当前时间(ISO格式) |

```json
{
  "version": "1.0.0",
  "bilichat_min_version": "0.1.0",
  "package": "bilichat-request",
  "datetime": "2024-01-01T12:00:00+08:00"
}
```

---

## GET /health

健康检查接口，用于容器健康检查，无需认证

### API 输入

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| 无 | - | - | 无需参数 |

```bash
curl -X GET "http://localhost:40432/health"
```

### API 输出

| 字段名 | 类型 | 说明 |
|--------|------|------|
| status | string | 服务状态，固定返回"ok" |

```json
{
  "status": "ok"
}
```
