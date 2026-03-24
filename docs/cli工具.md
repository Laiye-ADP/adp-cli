## 4.7 新增自定义抽取应用
### 故事描述
作为 ADP CLI用户，
我希望 直接使用CLI创建自定义抽取应用，无需前往ADP平台创建应用后使用
以便我 提升集成效率

### 创建自定义应用
#### 调用说明：
创建应用时进行字段配置：`adp custom-app create --app-name <app-name> --extract-fields <json> --parse-mode <mode> --enable-long-doc <bool> --long-doc-config <json>`
- `--app-name <app-name>`：应用名称，50字以内
- `--extract-fields <json>`：字段配置，需要包含字段`field_name`、字段类型`field_type`、字段提示词`field_prompt`
- `--parse-mode <mode>`：解析模式：标准解析 / 增强解析 / 智能体解析
- `--enable-long-doc <bool>`：是否开启长文档支持：true /false
- `--long-doc-config <json>`：长文档配置；仅 enable_long_doc=true 时生效；最多允许传入 5 组，超出无效，需要包含：文档类型`doc_type`、文档类型描述`doc_desc`

#### 补充说明：
- `--api-key`：如果设置过，可以不传
- 应用创建后，将自动返回`app_id`、`config_vision`
  - `app_id`：应用ID是作为应用唯一标识，可以用于执行抽取任务
  - `config_vision`：当前抽取配置的版本，用于区分与记录应用下不同版本的配置信息

#### 示例：
custom-app create \
  --api-key "your_api_key" \
  --app-name "财务票据抽取" \
  --extract-fields '[
    {"field_name":"发票号码","field_type":"文本","field_prompt":"提取发票左上角编号"},
    {"field_name":"开票日期","field_type":"日期","field_prompt":"提取发票开具日期"},
    {"field_name":"商品明细","field_type":"表格"}
  ]' \
  --parse-mode "增强解析" \
  --enable-long-doc true \
  --long-doc-config '[
    {"doc_type":"合同","doc_desc":"多页合同"},
    {"doc_type":"标书","doc_desc":"工程类标书"}
  ]'

### 查询自定义抽取应用配置（支持指定版本）
#### 调用说明：
- `--app-id <app-id>`：应用唯一标识
- `--config-version <version>`：可选，不填默认返回最新版本

#### 补充说明：
- `--api-key`：如果设置过，可以不传
- 查询结果参考API 输出的返回内容，包含版本下的所有字段配置、解析模式、长文档配置等信息

#### 示例：
custom-app get-config \
  --api-key "your_api_key" \
  --app-id "app_123456" \
  --config-version "v1"
  
### 查询自定义抽取应用的配置版本
#### 调用说明：
- `--app-id <app-id>`：应用唯一标识，可用于执行抽取任务，必填
- `--config-version <config-version>`：配置版本号，不填默认返回最新版本配置信息，非必填

#### 补充说明：
- `--api-key`：如果设置过，可以不传

#### 示例：
custom-app list-versions \
  --api-key "your_api_key" \
  --app-id "app_123456" 
  --config-version "v1"
  
### 删除自定义抽取应用
#### 调用说明：
`--app-id <app-id>`：应用唯一标识

#### 补充说明：
- `--api-key`：如果设置过，可以不传

#### 示例：
custom-app delete \
  --api-key "your_api_key" \
  --app-id "app_123456"

### 删除指定配置版本
#### 调用说明：
`--app-id <app-id>`：应用唯一标识
`--config-version <version>`：配置版本号

#### 补充说明：
- `--api-key`：如果设置过，可以不传

#### 示例：
custom-app delete-version \
  --api-key "your_api_key" \
  --app-id "app_123456" \
  --config-version "v2"

### AI 生成抽取字段与提示词推荐
#### 调用说明：
- `--file-url <url>`：示例文档地址
- `--file-base64`：示例文档base64编码

#### 补充说明：
- `--api-key`：如果设置过，可以不传

#### 示例：
custom-app ai-generate \
  --api-key "your_api_key" \
  --file-url "https://example.com/demo.pdf" 或者--file-base64
