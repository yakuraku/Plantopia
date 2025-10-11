"""
Comprehensive Live Testing for Plant Tracking Endpoints (Iteration 3)
Tests all plant tracking endpoints against a running backend server.

Requirements:
- Backend server running on http://localhost:8000
- Production database accessible
- Real Gemini API access for growth data generation

Test Coverage:
- All 13 plant tracking endpoints
- Success scenarios (2xx responses)
- Error scenarios (404, 400, 500)
- Edge cases and validation
- Data persistence verification
"""

import requests
import json
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any
import time


class PlantTrackingTester:
    """Comprehensive tester for plant tracking endpoints"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.test_results = []
        self.test_data = {}
        self.created_instances = []

    def log_test(self, test_name: str, status: str, details: Dict[str, Any]):
        """Log test result"""
        result = {
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)

        # Print concise result
        status_symbol = "✓" if status == "PASS" else "✗"
        print(f"{status_symbol} {test_name}: {status}")
        if status == "FAIL":
            print(f"  Error: {details.get('error', 'Unknown error')}")

    def test_start_tracking_success(self, user_data: Dict, plant_id: int, nickname: str, location: str) -> Optional[int]:
        """
        Test: POST /tracking/start - Success scenario
        Creates a new plant tracking instance
        """
        test_name = "Start Plant Tracking - Success"

        try:
            payload = {
                "user_id": user_data.get("user_id", 1),
                "plant_id": plant_id,
                "plant_nickname": nickname,
                "start_date": date.today().isoformat(),
                "location_details": location,
                "user_data": {
                    "email": user_data["email"],
                    "name": user_data["name"],
                    "suburb_id": user_data["suburb_id"],
                    "experience_level": user_data["experience_level"],
                    "garden_type": user_data["garden_type"],
                    "available_space": user_data["available_space"],
                    "climate_goal": user_data["climate_goal"]
                }
            }

            response = requests.post(f"{self.api_base}/tracking/start", json=payload)

            if response.status_code == 201:
                data = response.json()
                instance_id = data.get("instance_id")

                # Validate response structure
                assert "instance_id" in data, "Missing instance_id in response"
                assert "plant_nickname" in data, "Missing plant_nickname in response"
                assert "current_stage" in data, "Missing current_stage in response"
                assert data["plant_nickname"] == nickname, "Nickname mismatch"

                self.created_instances.append(instance_id)

                self.log_test(test_name, "PASS", {
                    "instance_id": instance_id,
                    "response": data
                })

                return instance_id
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })
                return None

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})
            return None

    def test_start_tracking_invalid_plant(self):
        """
        Test: POST /tracking/start - Invalid plant ID (404 error)
        """
        test_name = "Start Plant Tracking - Invalid Plant ID"

        try:
            payload = {
                "user_id": 1,
                "plant_id": 999999,  # Non-existent plant ID
                "plant_nickname": "Test Plant",
                "start_date": date.today().isoformat(),
                "user_data": {
                    "email": "test@example.com",
                    "name": "Test User",
                    "suburb_id": 1,
                    "experience_level": "beginner",
                    "garden_type": "backyard",
                    "available_space": 10.0,
                    "climate_goal": "general gardening"
                }
            }

            response = requests.post(f"{self.api_base}/tracking/start", json=payload)

            if response.status_code == 404:
                self.log_test(test_name, "PASS", {
                    "status_code": response.status_code,
                    "expected": "404 Not Found"
                })
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "expected": 404,
                    "error": "Should return 404 for non-existent plant"
                })

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    def test_get_user_plants(self, user_id: int, expected_count: int = None):
        """
        Test: GET /tracking/user/{user_id} - Get user's plant instances
        """
        test_name = "Get User Plant Instances"

        try:
            response = requests.get(f"{self.api_base}/tracking/user/{user_id}")

            if response.status_code == 200:
                data = response.json()

                # Validate response structure
                assert "plants" in data, "Missing plants in response"
                assert "total_count" in data, "Missing total_count"
                assert "active_count" in data, "Missing active_count"
                assert "pagination" in data, "Missing pagination info"

                if expected_count is not None:
                    assert len(data["plants"]) >= expected_count, f"Expected at least {expected_count} plants"

                self.log_test(test_name, "PASS", {
                    "total_count": data["total_count"],
                    "active_count": data["active_count"],
                    "plants_returned": len(data["plants"])
                })
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    def test_get_user_plants_pagination(self, user_id: int):
        """
        Test: GET /tracking/user/{user_id} - Pagination parameters
        """
        test_name = "Get User Plants - Pagination"

        try:
            response = requests.get(
                f"{self.api_base}/tracking/user/{user_id}",
                params={"page": 1, "limit": 2}
            )

            if response.status_code == 200:
                data = response.json()

                assert data["pagination"]["page"] == 1, "Page number mismatch"
                assert data["pagination"]["limit"] == 2, "Limit mismatch"
                assert len(data["plants"]) <= 2, "Returned more plants than limit"

                self.log_test(test_name, "PASS", {
                    "pagination": data["pagination"]
                })
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    def test_get_instance_details(self, instance_id: int):
        """
        Test: GET /tracking/instance/{instance_id} - Get detailed instance info
        """
        test_name = "Get Plant Instance Details"

        try:
            response = requests.get(f"{self.api_base}/tracking/instance/{instance_id}")

            if response.status_code == 200:
                data = response.json()

                # Validate comprehensive response structure
                assert "instance_id" in data, "Missing instance_id"
                assert "plant_details" in data, "Missing plant_details"
                assert "tracking_info" in data, "Missing tracking_info"
                assert "timeline" in data, "Missing timeline"
                assert "current_tips" in data, "Missing current_tips"

                # Validate nested structures
                assert "plant_id" in data["plant_details"], "Missing plant_id in plant_details"
                assert "current_stage" in data["tracking_info"], "Missing current_stage"
                assert "stages" in data["timeline"], "Missing stages in timeline"

                self.log_test(test_name, "PASS", {
                    "instance_id": data["instance_id"],
                    "current_stage": data["tracking_info"]["current_stage"],
                    "timeline_stages": len(data["timeline"]["stages"]),
                    "tips_count": len(data["current_tips"])
                })

                return data
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })
                return None

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})
            return None

    def test_get_instance_details_not_found(self):
        """
        Test: GET /tracking/instance/{instance_id} - Non-existent instance (404)
        """
        test_name = "Get Instance Details - Not Found"

        try:
            response = requests.get(f"{self.api_base}/tracking/instance/999999")

            if response.status_code == 404:
                self.log_test(test_name, "PASS", {
                    "status_code": response.status_code,
                    "expected": "404 Not Found"
                })
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "expected": 404
                })

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    def test_update_progress(self, instance_id: int, new_stage: str, notes: str):
        """
        Test: PUT /tracking/instance/{instance_id}/progress - Update plant progress
        """
        test_name = "Update Plant Progress"

        try:
            payload = {
                "current_stage": new_stage,
                "user_notes": notes
            }

            response = requests.put(
                f"{self.api_base}/tracking/instance/{instance_id}/progress",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()

                assert "message" in data, "Missing message in response"
                assert "data" in data, "Missing data in response"

                self.log_test(test_name, "PASS", {
                    "instance_id": instance_id,
                    "new_stage": new_stage,
                    "response": data
                })
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    def test_get_requirements(self, plant_id: int):
        """
        Test: GET /tracking/requirements/{plant_id} - Get AI-generated requirements
        """
        test_name = "Get Plant Requirements"

        try:
            response = requests.get(f"{self.api_base}/tracking/requirements/{plant_id}")

            if response.status_code == 200:
                data = response.json()

                assert "plant_id" in data, "Missing plant_id"
                assert "requirements" in data, "Missing requirements"
                assert isinstance(data["requirements"], list), "Requirements should be a list"

                self.log_test(test_name, "PASS", {
                    "plant_id": plant_id,
                    "categories_count": len(data["requirements"])
                })

                return data
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })
                return None

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})
            return None

    def test_get_instructions(self, plant_id: int):
        """
        Test: GET /tracking/instructions/{plant_id} - Get setup instructions
        """
        test_name = "Get Setup Instructions"

        try:
            response = requests.get(f"{self.api_base}/tracking/instructions/{plant_id}")

            if response.status_code == 200:
                data = response.json()

                assert "plant_id" in data, "Missing plant_id"
                assert "instructions" in data, "Missing instructions"
                assert isinstance(data["instructions"], list), "Instructions should be a list"

                self.log_test(test_name, "PASS", {
                    "plant_id": plant_id,
                    "steps_count": len(data["instructions"])
                })

                return data
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })
                return None

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})
            return None

    def test_get_timeline(self, plant_id: int):
        """
        Test: GET /tracking/timeline/{plant_id} - Get growth timeline
        """
        test_name = "Get Growth Timeline"

        try:
            response = requests.get(f"{self.api_base}/tracking/timeline/{plant_id}")

            if response.status_code == 200:
                data = response.json()

                assert "plant_id" in data, "Missing plant_id"
                assert "total_days" in data, "Missing total_days"
                assert "stages" in data, "Missing stages"
                assert isinstance(data["stages"], list), "Stages should be a list"

                self.log_test(test_name, "PASS", {
                    "plant_id": plant_id,
                    "total_days": data["total_days"],
                    "stages_count": len(data["stages"])
                })

                return data
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })
                return None

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})
            return None

    def test_get_current_tips(self, instance_id: int, limit: int = 3):
        """
        Test: GET /tracking/instance/{instance_id}/tips - Get current stage tips
        """
        test_name = "Get Current Stage Tips"

        try:
            response = requests.get(
                f"{self.api_base}/tracking/instance/{instance_id}/tips",
                params={"limit": limit}
            )

            if response.status_code == 200:
                data = response.json()

                assert "instance_id" in data, "Missing instance_id"
                assert "current_stage" in data, "Missing current_stage"
                assert "tips" in data, "Missing tips"
                assert len(data["tips"]) <= limit, f"Returned more than {limit} tips"

                self.log_test(test_name, "PASS", {
                    "instance_id": instance_id,
                    "current_stage": data["current_stage"],
                    "tips_count": len(data["tips"])
                })
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    def test_initialize_checklist(self, instance_id: int):
        """
        Test: POST /tracking/instance/{instance_id}/initialize-checklist
        """
        test_name = "Initialize Checklist"

        try:
            response = requests.post(
                f"{self.api_base}/tracking/instance/{instance_id}/initialize-checklist"
            )

            if response.status_code == 200:
                data = response.json()

                assert "message" in data, "Missing message"
                assert "data" in data, "Missing data"
                assert "items_created" in data["data"], "Missing items_created"

                self.log_test(test_name, "PASS", {
                    "instance_id": instance_id,
                    "items_created": data["data"]["items_created"]
                })

                return data["data"]["items_created"]
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })
                return 0

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})
            return 0

    def test_complete_checklist_item(self, instance_id: int, item_key: str):
        """
        Test: POST /tracking/checklist/complete - Mark checklist item complete
        """
        test_name = "Complete Checklist Item"

        try:
            payload = {
                "instance_id": instance_id,
                "checklist_item_key": item_key,
                "is_completed": True,
                "user_notes": "Test completion"
            }

            response = requests.post(
                f"{self.api_base}/tracking/checklist/complete",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()

                assert "success" in data, "Missing success field"
                assert "message" in data, "Missing message"
                assert "progress_summary" in data, "Missing progress_summary"

                self.log_test(test_name, "PASS", {
                    "instance_id": instance_id,
                    "item_key": item_key,
                    "progress": data["progress_summary"]
                })
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    def test_update_nickname(self, instance_id: int, new_nickname: str):
        """
        Test: PUT /tracking/instance/{instance_id}/nickname - Update plant nickname
        """
        test_name = "Update Plant Nickname"

        try:
            payload = {"plant_nickname": new_nickname}

            response = requests.put(
                f"{self.api_base}/tracking/instance/{instance_id}/nickname",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()

                assert "message" in data, "Missing message"
                assert "data" in data, "Missing data"
                assert data["data"]["plant_nickname"] == new_nickname, "Nickname not updated"

                self.log_test(test_name, "PASS", {
                    "instance_id": instance_id,
                    "new_nickname": new_nickname
                })
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    def test_update_nickname_empty(self, instance_id: int):
        """
        Test: PUT /tracking/instance/{instance_id}/nickname - Empty nickname (400 error)
        """
        test_name = "Update Nickname - Empty String"

        try:
            payload = {"plant_nickname": ""}

            response = requests.put(
                f"{self.api_base}/tracking/instance/{instance_id}/nickname",
                json=payload
            )

            if response.status_code == 400:
                self.log_test(test_name, "PASS", {
                    "status_code": response.status_code,
                    "expected": "400 Bad Request"
                })
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "expected": 400
                })

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    def test_auto_update_stage(self, instance_id: int):
        """
        Test: POST /tracking/instance/{instance_id}/auto-update-stage
        """
        test_name = "Auto Update Growth Stage"

        try:
            response = requests.post(
                f"{self.api_base}/tracking/instance/{instance_id}/auto-update-stage"
            )

            if response.status_code == 200:
                data = response.json()

                assert "message" in data, "Missing message"
                assert "data" in data, "Missing data"
                assert "updated" in data["data"], "Missing updated field"

                self.log_test(test_name, "PASS", {
                    "instance_id": instance_id,
                    "updated": data["data"]["updated"],
                    "new_stage": data["data"].get("new_stage")
                })
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    def test_deactivate_instance(self, instance_id: int):
        """
        Test: DELETE /tracking/instance/{instance_id} - Deactivate plant instance
        """
        test_name = "Deactivate Plant Instance"

        try:
            response = requests.delete(f"{self.api_base}/tracking/instance/{instance_id}")

            if response.status_code == 200:
                data = response.json()

                assert "message" in data, "Missing message"
                assert "data" in data, "Missing data"
                assert data["data"]["is_active"] == False, "Instance should be inactive"

                self.log_test(test_name, "PASS", {
                    "instance_id": instance_id,
                    "is_active": data["data"]["is_active"]
                })
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    def get_summary(self) -> Dict[str, Any]:
        """Generate test summary"""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = total - passed

        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "created_instances": self.created_instances,
            "results": self.test_results
        }


def run_comprehensive_tests():
    """Run all plant tracking tests"""
    print("\n" + "="*70)
    print("ITERATION 3 - PLANT TRACKING ENDPOINTS - COMPREHENSIVE TESTING")
    print("="*70 + "\n")

    tester = PlantTrackingTester()

    # Load test data
    with open('tests/iteration_3/fixtures/test_data.json', 'r') as f:
        test_data = json.load(f)

    user_data = test_data["test_user"]

    print("Phase 1: Core Tracking Endpoints")
    print("-" * 70)

    # Test 1: Start tracking - Success
    instance_id = tester.test_start_tracking_success(
        user_data=user_data,
        plant_id=1,  # Assuming plant ID 1 exists
        nickname=test_data["test_plants"][0]["nickname"],
        location=test_data["test_plants"][0]["location"]
    )

    # Test 2: Start tracking - Invalid plant
    tester.test_start_tracking_invalid_plant()

    if instance_id:
        # Test 3: Get user plants
        tester.test_get_user_plants(user_id=1, expected_count=1)

        # Test 4: Get user plants with pagination
        tester.test_get_user_plants_pagination(user_id=1)

        # Test 5: Get instance details
        tester.test_get_instance_details(instance_id)

        # Test 6: Get instance details - Not found
        tester.test_get_instance_details_not_found()

        # Test 7: Update progress
        tester.test_update_progress(
            instance_id,
            new_stage="seedling",
            notes=test_data["test_updates"]["user_notes"][0]
        )

        print("\nPhase 2: AI-Generated Data Endpoints")
        print("-" * 70)

        # Test 8: Get requirements
        tester.test_get_requirements(plant_id=1)

        # Test 9: Get instructions
        tester.test_get_instructions(plant_id=1)

        # Test 10: Get timeline
        tester.test_get_timeline(plant_id=1)

        # Test 11: Get current tips
        tester.test_get_current_tips(instance_id, limit=3)

        print("\nPhase 3: Checklist Management")
        print("-" * 70)

        # Test 12: Initialize checklist
        items_created = tester.test_initialize_checklist(instance_id)

        # Test 13: Complete checklist item
        if items_created > 0:
            tester.test_complete_checklist_item(instance_id, "test_item_key")

        print("\nPhase 4: Instance Management")
        print("-" * 70)

        # Test 14: Update nickname
        tester.test_update_nickname(instance_id, "Updated Test Nickname")

        # Test 15: Update nickname - Empty string
        tester.test_update_nickname_empty(instance_id)

        # Test 16: Auto update stage
        tester.test_auto_update_stage(instance_id)

        # Test 17: Deactivate instance (run last)
        tester.test_deactivate_instance(instance_id)

    # Generate summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    summary = tester.get_summary()
    print(f"\nTotal Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']} ✓")
    print(f"Failed: {summary['failed']} ✗")
    print(f"Pass Rate: {summary['pass_rate']:.2f}%")

    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"tests/iteration_3/reports/plant_tracking_results_{timestamp}.json"

    with open(report_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nDetailed results saved to: {report_file}")

    return summary


if __name__ == "__main__":
    run_comprehensive_tests()
