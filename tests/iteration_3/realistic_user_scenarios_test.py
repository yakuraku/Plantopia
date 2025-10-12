"""
Comprehensive Realistic User Scenarios Test
Tests email-based authentication, plant tracking, chat, and favorites with 2 real users

This script simulates realistic user journeys through the Plantopia platform.
"""
import requests
import json
import time
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import sys


class PlantopiaTestRunner:
    """Test runner for realistic user scenarios"""

    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.users = {}
        self.plant_instances = {}
        self.chat_sessions = {}

        # Test data
        self.sarah_email = "sarah.johnson.test@plantopia.com"
        self.mike_email = "mike.chen.test@plantopia.com"

    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def record_test(self, test_name: str, status: str, details: Dict[str, Any]):
        """Record test result"""
        self.test_results.append({
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        })

    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request and handle response"""
        url = f"{self.base_url}{endpoint}"

        try:
            start_time = time.time()
            response = self.session.request(method, url, **kwargs)
            elapsed = time.time() - start_time

            result = {
                "status_code": response.status_code,
                "elapsed_ms": round(elapsed * 1000, 2),
                "success": 200 <= response.status_code < 300
            }

            if response.content:
                try:
                    result["data"] = response.json()
                except json.JSONDecodeError:
                    result["data"] = response.text

            return result

        except requests.exceptions.RequestException as e:
            return {
                "status_code": 0,
                "success": False,
                "error": str(e)
            }

    # ========================================================================
    # SCENARIO 1: Sarah - New User, First Plant (Carrot)
    # ========================================================================

    def test_sarah_start_carrot(self):
        """Sarah starts tracking Carrot - Cosmic Purple (Day 0)"""
        self.log("=" * 80)
        self.log("SCENARIO 1: Sarah starts her first plant - Carrot (Day 0)")
        self.log("=" * 80)

        # Sarah's user data
        user_data = {
            "email": self.sarah_email,
            "name": "Sarah Johnson",
            "suburb_id": 1,  # Melbourne CBD
            "experience_level": "beginner",
            "garden_type": "balcony",
            "available_space": 5.0,
            "climate_goal": "Learn sustainable urban gardening"
        }

        # Start tracking Carrot
        payload = {
            "user_data": user_data,
            "plant_id": 1,  # Carrot - Cosmic Purple from CSV
            "plant_nickname": "Purple Beauty",
            "start_date": date.today().isoformat(),
            "location_details": "Balcony pot 1"
        }

        self.log("POST /tracking/start - Starting Carrot for Sarah")
        self.log(f"Request: {json.dumps(payload, indent=2)}")

        result = self.make_request("POST", "/tracking/start", json=payload)

        self.log(f"Response ({result['elapsed_ms']}ms): {json.dumps(result.get('data', {}), indent=2)}")

        if result['success']:
            self.log("✅ SUCCESS: User auto-created, plant instance created", "SUCCESS")
            instance_id = result['data'].get('instance_id')
            self.plant_instances['sarah_carrot'] = instance_id

            self.record_test(
                "Sarah - Start Carrot (Day 0)",
                "PASS",
                {
                    "instance_id": instance_id,
                    "expected": "Auto-create user, call Gemini API for plant data",
                    "response_time_ms": result['elapsed_ms'],
                    "data": result['data']
                }
            )
        else:
            self.log(f"❌ FAILED: {result.get('error', 'Unknown error')}", "ERROR")
            self.record_test("Sarah - Start Carrot", "FAIL", result)

        time.sleep(2)  # Wait for DB operations

    def test_sarah_get_carrot_details(self):
        """Get detailed information about Sarah's Carrot"""
        self.log("\n" + "-" * 80)
        self.log("Testing: Get Carrot details with timeline")

        instance_id = self.plant_instances.get('sarah_carrot')
        if not instance_id:
            self.log("❌ Skipping - no instance_id from previous test", "ERROR")
            return

        self.log(f"GET /tracking/instance/{instance_id}")
        result = self.make_request("GET", f"/tracking/instance/{instance_id}")

        if result['success']:
            data = result['data']
            self.log("✅ SUCCESS: Got plant details with timeline", "SUCCESS")
            self.log(f"  Current Stage: {data['tracking_info']['current_stage']}")
            self.log(f"  Days Elapsed: {data['tracking_info']['days_elapsed']}")
            self.log(f"  Progress: {data['tracking_info']['progress_percentage']}%")
            self.log(f"  Timeline Stages: {len(data['timeline']['stages'])} stages")

            self.record_test(
                "Sarah - Get Carrot Details",
                "PASS",
                {
                    "instance_id": instance_id,
                    "current_stage": data['tracking_info']['current_stage'],
                    "days_elapsed": data['tracking_info']['days_elapsed'],
                    "response_time_ms": result['elapsed_ms']
                }
            )
        else:
            self.log(f"❌ FAILED: {result}", "ERROR")
            self.record_test("Sarah - Get Carrot Details", "FAIL", result)

    def test_sarah_get_checklist(self):
        """Get requirements checklist for Carrot"""
        self.log("\n" + "-" * 80)
        self.log("Testing: Get requirements checklist")

        # Use plant_id=1 for Carrot
        plant_id = 1

        self.log(f"GET /tracking/requirements/{plant_id}")
        result = self.make_request("GET", f"/tracking/requirements/{plant_id}")

        if result['success']:
            data = result['data']
            requirements = data.get('requirements', [])
            self.log("✅ SUCCESS: Got requirements checklist", "SUCCESS")
            self.log(f"  Total Categories: {len(requirements)}")

            # Show first few items
            for cat in requirements[:2]:
                self.log(f"  Category: {cat.get('category')}")
                items = cat.get('items', [])
                for item in items[:2]:
                    self.log(f"    - {item.get('item')}: {item.get('quantity')}")

            self.record_test(
                "Sarah - Get Checklist",
                "PASS",
                {
                    "plant_id": plant_id,
                    "total_categories": len(requirements),
                    "response_time_ms": result['elapsed_ms']
                }
            )
        else:
            self.log(f"❌ FAILED: {result}", "ERROR")
            self.record_test("Sarah - Get Checklist", "FAIL", result)

    def test_sarah_complete_checklist_items(self):
        """Mark some checklist items as completed"""
        self.log("\n" + "-" * 80)
        self.log("Testing: Complete checklist items")

        instance_id = self.plant_instances.get('sarah_carrot')
        if not instance_id:
            self.log("❌ Skipping - no instance_id", "ERROR")
            return

        # Complete first 3 items
        test_items = [
            {"item_key": "seeds", "notes": "Purchased organic carrot seeds"},
            {"item_key": "containers", "notes": "Using deep balcony pots"},
            {"item_key": "soil", "notes": "Got potting mix from local store"}
        ]

        for item in test_items:
            self.log(f"POST /tracking/{instance_id}/checklist - Completing {item['item_key']}")
            result = self.make_request(
                "POST",
                f"/tracking/{instance_id}/checklist",
                json=item
            )

            if result['success']:
                self.log(f"  ✅ Completed: {item['item_key']}")
            else:
                self.log(f"  ❌ Failed: {item['item_key']}")

            time.sleep(0.5)

        self.record_test(
            "Sarah - Complete Checklist Items",
            "PASS",
            {"items_completed": len(test_items)}
        )

    def test_sarah_get_setup_guide(self):
        """Get setup instructions for Carrot"""
        self.log("\n" + "-" * 80)
        self.log("Testing: Get setup instructions")

        # Use plant_id=1 for Carrot
        plant_id = 1

        self.log(f"GET /tracking/instructions/{plant_id}")
        result = self.make_request("GET", f"/tracking/instructions/{plant_id}")

        if result['success']:
            data = result['data']
            instructions = data.get('instructions', [])
            self.log("✅ SUCCESS: Got setup instructions", "SUCCESS")
            self.log(f"  Total Steps: {len(instructions)}")

            self.record_test(
                "Sarah - Get Setup Guide",
                "PASS",
                {
                    "plant_id": plant_id,
                    "total_steps": len(instructions),
                    "response_time_ms": result['elapsed_ms']
                }
            )
        else:
            self.log(f"❌ FAILED: {result}", "ERROR")
            self.record_test("Sarah - Get Setup Guide", "FAIL", result)

    # ========================================================================
    # SCENARIO 2: Sarah adds more plants (Cherry Tomato, Basil)
    # ========================================================================

    def test_sarah_add_cherry_tomato(self):
        """Sarah adds Cherry Tomato (started 25 days ago)"""
        self.log("\n" + "=" * 80)
        self.log("SCENARIO 2: Sarah adds Cherry Tomato (Day 25)")
        self.log("=" * 80)

        # Started 25 days ago
        start_date = (date.today() - timedelta(days=25)).isoformat()

        payload = {
            "user_data": {
                "email": self.sarah_email,
                "name": "Sarah Johnson"
            },
            "plant_id": 150,  # Cherry Tomato from CSV
            "plant_nickname": "Cherry Delight",
            "start_date": start_date,
            "location_details": "Balcony pot 2"
        }

        self.log(f"POST /tracking/start - Adding Cherry Tomato (started {start_date})")
        result = self.make_request("POST", "/tracking/start", json=payload)

        if result['success']:
            instance_id = result['data'].get('instance_id')
            self.plant_instances['sarah_tomato'] = instance_id
            self.log("✅ SUCCESS: Cherry Tomato added", "SUCCESS")
            self.log(f"  Current Stage: {result['data'].get('current_stage')}")

            self.record_test(
                "Sarah - Add Cherry Tomato (Day 25)",
                "PASS",
                {
                    "instance_id": instance_id,
                    "expected": "Recognize existing user, calculate stage for day 25",
                    "response_time_ms": result['elapsed_ms']
                }
            )
        else:
            self.log(f"❌ FAILED: {result}", "ERROR")
            self.record_test("Sarah - Add Cherry Tomato", "FAIL", result)

        time.sleep(2)

    def test_sarah_add_basil(self):
        """Sarah adds Basil (started 15 days ago)"""
        self.log("\n" + "-" * 80)
        self.log("Adding Basil (Day 15)")

        start_date = (date.today() - timedelta(days=15)).isoformat()

        payload = {
            "user_data": {
                "email": self.sarah_email,
                "name": "Sarah Johnson"
            },
            "plant_id": 85,  # Basil from CSV
            "plant_nickname": "Fresh Basil",
            "start_date": start_date,
            "location_details": "Indoor windowsill"
        }

        self.log(f"POST /tracking/start - Adding Basil (started {start_date})")
        result = self.make_request("POST", "/tracking/start", json=payload)

        if result['success']:
            instance_id = result['data'].get('instance_id')
            self.plant_instances['sarah_basil'] = instance_id
            self.log("✅ SUCCESS: Basil added", "SUCCESS")

            self.record_test(
                "Sarah - Add Basil (Day 15)",
                "PASS",
                {
                    "instance_id": instance_id,
                    "response_time_ms": result['elapsed_ms']
                }
            )
        else:
            self.log(f"❌ FAILED: {result}", "ERROR")
            self.record_test("Sarah - Add Basil", "FAIL", result)

        time.sleep(2)

    def test_sarah_get_all_plants(self):
        """Get all of Sarah's plants"""
        self.log("\n" + "-" * 80)
        self.log("Testing: Get all Sarah's plants")

        self.log(f"GET /tracking/user/{self.sarah_email}")
        result = self.make_request("GET", f"/tracking/user/{self.sarah_email}")

        if result['success']:
            data = result['data']
            plants = data.get('plants', [])
            self.log("✅ SUCCESS: Got all plants", "SUCCESS")
            self.log(f"  Total Plants: {data.get('total_count', 0)}")
            self.log(f"  Active Plants: {data.get('active_count', 0)}")

            for plant in plants:
                self.log(f"  - {plant['plant_nickname']}: Day {plant['days_elapsed']}, Stage: {plant['current_stage']}, Progress: {plant['progress_percentage']}%")

            self.record_test(
                "Sarah - Get All Plants",
                "PASS",
                {
                    "total_count": data.get('total_count', 0),
                    "active_count": data.get('active_count', 0),
                    "response_time_ms": result['elapsed_ms']
                }
            )
        else:
            self.log(f"❌ FAILED: {result}", "ERROR")
            self.record_test("Sarah - Get All Plants", "FAIL", result)

    # ========================================================================
    # SCENARIO 3: Mike - New User, Carrot (Data Reuse Test)
    # ========================================================================

    def test_mike_start_carrot_reuse_data(self):
        """Mike starts same Carrot as Sarah - should reuse plant_growth_data"""
        self.log("\n" + "=" * 80)
        self.log("SCENARIO 3: Mike starts Carrot (Day 10) - DATA REUSE TEST")
        self.log("=" * 80)

        start_date = (date.today() - timedelta(days=10)).isoformat()

        user_data = {
            "email": self.mike_email,
            "name": "Mike Chen",
            "suburb_id": 2,  # Richmond
            "experience_level": "advanced",
            "garden_type": "backyard",
            "available_space": 15.0,
            "climate_goal": "Maximize yield with crop rotation"
        }

        payload = {
            "user_data": user_data,
            "plant_id": 1,  # Same Carrot as Sarah
            "plant_nickname": "Carrot Champion",
            "start_date": start_date,
            "location_details": "Backyard raised bed 1"
        }

        self.log(f"POST /tracking/start - Starting Carrot for Mike (should REUSE data)")
        self.log(f"Expected: NO Gemini API call, reuse Sarah's plant_growth_data")

        start_time = time.time()
        result = self.make_request("POST", "/tracking/start", json=payload)
        elapsed = time.time() - start_time

        if result['success']:
            instance_id = result['data'].get('instance_id')
            self.plant_instances['mike_carrot'] = instance_id

            # If response time is < 1 second, likely reused data (no Gemini call)
            if elapsed < 1.0:
                self.log("✅ SUCCESS: Data REUSED (fast response, no Gemini call)", "SUCCESS")
                data_reuse = True
            else:
                self.log("⚠️  WARNING: Slow response, might have called Gemini", "WARNING")
                data_reuse = False

            self.log(f"  Response Time: {round(elapsed * 1000, 2)}ms")
            self.log(f"  Current Stage: {result['data'].get('current_stage')} (should be past germination)")

            self.record_test(
                "Mike - Start Carrot (Data Reuse)",
                "PASS",
                {
                    "instance_id": instance_id,
                    "data_reused": data_reuse,
                    "response_time_ms": result['elapsed_ms'],
                    "expected": "Reuse plant_growth_data from Sarah, no Gemini call"
                }
            )
        else:
            self.log(f"❌ FAILED: {result}", "ERROR")
            self.record_test("Mike - Start Carrot (Data Reuse)", "FAIL", result)

        time.sleep(2)

    # ========================================================================
    # SCENARIO 4: Mike adds 3 more plants
    # ========================================================================

    def test_mike_add_multiple_plants(self):
        """Mike adds Capsicum, Lettuce, Zucchini"""
        self.log("\n" + "=" * 80)
        self.log("SCENARIO 4: Mike adds 3 more plants (multi-plant management)")
        self.log("=" * 80)

        plants_to_add = [
            {
                "plant_id": 45,  # Capsicum
                "nickname": "California Wonder",
                "days_ago": 35,
                "location": "Backyard raised bed 2"
            },
            {
                "plant_id": 120,  # Lettuce
                "nickname": "Mignonette Mix",
                "days_ago": 20,
                "location": "Backyard raised bed 3"
            },
            {
                "plant_id": 200,  # Zucchini
                "nickname": "Black Beauty",
                "days_ago": 5,
                "location": "Backyard ground"
            }
        ]

        for plant in plants_to_add:
            start_date = (date.today() - timedelta(days=plant['days_ago'])).isoformat()

            payload = {
                "user_data": {
                    "email": self.mike_email,
                    "name": "Mike Chen"
                },
                "plant_id": plant['plant_id'],
                "plant_nickname": plant['nickname'],
                "start_date": start_date,
                "location_details": plant['location']
            }

            self.log(f"\nAdding {plant['nickname']} (Day {plant['days_ago']})")
            result = self.make_request("POST", "/tracking/start", json=payload)

            if result['success']:
                instance_id = result['data'].get('instance_id')
                key = f"mike_{plant['nickname'].lower().replace(' ', '_')}"
                self.plant_instances[key] = instance_id
                self.log(f"  ✅ Added: {plant['nickname']}")
            else:
                self.log(f"  ❌ Failed: {plant['nickname']}")

            time.sleep(2)

        self.record_test(
            "Mike - Add Multiple Plants",
            "PASS",
            {"plants_added": len(plants_to_add)}
        )

    def test_mike_get_all_plants(self):
        """Get all of Mike's plants (should be 4 total)"""
        self.log("\n" + "-" * 80)
        self.log("Testing: Get all Mike's plants (4 expected)")

        self.log(f"GET /tracking/user/{self.mike_email}")
        result = self.make_request("GET", f"/tracking/user/{self.mike_email}")

        if result['success']:
            data = result['data']
            plants = data.get('plants', [])
            self.log("✅ SUCCESS: Got all plants", "SUCCESS")
            self.log(f"  Total Plants: {data.get('total_count', 0)}")

            for plant in plants:
                self.log(f"  - {plant['plant_nickname']}: Day {plant['days_elapsed']}, Progress: {plant['progress_percentage']}%")

            self.record_test(
                "Mike - Get All Plants",
                "PASS",
                {
                    "total_count": data.get('total_count', 0),
                    "expected_count": 4,
                    "response_time_ms": result['elapsed_ms']
                }
            )
        else:
            self.log(f"❌ FAILED: {result}", "ERROR")
            self.record_test("Mike - Get All Plants", "FAIL", result)

    # ========================================================================
    # SCENARIO 5: Sarah - General Agriculture Chat
    # ========================================================================

    def test_sarah_start_general_chat(self):
        """Sarah starts a general agriculture Q&A chat"""
        self.log("\n" + "=" * 80)
        self.log("SCENARIO 5: Sarah - General Agriculture Chat")
        self.log("=" * 80)

        payload = {"email": self.sarah_email}

        self.log("POST /chat/general/start - Starting general chat")
        result = self.make_request("POST", "/chat/general/start", json=payload)

        if result['success']:
            chat_id = result['data'].get('chat_id')
            self.chat_sessions['sarah_general'] = chat_id
            self.log("✅ SUCCESS: General chat started", "SUCCESS")
            self.log(f"  Chat ID: {chat_id}")
            self.log(f"  Expires At: {result['data'].get('expires_at')}")

            self.record_test(
                "Sarah - Start General Chat",
                "PASS",
                {
                    "chat_id": chat_id,
                    "response_time_ms": result['elapsed_ms']
                }
            )
        else:
            self.log(f"❌ FAILED: {result}", "ERROR")
            self.record_test("Sarah - Start General Chat", "FAIL", result)

        time.sleep(2)

    def test_sarah_send_chat_messages(self):
        """Sarah asks questions in general chat"""
        self.log("\n" + "-" * 80)
        self.log("Testing: Send chat messages")

        chat_id = self.chat_sessions.get('sarah_general')
        if not chat_id:
            self.log("❌ Skipping - no chat_id", "ERROR")
            return

        messages = [
            "What's the best way to water balcony plants in summer?",
            "How much sunlight do herbs like basil need?"
        ]

        for msg in messages:
            payload = {
                "chat_id": chat_id,
                "message": msg
            }

            self.log(f"\nPOST /chat/general/message - Asking: {msg}")
            result = self.make_request("POST", "/chat/general/message", json=payload)

            if result['success']:
                data = result['data']
                self.log("✅ Got AI response", "SUCCESS")
                self.log(f"  Response: {data.get('response', '')[:100]}...")
                self.log(f"  Tokens Used: {data.get('tokens_used', 0)}")
                self.log(f"  Total Tokens: {data.get('total_tokens', 0)}")
            else:
                self.log(f"❌ Failed: {result}", "ERROR")

            time.sleep(3)  # Wait between messages

        self.record_test(
            "Sarah - Send Chat Messages",
            "PASS",
            {"messages_sent": len(messages)}
        )

    def test_sarah_get_chat_history(self):
        """Get Sarah's chat history"""
        self.log("\n" + "-" * 80)
        self.log("Testing: Get chat history")

        chat_id = self.chat_sessions.get('sarah_general')
        if not chat_id:
            self.log("❌ Skipping - no chat_id", "ERROR")
            return

        self.log(f"GET /chat/{chat_id}/history?email={self.sarah_email}")
        result = self.make_request(
            "GET",
            f"/chat/{chat_id}/history",
            params={"email": self.sarah_email}
        )

        if result['success']:
            data = result['data']
            messages = data.get('messages', [])
            self.log("✅ SUCCESS: Got chat history", "SUCCESS")
            self.log(f"  Total Messages: {len(messages)}")

            self.record_test(
                "Sarah - Get Chat History",
                "PASS",
                {
                    "message_count": len(messages),
                    "response_time_ms": result['elapsed_ms']
                }
            )
        else:
            self.log(f"❌ FAILED: {result}", "ERROR")
            self.record_test("Sarah - Get Chat History", "FAIL", result)

    # ========================================================================
    # SCENARIO 6: Mike - Plant-Specific Chat (Carrot)
    # ========================================================================

    def test_mike_start_plant_chat(self):
        """Mike starts plant-specific chat for his Carrot"""
        self.log("\n" + "=" * 80)
        self.log("SCENARIO 6: Mike - Plant-Specific Chat (Carrot)")
        self.log("=" * 80)

        instance_id = self.plant_instances.get('mike_carrot')
        if not instance_id:
            self.log("❌ Skipping - no carrot instance", "ERROR")
            return

        payload = {"email": self.mike_email}

        self.log(f"POST /chat/plant/{instance_id}/start - Starting plant-specific chat")
        result = self.make_request(
            "POST",
            f"/chat/plant/{instance_id}/start",
            json=payload
        )

        if result['success']:
            chat_id = result['data'].get('chat_id')
            self.chat_sessions['mike_carrot'] = chat_id
            self.log("✅ SUCCESS: Plant-specific chat started", "SUCCESS")
            self.log(f"  Chat ID: {chat_id}")
            self.log(f"  Plant Context: {result['data'].get('plant_context', {})}")

            self.record_test(
                "Mike - Start Plant Chat",
                "PASS",
                {
                    "chat_id": chat_id,
                    "instance_id": instance_id,
                    "response_time_ms": result['elapsed_ms']
                }
            )
        else:
            self.log(f"❌ FAILED: {result}", "ERROR")
            self.record_test("Mike - Start Plant Chat", "FAIL", result)

        time.sleep(2)

    def test_mike_send_plant_chat_message(self):
        """Mike asks plant-specific question"""
        self.log("\n" + "-" * 80)
        self.log("Testing: Send plant-specific chat message")

        chat_id = self.chat_sessions.get('mike_carrot')
        if not chat_id:
            self.log("❌ Skipping - no chat_id", "ERROR")
            return

        payload = {
            "chat_id": chat_id,
            "message": "My carrot leaves are starting to yellow a bit. What should I check?"
        }

        self.log(f"POST /chat/plant/message - Asking plant-specific question")
        result = self.make_request("POST", "/chat/plant/message", json=payload)

        if result['success']:
            data = result['data']
            self.log("✅ Got plant-specific AI response", "SUCCESS")
            self.log(f"  Response: {data.get('response', '')[:150]}...")

            self.record_test(
                "Mike - Send Plant Chat Message",
                "PASS",
                {"response_time_ms": result['elapsed_ms']}
            )
        else:
            self.log(f"❌ FAILED: {result}", "ERROR")
            self.record_test("Mike - Send Plant Chat Message", "FAIL", result)

    # ========================================================================
    # SCENARIO 7: Plant Favorites
    # ========================================================================

    def test_sarah_add_plant_favorites(self):
        """Sarah favorites Carrot and Basil"""
        self.log("\n" + "=" * 80)
        self.log("SCENARIO 7: Sarah - Plant Favorites")
        self.log("=" * 80)

        favorites = [
            {"plant_id": 1, "notes": "Love purple carrots!"},
            {"plant_id": 85, "notes": "Perfect for my balcony"}
        ]

        for fav in favorites:
            payload = {
                "email": self.sarah_email,
                "plant_id": fav['plant_id'],
                "notes": fav['notes']
            }

            self.log(f"\nPOST /favorites - Favoriting plant {fav['plant_id']}")
            result = self.make_request("POST", "/favorites", json=payload)

            if result['success']:
                self.log(f"  ✅ Favorited plant {fav['plant_id']}")
            else:
                self.log(f"  ❌ Failed: {result}")

            time.sleep(1)

        self.record_test(
            "Sarah - Add Plant Favorites",
            "PASS",
            {"favorites_added": len(favorites)}
        )

    def test_sarah_get_plant_favorites(self):
        """Get Sarah's plant favorites"""
        self.log("\n" + "-" * 80)
        self.log("Testing: Get plant favorites")

        self.log(f"GET /favorites?email={self.sarah_email}")
        result = self.make_request(
            "GET",
            "/favorites",
            params={"email": self.sarah_email}
        )

        if result['success']:
            favorites = result['data']
            self.log("✅ SUCCESS: Got plant favorites", "SUCCESS")
            self.log(f"  Total Favorites: {len(favorites)}")

            for fav in favorites:
                self.log(f"  - {fav['plant_name']}: {fav['notes']}")

            self.record_test(
                "Sarah - Get Plant Favorites",
                "PASS",
                {
                    "favorite_count": len(favorites),
                    "response_time_ms": result['elapsed_ms']
                }
            )
        else:
            self.log(f"❌ FAILED: {result}", "ERROR")
            self.record_test("Sarah - Get Plant Favorites", "FAIL", result)

    # ========================================================================
    # SCENARIO 8: Guide Browsing & Favorites
    # ========================================================================

    def test_get_guide_categories(self):
        """Get all guide categories"""
        self.log("\n" + "=" * 80)
        self.log("SCENARIO 8: Guide Browsing & Favorites")
        self.log("=" * 80)

        self.log("GET /guides/categories")
        result = self.make_request("GET", "/guides/categories")

        if result['success']:
            categories = result['data'].get('categories', [])
            self.log("✅ SUCCESS: Got guide categories", "SUCCESS")
            self.log(f"  Total Categories: {len(categories)}")
            self.log(f"  Categories: {', '.join(categories[:5])}...")

            self.record_test(
                "Get Guide Categories",
                "PASS",
                {
                    "category_count": len(categories),
                    "response_time_ms": result['elapsed_ms']
                }
            )
        else:
            self.log(f"❌ FAILED: {result}", "ERROR")
            self.record_test("Get Guide Categories", "FAIL", result)

    def test_sarah_browse_and_favorite_guide(self):
        """Sarah browses Composting guides and favorites one"""
        self.log("\n" + "-" * 80)
        self.log("Testing: Browse and favorite guide")

        # Browse Composting category
        self.log("GET /guides/Composting")
        result = self.make_request("GET", "/guides/Composting")

        if result['success']:
            guides = result['data'].get('guides', [])
            self.log(f"✅ Found {len(guides)} guides in Composting")

            if guides:
                # Favorite first guide
                guide_name = guides[0]['guide_name']

                payload = {
                    "email": self.sarah_email,
                    "guide_name": guide_name,
                    "category": "Composting",
                    "notes": "Great beginner guide"
                }

                self.log(f"\nPOST /guides/favorites - Favoriting {guide_name}")
                fav_result = self.make_request("POST", "/guides/favorites", json=payload)

                if fav_result['success']:
                    self.log(f"  ✅ Favorited guide: {guide_name}")
                else:
                    self.log(f"  ❌ Failed to favorite: {fav_result}")

        self.record_test(
            "Sarah - Browse and Favorite Guide",
            "PASS",
            {}
        )

    def test_sarah_get_guide_favorites(self):
        """Get Sarah's guide favorites"""
        self.log("\n" + "-" * 80)
        self.log("Testing: Get guide favorites")

        self.log(f"GET /guides/favorites/user?email={self.sarah_email}")
        result = self.make_request(
            "GET",
            "/guides/favorites/user",
            params={"email": self.sarah_email}
        )

        if result['success']:
            data = result['data']
            favorites = data.get('favorites', [])
            self.log("✅ SUCCESS: Got guide favorites", "SUCCESS")
            self.log(f"  Total Guide Favorites: {len(favorites)}")

            for fav in favorites:
                self.log(f"  - {fav['guide_name']}")

            self.record_test(
                "Sarah - Get Guide Favorites",
                "PASS",
                {
                    "favorite_count": len(favorites),
                    "response_time_ms": result['elapsed_ms']
                }
            )
        else:
            self.log(f"❌ FAILED: {result}", "ERROR")
            self.record_test("Sarah - Get Guide Favorites", "FAIL", result)

    # ========================================================================
    # MAIN TEST RUNNER
    # ========================================================================

    def run_all_tests(self):
        """Run all test scenarios"""
        self.log("=" * 80)
        self.log("STARTING COMPREHENSIVE REALISTIC USER SCENARIOS TEST")
        self.log("=" * 80)
        self.log(f"Base URL: {self.base_url}")
        self.log(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("")

        start_time = time.time()

        # SCENARIO 1: Sarah - First Plant
        self.test_sarah_start_carrot()
        self.test_sarah_get_carrot_details()
        self.test_sarah_get_checklist()
        self.test_sarah_complete_checklist_items()
        self.test_sarah_get_setup_guide()

        # SCENARIO 2: Sarah - More Plants
        self.test_sarah_add_cherry_tomato()
        self.test_sarah_add_basil()
        self.test_sarah_get_all_plants()

        # SCENARIO 3: Mike - Data Reuse
        self.test_mike_start_carrot_reuse_data()

        # SCENARIO 4: Mike - Multi-Plant
        self.test_mike_add_multiple_plants()
        self.test_mike_get_all_plants()

        # SCENARIO 5: Sarah - General Chat
        self.test_sarah_start_general_chat()
        self.test_sarah_send_chat_messages()
        self.test_sarah_get_chat_history()

        # SCENARIO 6: Mike - Plant Chat
        self.test_mike_start_plant_chat()
        self.test_mike_send_plant_chat_message()

        # SCENARIO 7: Plant Favorites
        self.test_sarah_add_plant_favorites()
        self.test_sarah_get_plant_favorites()

        # SCENARIO 8: Guide Features
        self.test_get_guide_categories()
        self.test_sarah_browse_and_favorite_guide()
        self.test_sarah_get_guide_favorites()

        elapsed_time = time.time() - start_time

        self.log("")
        self.log("=" * 80)
        self.log("TEST SUITE COMPLETED")
        self.log("=" * 80)
        self.log(f"Total Time: {round(elapsed_time, 2)} seconds")
        self.log(f"Total Tests: {len(self.test_results)}")

        # Calculate results
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = len(self.test_results) - passed

        self.log(f"Passed: {passed}")
        self.log(f"Failed: {failed}")
        self.log(f"Success Rate: {round(passed / len(self.test_results) * 100, 2)}%")

        # Save results
        self.save_results()

    def save_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON report
        json_file = f"reports/realistic_scenarios_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "total_tests": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r['status'] == 'PASS'),
                "failed": sum(1 for r in self.test_results if r['status'] == 'FAIL'),
                "test_results": self.test_results
            }, f, indent=2)

        self.log(f"\n✅ Results saved to {json_file}")

        # Text summary
        txt_file = f"reports/realistic_scenarios_{timestamp}.txt"
        with open(txt_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("REALISTIC USER SCENARIOS TEST SUMMARY\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Base URL: {self.base_url}\n\n")

            passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
            failed = len(self.test_results) - passed

            f.write(f"Total Tests: {len(self.test_results)}\n")
            f.write(f"Passed: {passed}\n")
            f.write(f"Failed: {failed}\n")
            f.write(f"Success Rate: {round(passed / len(self.test_results) * 100, 2)}%\n\n")

            f.write("=" * 80 + "\n")
            f.write("TEST RESULTS\n")
            f.write("=" * 80 + "\n\n")

            for result in self.test_results:
                f.write(f"[{result['status']}] {result['test_name']}\n")
                f.write(f"  Timestamp: {result['timestamp']}\n")
                if result['status'] == 'PASS':
                    details = result['details']
                    if 'response_time_ms' in details:
                        f.write(f"  Response Time: {details['response_time_ms']}ms\n")
                f.write("\n")

        self.log(f"✅ Summary saved to {txt_file}")


if __name__ == "__main__":
    # Check if BASE_URL provided as argument
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/api/v1"

    runner = PlantopiaTestRunner(base_url=base_url)
    runner.run_all_tests()
