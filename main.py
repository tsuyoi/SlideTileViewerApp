import cv2
import matplotlib.pyplot as plt
import numpy as np


def count_cicles(path, min_area=5, max_area=100):
    img = cv2.imread(path)
    mask = cv2.threshold(img[:, :, 0], 255, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    stats = cv2.connectedComponentsWithStats(mask, 8)[2]
    label_area = stats[1:, cv2.CC_STAT_AREA]
    singular_mask = (min_area < label_area) & (label_area <= max_area)
    return np.sum(singular_mask == True)


def flood_fill_centers(path, seed_pt, min_area, max_area, thresh_method, print_every):
    img = cv2.imread(path, 0)
    fill_color = 0
    mask = np.zeros_like(img)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    for th in range(min_area, max_area):
        prev_mask = mask.copy()
        mask = cv2.threshold(img, th, 255, thresh_method)[1]
        if (th % print_every) == 0:
            fig, axs = plt.subplots(2, 2)
            axs[0, 0].imshow(mask)
        mask = cv2.floodFill(mask, None, seed_pt, fill_color)[1]
        if (th % print_every) == 0:
            axs[1, 0].imshow(mask)
        mask = cv2.bitwise_or(mask, prev_mask)
        if (th % print_every) == 0:
            axs[0, 1].imshow(mask)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        if (th % print_every) == 0:
            axs[1, 1].imshow(mask)
            plt.show()
    return cv2.connectedComponents(mask)[0] - 1

print(f"There are {count_cicles('images/circles.jpg')} and {flood_fill_centers('images/circles.jpg', (50, 50), 100, 150, cv2.THRESH_BINARY_INV, 1000)} in circles.jpg")
print(f"There are {count_cicles('images/source/masks/tile-4-mask.jpg')} and {flood_fill_centers('images/source/masks/tile-4-mask.jpg', (50, 50), 100, 150, cv2.THRESH_BINARY_INV, 1000)} in tile-4-mask.jpg")
print(f"There are {count_cicles('images/circles.png', 50, 350)} and {flood_fill_centers('images/circles.png', (25, 25), 60, 120, cv2.THRESH_BINARY, 1000)} in circles.png")
