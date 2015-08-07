Data Bang
=========

## 大众点评爬虫

#### 开发计划

1. detect shop ID.

     从已经下载的页面中解析出 ID. 起始页面, 人工选择一个皆可. 建议选择 shop list 页面.
2. download shop profile page
3. profile page 中解析出 review(评论), 评论数 大于等于 20 的, 加入 reviews 下载任务中.
4. shop review page 下载.
5. 用户的个人页面

先爬取页面在本地保存, 积累一定数量以后, 统一解析

#### 关键进展

- [609605178ba13c4a81f55d6c822dc1902340ebc8](https://github.com/JackonYang/dataBang/commit/609605178ba13c4a81f55d6c822dc1902340ebc8)

    拿到 203 条分类的 name 与 url. 其中, 不重复的, 175 条

    url 格式: `/search/category/\d{2}/\d{2}/g\d+`.

    去掉最后的最后的 gxxxx, 是一级分类. 一级分类数量不多.

    另, 基于地址的分类, url 格式: `/search/category/\d{2}/\d{2}/r\d+`. 最后的 g 变为 r

- [579b8014f474881b9b89db65b4c2cae4dc13fa27](https://github.com/JackonYang/dataBang/commit/579b8014f474881b9b89db65b4c2cae4dc13fa27)

    抓取各个分类的店铺列表页面, 拿到 2216 条不重复 shops

    婚庆类店铺, href 的 url 里面包含 ?KID=xxxxx, 使用正则匹配时需注意

    一个城市的某一个二级分类下, 可能一个店铺也没有.

- [35a9881ac3d2037a9ec9a24043a75ea9080ffdf8](https://github.com/JackonYang/dataBang/commit/35a9881ac3d2037a9ec9a24043a75ea9080ffdf8)

   可连续爬取店铺的所有评论, 当前参数为, 每个店铺最大爬取 9 页 180 条评论. 

    当前提取评论人的正则, 在个别页面中失效. 推测跟 shop 的类别有关.
    鉴于抓取 shop url 也存在个别类别的页面 url 模式不一致.
    存储 shop 时, 应该包含类别信息.

- [032e85412b0c42d45b18dd7a55719d73f821f83b](https://github.com/JackonYang/dataBang/commit/032e85412b0c42d45b18dd7a55719d73f821f83b)

    从店铺主页中, 解析出 12,142 条新店铺 id.

    从已下载的 2215 个店铺主页中, 解析出 name, star, 已保存至数据库 profile 表中

- [ec8a6f5cfad13ece87e9713aa8d2ba10f6a7f553](https://github.com/JackonYang/dataBang/commit/ec8a6f5cfad13ece87e9713aa8d2ba10f6a7f553)

    可以持续解析 shop_profile 页面, 得到 name, star 信息并保存.

    存在个别页面, 关联的 shop 是死链接. 比如 http://www.dianping.com/shop/2461414 的分店 http://www.dianping.com/shop/15923760

- [b3684496541003ebfe08d622913ad410412f00d8](https://github.com/JackonYang/dataBang/commit/b3684496541003ebfe08d622913ad410412f00d8)

    utils.py 中引入 log4f.py 文件打印日志, 重构之后发现 utils.py 就是一个垂直爬虫的 request 框架. 更名为 req.py

    shop 主页和评论的爬取, 都使用 req 重构, 支持写日志.

- [d5fa619077859f68bea1a2b7980c3e3ecbc6aa0b](https://github.com/JackonYang/dataBang/commit/d5fa619077859f68bea1a2b7980c3e3ecbc6aa0b)

    重构. 抽象出 profile 方法, 支持爬取大多数网站的个人/店铺主页.

    从写爬虫开始, 就在思考一个问题:

    爬取店铺主页有什么用?

    现在有了答案, 很多店铺, 点评数少于 20 条. 店铺首页最多呈现 20 条点评.

    所以, 先爬取首页, 解析出点评数. 如果首页为 20 条, 则爬取点评分页.

- [0c0ba29e4ab077bebe6cc9fdcf46eedfbd5f4580](https://github.com/JackonYang/dataBang/commit/0c0ba29e4ab077bebe6cc9fdcf46eedfbd5f4580)

    重构. 完成数据解析. 打印解析异常日志. 支持 ignore file list.

    54437 条店铺主页, 6m31.621s 完成解析 name, star

    没有评论的店铺, 大多有默认星级, 3 星或 3.5 星

    点评网的解释是: '评论来自业内综合评估', 代码是 `<i class="icon star-from item J-star-from"></i>`

    第一条评论之后的两三天后, 网站会更新得分数据, 不再使用默认得分. 并删除对应的解释代码.

    shop 中, 有评论/总数: 29807 / 58436, 占 51.0%. 评论数 10 条及以上的, 7820, 占 13.4%

    7G shop profile 文件, 压缩后 1.2G

    部分用户的评论, 没有打分信息, 或者没有评论内容. 少数评论中, 包含推荐信息.
