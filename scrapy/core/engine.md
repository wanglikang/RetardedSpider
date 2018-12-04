# Scrapy的engins模块流程图
## engine 
    负责request下载的转达（转达给scheduler去处理）
    下载内容的转发（可以通过下载器中间件）
    爬取中间件的执行
## engines的初始化中，
    主要设置了下载器downloader，设置了scraper，设置了相关的回调函数，
## engines的open_spider函数中,
    设置slot
    将_next_request函数包装到一个slot中，然后赋值回engines的slot成员，
    生成了调度器scheduler，并异步地开启了调度器的调度
    异步的开启刮取器
    异步的开启爬虫
    最重要的是使用slot进行了一次调度，并设置了slot默认为5秒一次的心跳，
        也就是slot以后会每5秒进行一次调度，这样就开启了引擎的主循环
