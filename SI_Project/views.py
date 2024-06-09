import numpy as np
from PIL import Image, ImageDraw
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import torch
from torchvision import transforms, models

# Define data transformations
data_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

# Load the classification model
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
classification_model = models.resnet18(weights=None)
num_ftrs = classification_model.fc.in_features
classification_model.fc = torch.nn.Linear(num_ftrs, 25)  # Assuming 25 classes
classification_model.load_state_dict(
    torch.load(os.path.join(os.path.dirname(__file__), '..', 'model.pth'), map_location=device), strict=False)
classification_model = classification_model.to(device)
classification_model.eval()

# Load the segmentation models with two classes each
def load_segmentation_model(model_path, num_classes):
    model = models.segmentation.deeplabv3_resnet50(weights=None, num_classes=num_classes)
    state_dict = torch.load(model_path, map_location=device)

    # Update state_dict to handle different number of classes
    if state_dict['classifier.4.weight'].shape[0] != num_classes:
        state_dict['classifier.4.weight'] = state_dict['classifier.4.weight'].repeat(num_classes, 1, 1, 1)
        state_dict['classifier.4.bias'] = state_dict['classifier.4.bias'].repeat(num_classes)

    model.load_state_dict(state_dict, strict=False)
    return model.to(device)

segmentation_model_hud = load_segmentation_model(os.path.join(os.path.dirname(__file__), 'segmentation_model_huds.pth'), 1)
segmentation_model_hud.eval()

segmentation_model_mobs = load_segmentation_model(os.path.join(os.path.dirname(__file__), 'segmentation_model_mobs.pth'), 1)
segmentation_model_mobs.eval()

# Game names list
game_names = [
    'Among Us', 'Apex Legends', 'Assassins Creed Black Flag', 'Cyberpunk 2077', 'Darksiders 2', 'Doom Eternal',
    'Elden Ring', 'Far Cry 5', 'Fortnite', 'Forza Horizon', 'Free Fire', 'GTA San Andreas', 'Genshin Impact',
    'Ghost of Tsushima', 'God of War', 'Grand Theft Auto V', 'Half-Life 2', 'League of Legends', 'Minecraft',
    'Red Dead Redemption', 'Roblox', 'Terraria', 'The Binding of Isaac', 'Undertale', 'Valheim'
]

def home(request):
    return render(request, 'index.html')

def classify_page(request):
    return render(request, 'classify.html')

def segment_page(request):
    return render(request, 'segment.html')

def classify_image(image_path):
    image = Image.open(image_path).convert('RGB')
    image = data_transforms(image).unsqueeze(0).to(device)
    with torch.no_grad():
        outputs = classification_model(image)
        _, preds = torch.max(outputs, 1)
    return preds.item()

def segment_image(image_path, model):
    image = Image.open(image_path).convert('RGB')
    original_size = image.size  # Store original size for resizing later
    image = data_transforms(image).unsqueeze(0).to(device)
    with torch.no_grad():
        outputs = model(image)['out']
        masks = torch.sigmoid(outputs).cpu().numpy()[0, 0]  # Select the first channel and remove extra dimension
    return masks, original_size

def save_mask_image(mask, original_size, file_path, colormap):
    # Resize the mask to the original size
    mask_img = Image.fromarray((mask * 255).astype(np.uint8)).resize(original_size)
    mask_img = mask_img.convert("RGBA")

    mask_array = np.array(mask_img)
    colored_mask = np.zeros((mask_array.shape[0], mask_array.shape[1], 4), dtype=np.uint8)

    # Apply colormap to the mask
    indices = mask_array[..., 3] > 0  # Assuming the alpha channel is at the 4th position
    colored_mask[indices] = colormap

    colored_mask_img = Image.fromarray(colored_mask)
    mask_img_path = file_path.replace(".png", "_mask.png")
    colored_mask_img.save(mask_img_path)
    return mask_img_path

def overlay_masks(image_path, masks_hud, masks_mobs, original_size):
    img = Image.open(image_path).convert("RGBA")
    mask_hud = (masks_hud * 255).astype(np.uint8)
    mask_mobs = (masks_mobs * 255).astype(np.uint8)

    mask_img_hud = Image.fromarray(mask_hud).resize(original_size)
    mask_img_mobs = Image.fromarray(mask_mobs).resize(original_size)

    overlay_hud = Image.new("RGBA", img.size)
    overlay_mobs = Image.new("RGBA", img.size)
    draw_hud = ImageDraw.Draw(overlay_hud)
    draw_mobs = ImageDraw.Draw(overlay_mobs)

    for y in range(img.height):
        for x in range(img.width):
            if mask_img_mobs.getpixel((x, y)) > 0 and mask_img_hud.getpixel((x, y)) > 0:
                overlay_mobs.putpixel((x, y), (255, 0, 255, 128))
            elif mask_img_hud.getpixel((x, y)) > 0:
                overlay_hud.putpixel((x, y), (0, 0, 255, 128))  # Transparent blue for HUD
            elif mask_img_mobs.getpixel((x, y)) > 0.1:
                overlay_mobs.putpixel((x, y), (255, 0, 0, 128))  # Transparent red for mobs
    blended = Image.alpha_composite(img, overlay_hud)
    blended = Image.alpha_composite(blended, overlay_mobs)

    return blended

@csrf_exempt
def upload_and_classify(request):
    if request.method == 'POST' and 'file' in request.FILES:
        file = request.FILES['file']
        file_name = default_storage.save(file.name, ContentFile(file.read()))
        file_path = default_storage.path(file_name)

        class_result = classify_image(file_path)
        game_name = game_names[class_result]

        # Generate a URL for the uploaded file
        file_url = default_storage.url(file_name)

        return render(request, 'classify_result.html', {'game_name': game_name, 'file_url': file_url})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def upload_and_segment(request):
    if request.method == 'POST' and 'file' in request.FILES:
        file = request.FILES['file']
        file_name = default_storage.save(file.name, ContentFile(file.read()))
        file_path = default_storage.path(file_name)

        masks_hud, original_size = segment_image(file_path, segmentation_model_hud)
        masks_mobs, _ = segment_image(file_path, segmentation_model_mobs)
        overlay_image = overlay_masks(file_path, masks_hud, masks_mobs, original_size)

        overlay_image_path = file_path.replace(".png", "_overlay.png")
        overlay_image.save(overlay_image_path)

        hud_mask_path = save_mask_image(masks_hud, original_size, file_path.replace(".png", "_hud.png"), (0, 0, 255, 255))
        mobs_mask_path = save_mask_image(masks_mobs, original_size, file_path.replace(".png", "_mobs.png"), (255, 0, 0, 255))

        os.remove(file_path)  # Clean up after processing

        # Generate URLs for the images
        overlay_image_url = default_storage.url(overlay_image_path)
        hud_mask_url = default_storage.url(hud_mask_path)
        mobs_mask_url = default_storage.url(mobs_mask_path)

        return render(request, 'segment_result.html', {'file_url': overlay_image_url, 'hud_mask_url': hud_mask_url, 'mobs_mask_url': mobs_mask_url})
    return JsonResponse({'error': 'Invalid request'}, status=400)
