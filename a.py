import re

def fix_latex_table_generic(latex_code: str) -> str:
    """
    Generic LaTeX table fixer using a simple approach:
    1. Detect actual number of columns from table data
    2. Replace corrupted column spec with clean |p{width}| format
    3. Wrap tables with adjustbox for automatic scaling

    Args:
        latex_code: A string containing the potentially corrupted LaTeX table.

    Returns:
        A string with the corrected LaTeX code.
    """
    # 1. Fix common typos like 'egin' -> 'begin'
    corrected_code = re.sub(r'\\egin{', r'\\begin{', latex_code)
    print("✅ Checked for and corrected 'egin' typos.")

    def detect_table_columns(table_content):
        """Detect actual number of columns by analyzing table data rows"""
        max_cols = 0
        
        # Find table data rows (lines with &)
        lines = table_content.split('\n')
        for line in lines:
            # Skip LaTeX commands and empty lines
            if ('&' in line and 
                not line.strip().startswith('%') and 
                '\\hline' not in line and
                '\\cline' not in line and
                '\\end{table' not in line):
                
                # Count columns, accounting for multicolumn
                base_cols = line.count('&') + 1
                
                # Adjust for multicolumn spans
                multicolumn_matches = re.findall(r'\\multicolumn\{(\d+)\}', line)
                extra_cols = sum(int(span) - 1 for span in multicolumn_matches)
                
                total_cols = base_cols + extra_cols
                max_cols = max(max_cols, total_cols)
        
        # Default to 3 if no data found
        return max_cols if max_cols > 0 else 3

    def calculate_column_width(num_cols):
        """Calculate appropriate column width based on number of columns"""
        if num_cols <= 2:
            return "6cm"
        elif num_cols == 3:
            return "4cm" 
        elif num_cols == 4:
            return "3cm"
        elif num_cols == 5:
            return "2.5cm"
        else:
            return "2cm"
    
    def fix_table_tabular(match):
        """Fix a single table's tabular definition and add adjustbox"""
        full_table = match.group(0)
        print(f"🔍 Processing table: '{full_table[:100]}...'")
        
        # Detect actual columns from this specific table's data
        num_cols = detect_table_columns(full_table)
        print(f"� Detected {num_cols} columns in this table")
        
        # Calculate appropriate column width
        width = calculate_column_width(num_cols)
        
        # Generate clean column specification: |p{width}|p{width}|...|
        new_spec = '|' + '|'.join([f'p{{{width}}}'] * num_cols) + '|'
        print(f"✅ Generated clean spec: '{new_spec}'")
        
        # Replace the corrupted tabular definition with clean one
        # Find and replace any tabular line in this table (including corrupted ones)
        fixed_table = re.sub(
            r'\\begin\{tabular\}\{[^}]*\}[^\n\\]*',
            f'\\\\begin{{tabular}}{{{new_spec}}}',
            full_table
        )
        
        # Remove any existing adjustbox around tabular
        fixed_table = re.sub(r'\\begin\{adjustbox\}\{max width=\\textwidth\}\s*', '', fixed_table)
        fixed_table = re.sub(r'\\end\{adjustbox\}', '', fixed_table)
        
        # Wrap the tabular with adjustbox for automatic scaling
        fixed_table = re.sub(
            r'(\\begin\{tabular\}.*\\end\{tabular\})',
            r'\\begin{adjustbox}{max width=\\textwidth}\n\1\n\\end{adjustbox}',
            fixed_table,
            flags=re.DOTALL
        )
        
        return fixed_table
    
    # Process each table individually (table, table*, etc.)
    table_pattern = r'\\begin\{table[*]?\}.*?\\end\{table[*]?\}'
    corrected_code = re.sub(table_pattern, fix_table_tabular, corrected_code, flags=re.DOTALL)
    
    print("✅ Successfully processed all tables with generic column detection and adjustbox wrapping.")
    return corrected_code

if __name__ == "__main__":
    # --- Read the LaTeX file to fix ---
    file_path = '/Users/abdullah/Desktop/Techinoid/final with fast api/pdf_conversion_output/converted_latex.tex'

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            corrupted_latex = f.read()
        print(f"✅ Successfully read the LaTeX file: {file_path}")
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        exit(1)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        exit(1)

    # --- Run the generic fix ---
    fixed_code = fix_latex_table_generic(corrupted_latex)

    # --- Save the fixed code back to the file ---
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_code)
        print(f"✅ Successfully saved the fixed LaTeX code back to: {file_path}")
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        exit(1)

    # --- Print the result ---
    print("\n--- 🛠️ FINAL CORRECTED CODE ---")
    print(fixed_code)