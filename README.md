# My Yandex Tank Fork

#### News: Added SignalFX support. See: [Wiki page](https://github.com/doctornkz/yandex-tank/wiki).

Yandex.Tank is an extensible open source load testing tool for advanced linux users which is especially good as a part of an automated load testing suite

![Quantiles chart example](/logos/sfx_screen.png)

## Main features
* different load generators supported:
  * Evgeniy Mamchits' [phantom](https://github.com/yandex-load/phantom) is a very fast (100 000+ RPS) shooter written in C++ (default)
  * [JMeter](http://jmeter.apache.org/) is an extendable and widely known one
  * BFG is a Python-based generator that allows you to write your load scenarios in Python
  * Powerful Golang generator: [pandora](https://github.com/yandex/pandora)
* performance analytics backend service: [Overload](http://overload.yandex.net/). Store and analyze your test results online
* several ammo formats supported like plain url list or access.log
* test autostop plugin: stop your test when the results have became obvious and save time
* customizable and extendable monitoring that works over SSH

## Documentation
- [Installation](http://yandextank.readthedocs.org/en/latest/install.html) 

- Official [documentation](https://yandextank.readthedocs.org/en/latest/) (90% compartible).

## See also
- [Overload𝛃](https://overload.yandex.net/) – performance analytics server

- Evgeniy Mamchits' [phantom](https://github.com/yandex-load/phantom) – phantom scalable IO engine
