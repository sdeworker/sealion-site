# sealion-tech.com — 广州海狮软件科技有限公司官网

纯静态站。**站点根 = `public/` 子目录**（不是仓库根）。无框架、无构建工具、无后端。
Cloudflare Workers 绑定本仓库，push 到 `main` 后自动构建（约 60 秒）上线。

## 部署

```
wrangler.jsonc       Cloudflare Workers 配置（静态资产目录 = ./public）
```

- push → main → Cloudflare 自动构建 → https://www.sealion-tech.com
- **Cloudflare 构建命令必须留空**（加了会挂）
- 推送凭证：Fine-grained PAT，**不在仓库内**。由仓库所有者（sdeworker@gmail.com）通过安全渠道提供，写进本地 git remote 或环境变量，切勿提交进仓库（仓库为 Public，GitHub Push Protection 会拦截明文令牌）。

## 结构

```
public/                     站点根目录
├── index.html              中文首页，15 个区块：
│                           about / growth / certs / culture / milestones /
│                           products / apply / apply-detail(产品应用) /
│                           techstr(技术实力) / calc / partners / cases /
│                           news / service(售后与服务) / contact
├── style.css product.css manual.css
├── en/                     英文站（index.html + 各子页镜像）
├── news/  + en/news/       32 个新闻详情页（中16 + 英16）
├── industries/             12 个应用行业页
├── products/               8 个产品页
├── manual/ downloads/ videos/ ip.html 404.html
└── assets/
    ├── apply/    7   产品应用场景图        ├── news/     16  新闻封面
    ├── tech/     5   技术实力配图          ├── partners/ 17  合作客户 logo
    ├── cases/    26  案例图20+视频封面6    ├── service/  3   售后服务配图
    ├── culture/  7   企业文化图            └── certs/ ip-certs/  证书/专利
```

导航（8 顶层项，首页与 60 个子页需保持一致）：
关于海狮▾(企业简介/企业文化/发展历程/资质证书/合作客户/海狮成长) · 产品中心 ·
海狮实力▾(产品应用/技术实力/售后与服务) · 应用行业 · 案例展示▾(米重/米重色母/超声波/视频案例) ·
海狮动态 · 省料计算器 · 联系我们

## 技术红线

- Cloudflare 构建命令留空；不引前端框架、不引构建工具；外部依赖仅 Google Fonts。
- 改导航要**首页 + 60 个子页一起改**（子页是扁平简化版），否则栏目对不上。
- 中英文双站：改中文首页区块时，`en/index.html` 对应区块通常也要同步。
- 图片只用站内自有素材或客户授权图，**不用网图**（版权风险）。

## 改完必做的验证

```bash
# 1) 标签配对（尤其 div/span/article 嵌套）
python3 - <<'PY'
import re,glob
for f in glob.glob('public/**/*.html',recursive=True):
    h=open(f,encoding='utf-8').read()
    for t in ['div','section','article','a','span']:
        if len(re.findall(r'<%s[\s>]'%t,h))!=len(re.findall(r'</%s>'%t,h)):
            print('✗ tag mismatch',f,t)
PY
# 2) 本地起服务，人工过一遍无 404、导航不溢出、锚点无死链
cd public && python3 -m http.server 8000
```

## 内容来源与边界

站内图文取自旧站（ASP.NET + SQL Server）备份，逐条核实迁移，含：关于/产品/应用/
技术实力/售后/案例/新闻(含详情页)/合作客户/英文站。**新增或补全内容须由公司提供原件**
（截图或文件）——旧站数据库仅存在于迁移时的工作环境，本仓库和常规开发环境都没有它，
不要凭记忆或推测编造正文/图片对应。仍待补：招聘文的岗位福利段、文章内插图、
合作客户表序号 9/10 的归属（详见交接文档）。
