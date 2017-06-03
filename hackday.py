from math import sqrt, floor, ceil
from operator import add

import plotly.offline as py
import plotly.graph_objs as go

import random


# @@@@@@@@@ HELPER FUNCTIONS @@@@@@@@@ #

def is_even(n):
    r = n / 2.0
    if r == int(r):
        return True
    else:
        return False


def parse_cidr(cidr):
    # Accepts a CIDR notation string          e.g.  "172.16.0.0/14"
    # Returns a tuple of address and netmask  e.g. ("172.16.0.0", "14")
    return cidr.split('/')[0], int(cidr.split('/')[1])


def calc_ip_int(address):
    octets = address.split('.')
    sum = 0
    for i, octet in enumerate(octets):
        value = int(octet) * (256 ** (3-i))
        sum += value
    return sum


def calc_scale_from_int(ip_int, netmask):
    # Returns absolute min & max IP address integers
    num_addresses = 2 ** (32 - netmask)
    max = ip_int + num_addresses - 1
    return ip_int, max


# @@@@@@@@@ APPLICATION FUNCTIONS @@@@@@@@@ #

def make_rectangle(square_length, region_address, region_netmask, cidr):
    # Returns a dict of x, y, dx, dy

    address, netmask = parse_cidr(cidr)

    if region_netmask == netmask:
        return dict({'x': 0, 'y': 0, 'dx': square_length, 'dy': square_length})

    hostmask = 32 - netmask

    if is_even(netmask):
        height = sqrt(2 ** hostmask)
        width = height
    else:
        width = sqrt(2 ** (hostmask + 1))
        height = width / 2

    ip_int = calc_ip_int(address)
    abs_region_int = calc_ip_int(region_address)
    x, y = calc_offsets(abs_region_int, ip_int, region_netmask, netmask)

    rect = {
        'x': x,
        'y': y,
        'dx': width,
        'dy': height
    }

    return rect


def calc_offsets(abs_region_int, ip_int, region_netmask, netmask):
    if region_netmask == netmask:
        return (0, 0)
    if region_netmask == netmask - 1:
        region_length = sqrt(2 ** (32 - region_netmask))
        rmin, rmax = calc_scale_from_int(abs_region_int, region_netmask)

        if ip_int == abs_region_int:
            offset_y = 0
        elif ip_int == int(rmin + ceil((rmax - abs_region_int) / 2)):
            offset_y = region_length / 2
        offset_x = 0
        return (offset_x, offset_y)

    # Calculate region max
    _, abs_region_int_max = calc_scale_from_int(abs_region_int, region_netmask)

    # Calculate quadrant that ip_int resides in
    fraction = (ip_int - abs_region_int)/float((abs_region_int_max - abs_region_int))
    quadrant = floor(fraction * 4)

    # return quadrant offset x & y
    # 0 1
    # 2 3
    region_length = sqrt(2 ** (32 - region_netmask))
    offset_x = 0 if quadrant in [0, 2] else region_length / 2
    offset_y = 0 if quadrant in [0, 1] else region_length / 2

    # Calculate next region min int
    abs_region_int += quadrant/4 * (2 ** (32 - region_netmask))

    x, y = calc_offsets(abs_region_int, ip_int, region_netmask + 2, netmask)

    offset_x += x
    offset_y += y
    return (offset_x, offset_y)


# @@@@@@@@@ MAIN @@@@@@@@@ #

def main():

    with open('network.csv', 'r') as f:
        lines = f.readlines()

    cidrs = [line.split(',')[0] for line in lines]
    labels = [line.split(',')[1] for line in lines]

    region_address, region_netmask = parse_cidr(cidrs[0])
    canvas_size = sqrt(2 ** (32 - region_netmask))

    rects = []
    annotations = []

    for i, cidr in enumerate(cidrs):
        rect = make_rectangle(canvas_size, region_address, region_netmask, cidr)
        rects.append(rect)

        r = rect

        annotation = dict(
            x = r['x']+(r['dx']/2),
            y = r['y']+(r['dy']/2)+random.randrange(0,40),
            text = labels[i],
            showarrow = False
        )
        annotations.append(annotation)


    # @@@@@@@@@ PLOTLY @@@@@@@@@ #

    x = 0
    y = 0
    width = canvas_size
    height = canvas_size

    # Choose colors from http://colorbrewer2.org/ under "Export"
    color_brewer = ['rgb(255,255,255)','rgb(31,120,180)','rgb(178,223,138)',
                    'rgb(51,160,44)','rgb(251,154,153)','rgb(227,26,28)',
                    'rgb(253,191,111)','rgb(255,127,0)','rgb(202,178,214)',
                    'rgb(106,61,154)','rgb(255,255,153)','rgb(177,89,40)']
    shapes = []
    counter = 0

    for r in rects:
        shapes.append(
            dict(
                type='rect',
                x0=r['x'],
                y0=r['y'],
                x1=r['x']+r['dx'],
                y1=r['y']+r['dy'],
                line=dict(width=2),
                fillcolor=color_brewer[counter],
                opacity=1.0
            )
        )
        counter = counter + 1
        if counter >= len(color_brewer):
            counter = 0

    # # For hover text
    trace0 = go.Scatter(
        x = [ r['x']+(r['dx']/2) for r in rects ], 
        y = [ r['y']+(r['dy']/2) for r in rects ],
        # text = [ str(v) for v in values ], 
        mode = 'text',
    )

    layout = dict(
        height=800,
        width=800,
        xaxis=dict(showgrid=True,zeroline=True,range=[0,canvas_size]),
        yaxis=dict(showgrid=True,zeroline=True,range=[canvas_size, 0]),
        shapes=shapes,
        annotations=annotations,
        hovermode='closest'
    )

    # With hovertext
    figure = dict(data=[trace0], layout=layout)

    # Without hovertext
    # figure = dict(data=[Scatter()], layout=layout)

    py.plot(figure, filename='output.html')


if __name__ == "__main__":
    main()
