class Road(object):
    def __init__(self, config):
        self.way = config['way']
        self.goods = config['goods']
        self.lower_capacity = config['lower_capacity']
        self.upper_capacity = config['upper_capacity']
        self.cost = config['cost']
        self.time = config['time']
