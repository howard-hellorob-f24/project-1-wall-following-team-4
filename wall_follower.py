import time
import numpy as np
from mbot_bridge.api import MBot


def find_min_dist(ranges, thetas):
    """Finds the length and angle of the minimum ray in the scan.

    Args:
        ranges (list): The length of each ray in the Lidar scan.
        thetas (list): The angle of each ray in the Lidar scan.

    Returns:
        tuple: The length and angle of the shortest ray in the Lidar scan.
    """
    valid_ranges = np.array(ranges)
    valid_thetas = np.array(thetas)

    valid_index = (valid_ranges > 0).nonzero()[0]
    if len(valid_index) == 0:
        return None, None

    min_index = valid_ranges[valid_index].argmin()
    min_dist = valid_ranges[valid_index][min_index]
    min_angle = valid_thetas[valid_index][min_index]

    return min_dist, min_angle


def cross_product(v1, v2):
    """Compute the Cross Product between two vectors.

    Args:
        v1 (list): First vector of length 3.
        v2 (list): Second vector of length 3.

    Returns:
        list: The result of the cross product operation.
    """
    res = np.zeros(3)
    res[0] = v1[1] * v2[2] - v1[2] * v2[1]
    res[1] = v1[2] * v2[0] - v1[0] * v2[2]
    res[2] = v1[0] * v2[1] - v1[1] * v2[0]
    return res


# Initialize the robot and parameters
robot = MBot()
setpoint = .5  # Desired distance from the wall, adjust as needed.
tolerance = 0.1  # Acceptable range around setpoint
approach_speed = 1  # Forward speed when approaching the wall
turn_speed = 0.3  # Turning speed for alignment

try:
    while True:
        # Step 1: Get Lidar data and find the closest wall
        ranges, thetas = robot.read_lidar()
        min_dist, min_angle = find_min_dist(ranges, thetas)

        if min_dist is None or min_angle is None:
            print("No valid wall detected.")
            continue

        print(f"Distance to wall: {min_dist}, Angle to wall: {min_angle}")

        if min_dist > setpoint + tolerance:
            # Step 2: Move toward the wall if too far away
            x_velocity = approach_speed
            y_velocity = 0
            angular_velocity = 0
            print("Moving toward the wall.")
            robot.drive(x_velocity,y_velocity,angular_velocity)
            time.sleep(1)

        
        else:
            # Step 3: If close enough to the wall, align parallel
            x_velocity = 0  # Stop forward movement
            y_velocity = 0
            print("stopping")
            robot.drive(0,0,0)
            time.sleep(1)
            if min_angle > 0:
                print(min_angle)
                angular_velocity = -turn_speed  # Turn left
                print("turning left")
                robot.drive(x_velocity,y_velocity,-1.57)
                
                time.sleep(1)
                robot.drive(1,0,0)
                time.sleep(.5)
            else:
                print(min_angle)
                angular_velocity = turn_speed  # Turn right
                print("turning right")
                robot.drive(x_velocity,y_velocity,1.57)
                robot.drive(1,0,0)
                time.sleep(.5)
                time.sleep(1)
            print("Turning to align parallel to the wall.")


       

        # Drive the robot with the specified x, y, and angular velocities
        #robot.drive(x_velocity, y_velocity, angular_velocity)

        # Small delay to avoid overloading the robot with commands
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Control+C pressed. Stopping the robot.")
    robot.stop()
