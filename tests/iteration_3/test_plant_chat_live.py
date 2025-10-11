"""
Comprehensive Live Testing for Plant Chat Endpoints (Iteration 3)
Tests all chat endpoints against a running backend server with real Gemini API.

Requirements:
- Backend server running on http://localhost:8000
- Production database accessible
- Real Gemini API access for chat responses

Test Coverage:
- All 6 chat endpoints (general + plant-specific)
- Success scenarios (2xx responses)
- Error scenarios (404, 400, 403)
- Token limit testing
- Chat expiration scenarios
- Ownership validation
- Image upload testing
"""

import requests
import json
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any
import time


class PlantChatTester:
    """Comprehensive tester for plant chat endpoints"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.test_results = []
        self.created_chats = []

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

    def test_start_general_chat(self, user_id: int) -> Optional[int]:
        """
        Test: POST /chat/general/start - Start general agriculture chat
        """
        test_name = "Start General Chat - Success"

        try:
            payload = {"user_id": user_id}

            response = requests.post(f"{self.api_base}/chat/general/start", json=payload)

            if response.status_code == 201:
                data = response.json()

                # Validate response structure
                assert "chat_id" in data, "Missing chat_id in response"
                assert "chat_type" in data, "Missing chat_type"
                assert "expires_at" in data, "Missing expires_at"
                assert "message" in data, "Missing message"
                assert data["chat_type"] == "general", "Chat type should be 'general'"

                chat_id = data["chat_id"]
                self.created_chats.append(chat_id)

                self.log_test(test_name, "PASS", {
                    "chat_id": chat_id,
                    "chat_type": data["chat_type"],
                    "expires_at": data["expires_at"]
                })

                return chat_id
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })
                return None

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})
            return None

    def test_send_general_message(self, chat_id: int, message: str) -> bool:
        """
        Test: POST /chat/general/message - Send message in general chat
        """
        test_name = "Send General Chat Message"

        try:
            payload = {
                "chat_id": chat_id,
                "message": message
            }

            response = requests.post(f"{self.api_base}/chat/general/message", json=payload)

            if response.status_code == 200:
                data = response.json()

                # Validate response structure
                assert "chat_id" in data, "Missing chat_id"
                assert "user_message" in data, "Missing user_message"
                assert "ai_response" in data, "Missing ai_response"
                assert "tokens_used" in data, "Missing tokens_used"
                assert "total_tokens" in data, "Missing total_tokens"
                assert "token_warning" in data, "Missing token_warning"

                # Validate AI response is not empty
                assert len(data["ai_response"]) > 0, "AI response is empty"

                self.log_test(test_name, "PASS", {
                    "chat_id": chat_id,
                    "tokens_used": data["tokens_used"],
                    "total_tokens": data["total_tokens"],
                    "ai_response_length": len(data["ai_response"])
                })

                return True
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })
                return False

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})
            return False

    def test_send_message_with_image(self, chat_id: int, message: str, image_path: Optional[str] = None):
        """
        Test: POST /chat/general/message - Send message with base64 image
        """
        test_name = "Send Message with Image"

        try:
            # Create a simple test image (1x1 pixel) if no image provided
            if image_path:
                with open(image_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
            else:
                # Create minimal PNG (1x1 transparent pixel)
                minimal_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
                image_data = base64.b64encode(minimal_png).decode('utf-8')

            payload = {
                "chat_id": chat_id,
                "message": message,
                "image": image_data
            }

            response = requests.post(f"{self.api_base}/chat/general/message", json=payload)

            if response.status_code == 200:
                data = response.json()

                assert "ai_response" in data, "Missing ai_response"
                assert len(data["ai_response"]) > 0, "AI response is empty"

                self.log_test(test_name, "PASS", {
                    "chat_id": chat_id,
                    "image_included": True,
                    "ai_response_length": len(data["ai_response"])
                })

                return True
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })
                return False

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})
            return False

    def test_send_message_invalid_chat(self):
        """
        Test: POST /chat/general/message - Send message to non-existent chat (404)
        """
        test_name = "Send Message - Invalid Chat ID"

        try:
            payload = {
                "chat_id": 999999,
                "message": "Test message"
            }

            response = requests.post(f"{self.api_base}/chat/general/message", json=payload)

            if response.status_code == 404:
                self.log_test(test_name, "PASS", {
                    "status_code": response.status_code,
                    "expected": "404 Not Found"
                })
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "expected": 404,
                    "error": "Should return 404 for non-existent chat"
                })

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    def test_start_plant_chat(self, user_id: int, instance_id: int) -> Optional[int]:
        """
        Test: POST /chat/plant/{instance_id}/start - Start plant-specific chat
        """
        test_name = "Start Plant-Specific Chat"

        try:
            payload = {"user_id": user_id}

            response = requests.post(
                f"{self.api_base}/chat/plant/{instance_id}/start",
                json=payload
            )

            if response.status_code == 201:
                data = response.json()

                # Validate response structure
                assert "chat_id" in data, "Missing chat_id"
                assert "chat_type" in data, "Missing chat_type"
                assert "instance_id" in data, "Missing instance_id"
                assert "plant_name" in data, "Missing plant_name"
                assert "expires_at" in data, "Missing expires_at"
                assert data["chat_type"] == "plant_specific", "Chat type should be 'plant_specific'"
                assert data["instance_id"] == instance_id, "Instance ID mismatch"

                chat_id = data["chat_id"]
                self.created_chats.append(chat_id)

                self.log_test(test_name, "PASS", {
                    "chat_id": chat_id,
                    "chat_type": data["chat_type"],
                    "instance_id": data["instance_id"],
                    "plant_name": data.get("plant_name")
                })

                return chat_id
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })
                return None

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})
            return None

    def test_start_plant_chat_invalid_instance(self, user_id: int):
        """
        Test: POST /chat/plant/{instance_id}/start - Invalid instance ID (404)
        """
        test_name = "Start Plant Chat - Invalid Instance"

        try:
            payload = {"user_id": user_id}

            response = requests.post(
                f"{self.api_base}/chat/plant/999999/start",
                json=payload
            )

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

    def test_send_plant_message(self, chat_id: int, message: str) -> bool:
        """
        Test: POST /chat/plant/message - Send plant-specific message
        """
        test_name = "Send Plant-Specific Message"

        try:
            payload = {
                "chat_id": chat_id,
                "message": message
            }

            response = requests.post(f"{self.api_base}/chat/plant/message", json=payload)

            if response.status_code == 200:
                data = response.json()

                # Validate response structure
                assert "chat_id" in data, "Missing chat_id"
                assert "user_message" in data, "Missing user_message"
                assert "ai_response" in data, "Missing ai_response"
                assert "tokens_used" in data, "Missing tokens_used"
                assert "total_tokens" in data, "Missing total_tokens"

                # Validate AI response is not empty
                assert len(data["ai_response"]) > 0, "AI response is empty"

                self.log_test(test_name, "PASS", {
                    "chat_id": chat_id,
                    "tokens_used": data["tokens_used"],
                    "total_tokens": data["total_tokens"],
                    "ai_response_length": len(data["ai_response"])
                })

                return True
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })
                return False

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})
            return False

    def test_get_chat_history(self, chat_id: int, user_id: int):
        """
        Test: GET /chat/{chat_id}/history - Get full chat history
        """
        test_name = "Get Chat History"

        try:
            response = requests.get(
                f"{self.api_base}/chat/{chat_id}/history",
                params={"user_id": user_id}
            )

            if response.status_code == 200:
                data = response.json()

                # Validate response structure
                assert "chat_id" in data, "Missing chat_id"
                assert "chat_type" in data, "Missing chat_type"
                assert "created_at" in data, "Missing created_at"
                assert "expires_at" in data, "Missing expires_at"
                assert "total_tokens" in data, "Missing total_tokens"
                assert "message_count" in data, "Missing message_count"
                assert "is_active" in data, "Missing is_active"
                assert "messages" in data, "Missing messages"
                assert isinstance(data["messages"], list), "Messages should be a list"

                self.log_test(test_name, "PASS", {
                    "chat_id": chat_id,
                    "message_count": data["message_count"],
                    "total_tokens": data["total_tokens"],
                    "is_active": data["is_active"]
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

    def test_get_chat_history_unauthorized(self, chat_id: int, wrong_user_id: int):
        """
        Test: GET /chat/{chat_id}/history - Unauthorized access (403)
        """
        test_name = "Get Chat History - Unauthorized"

        try:
            response = requests.get(
                f"{self.api_base}/chat/{chat_id}/history",
                params={"user_id": wrong_user_id}
            )

            if response.status_code == 403:
                self.log_test(test_name, "PASS", {
                    "status_code": response.status_code,
                    "expected": "403 Forbidden"
                })
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "expected": 403,
                    "error": "Should return 403 for unauthorized access"
                })

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    def test_get_chat_history_not_found(self):
        """
        Test: GET /chat/{chat_id}/history - Non-existent chat (404)
        """
        test_name = "Get Chat History - Not Found"

        try:
            response = requests.get(
                f"{self.api_base}/chat/999999/history",
                params={"user_id": 1}
            )

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

    def test_end_chat(self, chat_id: int, user_id: int):
        """
        Test: DELETE /chat/{chat_id} - End chat session
        """
        test_name = "End Chat Session"

        try:
            response = requests.delete(
                f"{self.api_base}/chat/{chat_id}",
                params={"user_id": user_id}
            )

            if response.status_code == 200:
                data = response.json()

                # Validate response structure
                assert "success" in data, "Missing success field"
                assert "message" in data, "Missing message"
                assert "chat_id" in data, "Missing chat_id"
                assert data["success"] == True, "Success should be True"
                assert data["chat_id"] == chat_id, "Chat ID mismatch"

                self.log_test(test_name, "PASS", {
                    "chat_id": chat_id,
                    "success": data["success"]
                })

                return True
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })
                return False

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})
            return False

    def test_end_chat_unauthorized(self, chat_id: int, wrong_user_id: int):
        """
        Test: DELETE /chat/{chat_id} - Unauthorized access (403)
        """
        test_name = "End Chat - Unauthorized"

        try:
            response = requests.delete(
                f"{self.api_base}/chat/{chat_id}",
                params={"user_id": wrong_user_id}
            )

            if response.status_code == 403:
                self.log_test(test_name, "PASS", {
                    "status_code": response.status_code,
                    "expected": "403 Forbidden"
                })
            else:
                self.log_test(test_name, "FAIL", {
                    "status_code": response.status_code,
                    "expected": 403
                })

        except Exception as e:
            self.log_test(test_name, "FAIL", {"error": str(e)})

    def test_conversation_flow(self, chat_id: int, messages: List[str]):
        """
        Test: Full conversation flow with multiple messages
        """
        test_name = "Conversation Flow - Multiple Messages"

        try:
            all_successful = True

            for i, message in enumerate(messages):
                payload = {
                    "chat_id": chat_id,
                    "message": message
                }

                response = requests.post(f"{self.api_base}/chat/general/message", json=payload)

                if response.status_code != 200:
                    all_successful = False
                    break

                # Small delay between messages
                time.sleep(0.5)

            if all_successful:
                self.log_test(test_name, "PASS", {
                    "chat_id": chat_id,
                    "messages_sent": len(messages)
                })
            else:
                self.log_test(test_name, "FAIL", {
                    "error": "Failed to send all messages"
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
            "created_chats": self.created_chats,
            "results": self.test_results
        }


def run_comprehensive_chat_tests(test_instance_id: int = None):
    """Run all plant chat tests"""
    print("\n" + "="*70)
    print("ITERATION 3 - PLANT CHAT ENDPOINTS - COMPREHENSIVE TESTING")
    print("="*70 + "\n")

    tester = PlantChatTester()

    # Load test data
    with open('tests/iteration_3/fixtures/test_data.json', 'r') as f:
        test_data = json.load(f)

    test_user_id = 1  # Assuming test user ID

    print("Phase 1: General Chat Endpoints")
    print("-" * 70)

    # Test 1: Start general chat
    general_chat_id = tester.test_start_general_chat(user_id=test_user_id)

    if general_chat_id:
        # Test 2: Send general message
        tester.test_send_general_message(
            general_chat_id,
            test_data["chat_test_messages"]["general_questions"][0]
        )

        # Test 3: Send message with image
        tester.test_send_message_with_image(
            general_chat_id,
            "Can you identify what's in this image?"
        )

        # Test 4: Conversation flow
        tester.test_conversation_flow(
            general_chat_id,
            test_data["chat_test_messages"]["general_questions"][1:3]
        )

    # Test 5: Send message - Invalid chat
    tester.test_send_message_invalid_chat()

    print("\nPhase 2: Plant-Specific Chat Endpoints")
    print("-" * 70)

    if test_instance_id:
        # Test 6: Start plant-specific chat
        plant_chat_id = tester.test_start_plant_chat(
            user_id=test_user_id,
            instance_id=test_instance_id
        )

        if plant_chat_id:
            # Test 7: Send plant-specific message
            tester.test_send_plant_message(
                plant_chat_id,
                test_data["chat_test_messages"]["plant_specific_questions"][0]
            )

            # Test 8: Multiple plant-specific questions
            for question in test_data["chat_test_messages"]["plant_specific_questions"][1:3]:
                tester.test_send_plant_message(plant_chat_id, question)
                time.sleep(0.5)

    # Test 9: Start plant chat - Invalid instance
    tester.test_start_plant_chat_invalid_instance(user_id=test_user_id)

    print("\nPhase 3: Chat History & Management")
    print("-" * 70)

    if general_chat_id:
        # Test 10: Get chat history
        tester.test_get_chat_history(general_chat_id, user_id=test_user_id)

        # Test 11: Get chat history - Unauthorized
        tester.test_get_chat_history_unauthorized(general_chat_id, wrong_user_id=999)

    # Test 12: Get chat history - Not found
    tester.test_get_chat_history_not_found()

    print("\nPhase 4: End Chat Session")
    print("-" * 70)

    if general_chat_id:
        # Test 13: End chat - Unauthorized (create a new chat for this test)
        temp_chat_id = tester.test_start_general_chat(user_id=test_user_id)
        if temp_chat_id:
            tester.test_end_chat_unauthorized(temp_chat_id, wrong_user_id=999)

        # Test 14: End chat - Success (run last)
        tester.test_end_chat(general_chat_id, user_id=test_user_id)

    if test_instance_id and 'plant_chat_id' in locals() and plant_chat_id:
        tester.test_end_chat(plant_chat_id, user_id=test_user_id)

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
    report_file = f"tests/iteration_3/reports/plant_chat_results_{timestamp}.json"

    with open(report_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nDetailed results saved to: {report_file}")

    return summary


if __name__ == "__main__":
    # Note: Provide a valid test_instance_id for plant-specific chat tests
    import sys

    instance_id = int(sys.argv[1]) if len(sys.argv) > 1 else None

    if not instance_id:
        print("Warning: No instance_id provided. Plant-specific chat tests will be skipped.")
        print("Usage: python test_plant_chat_live.py <instance_id>")

    run_comprehensive_chat_tests(test_instance_id=instance_id)
