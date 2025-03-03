# RSS 播客下载器

一个用于从RSS订阅源下载播客音频文件的简单Python脚本。

## 功能特点

- 从RSS订阅源解析播客剧集
- 下载播客音频文件
- 显示下载进度条
- 自动跳过已下载的文件
- 支持限制下载数量
- 文件名包含发布日期和标题
- 支持从OPML文件导入播客列表
- 支持并发下载多个播客
- 以JSON格式保存播客描述和元数据
- 将下载内容整理到音频和描述文件夹中
- 使用剧集标识符进行智能重复检测

## 安装

1. 确保您已安装Python 3.6或更高版本
2. 克隆或下载此仓库
3. 安装所需依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

下载单个播客的所有剧集：

```bash
python podcast_downloader.py https://example.com/podcast.xml
```

这将从指定的RSS订阅源下载所有播客剧集到`downloads`目录。

### 命令行选项

- `-o, --output-dir`：指定输出目录（默认：`downloads`）
- `-l, --limit`：限制要下载的剧集数量
- `--no-skip`：不跳过现有文件

### 示例

将最新的5个剧集下载到自定义目录：

```bash
python podcast_downloader.py https://example.com/podcast.xml -o my_podcasts -l 5
```

### 使用示例脚本

我们提供了一个示例脚本，可以下载几个流行的播客：

```bash
python example.py
```

## 保存的元数据

对于每个播客，将创建以下目录结构：

```
downloads/
├── audio/
│   ├── 20230101_Episode1.mp3
│   ├── 20230108_Episode2.mp3
│   └── ...
└── description/
    ├── podcast_info.json
    ├── 20230101_Episode1.json
    ├── 20230108_Episode2.json
    └── ...
```

元数据文件包含每个剧集的详细信息，包括：
- 标题
- 描述
- 摘要
- 发布日期
- 作者
- 时长
- 剧集编号
- 季编号
- 标签
- 图片URL
- 唯一标识符（GUID和音频URL哈希）

## 常见RSS订阅源示例

以下是一些流行播客的RSS订阅源URL：

- **Podcast Index**：在 https://podcastindex.org/ 浏览目录，查找数千个播客的RSS订阅源
- **小宇宙FM**：在小宇宙App中找到播客，分享链接，然后在浏览器中打开以找到RSS订阅源URL
- **Spotify**：Spotify不直接提供RSS订阅源，但您可以使用第三方服务查找等效的RSS订阅源
- **Google Podcasts**：复制播客URL并使用转换工具查找相应的RSS订阅源

## 注意事项

- 请尊重内容创作者的版权
- 下载的文件仅供个人使用
- 某些RSS订阅源可能需要身份验证或有访问限制 