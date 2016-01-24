import math
from PIL import Image, ImageDraw
from itertools import cycle
from numpy import arange


def point_distance(a, b):
    return math.sqrt(pow(a[0] - b[0], 2) + pow(a[1] - b[1], 2))


__NUM_STEPS = 20


def cubic_bezier_fn(control_pts, t):
    """
    Numerically calculate an x,y point for the bezier curve at position t.

    Parameters: control_pts -- list of 4 (x,y) control points
                t -- 'time' value should be between 0 and 1

    Return: (xpt, ypt) -- tuple of x,y data on the curve
    """
    check = ((0 <= t) and (t <= 1))
    assert check

    # define the actual cubic bezier equation here
    def fn(c, t):
        return c[0] * (1 - t) ** 3 + c[1] * 3 * t * (1 - t) ** 2 + c[2] * 3 * t ** 2 * (1 - t) + c[3] * t ** 3

    xs = [x for x, y in control_pts]
    ys = [y for x, y in control_pts]

    # now calculate the x,y position from the bezier equation
    xpt = fn(xs, t)
    ypt = fn(ys, t)

    return xpt, ypt


def get_control_points(coords, n, alpha):
    assert 0 < alpha < 1

    cpoints = []

    v = [(0, 0), list(coords[n - 1]), list(coords[0])]

    mid = [[0, 0],
           [(v[1][0] + v[2][0]) / 2.0, (v[1][1] + v[2][1]) / 2.0]]
    vdist = [0, point_distance(v[1], v[2])]
    anchor = [0, 0]

    for i in range(n):
        v[0] = v[1]
        v[1] = v[2]
        v[2] = coords[(i + 1) % n]

        mid[0][0] = mid[1][0]
        mid[0][1] = mid[1][1]
        mid[1][0] = (v[1][0] + v[2][0]) / 2.0
        mid[1][1] = (v[1][1] + v[2][1]) / 2.0

        vdist[0] = vdist[1]
        vdist[1] = point_distance(v[1], v[2])

        p = vdist[0] / (vdist[0] + vdist[1])

        anchor[0] = mid[0][0] + p * (mid[1][0] - mid[0][0])
        anchor[1] = mid[0][1] + p * (mid[1][1] - mid[0][1])

        xdelta = anchor[0] - v[1][0]
        ydelta = anchor[1] - v[1][1]

        c0 = (
            alpha * (v[1][0] - mid[0][0] + xdelta) + mid[0][0] - xdelta,
            alpha * (v[1][1] - mid[0][1] + ydelta) + mid[0][1] - ydelta)

        c1 = (
            alpha * (v[1][0] - mid[1][0] + xdelta) + mid[1][0] - xdelta,
            alpha * (v[1][1] - mid[1][1] + ydelta) + mid[1][1] - ydelta)

        cpoints.append([c0, c1])

    return cpoints


def cubic_bezier(start, end, ctrl1, ctrl2, nv):
    result = [start]

    for i in range(nv - 1):
        t = float(i) / (nv - 1)
        tc = 1.0 - t

        t0 = tc * tc * tc
        t1 = 3.0 * tc * tc * t
        t2 = 3.0 * tc * t * t
        t3 = t * t * t
        tsum = t0 + t1 + t2 + t3

        x = (t0 * start[0] + t1 * ctrl1[0] + t2 * ctrl2[0] + t3 * end[0]) / tsum
        y = (t0 * start[1] + t1 * ctrl1[1] + t2 * ctrl2[1] + t3 * end[1]) / tsum

        result.append((x, y))

    result.append(end)
    return result


def smooth_points(coords, alpha):
    vertices_count = len(coords)
    cpoints = get_control_points(coords, vertices_count, alpha)
    points = []

    for i in range(vertices_count):
        i_next = (i + 1) % vertices_count

        segment = cubic_bezier(coords[i], coords[i_next],
                               cpoints[i][1], cpoints[i_next][0],
                               10)
        points.extend(segment)

    return points


def main():
    im = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)

    coords = [(10, 30), (20, 20),
              (30, 10), (50, 10),
              (50, 30), (30, 30),
              (10, 30)]

    vertices_count = len(coords)

    cpoints = get_control_points(coords, vertices_count, 0.5)

    points = []

    for i in range(vertices_count):
        i_next = (i + 1) % vertices_count

        segment = cubic_bezier(coords[i], coords[i_next],
                               cpoints[i][1], cpoints[i_next][0],
                               10)
        points.extend(segment)

    draw.polygon(points, fill='red', outline='black')
    im.save('out2.png')


if __name__ == '__main__':
    main()
