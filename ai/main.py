# Image Processing
import cv2  # OpenCV for image manipulation
import numpy as np  # Numerical operations

# Neural Network
import torch  # For using PyTorch

# Visualization (optional for showing results)
import matplotlib.pyplot as plt  # For visualizing the grid and results

# File Handling and Utilities
import os  # For file path operations


class ImageProcessor:
    def __init__(self):
        self.model = torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.model.eval()

    def preprocess_image(self, image_paths):
        # Load and preprocess the image
        image = cv2.imread(image_paths)
        if image is None:
            raise ValueError(f"Image not found or unable to read: {image_paths}")

        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # Resize image to the expected input size for YOLOv5
        image_resized = cv2.resize(image_rgb, (640, 640))

        # Convert image to a tensor
        image_tensor = (
            torch.from_numpy(image_resized).float() / 255.0
        )  # Normalize to [0, 1]
        image_tensor = image_tensor.permute(2, 0, 1).unsqueeze(
            0
        )  # Change to (1, C, H, W)

        # Move the tensor to the appropriate device
        image_tensor = image_tensor.to(self.device)

        # Run the model
        result = self.model(image_tensor)

        return result

    @staticmethod
    def postprocess_image(result):
        # Render results on the original image
        image = result.render()[0]
        cv2.imshow(
            "Sudoku Solver", cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        )  # Convert back to BGR for OpenCV
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def run(self, image_paths):
        answer = self.preprocess_image(image_paths)
        self.postprocess_image(answer)

        return answer


if __name__ == "__main__":
    image_processor = ImageProcessor()
    image_path = "sudoku.png"
    try:
        results = image_processor.run(image_path)
    except Exception as e:
        print(f"An error occurred: {e}")
