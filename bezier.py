import math

from PIL import Image, ImageDraw


def point_distance(a, b):
    """
    Calculates distance between two points

    :rtype: float
    """
    return math.sqrt(pow(a[0] - b[0], 2) + pow(a[1] - b[1], 2))


def get_control_points(coords, alpha):
    """
    Returns list of control points that are created from coordinates.

    Result list will be 2 * len(coords)

    :param coords: list of coordinates
    :param alpha: smooth factor
    :rtype : list[tuple(2)]
    """
    assert 0 < alpha < 1

    cpoints = []
    n = len(coords)

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
    """
    Create bezier curve between start and end points

    :param start: start anchor point
    :param end: end anchor point
    :param ctrl1: control point 1
    :param ctrl2: control point 2
    :param nv: number of points should be created between start and end
    :return: list of smoothed points
    """
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
    """
    Converts a list of points to polygon based on bezier curves

    http://www.elvenprogrammer.org/projects/bezier/reference/

    :param coords: list of coordinates
    :param alpha: smooth factor
    :return: point list of smoothed polygon
    :rtype : list
    """
    vertices_count = len(coords)
    cpoints = get_control_points(coords, alpha)
    points = []

    for i in range(vertices_count):
        i_next = (i + 1) % vertices_count

        segment = cubic_bezier(coords[i], coords[i_next],
                               cpoints[i][1], cpoints[i_next][0],
                               10)
        points.extend(segment)

    return points


def __main():
    im = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)

    coords = [(10, 30), (20, 20),
              (30, 10), (50, 10),
              (50, 30), (30, 30),
              (10, 30)]

    vertices_count = len(coords)

    cpoints = get_control_points(coords, 0.5)

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
    __main()
