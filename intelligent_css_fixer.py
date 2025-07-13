#!/usr/bin/env python3
"""
INTELLIGENT CSS FIXER
Corrige solo errores reales de CSS, no falsos positivos
"""

import os
import re

def intelligent_css_fixer():
    """Corrige errores reales de CSS de manera inteligente."""
    print("🎨 INTELLIGENT CSS FIXER")
    print("=" * 50)
    
    css_file = 'web_app/static/css/main.css'
    
    if not os.path.exists(css_file):
        print(f"❌ File not found: {css_file}")
        return
    
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    lines = content.split('\n')
    fixed_lines = []
    fixes_made = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Skip empty lines, comments, and CSS rules
        if not stripped or stripped.startswith('/*') or stripped.startswith('*') or stripped.startswith('//'):
            fixed_lines.append(line)
            i += 1
            continue
        
        # Skip lines that are part of selectors (contain { or })
        if '{' in stripped or '}' in stripped:
            fixed_lines.append(line)
            i += 1
            continue
        
        # Skip lines that are clearly CSS properties with values
        if ':' in stripped and not stripped.endswith(';'):
            # Check if this is a multi-line property
            next_line_idx = i + 1
            is_multiline = False
            
            # Look ahead to see if this continues on next lines
            while next_line_idx < len(lines):
                next_line = lines[next_line_idx].strip()
                if not next_line:
                    next_line_idx += 1
                    continue
                
                # If next line starts with a property or selector, this line needs semicolon
                if ':' in next_line and not next_line.startswith('/*'):
                    # This line should end with semicolon
                    if not stripped.endswith(';'):
                        fixed_lines.append(line + ';')
                        fixes_made += 1
                        print(f"  ✅ Fixed line {i+1}: Added semicolon")
                    else:
                        fixed_lines.append(line)
                    break
                
                # If next line is part of the same property (starts with space/tab and has comma or parentheses)
                if (next_line.startswith((' ', '\t')) or 
                    ',' in next_line or 
                    ')' in next_line or
                    next_line.endswith(',')):
                    is_multiline = True
                    break
                
                # If next line is a closing brace, this line needs semicolon
                if next_line == '}':
                    if not stripped.endswith(';'):
                        fixed_lines.append(line + ';')
                        fixes_made += 1
                        print(f"  ✅ Fixed line {i+1}: Added semicolon before closing brace")
                    else:
                        fixed_lines.append(line)
                    break
                
                next_line_idx += 1
                break
            
            if not is_multiline and next_line_idx >= len(lines):
                # End of file, add semicolon if missing
                if not stripped.endswith(';'):
                    fixed_lines.append(line + ';')
                    fixes_made += 1
                    print(f"  ✅ Fixed line {i+1}: Added semicolon at end of file")
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
        
        i += 1
    
    # Write back the fixed content
    new_content = '\n'.join(fixed_lines)
    
    if new_content != original_content:
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"\n📊 RESUMEN:")
        print(f"  • Archivo: {css_file}")
        print(f"  • Correcciones realizadas: {fixes_made}")
        print(f"  • Estado: ✅ CORREGIDO")
    else:
        print(f"\n📊 RESUMEN:")
        print(f"  • Archivo: {css_file}")
        print(f"  • Correcciones realizadas: 0")
        print(f"  • Estado: ✅ YA ESTABA CORRECTO")
    
    print(f"\n🎉 INTELLIGENT CSS FIXER COMPLETADO")

if __name__ == "__main__":
    intelligent_css_fixer()
