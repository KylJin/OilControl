import argparse
import matplotlib.pyplot as plt
from env import OilControlEnv
from tools import load_json_config, load_sys_config


def run_game(args):
    # 读取配置文件
    all_conf = load_json_config("env/config.json")
    conf = all_conf['Oil_Control']
    sys_conf = load_sys_config("env/system_configs.xlsx")

    # 载入测试动作
    actions = load_json_config("decision.json")

    # 根据配置文件创建环境
    env = OilControlEnv(conf, sys_conf, is_simulate=True)

    reward_hist = []
    observation = env.reset()
    # 开始仿真
    while not env.is_terminal():
        joint_actions = actions
        observation_, reward, done, _ = env.step(joint_actions)

        if not args.silence:
            print("observation:", observation)
            print("reward:", reward)
            print('-------------------------------------')

        observation = observation_
        reward_hist.append(reward)

    return reward_hist


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--algo', default='random', type=str, help="random")
    parser.add_argument('--step_per_update', default=1, type=int)  # 两次更新的step间隔
    parser.add_argument('--silence', action='store_true')
    args = parser.parse_args()

    history = run_game(args)

    # 查看reward趋势
    plt.title(f"Algorithm {args.algo}'s performance on Oil Control Env")
    plt.xlabel("day")
    plt.ylabel("reward")
    plt.plot(list(range(len(history))), history)
    plt.show()


if __name__ == '__main__':
    main()
