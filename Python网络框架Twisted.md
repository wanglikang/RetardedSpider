#Twisted是用Python实现的基于事件驱动的网络引擎框架
Twisted支持许多常见的传输及应用层协议，包括TCP、UDP、SSL/TLS、HTTP、IMAP、SSH、IRC以及FTP。

参见http://www.cnblogs.com/tomato0906/articles/4678995.html

## twisted的reactor模型和java 的NIO中库中的模型相似
都是reactor模型的实现

都有selector角色

twisted中的Deferred：

![Deferred](http://s4.sinaimg.cn/middle/704b6af749ed2370a6a33&690)

## @defer.inlineCallbacks
+ @defer.inlineCallbacks 是twisted的一个装饰器类，用于简化deferred的操作。
将生成器变成了一系列的回调函数来执行。，方便编程
+ 当我们调用一个用inlineCallbacks 修饰的函数的时候,
我们不需要调用下一个或者发送或者抛出我们自己.
这个装饰器会帮我们完成这些并会确保我们的生成器会一直运行到底(假设它并没有抛出异常).