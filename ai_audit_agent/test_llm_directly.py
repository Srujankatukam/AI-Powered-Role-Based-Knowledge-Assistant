#!/usr/bin/env python3
"""
Direct LLM test to verify it's actually generating outputs
"""

import asyncio
import json
from llm_client import LLMClient

# Test data
test_data = {
    "company_name": "TestCorp Industries",
    "industry": "Manufacturing",
    "company_size": "Medium (51-200 employees)",
    "annual_revenue_inr": "150 Cr",
    "departments": {
        "Leadership & Management": {
            "track_business_metrics": "Excel spreadsheets",
            "competitor_analysis_frequency": "Quarterly"
        },
        "IT & Technology": {
            "website": "Basic static website",
            "backup_security": "Scheduled backup"
        }
    }
}

async def test_llm():
    print("="*70)
    print("Testing LLM Direct Output")
    print("="*70)
    
    client = LLMClient()
    
    print("\n1. Testing LLM initialization...")
    print(f"   API Key: {'Set' if client.api_key else 'NOT SET ❌'}")
    print(f"   Model URL: {client.model_url}")
    
    print("\n2. Calling LLM with test data...")
    print(f"   Company: {test_data['company_name']}")
    
    try:
        result = await client.generate_audit_analysis(test_data)
        
        print("\n3. LLM Response:")
        print("-" * 70)
        
        if result:
            # Check if it's a fallback
            summary = result.get('summary', {}).get('personalized_summary', '')
            
            if 'demonstrates foundational digital capabilities' in summary.lower():
                print("⚠️  WARNING: This looks like a FALLBACK response!")
                print("⚠️  The LLM might not be working properly")
                print("\nFallback indicators:")
                print("  - Generic summary text")
                print("  - Risk score exactly 60")
                print("  - Departments with identical drawbacks")
            else:
                print("✅ This appears to be a REAL LLM response!")
                print(f"✅ Company mentioned: {test_data['company_name'] in summary}")
            
            print("\nFull Response:")
            print(json.dumps(result, indent=2))
            
            # Detailed analysis
            print("\n4. Response Analysis:")
            print(f"   Summary length: {len(summary)} characters")
            print(f"   Risk score: {result.get('summary', {}).get('overall_risk_score')}")
            print(f"   Maturity level: {result.get('summary', {}).get('ai_maturity_level')}")
            print(f"   Number of sections: {len(result.get('sections', []))}")
            
            # Check if company name is in summary
            if test_data['company_name'] in summary:
                print(f"   ✅ Company name '{test_data['company_name']}' found in summary")
            else:
                print(f"   ❌ Company name NOT found in summary (might be fallback)")
            
            return result
        else:
            print("❌ LLM returned None")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_multiple_companies():
    """Test with different companies to verify customization"""
    print("\n" + "="*70)
    print("Testing with Multiple Companies")
    print("="*70)
    
    companies = [
        {
            "company_name": "Alpha Tech Solutions",
            "industry": "Technology",
            "company_size": "Small (11-50 employees)",
            "annual_revenue_inr": "50 Cr",
            "departments": {
                "IT & Technology": {
                    "website": "No website",
                    "backup_security": "No backup"
                }
            }
        },
        {
            "company_name": "Beta Manufacturing Ltd",
            "industry": "Manufacturing",
            "company_size": "Large (201-1000 employees)",
            "annual_revenue_inr": "500 Cr",
            "departments": {
                "IT & Technology": {
                    "website": "Dynamic website with AI chatbot",
                    "backup_security": "Real-time cloud backup with encryption"
                }
            }
        }
    ]
    
    client = LLMClient()
    results = []
    
    for company in companies:
        print(f"\n--- Testing {company['company_name']} ---")
        result = await client.generate_audit_analysis(company)
        
        if result:
            summary = result.get('summary', {}).get('personalized_summary', '')
            print(f"Summary preview: {summary[:150]}...")
            
            # Check if it's customized
            if company['company_name'] in summary:
                print(f"✅ Mentions company name")
            else:
                print(f"❌ Does NOT mention company name")
            
            if company['industry'] in summary:
                print(f"✅ Mentions industry")
            else:
                print(f"⚠️  Does NOT mention industry")
            
            results.append({
                'company': company['company_name'],
                'summary': summary,
                'risk_score': result.get('summary', {}).get('overall_risk_score')
            })
    
    # Compare results
    print("\n" + "="*70)
    print("Comparison:")
    print("="*70)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['company']}")
        print(f"   Risk Score: {result['risk_score']}")
        print(f"   Summary: {result['summary'][:100]}...")
    
    # Check if summaries are identical (bad!)
    if len(results) == 2:
        if results[0]['summary'] == results[1]['summary']:
            print("\n❌ WARNING: Summaries are IDENTICAL!")
            print("❌ LLM is NOT customizing output")
        else:
            print("\n✅ Summaries are DIFFERENT - LLM is working correctly!")

if __name__ == "__main__":
    print("Starting LLM diagnostics...\n")
    
    # Test 1: Single company
    asyncio.run(test_llm())
    
    # Test 2: Multiple companies
    asyncio.run(test_multiple_companies())
    
    print("\n" + "="*70)
    print("Diagnostic Complete")
    print("="*70)
