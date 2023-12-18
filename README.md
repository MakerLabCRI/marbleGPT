# marbleGPT
```
import math

def euclidean_distance(color1, color2):
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(color1, color2)))

def determine_color(r, g, b):
    red_rgb = (317, 164, 161)
    blue_rgb = (165, 406, 618)
    yellow_rgb = (890, 827, 366)
    white_rgb = (958, 1174, 1083)

    red_distance = euclidean_distance((r, g, b), red_rgb)
    blue_distance = euclidean_distance((r, g, b), blue_rgb)
    yellow_distance = euclidean_distance((r, g, b), yellow_rgb)
    white_distance = euclidean_distance((r, g, b), white_rgb)

    min_distance = min(red_distance, blue_distance, yellow_distance, white_distance)

    if min_distance == red_distance:
        return "Red"
    elif min_distance == blue_distance:
        return "Blue"
    elif min_distance == yellow_distance:
        return "Yellow"
    elif min_distance == white_distance:
        return "White"

# Test cases
print(determine_color(317, 164, 161))  # Should print "Red"
print(determine_color(164, 399, 607))  # Should print "Blue"
print(determine_color(909, 853, 376))  # Should print "Yellow"
print(determine_color(978, 1206, 1122))  # Should print "White"
```
