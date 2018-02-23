import bottle
import os
import random

directions = ['up', 'down', 'left', 'right']


@bottle.route('/')
def static():
    return "the server is running"


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data.get('game_id')
    board_width = data.get('width')
    board_height = data.get('height')

    head_url = '%s://%s/static/dwight.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    return {
        'color': '#ffcc00',
        'head_url': head_url,
        'name': 'Dwight Snake',
        'taunt': 'Bears, Beets, Battlestar Galactica',
        'head_type': 'safe',
        'tail_type': 'round-bum'
    }


@bottle.post('/move')
def move():
    global directions
    directions = ['up', 'down', 'left', 'right']
    taunt = 'Bears, Beets, Battlestar Galactica'
    data = bottle.request.json

    snakes = data['snakes']
    height = data['height']
    width = data['width']
    # food = data['food']

    me = data['you']['body']['data']

    donthitsnakes(me[0], snakes)
    donthitwalls(me, width, height)
    donthittail(me)

    if adjacenttodanger(me[0], me, snakes, width, height):
        print('danger zone')

    if directions:
        direction = random.choice(directions)
    else:
        print('Goodbye cruel world')
        taunt = 'MICHAEL!!!!!!'
        direction = 'up'

    # print(direction)
    return {
        'move': direction,
        'taunt': taunt
    }


def adjacenttodanger(point, me, snakes, width, height):
    """Checks if a point is adjacent to other snakes, edge of the board or the tail of my snake(not the head or neck)"""
    if istouchingwall(point, width, height):
        print('touching wall')
        return True
    if istouchingsnake(point, snakes):
        print('touching snake')
        return True
    if istouchingself(point, me):
        print('touching self')
        return True


def donthitsnakes(head, snakes):
    """goes through entire snake array and stops it from directly hitting other snakes"""
    global directions

    for snake in snakes['data']:
        for bodypart in snake['body']['data']:
            adj = findadjacentdir(head, bodypart)
            if adj and adj in directions:
                directions.remove(adj)


def donthittail(me):
    global directions
    head = me[0]

    for x in me:
        adj = findadjacentdir(head, x)
        if adj and adj in directions:
            directions.remove(adj)


def donthitwalls(me, width, height):
    """Stops the snake from hitting any walls"""
    global directions
    head = me[0]

    if head['x'] == 0:
        directions.remove('left')
    if head['x'] == width-1:
        directions.remove('right')
    if head['y'] == 0:
        directions.remove('up')
    if head['y'] == height-1:
        directions.remove('down')

#
#
# Below here are utility functions
#
#


def istouchingself(point, me):
    """checks if a point is touching this snake, not including head or neck"""
    self = me[2:]

    for x in self:
        adj = findadjacentdir(point, x)
        if adj:
            return True

    return False


def istouchingsnake(point, snakes):
    for snake in snakes['data']:
        for bodypart in snake['body']['data']:
            adj = findadjacentdir(point, bodypart)
            if adj:
                return True

    return False


def istouchingwall(point, width, height):
    if point['x'] == 0:
        return True
    if point['x'] == width - 1:
        return True
    if point['y'] == 0:
        return True
    if point['y'] == height - 1:
        return True

    return False


def findadjacentdir(a, b):
    """Gives direction from a to b if they are adjacent, if they are not adjacent returns false"""
    ax = a['x']
    ay = a['y']
    bx = b['x']
    by = b['y']
    xdiff = ax - bx
    ydiff = ay - by

    if (xdiff in range(-1, 2) and ydiff == 0) or (ydiff in range(-1, 2) and xdiff == 0):
        if xdiff != 0:
            if xdiff > 0:
                return 'left'
            else:
                return 'right'
        if ydiff != 0:
            if ydiff > 0:
                return 'up'
            else:
                return 'down'
    else:
        return False


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '127.0.0.1'),
        port=os.getenv('PORT', '8080'))
