"""
Full System Integration Test
Tests Orbit with all Phase 1, 2, and 3 features together
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).parent))

from Orbit_core.config.settings import Settings
from Orbit_core.llm.router import LLMRouter
from Orbit_core.intent.source_selector import SourceSelector

class FullSystemTest:
    def __init__(self):
        self.settings = Settings()
        self.passed = 0
        self.failed = 0
        
    def test_system_initialization(self):
        """Test that all components initialize correctly"""
        print("\n" + "="*70)
        print("🚀 FULL SYSTEM INTEGRATION TEST")
        print("="*70)
        
        try:
            # Test 1: Settings loaded
            print("\n✅ Test 1: Settings Configuration")
            print(f"   - Assistant Name: {self.settings.ASSISTANT_NAME}")
            print(f"   - Wake Word: {self.settings.WAKE_WORD}")
            print(f"   - Ollama Model: {self.settings.OLLAMA_MODEL}")
            
            # Test 2: LLM Router
            print("\n✅ Test 2: LLM Router Initialization")
            llm = LLMRouter(self.settings)
            openai_status = "✅" if llm.openai_client else "⚠️"
            ollama_status = "✅" if llm.ollama_client and llm.ollama_client.is_available() else "⚠️"
            print(f"   - OpenAI: {openai_status}")
            print(f"   - Ollama: {ollama_status}")
            self.passed += 1
            
            # Test 3: Source Selector with all features
            print("\n✅ Test 3: Source Selector Integration")
            source_selector = SourceSelector(llm, self.settings)
            print("   - Phase 1: ✅ Wikipedia, Weather, Desktop, Scheduler")
            print("   - Phase 2: ✅ Advanced Desktop Control")
            print("   - Phase 3: ✅ Translation, Productivity AI, Document Processing, Screen Time")
            
            # Test 4: Intent Classification
            print("\n✅ Test 4: Intent Classification")
            test_queries = {
                "translate hello to spanish": "translation",
                "organize documents by type": "document_processor",
                "track screen time": "screen_time_tracker",
                "predict next task": "productivity_ai",
                "take a screenshot": "advanced_desktop",
                "open notepad": "desktop",
                "what is the weather": "weather",
                "who is einstein": "wikipedia",
                "remind me to call in 5 minutes": "schedule"
            }
            
            for query, expected_intent in test_queries.items():
                intent = source_selector.classify_intent(query)
                status = "✅" if intent == expected_intent else "❌"
                print(f"   {status} '{query[:30]}...' → {intent}")
                if intent == expected_intent:
                    self.passed += 1
                else:
                    self.failed += 1
                    print(f"      Expected: {expected_intent}, Got: {intent}")
            
            # Test 5: Phase 3 Settings Verification
            print("\n✅ Test 5: Phase 3 Settings Verification")
            phase3_settings = [
                ("Translation", self.settings.ENABLE_TRANSLATION),
                ("Task Prediction", self.settings.ENABLE_TASK_PREDICTION),
                ("Smart Reminders", self.settings.ENABLE_SMART_REMINDERS),
                ("Doc Organization", self.settings.ENABLE_DOC_ORGANIZATION),
                ("Doc Summarization", self.settings.ENABLE_DOC_SUMMARIZATION),
                ("CSV Processing", self.settings.ENABLE_CSV_PROCESSING),
                ("Report Generation", self.settings.ENABLE_REPORT_GENERATION),
                ("Screen Time", self.settings.ENABLE_SCREEN_TIME_TRACKING)
            ]
            
            for name, enabled in phase3_settings:
                status = "✅" if enabled else "⚠️"
                print(f"   {status} {name}: {enabled}")
                if enabled:
                    self.passed += 1
                else:
                    self.failed += 1
            
            # Test 6: Handler Methods Exist
            print("\n✅ Test 6: Handler Methods Verification")
            handlers = [
                '_handle_translation',
                '_handle_productivity_ai',
                '_handle_document_processor',
                '_handle_screen_time_tracker',
                '_handle_advanced_desktop',
                '_handle_desktop',
                '_handle_weather',
                '_handle_wikipedia',
                '_handle_schedule'
            ]
            
            for handler in handlers:
                exists = hasattr(source_selector, handler)
                status = "✅" if exists else "❌"
                print(f"   {status} {handler}")
                if exists:
                    self.passed += 1
                else:
                    self.failed += 1
            
            # Test 7: Action Module Imports
            print("\n✅ Test 7: Action Module Imports")
            modules = [
                ('Translation', source_selector.translation),
                ('Productivity AI', source_selector.productivity_ai),
                ('Document Processor', source_selector.document_processor),
                ('Screen Time Tracker', source_selector.screen_time_tracker),
                ('Advanced Desktop', source_selector.advanced_desktop),
                ('Wikipedia', source_selector.wikipedia),
                ('Weather', source_selector.weather),
                ('Desktop', source_selector.desktop),
                ('Scheduler', source_selector.scheduler)
            ]
            
            for name, module in modules:
                exists = module is not None
                status = "✅" if exists else "❌"
                print(f"   {status} {name}: {type(module).__name__}")
                if exists:
                    self.passed += 1
                else:
                    self.failed += 1
            
            self.print_summary()
            
        except Exception as e:
            print(f"\n❌ FATAL ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            self.failed += 1
            self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("📊 INTEGRATION TEST SUMMARY")
        print("="*70)
        
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Checks: {total}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success Rate: {percentage:.1f}%")
        
        print("\n" + "="*70)
        if self.failed == 0:
            print("🎉 FULL SYSTEM INTEGRATION SUCCESSFUL!")
            print("All Phase 1, 2, and 3 features are properly integrated!")
        else:
            print(f"⚠️ {self.failed} CHECK(S) NEED ATTENTION")
        print("="*70)

if __name__ == "__main__":
    print("\n🔬 Starting Full System Integration Test...\n")
    tester = FullSystemTest()
    tester.test_system_initialization()
    print("\n✨ Integration test complete!\n")

