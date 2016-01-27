import math

from PIL import Image, ImageDraw


def get_angle(p1, p2, p3):
    """
    Calculates the angle between three points
    https://en.wikipedia.org/wiki/Law_of_cosines#Applications

    :param p1: center point
    :type p1: tuple
    :type p2: tuple
    :type p3: tuple

    :rtype: float
    """
    f = point_distance
    p12 = f(p1, p2)
    p13 = f(p1, p3)
    p23 = f(p2, p3)

    if p12 == 0 or p13 == 0:
        return math.acos(0)

    result = (p12 ** 2 + p13 ** 2 - p23 ** 2) / (2 * p12 * p13)
    return math.acos(result)


def convert_to_degree(radian):
    return math.degrees(radian)


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


def line(p0, p1):
    """
    Create line between two points based on Bresenham algorithm
    """

    steep = False
    x0 = p0[0]
    y0 = p0[1]
    x1 = p1[0]
    y1 = p1[1]

    if math.fabs(x0 - x1) < math.fabs(y0 - y1):
        x0, y0 = y0, x0
        x1, y1 = y1, x1
        steep = True

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0

    if dx == 0:
        derror = 0.1
    else:
        derror = math.fabs(dy / dx)

    error = 0.0
    y = y0
    x = x0
    points = []

    while x <= x1:
        points.append((y, x) if steep else (x, y))

        error += derror

        if error > 0.5:
            y += 1 if y1 > y0 else -1
            error -= 1.
        x += 1

    return points


def smooth_points(coords, alpha, min_angle=45):
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

    i = 0
    while i < vertices_count:
        i_prev = (i - 1) % vertices_count
        i_next = (i + 1) % vertices_count
        i_next_2 = (i + 2) % vertices_count

        p_current = coords[i]
        p_prev = coords[i_prev]
        p_next = coords[i_next]
        p_next_2 = coords[i_next_2]

        angle = convert_to_degree(get_angle(p_current, p_prev, p_next))
        angle2 = convert_to_degree(get_angle(p_next, p_current, p_next_2))

        if angle <= min_angle:
            segment = line(p_current, p_next)
        elif angle2 <= min_angle:
            segment = line(p_current, p_next)
        else:
            segment = cubic_bezier(p_current, p_next,
                                   cpoints[i][1], cpoints[i_next][0],
                                   10)
        points.extend(segment)
        i += 1

    return points


def __main():
    print(line((0, 0), (5, 10)))
    print(line((300, 100), (200, 250)))

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
