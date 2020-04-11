import cv2
import numpy as np
from random import randint
import datetime as dt
from tqdm import tqdm

height = 400
width = 400
rays_num = 36
intensity_multiplier = 2

image = np.full((height, width, 3), 50, np.uint8)


def draw_room(image):
    # walls
    walls = [[(300, 100), (310, 100)],
             [(310, 100), (310, 175)],
             [(310, 175), (300, 175)],
             [(300, 175), (300, 100)],

             [(50, 125), (200, 125)],
             [(50, 125), (50, 150)],
             [(200, 250), (200, 125)],
             [(200, 250), (150, 150)],
             [(150, 150), (50, 150)],

             [(100, 300), (175, 300)],
             [(175, 300), (175, 310)],
             [(175, 310), (100, 310)],
             [(100, 310), (100, 300)]]

    shape = []
    shape.append(np.array([[300, 100], [310, 100], [310, 175], [300, 175]]))
    shape.append(np.array([[200, 125], [50, 125], [50, 150], [150, 150], [200, 250]]))
    shape.append(np.array([[100, 300], [175, 300], [175, 310], [100, 310]]))
    for i in range(0, 3):
        cv2.fillPoly(image, pts=[shape[i]], color=(0, 0, 0))

    # lights
    lights = [[(50, 200), (100, 200)],
              [(100, 200), (100, 250)],
              [(100, 250), (50, 250)],
              [(50, 250), (50, 200)],

              [(250, 25), (260, 25)],
              [(260, 25), (260, 275)],
              [(260, 275), (250, 275)],
              [(250, 275), (250, 25)]]

    shape = []
    shape.append(np.array([[50, 200], [100, 200], [100, 250], [50, 250]]))
    shape.append(np.array([[250, 25], [260, 25], [260, 275], [250, 275]]))
    for i in range(0, 2):
        cv2.fillPoly(image, pts=[shape[i]], color=(255, 255, 255))

    for wall in walls:
        image = cv2.line(image, wall[0], wall[1], (0, 0, 0), 1)

    for light in lights:
        image = cv2.line(image, light[0], light[1], (255, 255, 255), 1)

    return image, lights, walls


def intersection(x1, y1, x2, y2, x3, y3, x4, y4):
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    n = (x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)

    if d == 0:
        return None

    t1 = n / d
    t2 = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / d

    if 0 < t1 < 1 and t2 > 0:
        point_x = x1 + t1 * (x2 - x1)
        point_y = y1 + t1 * (y2 - y1)

        return int(point_x), int(point_y)


def cast_rays(x, y, image, lights, walls):
    samples = []

    for i in range(0, rays_num):
        degree = randint(0, 360)

        # ray vector
        if 0 <= degree < 90:
            end_pos = (int((x - width) + (2*width*(degree/90))), y - height)
        elif 90 <= degree < 180:
            degree -= 90
            end_pos = (x + width, int((y - height) + (2*height*(degree/90))))
        elif 180 <= degree < 270:
            degree -= 180
            end_pos = (int((x + width) - (2*width*(degree/90))), y + height)
        else:
            degree -= 270
            end_pos = (x - width, int((y + height) - (2*height*(degree/90))))

        # # visualization
        # image = cv2.line(image, (x, y), end_pos, (255, 0, 0), 1)

        light_points = []
        wall_points = []

        def intersection_point(objects, type):
            for object in objects:
                point = intersection(object[0][0], object[0][1], object[1][0], object[1][1], x, y, end_pos[0], end_pos[1])

                if point is not None:
                    if type == "light":
                        light_points.append(point)
                    elif type == "wall":
                        wall_points.append(point)

        # for now we assume every light is white
        intersection_point(lights, "light")
        intersection_point(walls, "wall")

        # # dev stuff
        # print("Light points: ", light_points)
        # print("Wall points: ", wall_points)

        def closest_point(light_points, wall_points):
            points = []
            distances = []

            for point in light_points:
                points.append(point)

            for point in wall_points:
                points.append(point)

            if len(points) > 0:
                for point in points:
                    a = abs(x - point[0])
                    b = abs(y - point[1])
                    distance = int(np.sqrt(a**2 + b**2))

                    distances.append(distance)

                id = np.argmin(distances)

                # returns "light" only if light was the nearest intersection
                if id <= (len(light_points)-1) != -1:
                    return "light"
                else:
                    return None

            else:
                return None

        samples.append(closest_point(light_points, wall_points))

    return samples


image, lights, walls = draw_room(image)
cv2.imshow("Map", image)
cv2.waitKey(0)

# samples = cast_rays(150, 150, image, lights, walls)


print("Rendering... ({})".format(dt.datetime.now().strftime("%H:%M")))

for y in tqdm(range(height)):
    for x in range(width):
        if np.all(image[y, x] == 50):
            samples = cast_rays(x, y, image, lights, walls)

            intensity = (samples.count("light") / rays_num) * intensity_multiplier
            if intensity > 1:
                intensity = 1
            value = 255 * intensity

            image[y, x] = (value, value, value)

print("Finished ({})".format(dt.datetime.now().strftime("%H:%M")))

image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
cv2.destroyAllWindows()

now = dt.datetime.now()
datetime = str(now.strftime("%d-%m %H-%M"))
filename = "Render {} {} ".format((height, width, rays_num, intensity_multiplier), datetime)
cv2.imwrite("Renders\\{}.png".format(filename), image)

cv2.imshow("Rendered", image)
cv2.waitKey(0)