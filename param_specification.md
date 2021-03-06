## 参数格式设计

### 1 系统整体配置

```json
{
    'n_vertices': [],
    'process_scheme': [],
    'oilfield': [],
    'purchase': [],
    'transfer': [],
    'refinery': [],
    'saleregion': [],
    'province': [],
    'roads': []
}
```

### 2 n_vertices说明

该列表依次记录了系统中各类节点的数量，顺序依次为：

[`oilfield`, `purchase`, `transfer`, `refinery`, `saleregion`, `province`]

### 3 process_scheme说明

记录各类**加工方案**，每项加工方案以`Dict`的形式保存，格式如下：

```json
{
    'key': 0,
    'consume': {crude_idx: rc, ...},
    'output': (rg,rd)
}
```

其中，`consume`为加工单位原油所消耗的各类原油占比；`output`则为加工产品收率，第一项为汽油收率，第二项为柴油收率。

### 4 oilfield说明

记录各**油田节点**的参数，每项以`Dict`的形式保存，格式如下：

```json
{
    'key': 0,
    'crude_ratio': {crude_idx: rc, ...},  // 生产各原油比例
    'crude_depot': {}  // 原油库参数
}
```

接收的`action`格式为：

```json
{
    'production': 50,  // 生产量
    'crude_delivery': [[[0, 2, 1, ], [], ], [[], ], ]
}
```

其中，`crude_delivery`为该节点当日原油运输的决策结果，为一个3维列表（第1维依次表示该节点所连接的下级节点；第2维表示该节点与特定的下级节点间所有的运输途径；第3维则表示在某一运输途径上，该节点所含各类原油的运输量）。

### 5 purchase说明

记录各**采购节点**的参数，每项以`Dict`的形式保存，格式如下：

```json
{
    'key': 0,
    'crude_kinds': []  // 记录该节点采购的各类原油
}
```

接收的`action`格式为：

```json
{
    'purchase': [100, 200, ],  // 每种原油对应的采购量
    'crude_delivery': [[[0, 2, 1, ], [], ], [[], ], ]
}
```

### 6 transfer说明

记录各**原油管道中转节点**的参数，每项以`Dict`的形式保存，格式如下：

```json
{
    'key': 0,
    'crude_depot': {}  // 原油库参数
}
```

接收的`action`格式为：

```json
{
    'crude_delivery': [[[0, 2, 1, ], [], ], [[], ], ]
}
```

### 7 refinery说明

记录各**炼厂节点**的参数，每项以`Dict`的形式保存，格式如下：

```json
{
    'key': 0,
    'upper_process': 100,  // 加工能力上限
    'delivery_capacity': [],  // 各运输方式发运能力
    'crude_depot': {},
    'gas_depot': {},
    'diesel_depot': {}
}
```

其中，`delivery_capacity`中的数值依次表示该节点在**管道**、**公路**、**铁路**、**水运**和**联运**这五种运输方式中的发运能力。

接收的`action`格式为：

```json
{
    'scheme_idx': 0,  // 选择的加工方案下标
    'process': 50,  // 加工量
    'gas_delivery': [[1, 2, ], [], ],
    'diesel_delivery': [[1, 2, ], [], ]
}
```

其中，`gas/diesel_delivery`分别为该节点当日汽油/柴油运输的决策结果，为一个2维列表（第1维依次表示该节点所连接的下级节点；第2维则表示该节点与特定的下级节点间，所有运输途径上的汽油/柴油运输量）。

### 8 saleregion说明

记录各**销售大区节点**的参数，每项以`Dict`的形式保存，格式如下：

```json
{
    'key': 0,
    'delivery_capacity': [],  // 各运输方式发运能力
    'gas_depot': {},
    'diesel_depot': {}
}
```

接收的`action`格式为：

```json
{
    'gas_delivery': [[1, 2, ], [], ],
    'diesel_delivery': [[1, 2, ], [], ]
}
```

### 9 province说明

记录各**省库节点**的参数，每项以`Dict`的形式保存，格式如下：

```json
{
    'key': 0,
    'gas_lack_coef': 1,
    'diesel_lack_coef': 1,
    'gas_depot': {},
    'diesel_depot': {}
}
```

其中，`gas_lack_coef`和`diesel_lack_coef`分别为汽油和柴油库存出现缺口时，对应缺口量的惩罚系数。

该节点并不接收`action`，每天只接收当天的汽油需求量和柴油需求量，格式如下：

```json
{
    'gas_need': 10,
    'diesel_need': 20
}
```

### 10 roads说明

记录各**运输道路**的参数，每项以`Dict`的形式保存，格式如下：

```json
{
    'start': (kind, idx),
    'end': (kind, idx),
    'way': 0,  // 运输方式
    'goods': 0,  // 运输物料
    'lower_capacity': 0,
    'upper_capacity': 50,
    'cost': 1,  // 运输开销
    'time': 3  // 运输时间（天）
}
```

其中，`way`表示该道路的运输方式，0~4依次对应**管道**、**公路**、**铁路**、**水运**和**联运**5种运输方式；`goods`表示该道路所运输的物料，0~2依次对应**原油**、**汽油**和**柴油**。

### 11 depot说明

#### 11.1 汽油、柴油库

```json
{
    'init_storage': 100,
    'lower_storage': 0,
    'upper_storage': 200,
    'max_storage': 300,
    'warn_coef': 0.5,  // 库存警告惩罚系数
    'loss_coef': 1  // 溢出损失系数
}
```

#### 11.2 原油库

```json
{
    'crude_kinds': [],  // 原油种类下标
    'init_storage': [],  // 对应于各原油种类的初始库存量
    'lower_storage': 0,
    'upper_storage': 200,
    'max_storage': 300,
    'warn_coef': 0.5,  // 库存警告惩罚系数
    'loss_coef': 1  // 溢出损失系数
}
```

### 12 状态格式说明

整个环境模型提供的状态参数以`Dict`形式记录，格式如下：

```json
{
    'oilfield': [{}, ],
    'transfer': [{}, ],
    'refinery': [{}, ],
    'saleregion': [{}, ],
    'province': [{}, ],
    'signal': []
}
```

#### 12.1 oilfield、transfer状态

```json
{
    'crude_storage': [],
    'lower_crude': 0,
    'upper_crude': 100
}
```

#### 12.2 refinery状态

```json
{
    'crude_storage': [],
    'gas_storage': 20,
    'diesel_storage': 50,
    
    'upper_process': 50,
    
    'lower_crude': 0,
    'upper_crude': 100,
    'lower_gas': 0,
    'upper_gas': 100,
    'lower_diesel': 0,
    'upper_diesel': 100
}
```

#### 12.3 saleregion、province状态

```json
{
    'gas_storage': 20,
    'diesel_storage': 50,
    
    'lower_gas': 0,
    'upper_gas': 100,
    'lower_diesel': 0,
    'upper_diesel': 100
}
```

#### 12.4 signal项

按`oilfield`, `transfer`, `refinery`, `saleregion`, `province`的顺序，依次记录各个节点内，原油库/汽油库/柴油库的监测信号。

