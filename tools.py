import json
import pandas as pd
import pickle


def save_render(data, path="./render_data.pkl"):
    with open(path, 'wb') as f:
        pickle.dump(data, f)


def load_json_config(file_path):
    with open(file_path, 'r') as f:
        config = json.load(f)
    return config


def load_sys_config(file_path):
    configs = {}
    n_vertices = []
    excel = pd.ExcelFile(file_path)

    oilfield = excel.parse(sheet_name='oilfield')
    configs['oilfield'] = load_oilfield(oilfield)
    n_vertices.append(len(configs['oilfield']))

    purchase = excel.parse(sheet_name='purchase')
    configs['purchase'] = load_purchase(purchase)
    n_vertices.append(len(configs['purchase']))

    transfer = excel.parse(sheet_name='transfer')
    configs['transfer'] = load_transfer(transfer)
    n_vertices.append(len(configs['transfer']))

    refinery = excel.parse(sheet_name='refinery')
    configs['refinery'] = load_refinery(refinery)
    n_vertices.append(len(configs['refinery']))

    saleregion = excel.parse(sheet_name='saleregion')
    configs['saleregion'] = load_saleregion(saleregion)
    n_vertices.append(len(configs['saleregion']))

    province = excel.parse(sheet_name='province')
    configs['province'] = load_province(province)
    n_vertices.append(len(configs['province']))

    roads = excel.parse(sheet_name='roads')
    configs['roads'] = load_roads(roads)

    scheme = excel.parse(sheet_name='process_scheme')
    configs['process_scheme'] = load_scheme(scheme)

    configs['n_vertices'] = n_vertices

    return configs


def load_oilfield(df):
    df['生产原油种类'] = df['生产原油种类'].map(lambda x: eval(x))
    df['生产原油比例'] = df['生产原油比例'].map(lambda x: eval(x))
    df['库存原油种类'] = df['库存原油种类'].map(lambda x: eval(x))
    df['原油初始库存'] = df['原油初始库存'].map(lambda x: eval(x))
    data_types_dict = {'原油库存下限': float, '原油库存上限': float, '原油最大库存': float,
                       '原油警告惩罚系数': float, '原油溢出损失系数': float}
    df = df.astype(data_types_dict)

    configs = []
    for i in range(df.shape[0]):
        config = {
            'key': df.iloc[i, 0],
            'crude_ratio': {idx: r for idx, r in zip(df.iloc[i, 1], df.iloc[i, 2])},
            'crude_depot': get_crude_config(df.iloc[i, 3:10])
        }
        configs.append(config)
    return configs


def load_purchase(df):
    df['采购原油种类'] = df['采购原油种类'].map(lambda x: eval(x))

    configs = []
    for i in range(df.shape[0]):
        config = {
            'key': df.iloc[i, 0],
            'crude_kinds': df.iloc[i, 1]
        }
        configs.append(config)
    return configs


def load_transfer(df):
    df['库存原油种类'] = df['库存原油种类'].map(lambda x: eval(x))
    df['原油初始库存'] = df['原油初始库存'].map(lambda x: eval(x))
    data_types_dict = {'原油库存下限': float, '原油库存上限': float, '原油最大库存': float,
                       '原油警告惩罚系数': float, '原油溢出损失系数': float}
    df = df.astype(data_types_dict)

    configs = []
    for i in range(df.shape[0]):
        config = {
            'key': df.iloc[i, 0],
            'crude_depot': get_crude_config(df.iloc[i, 1:8])
        }
        configs.append(config)
    return configs


def load_refinery(df):
    df['发运能力'] = df['发运能力'].map(lambda x: eval(x))
    df['库存原油种类'] = df['库存原油种类'].map(lambda x: eval(x))
    df['原油初始库存'] = df['原油初始库存'].map(lambda x: eval(x))
    data_types_dict = {'原油库存下限': float, '原油库存上限': float, '原油最大库存': float,
                       '原油警告惩罚系数': float, '原油溢出损失系数': float, '汽油初始库存': float,
                       '汽油库存下限': float, '汽油库存上限': float, '汽油最大库存': float,
                       '汽油警告惩罚系数': float, '汽油溢出损失系数': float, '柴油初始库存': float,
                       '柴油库存下限': float, '柴油库存上限': float, '柴油最大库存': float,
                       '柴油警告惩罚系数': float, '柴油溢出损失系数': float}
    df = df.astype(data_types_dict)

    configs = []
    for i in range(df.shape[0]):
        config = {
            'key': df.iloc[i, 0],
            'upper_process': df.iloc[i, 1],
            'delivery_capacity': df.iloc[i, 2],
            'crude_depot': get_crude_config(df.iloc[i, 3:10]),
            'gas_depot': get_petrol_config(df.iloc[i, 10:16]),
            'diesel_depot': get_petrol_config(df.iloc[i, 16:22])
        }
        configs.append(config)
    return configs


def load_saleregion(df):
    df['发运能力'] = df['发运能力'].map(lambda x: eval(x))
    data_types_dict = {'汽油初始库存': float, '汽油库存下限': float, '汽油库存上限': float,
                       '汽油最大库存': float, '汽油警告惩罚系数': float, '汽油溢出损失系数': float,
                       '柴油初始库存': float, '柴油库存下限': float, '柴油库存上限': float,
                       '柴油最大库存': float, '柴油警告惩罚系数': float, '柴油溢出损失系数': float}
    df = df.astype(data_types_dict)

    configs = []
    for i in range(df.shape[0]):
        config = {
            'key': df.iloc[i, 0],
            'delivery_capacity': df.iloc[i, 1],
            'gas_depot': get_petrol_config(df.iloc[i, 2:8]),
            'diesel_depot': get_petrol_config(df.iloc[i, 8:14])
        }
        configs.append(config)
    return configs


def load_province(df):
    data_types_dict = {'汽油初始库存': float, '汽油库存下限': float, '汽油库存上限': float,
                       '汽油最大库存': float, '汽油警告惩罚系数': float, '汽油溢出损失系数': float,
                       '汽油缺口惩罚系数': float, '柴油初始库存': float, '柴油库存下限': float,
                       '柴油库存上限': float, '柴油最大库存': float, '柴油警告惩罚系数': float,
                       '柴油溢出损失系数': float, '柴油缺口惩罚系数': float}
    df = df.astype(data_types_dict)

    configs = []
    for i in range(df.shape[0]):
        config = {
            'key': df.iloc[i, 0],
            'gas_lack_coef': df.iloc[i, 7],
            'diesel_lack_coef': df.iloc[i, 14],
            'gas_depot': get_petrol_config(df.iloc[i, 1:7]),
            'diesel_depot': get_petrol_config(df.iloc[i, 8:14])
        }
        configs.append(config)
    return configs


def load_roads(df):
    df['起点'] = df['起点'].map(lambda x: eval(x))
    df['终点'] = df['终点'].map(lambda x: eval(x))

    configs = []
    for i in range(df.shape[0]):
        config = {
            'start': df.iloc[i, 0],
            'end': df.iloc[i, 1],
            'way': df.iloc[i, 2],
            'goods': df.iloc[i, 3],
            'lower_capacity': df.iloc[i, 4],
            'upper_capacity': df.iloc[i, 5],
            'cost': df.iloc[i, 6],
            'time': df.iloc[i, 7]
        }
        configs.append(config)
    return configs


def load_scheme(df):
    df['所需原油种类'] = df['所需原油种类'].map(lambda x: eval(x))
    df['所需原油比例'] = df['所需原油比例'].map(lambda x: eval(x))

    configs = []
    for i in range(df.shape[0]):
        config = {
            'key': df.iloc[i, 0],
            'consume': {idx: r for idx, r in zip(df.iloc[i, 1], df.iloc[i, 2])},
            'output': (df.iloc[i, 3], df.iloc[i, 4])
        }
        configs.append(config)
    return configs


def get_crude_config(series):
    config = {
        'crude_kinds': series[0],
        'init_storage': series[1],
        'lower_storage': series[2],
        'upper_storage': series[3],
        'max_storage': series[4],
        'warn_coef': series[5],
        'loss_coef': series[6]
    }
    return config


def get_petrol_config(series):
    config = {
        'init_storage': series[0],
        'lower_storage': series[1],
        'upper_storage': series[2],
        'max_storage': series[3],
        'warn_coef': series[4],
        'loss_coef': series[5]
    }
    return config
