# 工具服务接口

## GET /tools/b23_extract

提取B23短链接的原始链接，提取失败时返回400错误

### API 输入

| 参数名 | 类型   | 必需 | 说明              |
| ------ | ------ | ---- | ----------------- |
| url    | string | 是   | 需要提取的B23链接 |

```bash
curl -X GET "http://localhost:40432/bilichatapi/tools/b23_extract?url=https://b23.tv/abcd123" \
  -H "Authorization: Bearer <your_token>"
```

### API 输出

返回提取后的原始链接字符串。

```json
"https://www.bilibili.com/video/BV1xx411c7mu"
```

---

## GET /tools/b23_generate

生成B23短链接

**支持的链接类型**:
- 视频链接
- 专栏链接
- 动态链接
- 以上三种链接对应的B23短链接

### API 输入

| 参数名 | 类型   | 必需 | 说明                     |
| ------ | ------ | ---- | ------------------------ |
| url    | string | 是   | 需要生成短链接的原始链接 |

```bash
curl -X GET "http://localhost:40432/bilichatapi/tools/b23_generate?url=https://www.bilibili.com/video/BV1xx411c7mu" \
  -H "Authorization: Bearer <your_token>"
```

### API 输出

返回生成的B23短链接字符串。

```json
"https://b23.tv/abcd123"
```

---

## GET /tools/search_up

搜索UP主 **⚠️ 重要：返回值类型代表不同含义**

### 🔍 返回值类型说明

- **返回单个对象（非数组）**: 表示精确匹配，找到了完全匹配搜索关键词的UP主
- **返回对象数组**: 表示模糊搜索结果，包含多个相关的UP主候选

### API 输入

| 参数名  | 类型    | 必需 | 说明                |
| ------- | ------- | ---- | ------------------- |
| keyword | string  | 是   | 搜索关键词          |
| ps      | integer | 否   | 返回结果数量，默认5，建议不超过20 |

```bash
curl -X GET "http://localhost:40432/bilichatapi/tools/search_up?keyword=测试UP主&ps=3" \
  -H "Authorization: Bearer <your_token>"
```

### API 输出

返回SearchUp对象或SearchUp对象数组：

| 字段名   | 类型    | 说明     |
| -------- | ------- | -------- |
| nickname | string  | UP主昵称 |
| uid      | integer | UP主UID  |

**🎯 精确匹配时（返回单个对象）**:
```json
{
  "nickname": "测试UP主",
  "uid": 12345678
}
```

**🔍 模糊搜索时（返回对象数组）**:
```json
[
  {
    "nickname": "测试UP主1",
    "uid": 12345678
  },
  {
    "nickname": "测试UP主2",
    "uid": 87654321
  },
  {
    "nickname": "测试UP主3",
    "uid": 11111111
  }
]
```
