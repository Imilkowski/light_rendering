import cv2
import numpy as np
from random import randint
import datetime as dt
from tqdm import tqdm

height = 400
width = 400
rays_num = 144
intensity_multiplier = 2

image = np.full((height, width, 3), 50, np.uint8)


def draw_room():
    # no max width or height values (eg. 400->399)

    # walls
    walls_lines = []
    walls = [[[160, 110], [190, 110], [190, 140], [160, 140]],
             [[260, 210], [290, 210], [290, 240], [260, 240]],
             [[90, 270], [130, 270], [130, 310], [90, 310]]]

    for i in range(0, len(walls)):
        cv2.fillPoly(image, pts=[np.array(walls[i])], color=(0, 0, 0))

        for j in range(0, len(walls[i])):
            if j != len(walls[i])-1:
                walls_lines.append([walls[i][j], walls[i][j+1]])
            else:
                walls_lines.append([walls[i][j], walls[i][0]])

    # lights
    lights_lines = []
    lights = [[[250, 80], [300, 80], [320, 100], [320, 150], [300, 170], [250, 170], [230, 150], [230, 100]],
              [[160, 210], [180, 210], [190, 220], [190, 240], [180, 250], [160, 250], [150, 240], [150, 220]]]

    for i in range(0, len(lights)):
        cv2.fillPoly(image, pts=[np.array(lights[i])], color=(255, 255, 255))

        for j in range(0, len(lights[i])):
            if j != len(lights[i])-1:
                lights_lines.append([lights[i][j], lights[i][j+1]])
            else:
                lights_lines.append([lights[i][j], lights[i][0]])

    return walls_lines, lights_lines


def intersection(x1, y1, x2, y2, x3, y3, x4, y4):
    q1, q2, q3, q4 = (x1 - x2), (y3 - y4), (y1 - y2), (x3 - x4)

    d = q1 * q2 - q3 * q4

    if d == 0:
        return None

    q5, q6 = (x1 - x3), (y1 - y3)

    n = q5 * q2 - q6 * q4

    t1 = n / d
    t2 = -(q1 * q6 - q3 * q5) / d

    if 0 < t1 < 1 and t2 > 0:
        return int(x1 + t1 * (x2 - x1)), int(y1 + t1 * (y2 - y1))


def cast_rays(x, y):
    samples = []

    for i in range(0, rays_num):
        def draw_ray():
            degree = randint(0, 360)

            # ray vector
            if 0 <= degree < 90:
                return int((x - width) + (2 * width * (degree / 90))), y - height
            elif 90 <= degree < 180:
                return x + width, int((y - height) + (2 * height * ((degree - 90) / 90)))
            elif 180 <= degree < 270:
                return int((x + width) - (2 * width * ((degree - 180) / 90))), y + height
            else:
                return x - width, int((y + height) - (2 * height * ((degree - 270) / 90)))

        end_pos = draw_ray()

        # # visualization
        # image = cv2.line(image, (x, y), end_pos, (255, 0, 0), 1)

        light_points = []
        wall_points = []

        def intersection_point(objects, type):
            for object in objects:
                point = intersection(object[0][0], object[0][1], object[1][0], object[1][1], x, y, end_pos[0], end_pos[1])

                if point is not None:
                    if type == 0:
                        light_points.append(point)
                    elif type == 1:
                        wall_points.append(point)

        # for now we assume every light is white
        intersection_point(lights, 0)

        def closest_point():
            distances = []

            for point in light_points:
                distances.append(int(np.sqrt(abs(x - point[0]) ** 2 + abs(y - point[1]) ** 2)))

            for point in wall_points:
                distances.append(int(np.sqrt(abs(x - point[0]) ** 2 + abs(y - point[1]) ** 2)))

            # returns "light" only if light was the nearest intersection
            if np.argmin(distances) <= (len(light_points) - 1) != -1:
                return 0

        if len(light_points) != 0:
            intersection_point(walls, 1)

            samples.append(closest_point())

    return samples


walls, lights = draw_room()
cv2.imshow("Map", image)
cv2.waitKey(0)

# samples = cast_rays(150, 150, image, lights, walls)


print("Rendering... ({})".format(dt.datetime.now().strftime("%H:%M")))

for y in tqdm(range(height)):
    for x in range(width):
        if np.all(image[y, x] == 50):
            samples = cast_rays(x, y)

            # how many 0 (lights)
            intensity = (samples.count(0) / rays_num) * intensity_multiplier
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