from graphviz import Digraph
import json
import argparse

# need manually config
name_map = {
    'self_att_64': 'SA',
    'feed_forward': 'FFN',
    'guided_att_64': 'GA',
    'rel_self_att_64': 'RSA'
}

class INC:
    def __init__(self):
        self.k = -1
    def __call__(self):
        self.k += 1
        return str(self.k)


class COLOR_MAP:
    color_set = ['lightblue', 'lightyellow', 'palegreen', 'pink', 'gray', 'orange', 'MediumPurple']
    def __init__(self):
        self.name = []
        self.cm = dict()
        for n, c in zip(name_map, self.color_set):
            self.name.append(n)
            self.cm[n] = c
    def __getitem__(self, n):
        if n not in self.name:
            self.cm[n] = self.color_set[len(self.name)]
            self.name.append(n)
        return self.cm[n]

def draw(path, epoch, prefix=''):

    def chunk(blocks, in_node, out_node, w='2'):
        with dot.subgraph() as c:
            pre = in_node
            for i in blocks:
                name = i[0]
                cur_idx = inc()
                c.node(cur_idx, name_map[name], style='filled', fillcolor=cm[name])
                c.edge(pre, cur_idx, weight=w)
                pre = cur_idx
        dot.edge(pre, out_node)

    arch = json.load(open(path, 'r+'))['epoch' + str(epoch)]
    fn = prefix + path.split('/')[-1].split('.')[0] + f'_epoch{epoch}'
    cm = COLOR_MAP()

    dot = Digraph(name='dot', engine='dot', filename=fn, format='png')
    dot.attr('graph', rankdir='BT', resolution='100', ranksep='0.3')
    dot.attr('node', fontname='Microsoft YaHei', shape='Mrecord')

    # Draw basic input/output
    inc = INC()
    x = inc()
    y = inc()
    fuse = inc()
    out = inc()
    c = Digraph()

    with dot.subgraph() as c:
        c.attr(rank='same')
        c.node(x, 'x', shape='none')
        c.node(y, 'y', shape='none')
    dot.node(fuse, 'fuse')
    dot.node(out, 'cls', shape='none')
    dot.edge(fuse, out)

    # draw enc and dec
    chunk(arch['enc'], in_node=x, out_node=fuse)
    chunk(arch['dec'], in_node=y, out_node=fuse)

    # save
    dot.render(cleanup=True)
    return dot.source

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='visualization for MMNas(1-path)')
    parser.add_argument('-p', metavar='PATH', dest='path', type=str, required=True, help='arch path')
    parser.add_argument('-e', metavar='EPOCH', dest='epoch', type=int, required=True, help='arch epoch')
    args = parser.parse_args()

    draw(args.path, args.epoch, 'out/') 