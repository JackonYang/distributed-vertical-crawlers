Data Bang
=========

## 大众点评爬虫

#### 开发计划

1. 餐厅 list
2. 餐厅的点评及其用户
3. 用户的个人页面

先爬取页面在本地保存, 积累一定数量以后, 统一解析

#### 关键进展

- [609605178ba13c4a81f55d6c822dc1902340ebc8](https://github.com/JackonYang/dataBang/commit/609605178ba13c4a81f55d6c822dc1902340ebc8)

    拿到 203 条二级分类的 name 与 url. 其中, 不重复的, 175 条

    url 格式: `/search/category/\d{2}/\d{2}/g\d+`.

    去掉最后的最后的 gxxxx, 是一类分类. 一类分类数量不多.

- [579b8014f474881b9b89db65b4c2cae4dc13fa27](https://github.com/JackonYang/dataBang/commit/579b8014f474881b9b89db65b4c2cae4dc13fa27)

    拿到 2216 条不重复 shops

    婚庆类店铺, href 的 url 里面包含 ?KID=xxxxx, 使用正则匹配时需注意

    一个城市的某一个二级分类下, 可能一个店铺也没有.

- [35a9881ac3d2037a9ec9a24043a75ea9080ffdf8](https://github.com/JackonYang/dataBang/commit/35a9881ac3d2037a9ec9a24043a75ea9080ffdf8)

   可连续爬取店铺的所有评论, 当前参数为, 每个店铺最大爬取 9 页 180 条评论. 

    当前提取评论人的正则, 在个别页面中失效. 推测跟 shop 的类别有关.
    鉴于抓取 shop url 也存在个别类别的页面 url 模式不一致.
    存储 shop 时, 应该包含类别信息.
