#!/usr/bin/env python3
import rospy
import cv2
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo
import tf2_ros
import geometry_msgs.msg

def publish_static_tf():
    # Create a static transform broadcaster
    static_broadcaster = tf2_ros.StaticTransformBroadcaster()
    static_tf = geometry_msgs.msg.TransformStamped()
    static_tf.header.stamp = rospy.Time.now()
    static_tf.header.frame_id = "frontleft_fisheye"       # original frame
    static_tf.child_frame_id = "frontleft_fisheye_upright"  # desired upright frame
    
    # No translation:
    static_tf.transform.translation.x = 0.0
    static_tf.transform.translation.y = 0.0
    static_tf.transform.translation.z = 0.0
    
    # Use the inverse of the camera's known rotation if needed.
    # Here, as an example, we use the quaternion provided:
    static_tf.transform.rotation.x = -0.136
    static_tf.transform.rotation.y = -0.811
    static_tf.transform.rotation.z = 0.223
    static_tf.transform.rotation.w = 0.523
    
    # Broadcast once (static transform persists)
    static_broadcaster.sendTransform([static_tf])
    rospy.loginfo("Static transform published: %s -> %s", 
                  static_tf.header.frame_id, static_tf.child_frame_id)

def image_callback(msg):
    cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
    # Rotate the image (90 degrees clockwise in this example)
    rotated = cv2.rotate(cv_image, cv2.ROTATE_90_CLOCKWISE)
    out_msg = bridge.cv2_to_imgmsg(rotated, encoding="bgr8")
    out_msg.header = msg.header
    # Update frame_id to match our corrected frame
    out_msg.header.frame_id = "frontleft_fisheye_upright"
    image_pub.publish(out_msg)

def camera_info_callback(msg):
    msg.header.frame_id = "frontleft_fisheye_upright"
    caminfo_pub.publish(msg)

if __name__ == '__main__':
    rospy.init_node('combined_camera_processor')
    bridge = CvBridge()

    # Start static transform publisher
    publish_static_tf()

    # Publishers
    image_pub = rospy.Publisher('/spot/camera/frontleft/image_upright', Image, queue_size=1)
    caminfo_pub = rospy.Publisher('/spot/camera/frontleft/camera_info_upright', CameraInfo, queue_size=1)

    # Subscribers
    rospy.Subscriber('/spot/camera/frontleft/image', Image, image_callback, queue_size=1)
    rospy.Subscriber('/spot/camera/frontleft/camera_info', CameraInfo, camera_info_callback, queue_size=1)

    rospy.spin()