# Oil Control (Preview)

A simulator for oil refining and transportation (Preview). 关于油品炼制和运输的仿真器（预览版，目前仍在**调试修改ing...**）。



## 项目目录结构

```
|-- platform_lib
      |-- README.md
      |-- main.py        // 环境测试主函数
      |-- tools.py       // 配置文件加载工具
      |-- decision.json  // 各节点动作（环境测试用）
      |-- env            // 仿真环境
            |-- objects              // 仿真器中各类节点模块
                  |-- depot.py
                  |-- oilfield.py
                  |-- province.py
                  |-- purchase.py
                  |-- refinery.py
                  |-- road.py
                  |-- saleregion.py
                  |-- transfer.py
            |-- obs_interfaces       // observation 观测类接口
                  |-- observation.py
            |-- simulators           // 仿真器
                  |-- game.py
            |-- config.json          // 相关配置文件
            |-- chooseenv.py         // 继承自 Jidi
            |-- oilcontrolenv.py     // 物流仿真器逻辑代码
            |-- system_configs.xlsx  // 系统配置参数文件
      |-- utils          // 工具函数（继承自 Jidi）
```



## 系统参数配置

本仿真器提供了Excel文件用于快速配置所需的仿真器系统，该文件路径为：`env/system_configs.xlsx`。

**注意**：

1. 请勿修改该文件**路径**、**名称**、**表（Sheet）名称**，以及每张表中的**属性名称**；
2. 配置所需的仿真器系统时，只需在每张表中，**按格式**填入对应属性的参数即可；
3. 配置表中每条记录**不允许空缺**，否则可能会导致仿真器运行出错。



## 动作格式说明

关于在仿真器中，每个节点接收的`Action`格式，以及整个仿真器接收的`Joint Action`格式，可参考《参数格式设计》。



## 注意

1. 当前仿真器仍处于**测试中**，目前只测试了正常情况下的运行结果，在特殊、极端情况下仿真器的运行情况仍有待检验；
2. 该仿真器可判断接收的决策是否满足所有约束，若不满足则会修改这些决策。若保证在使用过程中，传给仿真器的决策参数都满足约束，则可在调用该仿真器时，设置**参数**`is_simulate`为`True`（该参数默认为`False`，即仿真器会对决策进行约束检验）；
3. 仍需说明，2中仿真器对决策参数进行约束的部分功能尚未完备，还需进一步的调试。

