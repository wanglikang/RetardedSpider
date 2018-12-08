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

Deferred对象以抽象化的方式表达了一种思想，即结果还尚不存在。
它同样能够帮助管理产生这个结果所需要的回调链。
当从函数中返回时，Deferred对象承诺在某个时刻函数将产生一个结果。
返回的Deferred对象中包含所有注册到事件上的回调引用，因此在函数间只需要传递这一个对象即可，
跟踪这个对象比单独管理所有的回调要简单的多。