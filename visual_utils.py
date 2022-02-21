from typing import List
import random
import numpy as np

import pyecharts.options as opts
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Timeline, Grid, Bar, Map, Geo, Pie, Line
from pyecharts.globals import ChartType, SymbolType
from render.my_geo import MY_Geo

TRANS_SPEED = 4
MIN_LIMIT = 0
MAX_LIMIT = 10
COLOR_KEY = '储存量'

node_type_list = ["oilfield", "purchase", "transfer", "refinery", "saleregion", "province"]
position_map = "./render/position.json"


def get_day_chart(data: dict, time_list: list, reward_list: list, idx: int):
    # 提取信息
    # 结点信息
    node_data = {}
    for key in node_type_list:
        node_data[key] = [
            [d['name'], d['value']] for d in data[key]
        ]

    # 运输信息
    trans_data = {}
    for key in data['trans'].keys():
        trans_data[key] = [
            [k, data['trans'][key][k]] for k in data['trans'][key].keys()
        ]

    # 创建图表
    geo_chart = (
        MY_Geo()
        .add_schema(
            maptype="china",
            zoom=1,
            center=[96, 36]
        )
        # 添加结点
        .add_coordinate_json(json_file=position_map)
        # 添加文字信息
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="石油运输系统",
                pos_left="center",
                pos_top="top",
                title_textstyle_opts=opts.TextStyleOpts(font_size=30, )
            ),
            legend_opts=opts.LegendOpts(
                pos_left="20%",
                pos_bottom='bottom',
                textstyle_opts=opts.TextStyleOpts(font_size=15),
            ),
        )
    )

    # 添加结点信息
    for kind in node_data.keys():
        geo_chart.add(
            kind,
            data_pair=node_data[kind],
            label_opts=opts.LabelOpts(is_show=False),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                formatter=JsCode(
                    """function(params) {
                    var inf_str = params.data.name;
                    if ('value' in params.data){
                        for (var key in params.data.value[2]){
                            inf_str = inf_str + '</br>' + key + ':\\t' + String(params.data.value[2][key]); 
                        }
                    }
                    return inf_str
                    }"""
                ),
            ),
            symbol_size=16,
        )

    # 添加运输数据
    for kind in trans_data.keys():
        for d in trans_data[kind]:
            local_i = geo_chart.get_coordinate(d[0][0])
            local_j = geo_chart.get_coordinate(d[0][1])
            dis = np.linalg.norm(np.array(local_i) - np.array(local_j))
            trans_time = dis / TRANS_SPEED
            geo_chart.add(
                kind,
                data_pair=[d],
                label_opts=opts.LabelOpts(is_show=False),
                type_=ChartType.LINES,
                effect_opts=opts.EffectOpts(
                    symbol=SymbolType.ARROW, symbol_size=8, period=trans_time
                ),
                linestyle_opts=opts.LineStyleOpts(curve=0.25, ),
                tooltip_opts=opts.TooltipOpts(
                    is_show=True,
                    formatter=JsCode(
                        """function(params) {
                        var inf_str = params.data.name;
                        if ('inf' in params.data){
                            for (var key in params.data.inf){
                                inf_str = inf_str + '</br>' + key + ':\\t' + String(params.data.inf[key]); 
                            }
                        }
                        return inf_str
                        }"""
                    ),
                ),
            )

    # 折线图
    data_mark = ['' for i in range(len(reward_list))]
    data_mark[idx] = reward_list[idx]

    line_chart = (
        Line()
        .add_xaxis(time_list)
        .add_yaxis(
            "",
            reward_list,
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_='max', name="最大值"),
                    opts.MarkPointItem(type_='min', name="最小值"),
                ]
            ),
            yaxis_index=0,
        )
        .add_yaxis(
            "",
            data_mark,
            markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]),
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="石油运输系统回报折线图", pos_left="7%", pos_top="20"
            )
        )
    )

    # 组合图表
    grid_chart = (
        Grid()
        .add(
            line_chart,
            grid_opts=opts.GridOpts(
                pos_left="60", pos_right="75%", pos_bottom="60%", pos_top="60"
            ),
        )
        .add(
            geo_chart,
            grid_opts=opts.GridOpts(
                pos_left="60%"
            ),
        )
    )

    return grid_chart


def data2web(dataset: dict, file_path=None):
    # 创建timeline
    timeline = Timeline(
        init_opts=opts.InitOpts(width="1600px", height="900px", theme=ThemeType.DARK)
    )

    # 添加图表
    time_list = [d['time'] for d in dataset]
    reward_list = [d['data']['text_info']['当日回报'] for d in dataset]

    for idx, d in enumerate(dataset):
        g = get_day_chart(d['data'], time_list, reward_list, idx)
        timeline.add(g, time_point=str(d['time']))

    timeline.add_schema(
        orient="vertical",
        is_auto_play=True,
        is_inverse=True,
        play_interval=5000,
        pos_right='20',
        pos_bottom="center",
        width='60',
        height='800',
        label_opts=opts.LabelOpts(is_show=True, color="#fff", font_size=14),
    )

    if file_path == None:
        timeline.render("oil_visual.html")
    else:
        timeline.render(file_path)


if __name__ == "__main__":
    import pickle
    import json

    with open("./render/render_data.pkl", "rb") as f:
        dataset = pickle.load(f)
        f.close()
        data2web(dataset)
