
def generate_solution_svg(pzl, path, selected_font, fontsize, gridline_thicknes, rand, vertical_alignment, padding=10):
    pzl_size_width = len(pzl[0])
    pzl_size_height = len(pzl)

    if pzl_size_height >= 7:
        font_size = fontsize
    else:
        font_size = fontsize + 20
    box_size = 100

    # Calculate the adjusted width and height including padding
    width = int(pzl_size_width * box_size) + 2 * padding
    height = int(pzl_size_height * box_size) + 2 * padding

    svg_content = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid meet">\n'

    for row_idx, row in enumerate(pzl):
        for col_idx, item in enumerate(row):
            # Calculate adjusted x and y positions with padding
            x = col_idx * box_size + padding + box_size / 2
            y = row_idx * box_size + padding + box_size / float(vertical_alignment)

            svg_content += f'<rect x="{col_idx * box_size + padding}" y="{row_idx * box_size + padding}" width="{box_size}" height="{box_size}" stroke="#000" fill="#fff" stroke-width="{gridline_thicknes}"/>\n'
            text = str(item)
            if isinstance(item, str):
                svg_content += f'<text x="{x}" y="{y}" font-family="{selected_font}" font-size="{font_size}" fill="black" text-anchor="middle" dominant-baseline="middle">'
            else:
                svg_content += f'<text x="{x}" y="{y}" font-family="{selected_font}" font-size="{font_size}" fill="#aaa" text-anchor="middle" dominant-baseline="middle">'
            svg_content += f'<tspan x="{x}" dy="0.35em">{text}</tspan>'
            svg_content += '</text>\n'

    svg_content += '</svg>'

    with open(f"{path}/Solution_{rand}.svg", "w") as svg_file:
        svg_file.write(svg_content)


def generate_puzzle_svg(pzl, path, selected_font, fontsize, gridline_thicknes, rand, vertical_alignment, padding=10):
    pzl_size_width = len(pzl[0])
    pzl_size_height = len(pzl)

    if pzl_size_height >= 7:
        font_size = fontsize
    else:
        font_size = fontsize + 20
    box_size = 100
    if len(pzl) >= 8:
        box_size = 110

    width = int(pzl_size_width * box_size) + 2 * padding
    height = int(pzl_size_height * box_size) + 2 * padding

    svg_content = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid meet">\n'

    for row_idx, row in enumerate(pzl):
        for col_idx, item in enumerate(row):
            x = col_idx * box_size + padding + box_size / 2
            y = row_idx * box_size + padding + box_size / float(vertical_alignment)

            if isinstance(item, str):
                svg_content += f'<rect x="{col_idx * box_size + padding}" y="{row_idx * box_size + padding}" width="{box_size}" height="{box_size}" stroke="black" fill="#fff" stroke-width="{gridline_thicknes}"/>\n'
            else:
                svg_content += f'<rect x="{col_idx * box_size + padding}" y="{row_idx * box_size + padding}" width="{box_size}" height="{box_size}" stroke="#000" fill="#fff" stroke-width="{gridline_thicknes}"/>\n'
                text = str(item)
                svg_content += f'<text x="{x}" y="{y}" font-family="{selected_font}" font-size="{font_size}" fill="black" text-anchor="middle" dominant-baseline="middle">'
                svg_content += f'<tspan x="{x}" dy="0.35em">{text}</tspan>'
                svg_content += '</text>\n'

    svg_content += '</svg>'

    with open(f"{path}/Puzzle_{rand}.svg", "w") as svg_file:
        svg_file.write(svg_content)
