

LEFT_DIRECTION = 'LEFT'
RIGHT_DIRECTION = 'RIGHT'
DOWN_DIRECTION = 'DOWN'
UP_DIRECTION = 'UP'
PAUSE_OPTION = 'PAUSE'
START_OPTION = 'START'
DISABLE_SOUND_OPTION = 'DISABLE_SOUND'

keyCode = {
    START_OPTION: 78,
    PAUSE_OPTION: 80,
    LEFT_DIRECTION: 37,
    RIGHT_DIRECTION: 39,
    DOWN_DIRECTION: 40,
    UP_DIRECTION: 38,
    DISABLE_SOUND_OPTION: 83,
}


def euclidian_distance(p1, p2):
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def get_point_proyection(center, point, distance):
    if euclidian_distance(center, point) <= distance ** 2:
        return point
    else:
        x = point[0] - center[0]
        y = point[1] - center[1]
        k = (distance ** 2) / (x ** 2 + y ** 2)
        xp = k * x
        yp = k * y
        return center[0] + int(xp), center[1] + int(yp)
