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
