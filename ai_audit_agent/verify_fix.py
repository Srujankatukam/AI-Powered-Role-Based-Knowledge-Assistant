#!/usr/bin/env python3
"""
Quick verification script to ensure the style fix works
Run this to verify the pdf_builder module loads without errors
"""

import sys

def verify_imports():
    """Verify all imports work"""
    print("🔍 Verifying imports...")
    
    try:
        print("  ✓ Importing pdf_builder...")
        from pdf_builder import PDFBuilder
        print("  ✓ pdf_builder imported successfully!")
        
        print("\n🏗️  Testing PDFBuilder initialization...")
        builder = PDFBuilder()
        print("  ✓ PDFBuilder initialized successfully!")
        
        print("\n✅ All checks passed!")
        print("  • No style conflicts")
        print("  • PDFBuilder ready to use")
        print("  • Application should start normally")
        
        return True
        
    except KeyError as e:
        print(f"  ❌ Style conflict error: {e}")
        print("\n  This means there's still a style name conflict.")
        return False
        
    except ImportError as e:
        print(f"  ⚠️  Import error: {e}")
        print("\n  Make sure dependencies are installed:")
        print("  pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("AI Audit Agent - Style Fix Verification")
    print("="*60 + "\n")
    
    success = verify_imports()
    
    print("\n" + "="*60)
    if success:
        print("✨ Fix verified! Application is ready to run.")
        print("="*60)
        print("\nNext steps:")
        print("  1. Start application: python main.py")
        print("  2. Or with Docker: docker-compose up -d")
        print("  3. Test: python test_example.py")
        sys.exit(0)
    else:
        print("❌ Verification failed. Please check errors above.")
        print("="*60)
        sys.exit(1)
