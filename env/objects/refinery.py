from env.objects.depot import CrudeDepot, PetrolDepot
from utils.box import Box
from utils.discrete import Discrete
import numpy as np


class Refinery(object):
    def __init__(self, config, process_scheme):
        self.key = config['key']
        self.process_scheme = process_scheme
        self.upper_process = config['upper_process']
        self.delivery_capacity = config['delivery_capacity']

        self.crude = CrudeDepot(belongsTo=self.key, config=config['crude_depot'])
        self.gas = PetrolDepot(belongsTo=self.key, config=config['gas_depot'])
        self.diesel = PetrolDepot(belongsTo=self.key, config=config['diesel_depot'])

    def set_action_space(self):
        gas_action_space, diesel_action_space = [], []
        for nbr in self.get_gas_connections():
            action_space_i = []
            roads = self.get_gas_roads(nbr)
            for road in roads:
                space = Box(road.lower_capacity, road.upper_capacity,
                            shape=(1,), dtype=np.float64)
                action_space_i.append(space)
            gas_action_space.append(action_space_i)

        for nbr in self.get_diesel_connections():
            action_space_i = []
            roads = self.get_diesel_roads(nbr)
            for road in roads:
                space = Box(road.lower_capacity, road.upper_capacity,
                            shape=(1,), dtype=np.float64)
                action_space_i.append(space)
            diesel_action_space.append(action_space_i)

        action_space = {
            'scheme_idx': Discrete(len(self.process_scheme)),
            'process': Box(0, self.upper_process, shape=(1,), dtype=np.float64),
            'gas_action_space': gas_action_space,
            'diesel_action_space': diesel_action_space
        }
        return action_space

    def bound_action(self, action):
        bounded_action = {
            'scheme_idx': action['scheme_idx'],
        }
        # 对加工量进行约束
        consume = self.process_scheme[action['scheme_idx']]['consume']
        process = action['process'] if action['process'] <= self.upper_process else self.upper_process
        for idx in consume.keys():
            if process * consume[idx] > self.crude.storage[idx]:
                process = self.crude.storage[idx] / consume[idx]
        bounded_action['process'] = process

        # 对汽油运输量进行统计
        gas_total = 0
        gas_way = [0] * len(self.delivery_capacity)
        gas_connections = self.get_gas_connections()
        for nbr, delivery in zip(gas_connections, action['gas_delivery']):
            gas_total += sum(delivery)
            roads = self.get_gas_roads(nbr)
            for road, vol in zip(roads, delivery):
                gas_way[road.way] += vol
        g_coef = self.gas.storage / gas_total if gas_total > self.gas.storage else 1.

        # 对柴油运输量进行统计
        diesel_total = 0
        diesel_way = [0] * len(self.delivery_capacity)
        diesel_connections = self.get_diesel_connections()
        for nbr, delivery in zip(diesel_connections, action['diesel_delivery']):
            diesel_total += sum(delivery)
            roads = self.get_diesel_roads(nbr)
            for road, vol in zip(roads, delivery):
                diesel_way[road.way] += vol
        d_coef = self.diesel.storage / diesel_total if diesel_total > self.diesel.storage else 1.

        # 计算各运输方式的缩放系数
        w_coef = [1.] * len(gas_way)
        for i in range(len(w_coef)):
            way_delivery = gas_way[i] + diesel_way[i]
            if way_delivery > self.delivery_capacity[i]:
                w_coef[i] = self.delivery_capacity[i] / way_delivery

        # 对动作进行约束
        gas_bounded = action['gas_delivery'].copy()
        for nbr, delivery in zip(gas_connections, gas_bounded):
            roads = self.get_gas_roads(nbr)
            for i, road in enumerate(roads):
                delivery[i] *= (g_coef * w_coef[road.way])
        bounded_action['gas_delivery'] = gas_bounded

        diesel_bounded = action['diesel_delivery'].copy()
        for nbr, delivery in zip(gas_connections, diesel_bounded):
            roads = self.get_diesel_roads(nbr)
            for i, road in enumerate(roads):
                delivery[i] *= (d_coef * w_coef[road.way])
        bounded_action['diesel_delivery'] = diesel_bounded

        return bounded_action

    def update(self, action):
        # 更新原油库
        scheme = self.process_scheme[action['scheme_idx']]
        amount = action['process']
        crude_out = {idx: amount * scheme['consume'][idx] for idx in scheme['consume'].keys()}
        crude_in = self.crude.get_today_receive()
        self.crude.update_storage(crude_out, crude_in)

        # 更新汽油库
        gas_out = 0
        for delivery in action['gas_delivery']:
            gas_out += sum(delivery)
        gas_in = amount * scheme['output'][0]
        self.gas.update_storage(gas_out, gas_in)

        # 更新柴油库
        diesel_out = 0
        for delivery in action['diesel_delivery']:
            diesel_out += sum(delivery)
        diesel_in = amount * scheme['output'][1]
        self.diesel.update_storage(diesel_out, diesel_in)

    def get_state(self):
        state = {
            'crude_storage': list(self.crude.storage.values()),
            'gas_storage': self.gas.storage,
            'diesel_storage': self.diesel.storage,
            'upper_process': self.upper_process,
            'lower_crude': self.crude.lower_storage,
            'upper_crude': self.crude.upper_storage,
            'lower_gas': self.gas.lower_storage,
            'upper_gas': self.gas.upper_storage,
            'lower_diesel': self.diesel.lower_storage,
            'upper_diesel': self.diesel.upper_storage
        }
        return state

    def get_signal(self):
        return [self.crude.signal, self.gas.signal, self.diesel.signal]

    def get_reward(self, action):
        # 油品运输费用
        t_reward = 0
        # 汽油运输费用
        g_connections = self.get_gas_connections()
        for nbr, delivery in zip(g_connections, action['gas_delivery']):
            roads = self.get_gas_roads(nbr)
            for i, road in enumerate(roads):
                t_reward += road.cost * delivery[i]
        # 柴油运输费用
        d_connections = self.get_diesel_connections()
        for nbr, delivery in zip(d_connections, action['diesel_delivery']):
            roads = self.get_diesel_roads(nbr)
            for i, road in enumerate(roads):
                t_reward += road.cost * delivery[i]

        # 原油库存警告惩罚、库存舍弃损失
        c_o_reward, c_l_reward = self.crude.get_part_reward()
        # 汽油库存警告惩罚、库存舍弃损失
        g_o_reward, g_l_reward = self.gas.get_part_reward()
        # 柴油库存警告惩罚、库存舍弃损失
        d_o_reward, d_l_reward = self.diesel.get_part_reward()
        o_reward = c_o_reward + g_o_reward + d_o_reward
        l_reward = c_l_reward + g_l_reward + d_l_reward

        return [-t_reward, -o_reward, -l_reward, 0]

    # 原油库相关操作
    def add_crude2receive(self, crude, day):
        self.crude.add_future_receive(crude, day)

    # 汽油库相关操作
    def add_gas_neighbor(self, nbr, road):
        self.gas.add_neighbor(nbr, road)

    def get_gas_connections(self):
        return self.gas.get_connections()

    def get_gas_roads(self, nbr):
        return self.gas.get_roads(nbr)

    # 柴油库相关操作
    def add_diesel_neighbor(self, nbr, road):
        self.diesel.add_neighbor(nbr, road)

    def get_diesel_connections(self):
        return self.diesel.get_connections()

    def get_diesel_roads(self, nbr):
        return self.diesel.get_roads(nbr)
