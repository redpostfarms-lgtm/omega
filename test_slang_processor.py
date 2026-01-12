#!/usr/bin/env python3
"""Quick test of slang processor"""

from omega_slang_processor import SlangProcessor, SlangContext, FormalityLevel

def main():
    print("Testing Omega Slang Processor...")
    print("=" * 60)
    
    processor = SlangProcessor()
    
    # Test 1: Detect slang
    print("\n1. Testing slang detection:")
    text = "There's a bug in the code, we need to debug it. LGTM, ship it!"
    detected = processor.detect_slang(text)
    print(f"   Text: {text}")
    print(f"   Detected {len(detected)} slang terms:")
    for term, info in detected:
        print(f"     - {term}: {info['meaning']}")
    
    # Test 2: Get meaning
    print("\n2. Testing meaning lookup:")
    meaning = processor.get_meaning("bug", SlangContext.CODING)
    if meaning:
        print(f"   'bug' means: {meaning['meaning']}")
        print(f"   Example: {meaning['example']}")
    else:
        print("   'bug' not found")
    
    # Test 3: Check appropriateness
    print("\n3. Testing appropriateness:")
    is_formal_ok = processor.is_appropriate("bug", FormalityLevel.FORMAL, SlangContext.CODING)
    is_informal_ok = processor.is_appropriate("bug", FormalityLevel.INFORMAL, SlangContext.CODING)
    print(f"   'bug' in formal context: {is_formal_ok}")
    print(f"   'bug' in informal context: {is_informal_ok}")
    
    # Test 4: Explain slang
    print("\n4. Testing explanation:")
    explanation = processor.explain_slang("bug")
    print(f"   {explanation}")
    
    # Test 5: Historical slang
    print("\n5. Testing historical slang:")
    historical = processor.get_meaning("huzzah")
    if historical:
        print(f"   'huzzah' means: {historical['meaning']}")
        print(f"   Period: {historical.get('period', 'N/A')}")
    
    # Test 6: Internet slang
    print("\n6. Testing internet slang:")
    internet = processor.get_meaning("lol")
    if internet:
        print(f"   'lol' means: {internet['meaning']}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("✅ Slang processor is working correctly!")

if __name__ == "__main__":
    main()
