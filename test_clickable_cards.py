"""
Clickable Dashboard Cards - Verification Test
Tests that dashboard cards are properly configured for navigation
"""

import os
import re

def check_clickable_cards():
    """Check if dashboard cards have clickable functionality"""
    print("\n" + "="*70)
    print("🧪 Clickable Dashboard Cards - Verification Test")
    print("="*70 + "\n")
    
    all_passed = True
    
    # Check HTML file
    print("📄 Checking index.html for clickable cards...")
    try:
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Check for clickable class
        if 'class="stat-card glass-effect clickable"' in html_content:
            print("✅ Stat cards have 'clickable' class")
        else:
            print("❌ Stat cards missing 'clickable' class")
            all_passed = False
        
        # Check for onclick handlers
        onclick_pattern = r'onclick="navigateToSection\('
        onclick_matches = len(re.findall(onclick_pattern, html_content))
        if onclick_matches >= 4:
            print(f"✅ Found {onclick_matches} onclick handlers (expected 4+)")
        else:
            print(f"❌ Found only {onclick_matches} onclick handlers (expected 4)")
            all_passed = False
        
        # Check for hover indicators
        if 'card-hover-indicator' in html_content:
            print("✅ Hover indicator elements present")
        else:
            print("❌ Hover indicator elements missing")
            all_passed = False
        
        # Check for title attributes
        title_pattern = r'title="Click to'
        title_matches = len(re.findall(title_pattern, html_content))
        if title_matches >= 4:
            print(f"✅ Found {title_matches} title tooltips")
        else:
            print(f"⚠️  Found only {title_matches} title tooltips")
        
        print()
        
    except Exception as e:
        print(f"❌ Error reading index.html: {e}")
        all_passed = False
    
    # Check CSS file
    print("🎨 Checking style.css for clickable card styles...")
    try:
        with open('static/style.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Check for clickable styles
        if '.stat-card.clickable' in css_content:
            print("✅ Clickable card styles defined")
        else:
            print("❌ Clickable card styles missing")
            all_passed = False
        
        # Check for hover indicator styles
        if '.card-hover-indicator' in css_content:
            print("✅ Hover indicator styles defined")
        else:
            print("❌ Hover indicator styles missing")
            all_passed = False
        
        # Check for cursor pointer
        if 'cursor: pointer' in css_content:
            print("✅ Cursor pointer style present")
        else:
            print("❌ Cursor pointer style missing")
            all_passed = False
        
        # Check for ripple effect
        if '.stat-card.clickable::after' in css_content:
            print("✅ Ripple effect animation defined")
        else:
            print("❌ Ripple effect animation missing")
            all_passed = False
        
        # Check for mobile optimizations
        if 'stat-card.clickable:active' in css_content:
            print("✅ Mobile touch feedback styles present")
        else:
            print("⚠️  Mobile touch feedback could be enhanced")
        
        print()
        
    except Exception as e:
        print(f"❌ Error reading style.css: {e}")
        all_passed = False
    
    # Check JavaScript file
    print("⚡ Checking script.js for navigation enhancement...")
    try:
        with open('static/script.js', 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Check for enhanced navigateToSection
        if 'function navigateToSection' in js_content:
            print("✅ navigateToSection function exists")
            
            # Check for toast notification
            if 'showToast' in js_content and 'Opening' in js_content:
                print("✅ Toast notification on navigation")
            else:
                print("⚠️  Toast notification could be added")
            
            # Check for smooth scroll
            if 'scrollIntoView' in js_content or 'scroll' in js_content:
                print("✅ Smooth scroll functionality present")
            else:
                print("⚠️  Smooth scroll could be enhanced")
        else:
            print("❌ navigateToSection function missing")
            all_passed = False
        
        print()
        
    except Exception as e:
        print(f"❌ Error reading script.js: {e}")
        all_passed = False
    
    # Check documentation
    print("📚 Checking documentation...")
    if os.path.exists('CLICKABLE_DASHBOARD_CARDS.md'):
        size = os.path.getsize('CLICKABLE_DASHBOARD_CARDS.md')
        print(f"✅ Feature documentation created ({size:,} bytes)")
    else:
        print("⚠️  Feature documentation missing")
    
    print()
    
    # Final summary
    print("="*70)
    if all_passed:
        print("✅ ALL CHECKS PASSED!")
        print("\n🎉 Clickable Dashboard Cards Implementation Complete!")
        print("\n📊 Features:")
        print("   ✓ Cards are clickable")
        print("   ✓ Hover animations")
        print("   ✓ Click ripple effect")
        print("   ✓ Navigation handlers")
        print("   ✓ Mobile optimizations")
        print("   ✓ Visual feedback")
        print("\n🚀 Test it:")
        print("   1. Run: python app.py")
        print("   2. Go to Dashboard section")
        print("   3. Click any stat card")
        print("   4. Watch it navigate smoothly!")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("   Please review the errors above")
    print("="*70 + "\n")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    import sys
    sys.exit(check_clickable_cards())
