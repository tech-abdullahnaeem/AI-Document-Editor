#!/usr/bin/env python3
"""
Apply comprehensive table transformation to abdullah.tex
"""

import re

def analyze_table_content(table_content):
    """Analyze table content to determine optimal column widths"""
    
    # Extract table rows
    rows = []
    lines = table_content.split('\n')
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('\\') and '&' in line:
            # Split by & and clean up
            cells = [cell.strip() for cell in line.split('&')]
            if len(cells) > 1:  # Valid row
                rows.append(cells)
    
    if not rows:
        return []
    
    num_cols = len(rows[0])
    max_lengths = [0] * num_cols
    
    # Calculate maximum content length for each column
    for row in rows:
        for i, cell in enumerate(row):
            if i < num_cols:
                # Remove LaTeX commands and get clean text length
                clean_cell = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', cell)
                clean_cell = re.sub(r'\\[a-zA-Z]+', '', clean_cell)
                clean_cell = clean_cell.replace('\\\\', '').strip()
                max_lengths[i] = max(max_lengths[i], len(clean_cell))
    
    # Convert to cm with dynamic bounds but scale to fit page
    char_to_cm = 0.09  # Reduced from 0.11
    min_width = 0.8    # Reduced minimum
    
    # Calculate initial widths
    initial_widths = []
    for length in max_lengths:
        width = max(min_width, length * char_to_cm + 0.2)  # Reduced padding
        initial_widths.append(width)
    
    # Scale to fit within page (target ~10cm for content + borders)
    target_width = 9.5  # Leave room for borders and positioning
    total_initial = sum(initial_widths)
    
    if total_initial > target_width:
        scale_factor = target_width / total_initial
        column_widths = [max(min_width, w * scale_factor) for w in initial_widths]
    else:
        column_widths = initial_widths
    
    # Round to 1 decimal place
    column_widths = [round(w, 1) for w in column_widths]
    
    return column_widths

def calculate_positioning(total_width, page_width=10.8):
    """Calculate optimal positioning for table"""
    if total_width <= page_width:
        return 0  # No positioning needed
    
    # Calculate left shift needed (up to 2.5cm maximum)
    overflow = total_width - page_width
    shift = min(overflow * 0.7, 2.5)  # 70% of overflow, max 2.5cm
    return round(shift, 1)

def transform_table(content):
    """Apply comprehensive table transformation"""
    
    # Find the table
    table_pattern = r'(\\begin\{table\}.*?\\end\{table\})'
    table_match = re.search(table_pattern, content, re.DOTALL)
    
    if not table_match:
        print("No table found")
        return content
    
    table = table_match.group(1)
    print("Original table found")
    
    # Analyze table content for optimal widths
    column_widths = analyze_table_content(table)
    
    if not column_widths:
        print("Could not analyze table content")
        return content
    
    print(f"Calculated column widths: {column_widths}")
    
    # Calculate total width
    total_width = sum(column_widths) + 0.2 * (len(column_widths) + 1)  # borders
    print(f"Total table width: {total_width:.1f}cm")
    
    # Calculate positioning
    left_shift = calculate_positioning(total_width)
    print(f"Left positioning: {left_shift}cm")
    
    # Generate column specification
    col_spec = '|' + '|'.join([f'p{{{w}cm}}' for w in column_widths]) + '|'
    print(f"New column spec: {col_spec}")
    
    # Transform the table
    new_table = table
    
    # 1. Fix table placement
    new_table = re.sub(r'\\begin\{table\}\[h\]', r'\\begin{table}[!htbp]', new_table)
    
    # 2. Replace center with centering
    new_table = re.sub(r'\\begin\{center\}', r'\\centering', new_table)
    new_table = re.sub(r'\\end\{center\}', r'', new_table)
    
    # 3. Add label if missing
    if '\\label{' not in new_table:
        caption_match = re.search(r'(\\caption\{[^}]+\})', new_table)
        if caption_match:
            caption = caption_match.group(1)
            new_table = new_table.replace(caption, caption + '\n\\label{tab:table_i_literature_survey_summ}')
    
    # 4. Add positioning if needed
    if left_shift > 0:
        centering_pos = new_table.find('\\centering')
        if centering_pos != -1:
            insert_pos = new_table.find('\n', centering_pos) + 1
            new_table = new_table[:insert_pos] + f'\\hspace*{{-{left_shift}cm}}\n' + new_table[insert_pos:]
    
    # 5. Replace column specification
    tabular_match = re.search(r'\\begin\{tabular\}\{([^}]+)\}', new_table)
    if tabular_match:
        old_spec = tabular_match.group(1)
        new_table = new_table.replace(f'\\begin{{tabular}}{{{old_spec}}}', f'\\begin{{tabular}}{{{col_spec}}}')
    
    # Replace in content
    new_content = content.replace(table, new_table)
    
    print("\\nTable transformation completed!")
    return new_content

# Main execution
if __name__ == "__main__":
    # Read original file
    input_file = "/Users/abdullah/Desktop/Techinoid/Document agent-tagged copy 2/final research paper/abdullah.tex"
    output_file = "/Users/abdullah/Desktop/Techinoid/Document agent-tagged copy 2/Rag latex fixer/output/abdullah_fixed_table.tex"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Transform table
    transformed_content = transform_table(content)
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(transformed_content)
    
    print(f"Fixed document saved to: {output_file}")