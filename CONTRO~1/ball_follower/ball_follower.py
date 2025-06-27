from controller import Robot, Motor, Camera, TouchSensor

TIME_STEP = 64

# Init robot and devices
robot = Robot()
# Fix motor names to match world file
left_motor = robot.getDevice("left wheel")
right_motor = robot.getDevice("right wheel")
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

# Fix camera name to match world file
camera = robot.getDevice("camera")
camera.enable(TIME_STEP)

# Add touch sensors for obstacle detection
bumper_left = robot.getDevice("bumper_left")
bumper_right = robot.getDevice("bumper_right")
if bumper_left:
    bumper_left.enable(TIME_STEP)
if bumper_right:
    bumper_right.enable(TIME_STEP)

MAX_SPEED = 6.28

# Ball color to detect (e.g., red ball)
target_color = (255, 0, 0)  # RGB

def detect_ball(image):
    if not image:
        return None
    
    width = camera.getWidth()
    height = camera.getHeight()
    red_pixels = []
    
    # Sample fewer pixels for better performance
    step = 4  # Check every 4th pixel
    for x in range(0, width, step):
        for y in range(0, height, step):
            r = Camera.imageGetRed(image, width, x, y)
            g = Camera.imageGetGreen(image, width, x, y)
            b = Camera.imageGetBlue(image, width, x, y)
            if r > 200 and g < 100 and b < 100:  # Detect red
                red_pixels.append(x)
    
    if red_pixels:
        avg_x = sum(red_pixels) / len(red_pixels)
        if avg_x < width / 3:
            return 'left'
        elif avg_x > 2 * width / 3:
            return 'right'
        else:
            return 'center'
    return None

print("Ball follower controller started")

# Main loop
while robot.step(TIME_STEP) != -1:
    image = camera.getImage()
    direction = detect_ball(image)

    # Check for obstacle collision
    bump_left = bumper_left.getValue() if bumper_left else 0
    bump_right = bumper_right.getValue() if bumper_right else 0

    if bump_left > 0 or bump_right > 0:
        print("Obstacle detected! Avoiding...")
        # Avoid obstacle
        left_motor.setVelocity(-0.5 * MAX_SPEED)
        right_motor.setVelocity(-0.5 * MAX_SPEED)
        # Back up for a short time
        for _ in range(10):
            robot.step(TIME_STEP)
        # Turn away from obstacle
        if bump_left > 0:
            left_motor.setVelocity(-0.3 * MAX_SPEED)
            right_motor.setVelocity(0.5 * MAX_SPEED)
        else:
            left_motor.setVelocity(0.5 * MAX_SPEED)
            right_motor.setVelocity(-0.3 * MAX_SPEED)
        # Turn for a short time
        for _ in range(15):
            robot.step(TIME_STEP)
    elif direction == 'left':
        print("Ball detected on left, turning left")
        left_motor.setVelocity(0.3 * MAX_SPEED)
        right_motor.setVelocity(0.6 * MAX_SPEED)
    elif direction == 'right':
        print("Ball detected on right, turning right")
        left_motor.setVelocity(0.6 * MAX_SPEED)
        right_motor.setVelocity(0.3 * MAX_SPEED)
    elif direction == 'center':
        print("Ball detected in center, moving forward")
        left_motor.setVelocity(0.6 * MAX_SPEED)
        right_motor.setVelocity(0.6 * MAX_SPEED)
    else:
        # No ball detected, search by rotating
        left_motor.setVelocity(0.2 * MAX_SPEED)
        right_motor.setVelocity(-0.2 * MAX_SPEED)
