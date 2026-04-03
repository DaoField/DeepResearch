# DeepResearch Sphinx文档说明

本目录包含DeepResearch项目的Sphinx文档配置和构建脚本。

## 目录结构

- `api/` - API文档
- `architecture/` - 架构设计文档
- `contributing/` - 贡献指南
- `deployment/` - 部署文档
- `releases/` - 版本发布说明
- `user_guide/` - 用户操作手册
- `_build/` - 构建输出目录
- `conf.py` - Sphinx配置文件
- `index.rst` - 文档索引

## 构建文档

1. 确保已安装Sphinx及相关扩展：
   ```bash
   pip install sphinx myst-parser sphinx-rtd-theme linkify-it-py
   ```

2. 确保已安装taolib库（用于文档站点功能）：
   ```bash
   pip install -e ../tao
   ```

3. 运行构建命令：
   ```bash
   invoke doc.build
   ```

4. 构建成功后，HTML文档会生成在 `doc/_build/html` 目录中。

## 预览文档

1. 确保已构建文档（参见上面的构建步骤）。

2. 运行预览命令：
   ```bash
   invoke doc.serve
   ```

3. 在浏览器中访问 `http://localhost:8000` 查看文档。

## 配置说明

- **conf.py**：Sphinx配置文件，包含项目信息、扩展配置和主题设置。
- **index.rst**：文档索引，定义了文档的目录结构。
- **auto_api.md**：自动生成的API文档，从代码中提取。

## 注意事项

- 文档构建过程中可能会出现一些警告，这些主要是由于文档链接和格式问题导致的，不影响文档的生成。
- 如果需要更新API文档，只需重新运行构建脚本即可，Sphinx会自动从代码中提取最新的文档字符串。

## 常见问题

### 构建失败

如果构建失败，请检查以下几点：
1. 是否安装了所有必要的依赖
2. 代码文件是否存在且可导入
3. 文档文件格式是否正确

### 预览失败

如果预览失败，请检查：
1. 文档是否已成功构建
2. 端口8000是否被占用
3. 是否有防火墙阻止访问