# sealion-tech.com — 广州海狮软件科技有限公司官网

纯静态站。仓库根目录 = 站点根目录。无框架、无构建工具、无后端。
Cloudflare Workers 绑定本仓库，push 到 main 后自动构建（约 60 秒）上线。

## 结构
```
index.html    首页（唯一内容页：Hero / 关于 / 产品 / 应用行业 / 联系）
style.css     全站样式
assets/       logo、favicon、3 张旧站保留图片
404.html
robots.txt / sitemap.xml / .nojekyll
```

## 技术红线
- Cloudflare 构建命令必须留空（加了会挂）
- 不引前端框架、不引构建工具
- 外部依赖仅 Google Fonts

## 来源
内容与图片取自旧站（ASP.NET + SQL Server）备份，只保留必需项：
公司简介、七套产品、资质、联系方式、logo。旧站的新闻、案例、合作伙伴、
英文站、后台系统一律未迁移。
