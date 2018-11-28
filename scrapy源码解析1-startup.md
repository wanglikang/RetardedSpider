# Scrapy的启动
### 以命令scrapy crawl spidername为例

**命令scrapy crawl spidername的格式是：scrapy command  args...**

简略过程如下：

1.在运行scrapy crawl spidername 的时候，
实际上是在用python虚拟环境中的Scripts文件夹下的scrapy.exe文件，将crawl spidername作为参数传入

2.scrapy的是在调用同目录下的scrapy-script.py文件,其文件内容如下：

scrapy 1.3.1
```python
if __name__ == '__main__':
    import sys
    import scrapy.cmdline

    sys.exit(scrapy.cmdline.execute())
    
```

scrapy 1.5.1
```python 
import re
import sys

from scrapy.cmdline import execute

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(execute())


```
通过文件的内容可知，就是调用scrapy.cmdline包下的excute方法

3.在scrapy.cmdline文件中，暂时忽略一下关于参数设置的代码，关键也就是执行了execute方法：
在这个方法里，主要是根据command的不同来对应的执行scrapy.commands包下对应的文件的代码。
```
    ...
    #cmds中有scrapy.commands目录下所有命令
    cmd = cmds[cmdname]
    parser.usage = "scrapy %s %s" % (cmdname, cmd.syntax())
    parser.description = cmd.long_desc()
    settings.setdict(cmd.default_settings, priority='command')
    cmd.settings = settings
    cmd.add_options(parser)
    opts, args = parser.parse_args(args=argv[1:])
    _run_print_help(parser, cmd.process_options, args, opts)

    # 真正执行CrawlerProcess的入口在这里
    cmd.crawler_process = CrawlerProcess(settings)
    #运行CrawlerProcess
    _run_print_help(parser, _run_command, cmd, args, opts)
    sys.exit(cmd.exitcode)
    ...

```
这里excute方法关键是实例化了一个CrawlerProcess实例，然后调用了其run方法(跟踪代码可知)
在这里例子中，就是对应执行scrapy.commands.crawl类

4.在crawl类中的run方法，主要执行了两句代码
```
        self.crawler_process.crawl(spname, **opts.spargs)
        self.crawler_process.start()
```
也就是执行了crawl_process实例的crawl方法和start方法

自此，scrapy爬虫才真正的跑了起来。

