"""
PHASE 3: AI & PRODUCTIVITY - Integration Test
Tests all 13 Phase 3 features to ensure proper integration
"""
import os
import sys
import json
import tempfile
from pathlib import Path

# Add parent directory to path (project root)
sys.path.insert(0, str(Path(__file__).parent.parent))

from Orbit_core.config.settings import Settings
from Orbit_core.actions.translation import TranslationService
from Orbit_core.actions.productivity_ai import ProductivityAI
from Orbit_core.actions.document_processor import DocumentProcessor
from Orbit_core.actions.screen_time_tracker import ScreenTimeTracker

class Phase3Tester:
    def __init__(self):
        self.settings = Settings()
        self.passed = 0
        self.failed = 0
        self.results = []
        
    def test(self, name, function):
        """Run a test and track results"""
        try:
            print(f"\n🧪 Testing: {name}")
            result = function()
            if result:
                print(f"   ✅ PASSED: {name}")
                self.passed += 1
                self.results.append({"test": name, "status": "PASSED", "message": result})
                return True
            else:
                print(f"   ❌ FAILED: {name} - No result returned")
                self.failed += 1
                self.results.append({"test": name, "status": "FAILED", "message": "No result"})
                return False
        except Exception as e:
            print(f"   ❌ FAILED: {name}")
            print(f"      Error: {str(e)}")
            self.failed += 1
            self.results.append({"test": name, "status": "FAILED", "message": str(e)})
            return False
    
    def run_all_tests(self):
        """Run all Phase 3 integration tests"""
        print("=" * 70)
        print("🧠 PHASE 3: AI & PRODUCTIVITY - INTEGRATION TEST")
        print("=" * 70)
        
        # Test 1-3: Translation Services
        print("\n" + "=" * 70)
        print("📝 TRANSLATION SERVICES (3 features)")
        print("=" * 70)
        
        translation = TranslationService(self.settings)
        
        self.test("1. Text Translation", 
                  lambda: translation.translate_text("Hello, how are you?", target_lang="es"))
        
        self.test("2. Language Detection", 
                  lambda: translation.detect_language("Bonjour, comment allez-vous?"))
        
        self.test("3. Batch Translation", 
                  lambda: translation.batch_translate(
                      ["Hello", "Goodbye", "Thank you"], 
                      target_lang="fr"
                  ))
        
        # Test 4-6: Productivity AI
        print("\n" + "=" * 70)
        print("🎯 PRODUCTIVITY AI (3 features)")
        print("=" * 70)
        
        productivity_ai = ProductivityAI(self.settings)
        
        # Create some sample task history
        sample_tasks = [
            {"task": "Check emails", "time": "09:00", "day": "Monday"},
            {"task": "Team meeting", "time": "10:00", "day": "Monday"},
            {"task": "Code review", "time": "14:00", "day": "Monday"},
        ]
        history_file = self.settings.TASK_HISTORY_FILE
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        with open(history_file, 'w') as f:
            json.dump(sample_tasks, f)
        
        self.test("4. Task Prediction", 
                  lambda: productivity_ai.predict_next_task())
        
        self.test("5. Smart Reminder Creation", 
                  lambda: productivity_ai.create_smart_reminder("Finish report", priority="high"))
        
        self.test("6. Schedule Optimization", 
                  lambda: productivity_ai.optimize_schedule())
        
        # Test 7-9: Document Processing
        print("\n" + "=" * 70)
        print("📁 DOCUMENT PROCESSING (4 features)")
        print("=" * 70)
        
        doc_processor = DocumentProcessor(self.settings)
        
        # Create temp directory with sample files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create sample files
            (Path(temp_dir) / "test1.txt").write_text("Sample document 1")
            (Path(temp_dir) / "test2.pdf").write_text("Sample PDF")  # Not real PDF but OK for test
            (Path(temp_dir) / "data.csv").write_text("name,age\nJohn,30\nJane,25")
            
            self.test("7. Document Organization by Type", 
                      lambda: doc_processor.organize_documents_by_type(temp_dir))
            
            self.test("8. Document Organization by Date", 
                      lambda: doc_processor.organize_documents_by_date(temp_dir))
            
            # Test summarization with a text file
            test_file = Path(temp_dir) / "test_summary.txt"
            test_file.write_text("This is a test document. " * 50)
            
            self.test("9. Document Summarization", 
                      lambda: doc_processor.summarize_document(str(test_file)))
            
            # Test CSV processing
            csv_file = Path(temp_dir) / "test.csv"
            csv_file.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\nCharlie,35,Chicago")
            
            self.test("10. CSV Processing", 
                      lambda: doc_processor.process_csv(str(csv_file)))
        
        # Test 11: Report Generation
        self.test("11. Report Generation", 
                  lambda: doc_processor.generate_report(
                      "Phase 3 Test Report",
                      {"tests_run": 13, "status": "In Progress"}
                  ))
        
        # Test 12-13: Screen Time Tracking
        print("\n" + "=" * 70)
        print("⏱️ SCREEN TIME TRACKING (3 features)")
        print("=" * 70)
        
        screen_time = ScreenTimeTracker(self.settings)
        
        self.test("12. Start Screen Time Tracking", 
                  lambda: screen_time.start_tracking())
        
        import time
        time.sleep(2)  # Track for 2 seconds
        
        self.test("13. Stop Tracking & Daily Report", 
                  lambda: screen_time.stop_tracking() + "\n" + screen_time.get_daily_report())
        
        # Configuration Test
        print("\n" + "=" * 70)
        print("⚙️ CONFIGURATION VERIFICATION")
        print("=" * 70)
        
        self.test("Settings: Translation Enabled", 
                  lambda: self.settings.ENABLE_TRANSLATION)
        
        self.test("Settings: Task Prediction Enabled", 
                  lambda: self.settings.ENABLE_TASK_PREDICTION)
        
        self.test("Settings: Doc Organization Enabled", 
                  lambda: self.settings.ENABLE_DOC_ORGANIZATION)
        
        self.test("Settings: Screen Time Tracking Enabled", 
                  lambda: self.settings.ENABLE_SCREEN_TIME_TRACKING)
        
        # Print Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success Rate: {percentage:.1f}%")
        
        if self.failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if result['status'] == 'FAILED':
                    print(f"   - {result['test']}: {result['message']}")
        
        print("\n" + "=" * 70)
        if self.failed == 0:
            print("🎉 ALL PHASE 3 FEATURES WORKING PERFECTLY!")
        else:
            print(f"⚠️ {self.failed} TEST(S) NEED ATTENTION")
        print("=" * 70)
        
        # Save detailed results
        results_file = "phase3_test_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                "total": total,
                "passed": self.passed,
                "failed": self.failed,
                "success_rate": percentage,
                "tests": self.results
            }, f, indent=2)
        print(f"\n📄 Detailed results saved to: {results_file}")

if __name__ == "__main__":
    print("\n🚀 Starting Phase 3 Integration Tests...\n")
    
    # Check if config file exists
    if not os.path.exists("phase3_config.json"):
        print("⚠️ Warning: phase3_config.json not found. Using default settings.")
    
    tester = Phase3Tester()
    tester.run_all_tests()
    
    print("\n✨ Phase 3 testing complete!")
