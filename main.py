import argparse
import matplotlib.pyplot as plt
from env import OilControlEnv
from tools import load_json_config, load_sys_config, save_render


def run_game(args):
    # 读取配置文件
    all_conf = load_json_config("env/config.json")
    conf = all_conf['Oil_Control']
    sys_conf = load_sys_config(args.config_path)

    # 载入测试动作
    actions = load_json_config("test/decision.json")

    # 根据配置文件创建环境
    env = OilControlEnv(conf, sys_conf, is_simulate=True)  # 只进行仿真，默认接收的动作都是合法的

    reward_hist, render_data = [], []
    observation = env.reset()
    # 开始仿真
    while not env.is_terminal():
        joint_actions = actions
        observation_, reward, done, _ = env.step(joint_actions)

        if args.render:
            data = env.get_render_data(joint_actions)
            render_data.append(data)
            print(data)
        if not args.silence:
            print("observation:", observation)
            print("reward:", reward)
            print('-------------------------------------')

        observation = observation_
        reward_hist.append(reward)

    # 保存可视化数据
    if args.render:
        save_render(render_data, path="./render/render_data.pkl")

    return reward_hist


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--algo', default='random', type=str, help="random")  # 所用算法
    parser.add_argument('--config_path', default="env/system_configs.xlsx", type=str)  # 指定环境配置文件路径
    parser.add_argument('--silence', action='store_true')  # 静默模式（即不在控制台输出中间结果），默认为False
    parser.add_argument('--plot', action='store_true')  # 是否绘制回报曲线，默认为False
    parser.add_argument('--render', action='store_false')  # 是否保存可视化数据，默认为False
    args = parser.parse_args()

    history = run_game(args)

    # 绘制reward曲线
    if args.plot:
        plt.title(f"Algorithm {args.algo}'s performance on Oil Control Env")
        plt.xlabel("day")
        plt.ylabel("reward")
        plt.plot(list(range(len(history))), history)
        plt.show()


if __name__ == '__main__':
    main()
