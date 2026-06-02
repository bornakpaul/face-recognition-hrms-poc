import cv2
import numpy as np


def decode_image(image_bytes):

    image_np = np.frombuffer(
        image_bytes,
        np.uint8
    )

    image = cv2.imdecode(
        image_np,
        cv2.IMREAD_COLOR
    )

    return image