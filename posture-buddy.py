import cv2
import time
import math as m
import mediapipe as mp

# =============================CONSTANTS and INITIALIZATIONS=====================================#
# Colors.
red = (50, 50, 255)
green = (127, 255, 0)
light_green = (127, 233, 100)
yellow = (0, 255, 255)
pink = (255, 0, 255)

# Font type.
font = cv2.FONT_HERSHEY_SIMPLEX

# Timer variables
bad_posture_start_time = None
current_posture_state = "GOOD"  # "GOOD" or "BAD"
WARNING_THRESHOLD = 7.0  # seconds
last_warning_time = 0
WARNING_COOLDOWN = 10.0  # seconds between warnings

# Initialize mediapipe pose class.
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Stream settings -> This url should be the same as the one used in the RPi camera command.
stream_url = "tcp://<RASPBERRY_IP>:5000"
# ===============================================================================================#

def sendWarning():
    """
    Function to send alert when bad posture detected for too long.
    Customize this as needed - could play sound, send notification, etc.
    """
    print("NOTE:  POSTURE WARNING! You've had bad posture for too long!")
    # Space for integrtion with notification system, sound alert, etc.


def connect_to_stream(stream_url, max_retries=5):
    for attempt in range(max_retries):
        try:
            print(f"Connecting to stream... (Attempt {attempt + 1}/{max_retries})")
            cap = cv2.VideoCapture(stream_url)
            
            # Test if we can read a frame
            ret, _ = cap.read()
            if ret:
                print("MESSAGE: Successfully connected to stream!")
                return cap
            else:
                cap.release()
                
        except Exception as e:
            print(f"Connection attempt {attempt + 1} failed: {e}")
            
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    print("ERROR_MSG: Failed to connect to stream after all attempts")
    return None

# Calculate distance
def findDistance(x1, y1, x2, y2):
    dist = m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist

# Calculate angle.
def findAngle(x1, y1, x2, y2):
    theta = m.acos((y2 - y1) * (-y1) / (m.sqrt(
        (x2 - x1) ** 2 + (y2 - y1) ** 2) * y1))
    degree = int(180 / m.pi) * theta
    return degree

def main():
    global bad_posture_start_time, current_posture_state, last_warning_time
    
    # Connect to stream
    cap = connect_to_stream(stream_url)
    if cap is None:
        return
    
    consecutive_failures = 0
    max_consecutive_failures = 10
    
    print("Starting real-time posture analysis...")
    print(f"Warning will trigger after {WARNING_THRESHOLD} seconds of bad posture")
    
    while True:
        # Capture frames with error handling
        success, image = cap.read()
        
        if not success:
            consecutive_failures += 1
            print(f"ERROR_MSG: Frame read failed ({consecutive_failures}/{max_consecutive_failures})")
            
            if consecutive_failures >= max_consecutive_failures:
                print("ERROR_MSG: Too many failures, attempting to reconnect...")
                cap.release()
                cap = connect_to_stream(stream_url)
                if cap is None:
                    break
                consecutive_failures = 0
                continue
            else:
                time.sleep(0.1)  # Brief pause before retry
                continue
        
        # Reset failure counter on successful read
        consecutive_failures = 0
        current_time = time.time()
        
        # Get height and width.
        h, w = image.shape[:2]

        # Convert the BGR image to RGB.
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the image.
        keypoints = pose.process(image)

        # Convert the image back to BGR.
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Check if pose landmarks are detected
        if keypoints.pose_landmarks is None:
            cv2.putText(image, 'No pose detected', (50, 50), font, 1, red, 2)
            cv2.imshow('Real-time Posture Analysis', image)
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
            continue

        # Use lm and lmPose as representative of the following methods.
        lm = keypoints.pose_landmarks
        lmPose = mp_pose.PoseLandmark

        try:
            # Acquire the landmark coordinates.
            # Left shoulder.
            l_shldr_x = int(lm.landmark[lmPose.LEFT_SHOULDER].x * w)
            l_shldr_y = int(lm.landmark[lmPose.LEFT_SHOULDER].y * h)
            # Right shoulder
            r_shldr_x = int(lm.landmark[lmPose.RIGHT_SHOULDER].x * w)
            r_shldr_y = int(lm.landmark[lmPose.RIGHT_SHOULDER].y * h)
            # Left ear.
            l_ear_x = int(lm.landmark[lmPose.LEFT_EAR].x * w)
            l_ear_y = int(lm.landmark[lmPose.LEFT_EAR].y * h)
            # Left hip.
            l_hip_x = int(lm.landmark[lmPose.LEFT_HIP].x * w)
            l_hip_y = int(lm.landmark[lmPose.LEFT_HIP].y * h)

            # Calculate distance between left shoulder and right shoulder points.
            offset = findDistance(l_shldr_x, l_shldr_y, r_shldr_x, r_shldr_y)

            # Assist to align the camera to point at the side view of the person.
            if offset < 100:
                cv2.putText(image, str(int(offset)) + ' Aligned', (w - 150, 30), font, 0.5, green, 2)
            else:
                cv2.putText(image, str(int(offset)) + ' Not Aligned', (w - 150, 30), font, 0.5, red, 2)

            # Calculate angles.
            neck_inclination = findAngle(l_shldr_x, l_shldr_y, l_ear_x, l_ear_y)
            torso_inclination = findAngle(l_hip_x, l_hip_y, l_shldr_x, l_shldr_y)

            # Draw landmarks.
            cv2.circle(image, (l_shldr_x, l_shldr_y), 7, yellow, -1)
            cv2.circle(image, (l_ear_x, l_ear_y), 7, yellow, -1)
            cv2.circle(image, (l_shldr_x, l_shldr_y - 100), 7, yellow, -1)
            cv2.circle(image, (r_shldr_x, r_shldr_y), 7, pink, -1)
            cv2.circle(image, (l_hip_x, l_hip_y), 7, yellow, -1)
            cv2.circle(image, (l_hip_x, l_hip_y - 100), 7, yellow, -1)

            # Text string for display.
            angle_text_string = 'Neck : ' + str(int(neck_inclination)) + '  Torso : ' + str(int(torso_inclination))

            # Determine whether good posture or bad posture.
            # !Important: Adjust these thresholds based on your needs.
            is_good_posture = neck_inclination < 33 and torso_inclination < 10
            
            if is_good_posture:
                # Good posture detected
                #if current_posture_state == "BAD":
                    #print("NOTE: Good posture restored!")
                    
                current_posture_state = "GOOD"
                bad_posture_start_time = None  # Reset bad posture timer
                
                cv2.putText(image, angle_text_string, (10, 30), font, 0.5, light_green, 2)
                cv2.putText(image, str(int(neck_inclination)), (l_shldr_x + 10, l_shldr_y), font, 0.5, light_green, 2)
                cv2.putText(image, str(int(torso_inclination)), (l_hip_x + 10, l_hip_y), font, 0.5, light_green, 2)

                # Join landmarks in green
                cv2.line(image, (l_shldr_x, l_shldr_y), (l_ear_x, l_ear_y), green, 4)
                cv2.line(image, (l_shldr_x, l_shldr_y), (l_shldr_x, l_shldr_y - 100), green, 4)
                cv2.line(image, (l_hip_x, l_hip_y), (l_shldr_x, l_shldr_y), green, 4)
                cv2.line(image, (l_hip_x, l_hip_y), (l_hip_x, l_hip_y - 100), green, 4)
                
                # Display good posture message
                cv2.putText(image, 'Good Posture ✓', (10, h - 20), font, 0.5, green, 2)

            else:
                # Bad posture detected
                if current_posture_state == "GOOD":
                    #print("NOTE: Bad posture detected - timer started")
                    bad_posture_start_time = current_time
                    
                current_posture_state = "BAD"
                
                # Calculate how long we've been in bad posture
                bad_posture_duration = current_time - bad_posture_start_time
                
                cv2.putText(image, angle_text_string, (10, 30), font, 0.5, red, 2)
                cv2.putText(image, str(int(neck_inclination)), (l_shldr_x + 10, l_shldr_y), font, 0.5, red, 2)
                cv2.putText(image, str(int(torso_inclination)), (l_hip_x + 10, l_hip_y), font, 0.5, red, 2)

                # Join landmarks in red
                cv2.line(image, (l_shldr_x, l_shldr_y), (l_ear_x, l_ear_y), red, 4)
                cv2.line(image, (l_shldr_x, l_shldr_y), (l_shldr_x, l_shldr_y - 100), red, 4)
                cv2.line(image, (l_hip_x, l_hip_y), (l_shldr_x, l_shldr_y), red, 4)
                cv2.line(image, (l_hip_x, l_hip_y), (l_hip_x, l_hip_y - 100), red, 4)
                
                # Display bad posture time
                time_remaining = max(0, WARNING_THRESHOLD - bad_posture_duration)
                if time_remaining > 0:
                    time_string = f'Bad Posture: {bad_posture_duration:.1f}s (Warning in {time_remaining:.1f}s)'
                    cv2.putText(image, time_string, (10, h - 20), font, 0.6, red, 2)
                else:
                    cv2.putText(image, f'BAD POSTURE WARNING! {bad_posture_duration:.1f}s', (10, h - 20), font, 0.6, red, 2)
                
                # Check if we need to send warning
                if bad_posture_duration >= WARNING_THRESHOLD:
                    # Only send warning if cooldown period has passed
                    if current_time - last_warning_time >= WARNING_COOLDOWN:
                        sendWarning()
                        last_warning_time = current_time

        except Exception as e:
            print(f"Error processing pose landmarks: {e}")
            cv2.putText(image, 'Error processing pose', (50, 50), font, 1, red, 2)

        # Display connection status
        cv2.putText(image, 'LIVE', (w - 60, h - 10), font, 0.7, green, 2)
        
        # Display the image
        cv2.imshow('PostureBoyV2', image)
        
        # Break on 'q' key press
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("MESSAGE: Posture analysis ended")


if __name__ == "__main__":
    main()
