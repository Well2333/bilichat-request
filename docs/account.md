# 账户管理接口

## GET /account/web_account

获取当前管理的Web账户列表

### API 输入

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| 无 | - | - | 无需参数 |

```bash
curl -X GET "http://localhost:40432/bilichatapi/account/web_account" \
  -H "Authorization: Bearer <your_token>"
```

### API 输出

| 字段名 | 类型 | 说明 |
|--------|------|------|
| uid | string | 用户UID |
| note | object | 账户备注信息 |

```json
[
  {
    "uid": "12345678",
    "note": {
      "create_time": "2024-01-01T12:00:00+08:00",
      "source": "manual"
    }
  }
]
```

---

## POST /account/web_account/create

添加普通Web账号，不支持CookieCloud账号（请在config.yaml中配置），cookies必须包含有效的DedeUserID

### API 输入

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| cookies | object | 是 | 键值对格式的cookies，必须包含DedeUserID |
| note | object | 否 | 账户备注信息 |

```bash
curl -X POST "http://localhost:40432/bilichatapi/account/web_account/create" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "cookies": {
      "DedeUserID": "12345678",
      "SESSDATA": "your_sessdata",
      "bili_jct": "your_csrf_token"
    },
    "note": {
      "create_time": "2024-01-01T12:00:00+08:00",
      "source": "api"
    }
  }'
```

### API 输出

| 字段名 | 类型 | 说明 |
|--------|------|------|
| uid | string | 用户UID |
| note | object | 账户备注信息 |

```json
{
  "uid": "12345678",
  "note": {
    "create_time": "2024-01-01T12:00:00+08:00",
    "source": "api"
  }
}
```

---

## GET /account/web_account/delete

删除普通Web账号，仅支持删除普通账号，CookieCloud账号请在config.yaml中移除，账号不存在时返回404错误

### API 输入

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| uid | integer/string | 是 | 要删除的用户UID |

```bash
curl -X GET "http://localhost:40432/bilichatapi/account/web_account/delete?uid=12345678" \
  -H "Authorization: Bearer <your_token>"
```

### API 输出

| 字段名 | 类型 | 说明 |
|--------|------|------|
| uid | string | 被删除的用户UID |
| note | object | 账户备注信息 |

```json
{
  "uid": "12345678",
  "note": {
    "create_time": "2024-01-01T12:00:00+08:00",
    "source": "api"
  }
}
``` 