from collections import defaultdict
from utils.box import Box
import numpy as np


class Purchase(object):
    def __init__(self, config):
        self.key = config['key']
        self.crude_kinds = config['crude_kinds']
        self.connectedTo = defaultdict(list)

    def set_action_space(self):
        num_crude = len(self.get_crude_kinds())

        crude_action_space = []
        for nbr in self.get_crude_connections():
            action_space_i = []
            roads = self.get_crude_roads(nbr)
            for road in roads:
                space = Box(road.lower_capacity, road.upper_capacity,
                            shape=(num_crude, ), dtype=np.float64)
                action_space_i.append(space)
            crude_action_space.append(action_space_i)

        action_space = {'crude_action_space': crude_action_space}
        return action_space

    def bound_action(self, action):
        purchase = action['purchase']
        # 统计每种原油的运输量
        temp_action = []
        crude_total = np.zeros(len(purchase))
        connections = self.get_crude_connections()
        for nbr, delivery in zip(connections, action['crude_delivery']):
            nbr_action = np.array(delivery, dtype=np.float64)
            roads = self.get_crude_roads(nbr)
            for i, road in enumerate(roads):
                total_vol = np.sum(nbr_action[i])
                if total_vol <= 0:
                    nbr_action[i] = np.zeros_like(nbr_action[i])
                elif total_vol > road.upper_capacity:
                    nbr_action[i] *= (road.upper_capacity / total_vol)
                elif total_vol < road.lower_capacity:
                    nbr_action[i] *= (road.lower_capacity / total_vol)
            crude_total += np.sum(nbr_action, axis=0)
            temp_action.append(nbr_action)

        # 计算每种原油的缩放系数
        crude_coef = np.ones(len(self.crude_kinds))
        for i in range(len(purchase)):
            crude_coef = purchase[i] / crude_total[i]
        crude_bounded = []
        # 对每种原油的运输量进行约束
        for delivery in temp_action:
            new_delivery = np.multiply(delivery, crude_coef)
            crude_bounded.append(new_delivery.tolist())

        bounded_action = {
            'purchase': purchase,
            'crude_delivery': crude_bounded
        }
        return bounded_action

    def get_reward(self, action):
        # 油品运输费用
        t_reward = 0
        connections = self.get_crude_connections()
        for nbr, delivery in zip(connections, action['crude_delivery']):
            roads = self.get_crude_roads(nbr)
            for i, road in enumerate(roads):
                total_vol = sum(delivery[i])
                t_reward += road.cost * total_vol

        return [-t_reward, 0, 0, 0]

    def get_info(self, action):
        vertex_name = f'purchase{self.key}'

        # 获取节点信息
        vertex_info = {
            'name': vertex_name,
            'value': {
                '采购原油种类': self.crude_kinds,
                '原油采购量': action['purchase']
            }
        }

        # 获取运输信息
        trans_info = {str(i): defaultdict(dict) for i in range(5)}
        connections = self.get_crude_connections()
        for nbr, delivery in zip(connections, action['crude_delivery']):
            nbr_name = f'{nbr[0]}{nbr[1]}'
            roads = self.get_crude_roads(nbr)
            for i, road in enumerate(roads):
                if sum(delivery[i]) == 0:
                    continue
                trans_collection = trans_info[str(road.way)]
                route = (vertex_name, nbr_name)
                for idx, vol in zip(self.crude_kinds, delivery[i]):
                    if vol == 0:
                        continue
                    key = f'原油{idx}'
                    if key in trans_collection[route]:
                        trans_collection[route][key] += vol
                    else:
                        trans_collection[route][key] = vol

        return vertex_info, trans_info

    # 原油库相关操作
    def add_crude_neighbor(self, nbr, road):
        self.connectedTo[nbr].append(road)

    def get_crude_connections(self):
        return list(self.connectedTo.keys())

    def get_crude_roads(self, nbr):
        return self.connectedTo.get(nbr)

    def get_crude_kinds(self):
        return self.crude_kinds
