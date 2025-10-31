#!/usr/bin/env python3
"""
Test script to verify orbit setup and components
"""

import sys
import os

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    try:
        from Orbit_core.config.settings import Settings
        from Orbit_core.llm.ollama_client import OllamaClient
        from Orbit_core.llm.router import LLMRouter
        from Orbit_core.memory.sqlite_store import MemoryStore
        from Orbit_core.actions.wikipedia import WikipediaAction
        from Orbit_core.actions.weather import WeatherAction
        from Orbit_core.actions.desktop import DesktopAction
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_ollama_connection():
    """Test Ollama connection"""
    print("\nTesting Ollama connection...")
    try:
        from Orbit_core.config.settings import Settings
        from Orbit_core.llm.ollama_client import OllamaClient
        
        settings = Settings()
        client = OllamaClient(settings.OLLAMA_URL, settings.OLLAMA_MODEL)
        
        if client.is_available():
            print(f"✅ Connected to Ollama at {settings.OLLAMA_URL}")
            models = client.list_models()
            if models:
                print(f"   Available models: {', '.join(models)}")
            return True
        else:
            print(f"❌ Cannot connect to Ollama at {settings.OLLAMA_URL}")
            print("   Make sure Ollama is running: ollama serve")
            return False
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        return False

def test_memory():
    """Test database creation"""
    print("\nTesting memory store...")
    try:
        from Orbit_core.memory.sqlite_store import MemoryStore
        
        db_path = "data/test_memory.db"
        store = MemoryStore(db_path)
        
        store.add_message("user", "Test message")
        context = store.get_recent_context(limit=1)
        store.close()
        
        # Clean up
        if os.path.exists(db_path):
            os.remove(db_path)
        
        if context and context[0]['content'] == "Test message":
            print("✅ Memory store working")
            return True
        else:
            print("❌ Memory store not working correctly")
            return False
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        return False

def test_wikipedia():
    """Test Wikipedia API"""
    print("\nTesting Wikipedia integration...")
    try:
        from Orbit_core.actions.wikipedia import WikipediaAction
        
        wiki = WikipediaAction()
        result = wiki.search("Python programming", sentences=1)
        
        if result and "Wikipedia" in result:
            print("✅ Wikipedia API working")
            print(f"   Sample: {result[:100]}...")
            return True
        else:
            print("❌ Wikipedia API failed")
            return False
    except Exception as e:
        print(f"❌ Wikipedia test failed: {e}")
        return False

def test_weather():
    """Test Weather API"""
    print("\nTesting Weather integration...")
    try:
        from Orbit_core.config.settings import Settings
        from Orbit_core.actions.weather import WeatherAction
        
        settings = Settings()
        weather = WeatherAction(settings)
        result = weather.get_weather("London")
        
        if result and "Weather" in result:
            print("✅ Weather API working")
            print(f"   Sample: {result[:100]}...")
            return True
        else:
            print("❌ Weather API failed")
            return False
    except Exception as e:
        print(f"❌ Weather test failed: {e}")
        return False

def test_tts():
    """Test TTS (without actually speaking)"""
    print("\nTesting TTS initialization...")
    try:
        from Orbit_core.tts.dispatcher import TTSDispatcher
        
        tts = TTSDispatcher()
        if tts.is_enabled():
            print("✅ TTS initialized successfully")
            print("   Note: Not testing audio output")
            return True
        else:
            print("⚠️  TTS initialized but disabled")
            return True
    except Exception as e:
        print(f"⚠️  TTS test failed (non-critical): {e}")
        return True  # TTS is optional

def test_stt():
    """Test STT initialization"""
    print("\nTesting STT initialization...")
    try:
        from Orbit_core.stt.deep import SpeechRecognizer
        
        # Just test initialization, not actual recognition
        print("   Initializing microphone (this may take a moment)...")
        sr = SpeechRecognizer()
        print("✅ STT initialized successfully")
        print("   Note: Not testing actual speech recognition")
        return True
    except Exception as e:
        print(f"⚠️  STT test failed (non-critical): {e}")
        print("   Voice features may not work, but text mode will")
        return True  # STT is optional

def main():
    """Run all tests"""
    print("""
    ╔═══════════════════════════════════════╗
    ║   🧪 orbit SYSTEM TEST               ║
    ╚═══════════════════════════════════════╝
    """)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Ollama", test_ollama_connection()))
    results.append(("Memory", test_memory()))
    results.append(("Wikipedia", test_wikipedia()))
    results.append(("Weather", test_weather()))
    results.append(("TTS", test_tts()))
    results.append(("STT", test_stt()))
    
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:15} {status}")
    
    print("="*50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! orbit is ready to use.")
        print("   Run: python bin/orbit.py")
    elif results[0][1] and results[1][1]:  # Imports and Ollama work
        print("\n⚠️  Some optional features failed, but core functionality works.")
        print("   Run: python bin/orbit.py")
    else:
        print("\n❌ Critical tests failed. Please fix the issues above.")
        print("   Check the troubleshooting section in README.md")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
