# Oil Control (Preview)

A simulator for oil refining and transportation (Preview). 关于油品炼制和运输的仿真器（预览版）。



## 项目目录结构

```
|-- platform_lib
      |-- README.md
      |-- main.py          // 环境测试主函数
      |-- tools.py         // 配置文件加载工具
      |-- visual_utils.py  // 可视化代码
      |-- oil_visual.html  // 可视化结果
      |-- test             // 环境测试用动作
            |-- decision.json        // 各节点动作（对应系统配置 system_configs.xlsx，测试用）
      |-- env              // 仿真环境
            |-- objects              // 仿真器中各类节点模块
                  |-- depot.py
                  |-- oilfield.py
                  |-- province.py
                  |-- purchase.py
                  |-- refinery.py
                  |-- road.py
                  |-- saleregion.py
                  |-- transfer.py
            |-- simulators           // 仿真器
                  |-- game.py
            |-- config.json          // 相关配置文件
            |-- chooseenv.py         // 继承自 Jidi
            |-- oilcontrolenv.py     // 物流仿真器逻辑代码
            |-- system_configs.xlsx  // 系统配置参数文件
      |-- render           // 可视化相关数据及文件
            |-- my_geo.py            // 地理信息可视化模块（visual_utils.py 中使用）
            |-- position.json        // 节点映射表（将系统配置文件中的节点映射为真实地理坐标）
            |-- render_data.pkl      // 可视化渲染数据（由 main.py 生成）
      |-- utils            // 工具函数（继承自 Jidi）
```



## 系统参数配置

本仿真器提供了Excel文件用于快速配置所需的仿真器系统，该文件路径为：`env/system_configs.xlsx`。

**注意**：

1. 请勿修改该文件**路径**、**名称**、**表（Sheet）名称**，以及每张表中的**属性名称**；
2. 配置所需的仿真器系统时，只需在每张表中，**按格式**填入对应属性的参数即可；
3. 配置表中每条记录**不允许空缺**，否则可能会导致仿真器运行出错。



## 动作格式说明

关于在仿真器中，每个节点接收的`Action`格式，以及整个仿真器接收的`Joint Action`格式，可参考`param_specification.md`。



## 可视化说明

在进行可视化之前，需要根据当前仿真系统的配置信息（`system_configs.xlsx`中的内容），在`./render/position.json`文件中给每个节点指定其真实的**经纬度信息**。

当完成一次仿真后，程序就会在`./render`文件夹下生成一个名为`render_data.pkl`的文件，该文件记录了本次仿真中，每个step的运行结果。

之后，直接运行`visual_utils.py`文件，便会在**项目根目录**中生成一个名为`oil_visual.html`的文件，该文件便是本次系统仿真的可视化结果。



## 注意

1. 该仿真器可判断接收的决策是否满足所有约束，若不满足则会修改这些决策。若保证在使用过程中，传给仿真器的决策参数都满足约束，则可在调用该仿真器时，设置**参数`is_simulate`**为`True`（该参数默认为`False`，即仿真器会对决策进行约束检验与调整）；
2. 当前仿真器基本测试完毕，在仅用于仿真时（即`is_simulate`为`True`时）尚未发现问题；
3. 仍需说明，1中仿真器对决策参数进行约束的部分功能还未彻底完备（主要为**道路运输下限**的约束问题），可能需要进一步的调试。

