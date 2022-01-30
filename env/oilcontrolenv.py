from collections import defaultdict
from env.simulators.game import Game
from env.objects import (OilField, Purchase, Transfer, Refinery, SaleRegion, Province, Road)
import numpy as np

vertex_kinds = {
    'oilfield': OilField, 'purchase': Purchase, 'transfer': Transfer,
    'refinery': Refinery, 'saleregion': SaleRegion, 'province': Province
}
P = 100  # 出现预警第一天的惩罚项
gamma = 1.1  # 倍数因子，用于放大预警时长惩罚
rou = [0.2, 0.2, 0.2, 0.2, 0.2]  # 各类回报在总回报中的系数


class OilControlEnv(Game):
    def __init__(self, conf, sys_conf, is_simulate=False):
        super().__init__(sum(sys_conf['n_vertices']), conf['is_obs_continuous'], conf['is_act_continuous'],
                         conf['game_name'], sum(sys_conf['n_vertices']), conf['obs_type'])
        self.sys_conf = sys_conf
        # 判断当前环境是否只是仿真，是否需要对动作进行约束s
        self.is_simulate = is_simulate
        self.vertices = {
            'oilfield': [], 'purchase': [], 'transfer': [],
            'refinery': [], 'saleregion': [], 'province': []
        }

        self.max_step = int(conf['max_step'])
        self.step_cnt = 0
        self.warning_cnt = 0  # 记录连续预警的天数
        self.current_state = None
        self.all_observes = None
        self.joint_action_space = None

    def init_system(self):
        # 初始化各节点信息
        for k in self.vertices.keys():
            v_configs = self.sys_conf[k]
            if k != 'refinery':
                for conf in v_configs:
                    vertex = vertex_kinds[k](conf)
                    self.vertices[k].append(vertex)
            else:
                process_scheme = self.sys_conf['process_scheme']
                for conf in v_configs:
                    vertex = vertex_kinds[k](conf, process_scheme)
                    self.vertices[k].append(vertex)

        # 初始化道路信息
        r_configs = self.sys_conf['roads']
        for conf in r_configs:
            start = conf['start']
            end = conf['end']
            road = Road(conf)
            vertex = self.vertices[start[0]][start[1]]
            if conf['goods'] == 0:  # 运输原油
                vertex.add_crude_neighbor(end, road)
            elif conf['goods'] == 1:  # 运输汽油
                vertex.add_gas_neighbor(end, road)
            else:  # 运输柴油
                vertex.add_diesel_neighbor(end, road)

    def reset(self):
        self.step_cnt = 0
        self.warning_cnt = 0

        self.vertices = {
            'oilfield': [], 'purchase': [], 'transfer': [],
            'refinery': [], 'saleregion': [], 'province': []
        }
        self.init_system()

        self.current_state = self.get_state()
        self.all_observes = self.get_observations()
        self.joint_action_space = self.set_action_space()

        return self.all_observes

    def step(self, all_action):
        self.step_cnt += 1
        if self.is_simulate:
            all_action = self.bound_action(all_action)

        self.current_state = self.get_next_state(all_action)
        self.all_observes = self.get_observations()

        # 更新连续预警天数
        signal = self.current_state['signal']
        if sum(signal) == 0:
            self.warning_cnt = 0
        else:
            self.warning_cnt += 1

        reward = self.get_reward(all_action)
        done = self.is_terminal()

        return self.all_observes, reward, done, None

    def bound_action(self, all_action):
        bounded_action = defaultdict(list)
        for k in all_action.keys():
            if k == 'province':
                bounded_action[k] = all_action[k].copy()
                continue
            actions = all_action[k]
            for idx, vertex in enumerate(self.vertices[k]):
                action_i = vertex.bound_action(actions[idx])
                bounded_action[k].append(action_i)
        return bounded_action

    def get_state(self):
        signal = []
        state = {
            'oilfield': [], 'transfer': [], 'refinery': [],
            'saleregion': [], 'province': []
        }
        for k in state.keys():
            for vertex in self.vertices[k]:
                state[k].append(vertex.get_state())
                signal += vertex.get_signal()
        state['signal'] = signal
        return state

    def get_next_state(self, all_action):
        trans_order = ['oilfield', 'purchase', 'transfer', 'refinery', 'saleregion', 'province']
        for k in trans_order:
            actions = all_action[k]
            for idx, vertex in enumerate(self.vertices[k]):
                # 将当天各道路上的运输添加到相应节点的接收列表
                self.update_receive_list(vertex, actions[idx], k)
                if k != 'purchase':
                    vertex.update(actions[idx])
        next_state = self.get_state()
        return next_state

    def update_receive_list(self, vertex, action, kind):
        if kind in ['oilfield', 'purchase', 'transfer']:
            # 原油入接收列表
            crude_kinds = vertex.get_crude_kinds()
            connections = vertex.get_crude_connections()
            for nbr, deliveries in zip(connections, action['crude_delivery']):
                nbr_vertex = self.vertices[nbr[0]][nbr[1]]
                roads = vertex.get_crude_roads(nbr)
                for delivery, road in zip(deliveries, roads):
                    if sum(delivery) == 0:
                        continue
                    receive = {crude_kinds[i]: delivery[i]
                               for i in range(len(crude_kinds)) if delivery[i] != 0}
                    nbr_vertex.add_crude2receive(receive, road.time)
        elif kind in ['refinery', 'saleregion']:
            # 汽油入接收列表
            g_connections = vertex.get_gas_connections()
            for nbr, deliveries in zip(g_connections, action['gas_delivery']):
                nbr_vertex = self.vertices[nbr[0]][nbr[1]]
                roads = vertex.get_gas_roads(nbr)
                for delivery, road in zip(deliveries, roads):
                    if delivery == 0:
                        continue
                    nbr_vertex.add_gas2receive(delivery, road.time)
            # 柴油入接收列表
            d_connections = vertex.get_diesel_connections()
            for nbr, deliveries in zip(d_connections, action['diesel_delivery']):
                nbr_vertex = self.vertices[nbr[0]][nbr[1]]
                roads = vertex.get_diesel_roads(nbr)
                for delivery, road in zip(deliveries, roads):
                    if delivery == 0:
                        continue
                    nbr_vertex.add_diesel2receive(delivery, road.time)

    def get_observations(self):
        return self.current_state

    def set_action_space(self):
        joint_action_space = {
            'oilfield': [], 'purchase': [], 'transfer': [],
            'refinery': [], 'saleregion': []
        }
        for k in joint_action_space.keys():
            for vertex in self.vertices[k]:
                action_space = vertex.set_action_space()
                joint_action_space[k].append(action_space)
        return joint_action_space

    def get_single_action_space(self, kind, idx):
        vertex_list = self.joint_action_space.get(kind)
        if not vertex_list:
            return None
        return vertex_list[idx]

    def get_reward(self, all_action):
        # 计算每个节点的回报（油品运输费用/库存警告惩罚/库存舍弃损失/库存缺口惩罚之一或多项）
        single_rewards = np.zeros(4)
        for k in self.vertices.keys():
            for vertex, action in zip(self.vertices[k], all_action[k]):
                reward = vertex.get_reward(action)
                single_rewards += np.array(reward)

        # 计算系统的预警时长惩罚
        w_reward = -P * (gamma ** (self.warning_cnt - 1)) if self.warning_cnt > 0 else 0

        # 按系数计算总回报
        single_rewards = np.append(single_rewards, [w_reward], axis=0)
        total_reward = np.dot(single_rewards, np.array(rou))

        return total_reward

    def is_terminal(self):
        is_done = self.step_cnt >= self.max_step
        return is_done
