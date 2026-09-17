import cv2

def preprocess_frame(frame, blur_kernel=(5, 5)):
    """
    Prepares a raw video frame for background subtraction.
    Steps: grayscale conversion -> Gaussian blur (noise reduction).
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, blur_kernel, 0)
    return blurred


def clean_mask(mask, kernel_size=(5, 5)):
    """
    Removes small noise from the foreground mask using morphological operations.
    Erosion removes small white noise specks; dilation restores object size.
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, kernel_size)
    eroded = cv2.erode(mask, kernel, iterations=1)
    dilated = cv2.dilate(eroded, kernel, iterations=2)
    return dilated