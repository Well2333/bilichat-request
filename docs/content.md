# 内容服务接口

## GET /content/video

获取视频内容截图

### API 输入

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| video_id | integer/string | 是 | 视频ID（AV号或BV号） |
| quality | integer | 否 | 图片质量(0-100)，默认75 |

```bash
curl -X GET "http://localhost:40432/bilichatapi/content/video?video_id=BV1xx411c7mu&quality=85" \
  -H "Authorization: Bearer <your_token>"
```

### API 输出

| 字段名 | 类型 | 说明 |
|--------|------|------|
| type | string | 内容类型，固定为"video" |
| id | string | 视频AV号 |
| b23 | string | B23短链接 |
| img | string | Base64编码的截图数据 |

```json
{
  "type": "video",
  "id": "av123456",
  "b23": "https://b23.tv/abcd123",
  "img": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

---

## GET /content/column

获取专栏内容截图

### API 输入

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| cvid | integer/string | 是 | 专栏ID（cv号或纯数字） |
| quality | integer | 否 | 图片质量(0-100)，默认75 |

```bash
curl -X GET "http://localhost:40432/bilichatapi/content/column?cvid=cv123456&quality=85" \
  -H "Authorization: Bearer <your_token>"
```

### API 输出

| 字段名 | 类型 | 说明 |
|--------|------|------|
| type | string | 内容类型，固定为"column" |
| id | string | 专栏CV号 |
| b23 | string | B23短链接 |
| img | string | Base64编码的截图数据 |

```json
{
  "type": "column",
  "id": "cv123456",
  "b23": "https://b23.tv/efgh456",
  "img": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

---

## GET /content/dynamic

获取动态内容截图

### API 输入

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| dynamic_id | string | 是 | 动态ID |
| quality | integer | 否 | 图片质量(0-100)，默认75 |
| mobile_style | boolean | 否 | 是否使用移动端样式，默认true |

```bash
curl -X GET "http://localhost:40432/bilichatapi/content/dynamic?dynamic_id=123456789&quality=85&mobile_style=true" \
  -H "Authorization: Bearer <your_token>"
```

### API 输出

| 字段名 | 类型 | 说明 |
|--------|------|------|
| type | string | 内容类型，固定为"dynamic" |
| id | string | 动态ID |
| b23 | string | B23短链接 |
| img | string | Base64编码的截图数据 |

```json
{
  "type": "dynamic",
  "id": "123456789",
  "b23": "https://b23.tv/ijkl789",
  "img": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

---

## GET /content/

通用内容链接解析，仅解析内容类型和ID，不生成截图和短链接

**支持的链接格式**:
- 视频: `av123456`、`BV1xx411c7mu`
- 专栏: `cv123456`
- 动态: `dynamic/123456`、`opus/123456`、`t.bilibili.com/123456`

### API 输入

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| bililink | string | 是 | 哔哩哔哩链接或ID |

```bash
curl -X GET "http://localhost:40432/bilichatapi/content/?bililink=https://www.bilibili.com/video/BV1xx411c7mu" \
  -H "Authorization: Bearer <your_token>"
```

### API 输出

| 字段名 | 类型 | 说明 |
|--------|------|------|
| type | string | 内容类型（video/column/dynamic） |
| id | string | 内容ID |
| b23 | string | B23短链接（空字符串） |
| img | string | 截图数据（空字符串） |

```json
{
  "type": "video",
  "id": "av123456",
  "b23": "",
  "img": ""
}
``` 