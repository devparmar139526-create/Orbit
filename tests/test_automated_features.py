"""
Automated Feature Test - Tests all 31 features without user interaction
"""
import sys
from pathlib import Path
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).parent))

from Orbit_core.config.settings import Settings
from Orbit_core.llm.router import LLMRouter
from Orbit_core.intent.source_selector import SourceSelector

class AutomatedFeatureTest:
    def __init__(self):
        self.settings = Settings()
        self.llm = LLMRouter(self.settings)
        self.source_selector = SourceSelector(self.llm, self.settings)
        self.passed = 0
        self.failed = 0
        
    def test_feature(self, phase, feature_name, query):
        """Test a single feature"""
        try:
            print(f"\n🧪 Testing [{phase}] {feature_name}")
            print(f"   Query: '{query}'")
            
            result = ""
            for chunk in self.source_selector.process(query):
                result += chunk
            
            if result and "error" not in result.lower():
                print(f"   ✅ PASS: {result[:100]}...")
                self.passed += 1
                return True
            else:
                print(f"   ❌ FAIL: {result}")
                self.failed += 1
                return False
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            self.failed += 1
            return False
    
    def run_all_tests(self):
        """Test all 31 features"""
        print("\n" + "="*70)
        print("🚀 AUTOMATED FEATURE TEST - ALL 31 FEATURES")
        print("="*70)
        
        # Phase 1: Core Features (8)
        print("\n" + "="*70)
        print("🎤 PHASE 1: CORE FEATURES (8)")
        print("="*70)
        
        self.test_feature("Phase 1", "Wikipedia Search", "who is einstein")
        self.test_feature("Phase 1", "Weather Information", "what's the weather")
        self.test_feature("Phase 1", "LLM Conversation", "hello")
        self.test_feature("Phase 1", "LLM Conversation", "what can you do")
        # Desktop control and scheduling require actual execution, skip in automated test
        print("   ⚠️  Desktop Control - Requires manual testing")
        print("   ⚠️  Task Scheduling - Requires manual testing")
        print("   ⚠️  Wake Word - Requires microphone")
        print("   ⚠️  STT/TTS - Requires audio hardware")
        
        # Phase 2: Device Control (10)
        print("\n" + "="*70)
        print("🖥️  PHASE 2: DEVICE CONTROL (10)")
        print("="*70)
        
        print("   ⚠️  Screenshots - Requires display")
        print("   ⚠️  Screen Recording - Requires display")
        print("   ⚠️  File Operations - Requires file system access")
        print("   ⚠️  Auto-Organize - Requires file system access")
        print("   ⚠️  Keyboard Macros - Requires input simulation")
        print("   ⚠️  Window Management - Requires GUI")
        # These require actual system interaction
        
        # Phase 3: AI & Productivity (13)
        print("\n" + "="*70)
        print("🧠 PHASE 3: AI & PRODUCTIVITY (13)")
        print("="*70)
        
        self.test_feature("Phase 3", "Text Translation", "translate hello to spanish")
        self.test_feature("Phase 3", "Language Detection", "what language is bonjour")
        self.test_feature("Phase 3", "Task Prediction", "predict next task")
        self.test_feature("Phase 3", "Schedule Optimization", "optimize my schedule")
        
        # Document processing requires files
        print("   ⚠️  Document Organization - Requires file system")
        print("   ⚠️  Document Summarization - Requires PDF files")
        print("   ⚠️  CSV Processing - Requires CSV files")
        print("   ⚠️  Report Generation - Requires file system")
        
        self.test_feature("Phase 3", "Screen Time Tracking", "track screen time")
        
        # Intent Classification Tests
        print("\n" + "="*70)
        print("🎯 INTENT CLASSIFICATION")
        print("="*70)
        
        test_cases = {
            "translate hello to spanish": "translation",
            "organize documents by type": "document_processor",
            "track screen time": "screen_time_tracker",
            "predict next task": "productivity_ai",
            "what is the weather": "weather",
            "who is einstein": "wikipedia"
        }
        
        intent_passed = 0
        for query, expected in test_cases.items():
            intent = self.source_selector.classify_intent(query)
            if intent == expected:
                print(f"   ✅ '{query[:30]}...' → {intent}")
                intent_passed += 1
            else:
                print(f"   ❌ '{query[:30]}...' → {intent} (expected: {expected})")
        
        self.passed += intent_passed
        self.failed += (len(test_cases) - intent_passed)
        
        # Module Availability Tests
        print("\n" + "="*70)
        print("📦 MODULE AVAILABILITY")
        print("="*70)
        
        modules_passed = 0
        modules = [
            ('Translation Service', self.source_selector.translation),
            ('Productivity AI', self.source_selector.productivity_ai),
            ('Document Processor', self.source_selector.document_processor),
            ('Screen Time Tracker', self.source_selector.screen_time_tracker),
            ('Advanced Desktop', self.source_selector.advanced_desktop),
            ('Wikipedia', self.source_selector.wikipedia),
            ('Weather', self.source_selector.weather),
            ('Desktop', self.source_selector.desktop),
            ('Scheduler', self.source_selector.scheduler)
        ]
        
        for name, module in modules:
            if module is not None:
                print(f"   ✅ {name}: Available")
                modules_passed += 1
            else:
                print(f"   ❌ {name}: Not available")
        
        self.passed += modules_passed
        self.failed += (len(modules) - modules_passed)
        
        # Settings Verification
        print("\n" + "="*70)
        print("⚙️  SETTINGS VERIFICATION")
        print("="*70)
        
        settings_checks = [
            ('Translation', self.settings.ENABLE_TRANSLATION),
            ('Task Prediction', self.settings.ENABLE_TASK_PREDICTION),
            ('Smart Reminders', self.settings.ENABLE_SMART_REMINDERS),
            ('Doc Organization', self.settings.ENABLE_DOC_ORGANIZATION),
            ('Screen Time', self.settings.ENABLE_SCREEN_TIME_TRACKING)
        ]
        
        settings_passed = 0
        for name, value in settings_checks:
            if value:
                print(f"   ✅ {name}: Enabled")
                settings_passed += 1
            else:
                print(f"   ⚠️  {name}: Disabled")
        
        self.passed += settings_passed
        self.failed += (len(settings_checks) - settings_passed)
        
        # Print Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("📊 AUTOMATED TEST SUMMARY")
        print("="*70)
        
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success Rate: {percentage:.1f}%")
        
        print("\n" + "="*70)
        if self.failed == 0:
            print("🎉 ALL TESTABLE FEATURES WORKING!")
        elif percentage >= 80:
            print("✅ SYSTEM FUNCTIONAL - Most features working")
        else:
            print(f"⚠️  NEEDS ATTENTION - {self.failed} tests failed")
        print("="*70)
        
        print("\n📝 NOTE: Some features require manual testing:")
        print("   - Desktop control (requires apps)")
        print("   - File operations (requires file system)")
        print("   - Screenshots (requires display)")
        print("   - Voice input/output (requires audio hardware)")

if __name__ == "__main__":
    print("\n🔬 Starting Automated Feature Test...\n")
    tester = AutomatedFeatureTest()
    tester.run_all_tests()
    print("\n✨ Automated testing complete!\n")

