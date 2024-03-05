import random

from PIL import Image, ImageDraw, ImageFont
import matplotlib.font_manager as fm


def generate_solution_img(pzl, path, selected_font, fontsize, gridline_thicknes, rand, padding=10):
    pzl_size_width = len(pzl[0])
    pzl_size_height = len(pzl)

    # Define box width and height
    box_width, box_height = 400, 400
    if pzl_size_height >= 6:
        font_size = box_width * (fontsize / 100) + 20
    else:
        font_size = box_width * (fontsize / 100) + 80

    # Calculate image width and height based on puzzle size and box dimensions, including padding on all sides
    width = pzl_size_width * box_width + 2 * padding
    height = pzl_size_height * box_height + 2 * padding

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    prop = fm.FontProperties(fname=fm.findfont(fm.FontProperties(family=selected_font)))
    selected_font_path = prop.get_file()
    font = ImageFont.truetype(selected_font_path, font_size)

    outer_border_coords = [padding - (gridline_thicknes + 2), padding - (gridline_thicknes + 2),
                           width - padding + (gridline_thicknes + 2), height - padding + (gridline_thicknes + 2)]
    draw.rectangle(outer_border_coords, outline="#000", width=gridline_thicknes + 2)


    # Render the puzzle data onto the image with padding
    for row_idx, row in enumerate(pzl):
        for col_idx, item in enumerate(row):
            x = col_idx * box_width + padding
            y = row_idx * box_height + padding
            box_coords = [x, y, x + box_width, y + box_height]

            # Draw the box
            if isinstance(item, int):
                draw.rectangle(box_coords, outline="#000", width=gridline_thicknes+2)
            else:
                draw.rectangle(box_coords, outline="#000", fill="#fff", width=gridline_thicknes+2)

            # Draw the text
            text = str(item)
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] + text_bbox[1] - pzl_size_height
            text_x = x + (box_width - text_width) / 2
            text_y = y + (box_height - text_height) / 2
            if isinstance(item, int):
                draw.text((text_x, text_y), text, fill="#aaa", font=font)
            else:
                draw.text((text_x, text_y), text, fill="black", font=font)

    # Save the generated image
    image.save(f"{path}/Solution_{rand}.png", dpi=(300, 300))


def generate_puzzle_img(pzl, path, selected_font, fontsize, gridline_thicknes, rand, padding=10):
    pzl_size_width = len(pzl[0])
    pzl_size_height = len(pzl)

    box_width, box_height = 400, 400
    if pzl_size_height >= 6:
        font_size = box_width * (fontsize / 100) + 20
    else:
        font_size = box_width * (fontsize/100) + 80

    width = pzl_size_width * box_width + 2 * padding
    height = pzl_size_height * box_height + 2 * padding

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    prop = fm.FontProperties(fname=fm.findfont(fm.FontProperties(family=selected_font)))
    selected_font_path = prop.get_file()
    font = ImageFont.truetype(selected_font_path, font_size)

    outer_border_coords = [padding - (gridline_thicknes + 2), padding - (gridline_thicknes + 2),
                           width - padding + (gridline_thicknes + 2), height - padding + (gridline_thicknes + 2)]
    draw.rectangle(outer_border_coords, outline="#000", width=gridline_thicknes + 2)

    # Render the puzzle data onto the image
    for row_idx, row in enumerate(pzl):
        for col_idx, item in enumerate(row):
            x = col_idx * box_width + padding
            y = row_idx * box_height + padding
            box_coords = [x, y, x + box_width, y + box_height]

            # Draw the box
            if isinstance(item, str):
                draw.rectangle(box_coords, outline="#000", width=gridline_thicknes+2)
            else:
                draw.rectangle(box_coords, outline="#000", width=gridline_thicknes+2)

            # Draw the text
            text = str(item)
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] + text_bbox[1] - pzl_size_height
            text_x = x + (box_width - text_width) / 2
            text_y = y + (box_height - text_height) / 2
            if isinstance(item, str):
                pass
            else:
                draw.text((text_x, text_y), text, fill="black", font=font)
                
    # Save the generated image
    image.save(f"{path}/Puzzle_{rand}.png", dpi=(300, 300))

