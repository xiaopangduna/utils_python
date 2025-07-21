object_points = [
    [254.8, 20, 0],
    [254.8, -70, 0],
    [165, 20, 0],
    [165, -70, 0],
    [415, -65, 0],
    [415, -155, 0],
    [325, -65, 0],
    [325, -155, 0],
    [560, 200, 0],
    [560, 110.4, 0],
    [560, 30, 0],
    [560, -60, 0],
    [560, -135.2, 0],
    [560, -225, 0],
]
for i in range(len(object_points)):
    point = object_points[i]
    point[0] = point[0]
    point[1] = point[1] + 26.85
    point[2] = point[2] - 7
for i in range(len(object_points)):
    point = object_points[i]
    point[0] = point[0] * 0.01
    point[1] = point[1] * 0.01
    point[2] = point[2] * 0.01
    print(point)
print(object_points)