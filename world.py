'''A 2d world that supports agents with steering behaviour

Created for COS30002 AI for Games by Clinton Woodward <cwoodward@swin.edu.au>

For class use only. Do not publically share or post this code without permission.

'''

from vector2d import Vector2D
from matrix33 import Matrix33
from graphics import egi
import random


class World(object):

    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.target = Vector2D(cx / 2, cy / 2)
        self.agents = []
        self.paused = True
        self.show_info = True
        self.obstacles = []
        self.create_circle_obstacles()
        self.scale = 2
        self.best_hiding_pos = Vector2D()
        self.hunter = None
        self.prey = None
        self.nearest_index = 0

    def update(self, delta):
        if not self.paused:
            for agent in self.agents:
                agent.update(delta)

    def create_circle_obstacles(self, num_circles=5, radius=30):
        for i in range(num_circles):
            # choose a random position and radius for the circle
            x = random.uniform(radius, self.cx - radius)
            y = random.uniform(radius, self.cy - radius)
            position = Vector2D(x, y)

            # check if the circle overlaps with any of the previously generated circles
            overlapping = True
            while overlapping:
                overlapping = False
                for obstacle in self.obstacles:
                    distance = obstacle['position'].distance(position)
                    if distance < obstacle['radius'] + radius:
                        overlapping = True
                        # generate a new position and radius for the circle
                        x = random.uniform(radius, self.cx - radius)
                        y = random.uniform(radius, self.cy - radius)
                        position = Vector2D(x, y)
                        break

            # add the circle to the list of obstacles
            self.obstacles.append({'position': position, 'radius': radius})

    def hiding_pos(self, obs_pos, agent_pos):
        temp = Vector2D(agent_pos.x - obs_pos.x, agent_pos.y - obs_pos.y).normalise()
        return obs_pos - 30 * self.scale * temp

    def render(self):
        # Calculate distances from prey to obstacles
        if self.prey is not None:
            distances = [self.prey.pos.distance(obstacle['position']) for obstacle in self.obstacles]
            self.nearest_index = distances.index(min(distances))

        for agent in self.agents:
            if agent.mode == 'hunter':
                self.hunter = agent
                egi.red_pen()
                for obstacle in self.obstacles:
                    hiding_position = self.hiding_pos(obstacle['position'], agent.pos)
                    egi.line_by_pos(agent.pos, hiding_position)
                    egi.cross(hiding_position, 7)

            if agent.mode == 'prey':
                # Calculate the best hiding position for the prey
                self.prey = agent
                max_distance = -1
                for obstacle in self.obstacles:
                    hiding_position = self.hiding_pos(obstacle['position'], agent.pos)
                    distance_to_hunter = hiding_position.distance(self.hunter.pos)
                    if distance_to_hunter > max_distance:
                        max_distance = distance_to_hunter
                        self.best_hiding_pos = hiding_position

            agent.render()

        # render the obstacles as circles
        for i, obstacle in enumerate(self.obstacles):
            if i == self.nearest_index:
                egi.aqua_pen()
            else:
                egi.green_pen()
            egi.circle(obstacle['position'], obstacle['radius'])

        if self.show_info:
            infotext = ', '.join(set(agent.mode for agent in self.agents))
            egi.white_pen()
            egi.text_at_pos(0, 0, infotext)

    def wrap_around(self, pos):
        ''' Treat world as a toroidal space. Updates parameter object pos '''
        max_x, max_y = self.cx, self.cy
        if pos.x > max_x:
            pos.x = pos.x - max_x
        elif pos.x < 0:
            pos.x = max_x - pos.x
        if pos.y > max_y:
            pos.y = pos.y - max_y
        elif pos.y < 0:
            pos.y = max_y - pos.y

    def transform_points(self, points, pos, forward, side, scale):
        ''' Transform the given list of points, using the provided position,
            direction and scale, to object world space. '''
        # make a copy of original points (so we don't trash them)
        wld_pts = [pt.copy() for pt in points]
        # create a transformation matrix to perform the operations
        mat = Matrix33()
        # scale,
        mat.scale_update(scale.x, scale.y)
        # rotate
        mat.rotate_by_vectors_update(forward, side)
        # and translate
        mat.translate_update(pos.x, pos.y)
        # now transform all the points (vertices)
        mat.transform_vector2d_list(wld_pts)
        # done
        return wld_pts

    def transform_point(self, point, pos, forward, side):
        ''' Transform the given single point, using the provided position,
        and direction (forward and side unit vectors), to object world space. '''
        # make a copy of the original point (so we don't trash it)
        wld_pt = point.copy()
        # create a transformation matrix to perform the operations
        mat = Matrix33()
        # rotate
        mat.rotate_by_vectors_update(forward, side)
        # and translate
        mat.translate_update(pos.x, pos.y)
        # now transform the point (in place)
        mat.transform_vector2d(wld_pt)
        # done
        return wld_pt
