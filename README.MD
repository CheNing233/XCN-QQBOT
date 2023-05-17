# XCN-QQBOT 项目

基于 PYCQBOT 基于 go-cqhttp 基于 Mirai 以及 MiraiGo 的 OneBot Golang 原生实现

该项目仅自用测试，如果出现任何问题请自行承担责任。（好玩记得点个star）

内含“sdapi”插件，该插件定位于面向小群自用的sdwebui画图需求，消费级电脑也能带（作者thinkbook+3050）

## Feature

插件sdapi：
使用方法：`#help`，也可自行翻源代码查找实现

- 支持查看任务队列，查看显卡状态（基于pynvml实现，部分显卡不支持）
- 支持文生图（及其Hires.fix）、图生图以及单张图片超分放大
- 支持修改steps、seed、cfg以及高清修复算法、超分放大算法、采样器、模型、**VAE**、CLIP等参数，支持对指定任务指定参数
- 支持pnginfo功能，支持tagger插件反推及涩涩鉴定，**支持tagger模型卸载指令，防止爆显存**
- **支持重载模型，用于解决炸炉后显存不释放的问题**

## Environment

1、该项目已将原`PYCQBOT`项目修改并内嵌，不需要`pip install pycqbot`

2、python version 3.10.6（SD Webui可能强制该版本）

3、git version 2.40.0.windows.1

4、使用`pip install`下面的`module`

```shell
pip install websockets
pip install aiohttp
pip install aiofiles
pip install pyyaml
pip install psutil
pip install pynvml
```

## Usage

0、`/plugin/sdapi/sdapi_ctrler.py`中绑定SD为本地路径，请自行配置SD

1、使用`git clone`克隆当前项目

1.5、根据需求安装环境

2、修改`config.yml`中的`uin`QQ号和`password`QQ密码

2、双击`launch.sh`即可运行当前项目

## Tips

1、如登陆失败，可修改`device.json`中的`protocol`字段为`2`，并删除`config.yml`的密码，使用手表扫码登录