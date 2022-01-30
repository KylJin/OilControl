from collections import defaultdict
from env.objects.depot import CrudeDepot
from utils.box import Box
import numpy as np


class Transfer(object):
    def __init__(self, config):
        self.key = config['key']
        self.crude = CrudeDepot(belongsTo=self.key, config=config['crude_depot'])

    def set_action_space(self):
        num_crude = len(self.get_crude_kinds())

        crude_action_space = []
        for nbr in self.get_crude_connections():
            action_space_i = []
            roads = self.get_crude_roads(nbr)
            for road in roads:
                space = Box(road.lower_capacity, road.upper_capacity,
                            shape=(num_crude,), dtype=np.float64)
                action_space_i.append(space)
            crude_action_space.append(action_space_i)

        action_space = {'crude_action_space': crude_action_space}
        return action_space

    def bound_action(self, action):
        crude_total = np.zeros(len(self.crude.crude_kinds))
        # 对每种原油的运输量进行约束
        temp_action = []
        for delivery in action['crude_delivery']:
            nbr_action = np.array(delivery, dtype=np.float64)
            crude_total += np.sum(nbr_action, axis=0)
            temp_action.append(nbr_action)
        # 计算每种原油的缩放系数
        crude_coef = np.ones_like(crude_total)
        for i, idx in enumerate(self.crude.crude_kinds):
            if crude_total[i] > self.crude.storage[idx]:
                crude_coef[i] = self.crude.storage[idx] / crude_total[i]

        # 对每条道路上的运输量进行约束
        crude_bounded = []
        connections = self.get_crude_connections()
        for nbr, delivery in zip(connections, temp_action):
            new_delivery = np.multiply(delivery, crude_coef)
            roads = self.get_crude_roads(nbr)
            for i, road in enumerate(roads):
                total_vol = np.sum(new_delivery[i])
                if total_vol <= 0:
                    new_delivery[i] = np.zeros_like(new_delivery[i])
                elif total_vol > road.upper_capacity:
                    new_delivery[i] *= (road.upper_capacity / total_vol)
                elif total_vol < road.lower_capacity:
                    new_delivery[i] *= (road.lower_capacity / total_vol)
            crude_bounded.append(new_delivery.tolist())

        bounded_action = {'crude_delivery': crude_bounded}
        return bounded_action

    def update(self, action):
        # 更新原油库
        crude_out = defaultdict(int)
        for delivery in action['crude_delivery']:
            for crude in delivery:
                for idx, vol in zip(self.crude.crude_kinds, crude):
                    crude_out[idx] += vol
        crude_in = self.crude.get_today_receive()
        self.crude.update_storage(crude_out, crude_in)

    def get_state(self):
        state = {
            'crude_storage': list(self.crude.storage.values()),
            'lower_storage': self.crude.lower_storage,
            'upper_storage': self.crude.upper_storage
        }
        return state

    def get_signal(self):
        return [self.crude.signal]

    def get_reward(self, action):
        # 油品运输费用
        t_reward = 0
        connections = self.get_crude_connections()
        for nbr, delivery in zip(connections, action['crude_delivery']):
            roads = self.get_crude_roads(nbr)
            for i, road in enumerate(roads):
                total_vol = sum(delivery[i])
                t_reward += road.cost * total_vol

        # 库存警告惩罚、库存舍弃损失
        o_reward, l_reward = self.crude.get_part_reward()

        return [-t_reward, -o_reward, -l_reward, 0]

    # 原油库相关操作
    def add_crude_neighbor(self, nbr, road):
        self.crude.add_neighbor(nbr, road)

    def get_crude_connections(self):
        return self.crude.get_connections()

    def get_crude_roads(self, nbr):
        return self.crude.get_roads(nbr)

    def get_crude_kinds(self):
        return self.crude.crude_kinds

    def add_crude2receive(self, crude, day):
        self.crude.add_future_receive(crude, day)
