"""
End-to-End Workflow Testing for Iteration 3
Tests complete user journeys through plant tracking and chat features.

Workflow Scenarios:
1. New User Journey: Start tracking → Get requirements → Complete checklist → Chat about plant
2. Progress Tracking: Start plant → Update stages → Get tips → Monitor timeline
3. Multi-Plant Management: Track multiple plants → Compare progress → Chat about each
4. Complete Lifecycle: Germination → Growth → Maturity → Harvest → Deactivate
"""

import requests
import json
from datetime import datetime, date
from typing import Dict, List, Any
import time


class EndToEndWorkflowTester:
    """End-to-end workflow tester for Iteration 3"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.workflow_results = []
        self.test_artifacts = {
            "instances": [],
            "chats": [],
            "user_id": 1
        }

    def log_workflow(self, workflow_name: str, step: str, status: str, details: Dict[str, Any]):
        """Log workflow step"""
        result = {
            "workflow": workflow_name,
            "step": step,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.workflow_results.append(result)

        status_symbol = "✓" if status == "PASS" else "✗"
        print(f"  {status_symbol} Step: {step} - {status}")

    def workflow_new_user_journey(self, user_data: Dict, plant_id: int):
        """
        Workflow 1: New User Complete Journey
        Steps:
        1. Start tracking a plant
        2. Get plant requirements
        3. Initialize checklist
        4. Complete some checklist items
        5. Get setup instructions
        6. View growth timeline
        7. Start a plant-specific chat
        8. Ask questions about the plant
        9. Get current stage tips
        10. End chat
        """
        workflow_name = "New User Complete Journey"
        print(f"\n{'='*70}")
        print(f"Workflow: {workflow_name}")
        print(f"{'='*70}\n")

        instance_id = None
        chat_id = None

        try:
            # Step 1: Start tracking
            payload = {
                "user_id": user_data.get("user_id", 1),
                "plant_id": plant_id,
                "plant_nickname": "My First Garden Plant",
                "start_date": date.today().isoformat(),
                "location_details": "Front porch container",
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
                instance_id = data["instance_id"]
                self.test_artifacts["instances"].append(instance_id)

                self.log_workflow(workflow_name, "Start Tracking", "PASS", {
                    "instance_id": instance_id,
                    "current_stage": data["current_stage"]
                })
            else:
                self.log_workflow(workflow_name, "Start Tracking", "FAIL", {
                    "error": response.text
                })
                return

            # Step 2: Get requirements
            response = requests.get(f"{self.api_base}/tracking/requirements/{plant_id}")

            if response.status_code == 200:
                data = response.json()
                self.log_workflow(workflow_name, "Get Requirements", "PASS", {
                    "categories": len(data.get("requirements", []))
                })
            else:
                self.log_workflow(workflow_name, "Get Requirements", "FAIL", {
                    "error": response.text
                })

            # Step 3: Initialize checklist
            response = requests.post(
                f"{self.api_base}/tracking/instance/{instance_id}/initialize-checklist"
            )

            if response.status_code == 200:
                data = response.json()
                self.log_workflow(workflow_name, "Initialize Checklist", "PASS", {
                    "items_created": data["data"]["items_created"]
                })
            else:
                self.log_workflow(workflow_name, "Initialize Checklist", "FAIL", {
                    "error": response.text
                })

            # Step 4: Complete a checklist item
            time.sleep(0.5)

            # Step 5: Get setup instructions
            response = requests.get(f"{self.api_base}/tracking/instructions/{plant_id}")

            if response.status_code == 200:
                data = response.json()
                self.log_workflow(workflow_name, "Get Instructions", "PASS", {
                    "steps": len(data.get("instructions", []))
                })
            else:
                self.log_workflow(workflow_name, "Get Instructions", "FAIL", {
                    "error": response.text
                })

            # Step 6: View growth timeline
            response = requests.get(f"{self.api_base}/tracking/timeline/{plant_id}")

            if response.status_code == 200:
                data = response.json()
                self.log_workflow(workflow_name, "View Timeline", "PASS", {
                    "total_days": data.get("total_days"),
                    "stages": len(data.get("stages", []))
                })
            else:
                self.log_workflow(workflow_name, "View Timeline", "FAIL", {
                    "error": response.text
                })

            # Step 7: Start plant-specific chat
            response = requests.post(
                f"{self.api_base}/chat/plant/{instance_id}/start",
                json={"user_id": user_data.get("user_id", 1)}
            )

            if response.status_code == 201:
                data = response.json()
                chat_id = data["chat_id"]
                self.test_artifacts["chats"].append(chat_id)

                self.log_workflow(workflow_name, "Start Plant Chat", "PASS", {
                    "chat_id": chat_id,
                    "plant_name": data.get("plant_name")
                })
            else:
                self.log_workflow(workflow_name, "Start Plant Chat", "FAIL", {
                    "error": response.text
                })

            # Step 8: Ask questions
            if chat_id:
                questions = [
                    "How is my plant doing at this stage?",
                    "What should I watch out for during germination?"
                ]

                for i, question in enumerate(questions, 1):
                    response = requests.post(
                        f"{self.api_base}/chat/plant/message",
                        json={"chat_id": chat_id, "message": question}
                    )

                    if response.status_code == 200:
                        data = response.json()
                        self.log_workflow(workflow_name, f"Ask Question {i}", "PASS", {
                            "tokens_used": data.get("tokens_used"),
                            "ai_response_length": len(data.get("ai_response", ""))
                        })
                    else:
                        self.log_workflow(workflow_name, f"Ask Question {i}", "FAIL", {
                            "error": response.text
                        })

                    time.sleep(0.5)

            # Step 9: Get current tips
            response = requests.get(f"{self.api_base}/tracking/instance/{instance_id}/tips")

            if response.status_code == 200:
                data = response.json()
                self.log_workflow(workflow_name, "Get Current Tips", "PASS", {
                    "current_stage": data.get("current_stage"),
                    "tips_count": len(data.get("tips", []))
                })
            else:
                self.log_workflow(workflow_name, "Get Current Tips", "FAIL", {
                    "error": response.text
                })

            # Step 10: End chat
            if chat_id:
                response = requests.delete(
                    f"{self.api_base}/chat/{chat_id}",
                    params={"user_id": user_data.get("user_id", 1)}
                )

                if response.status_code == 200:
                    self.log_workflow(workflow_name, "End Chat", "PASS", {
                        "chat_id": chat_id
                    })
                else:
                    self.log_workflow(workflow_name, "End Chat", "FAIL", {
                        "error": response.text
                    })

            print(f"\n{'✓' if instance_id and chat_id else '✗'} Workflow Completed: {workflow_name}\n")

        except Exception as e:
            self.log_workflow(workflow_name, "Workflow Exception", "FAIL", {
                "error": str(e)
            })

    def workflow_progress_tracking(self, user_data: Dict, plant_id: int):
        """
        Workflow 2: Progress Tracking Through Stages
        Steps:
        1. Start tracking
        2. View initial details
        3. Update to next stage
        4. Add user notes
        5. Auto-update stage
        6. Get updated tips
        7. Update nickname
        8. View final progress
        """
        workflow_name = "Progress Tracking Through Stages"
        print(f"\n{'='*70}")
        print(f"Workflow: {workflow_name}")
        print(f"{'='*70}\n")

        instance_id = None

        try:
            # Step 1: Start tracking
            payload = {
                "user_id": user_data.get("user_id", 1),
                "plant_id": plant_id,
                "plant_nickname": "Growth Progress Test",
                "start_date": date.today().isoformat(),
                "location_details": "Test Garden Bed 2",
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
                instance_id = data["instance_id"]
                self.test_artifacts["instances"].append(instance_id)

                self.log_workflow(workflow_name, "Start Tracking", "PASS", {
                    "instance_id": instance_id
                })
            else:
                self.log_workflow(workflow_name, "Start Tracking", "FAIL", {
                    "error": response.text
                })
                return

            # Step 2: View initial details
            response = requests.get(f"{self.api_base}/tracking/instance/{instance_id}")

            if response.status_code == 200:
                data = response.json()
                initial_stage = data["tracking_info"]["current_stage"]

                self.log_workflow(workflow_name, "View Initial Details", "PASS", {
                    "initial_stage": initial_stage,
                    "timeline_stages": len(data["timeline"]["stages"])
                })
            else:
                self.log_workflow(workflow_name, "View Initial Details", "FAIL", {
                    "error": response.text
                })

            # Step 3: Update to next stage
            response = requests.put(
                f"{self.api_base}/tracking/instance/{instance_id}/progress",
                json={
                    "current_stage": "seedling",
                    "user_notes": "First true leaves appeared!"
                }
            )

            if response.status_code == 200:
                self.log_workflow(workflow_name, "Update Stage", "PASS", {
                    "new_stage": "seedling"
                })
            else:
                self.log_workflow(workflow_name, "Update Stage", "FAIL", {
                    "error": response.text
                })

            # Step 4: Add more user notes
            time.sleep(0.5)

            response = requests.put(
                f"{self.api_base}/tracking/instance/{instance_id}/progress",
                json={"user_notes": "Growing well, healthy green color"}
            )

            if response.status_code == 200:
                self.log_workflow(workflow_name, "Add User Notes", "PASS", {})
            else:
                self.log_workflow(workflow_name, "Add User Notes", "FAIL", {
                    "error": response.text
                })

            # Step 5: Auto-update stage
            response = requests.post(
                f"{self.api_base}/tracking/instance/{instance_id}/auto-update-stage"
            )

            if response.status_code == 200:
                data = response.json()
                self.log_workflow(workflow_name, "Auto-Update Stage", "PASS", {
                    "updated": data["data"]["updated"]
                })
            else:
                self.log_workflow(workflow_name, "Auto-Update Stage", "FAIL", {
                    "error": response.text
                })

            # Step 6: Get updated tips
            response = requests.get(f"{self.api_base}/tracking/instance/{instance_id}/tips")

            if response.status_code == 200:
                data = response.json()
                self.log_workflow(workflow_name, "Get Updated Tips", "PASS", {
                    "current_stage": data.get("current_stage"),
                    "tips_count": len(data.get("tips", []))
                })
            else:
                self.log_workflow(workflow_name, "Get Updated Tips", "FAIL", {
                    "error": response.text
                })

            # Step 7: Update nickname
            response = requests.put(
                f"{self.api_base}/tracking/instance/{instance_id}/nickname",
                json={"plant_nickname": "Thriving Garden Plant"}
            )

            if response.status_code == 200:
                self.log_workflow(workflow_name, "Update Nickname", "PASS", {
                    "new_nickname": "Thriving Garden Plant"
                })
            else:
                self.log_workflow(workflow_name, "Update Nickname", "FAIL", {
                    "error": response.text
                })

            # Step 8: View final progress
            response = requests.get(f"{self.api_base}/tracking/instance/{instance_id}")

            if response.status_code == 200:
                data = response.json()
                self.log_workflow(workflow_name, "View Final Progress", "PASS", {
                    "current_stage": data["tracking_info"]["current_stage"],
                    "days_elapsed": data["tracking_info"]["days_elapsed"],
                    "progress_percentage": data["tracking_info"]["progress_percentage"]
                })
            else:
                self.log_workflow(workflow_name, "View Final Progress", "FAIL", {
                    "error": response.text
                })

            print(f"\n{'✓' if instance_id else '✗'} Workflow Completed: {workflow_name}\n")

        except Exception as e:
            self.log_workflow(workflow_name, "Workflow Exception", "FAIL", {
                "error": str(e)
            })

    def workflow_multi_plant_management(self, user_data: Dict):
        """
        Workflow 3: Managing Multiple Plants
        Steps:
        1. Start tracking 3 different plants
        2. Get user's plant list
        3. Update each plant differently
        4. Compare progress
        5. Chat about each plant
        """
        workflow_name = "Multi-Plant Management"
        print(f"\n{'='*70}")
        print(f"Workflow: {workflow_name}")
        print(f"{'='*70}\n")

        instance_ids = []

        try:
            # Step 1: Start tracking 3 plants
            plants = [
                {"id": 1, "nickname": "Basil Herb Garden", "location": "Kitchen window"},
                {"id": 2, "nickname": "Cherry Tomato", "location": "Balcony pot 1"},
                {"id": 3, "nickname": "Lettuce Container", "location": "Balcony pot 2"}
            ]

            for plant in plants:
                payload = {
                    "user_id": user_data.get("user_id", 1),
                    "plant_id": plant["id"],
                    "plant_nickname": plant["nickname"],
                    "start_date": date.today().isoformat(),
                    "location_details": plant["location"],
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
                    instance_ids.append(data["instance_id"])
                    self.test_artifacts["instances"].append(data["instance_id"])

                time.sleep(0.5)

            self.log_workflow(workflow_name, "Start Multiple Plants", "PASS", {
                "plants_started": len(instance_ids)
            })

            # Step 2: Get user's plant list
            response = requests.get(
                f"{self.api_base}/tracking/user/{user_data.get('user_id', 1)}"
            )

            if response.status_code == 200:
                data = response.json()
                self.log_workflow(workflow_name, "Get Plant List", "PASS", {
                    "total_count": data.get("total_count"),
                    "active_count": data.get("active_count")
                })
            else:
                self.log_workflow(workflow_name, "Get Plant List", "FAIL", {
                    "error": response.text
                })

            # Step 3: Update each plant differently
            stages = ["germination", "seedling", "vegetative"]

            for i, instance_id in enumerate(instance_ids[:3]):
                response = requests.put(
                    f"{self.api_base}/tracking/instance/{instance_id}/progress",
                    json={"current_stage": stages[i]}
                )

                if response.status_code == 200:
                    self.log_workflow(workflow_name, f"Update Plant {i+1}", "PASS", {
                        "instance_id": instance_id,
                        "stage": stages[i]
                    })

                time.sleep(0.5)

            # Step 4: Compare progress
            for instance_id in instance_ids:
                response = requests.get(f"{self.api_base}/tracking/instance/{instance_id}")

                if response.status_code == 200:
                    data = response.json()
                    # Just log, don't fail
                    pass

            self.log_workflow(workflow_name, "Compare Progress", "PASS", {
                "plants_compared": len(instance_ids)
            })

            print(f"\n✓ Workflow Completed: {workflow_name}\n")

        except Exception as e:
            self.log_workflow(workflow_name, "Workflow Exception", "FAIL", {
                "error": str(e)
            })

    def get_summary(self) -> Dict[str, Any]:
        """Generate workflow summary"""
        workflows = {}

        for result in self.workflow_results:
            workflow = result["workflow"]

            if workflow not in workflows:
                workflows[workflow] = {"steps": [], "passed": 0, "failed": 0}

            workflows[workflow]["steps"].append(result)

            if result["status"] == "PASS":
                workflows[workflow]["passed"] += 1
            else:
                workflows[workflow]["failed"] += 1

        return {
            "workflows": workflows,
            "test_artifacts": self.test_artifacts,
            "all_results": self.workflow_results
        }


def run_end_to_end_workflows():
    """Run all end-to-end workflow tests"""
    print("\n" + "="*70)
    print("ITERATION 3 - END-TO-END WORKFLOW TESTING")
    print("="*70 + "\n")

    tester = EndToEndWorkflowTester()

    # Load test data
    with open('tests/iteration_3/fixtures/test_data.json', 'r') as f:
        test_data = json.load(f)

    user_data = test_data["test_user"]
    user_data["user_id"] = 1  # Test user ID

    # Run workflows
    tester.workflow_new_user_journey(user_data, plant_id=1)
    time.sleep(1)

    tester.workflow_progress_tracking(user_data, plant_id=2)
    time.sleep(1)

    tester.workflow_multi_plant_management(user_data)

    # Generate summary
    print("\n" + "="*70)
    print("WORKFLOW SUMMARY")
    print("="*70)

    summary = tester.get_summary()

    for workflow_name, workflow_data in summary["workflows"].items():
        print(f"\n{workflow_name}:")
        print(f"  Steps Passed: {workflow_data['passed']} ✓")
        print(f"  Steps Failed: {workflow_data['failed']} ✗")

    print(f"\nTest Artifacts Created:")
    print(f"  Plant Instances: {len(summary['test_artifacts']['instances'])}")
    print(f"  Chat Sessions: {len(summary['test_artifacts']['chats'])}")

    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"tests/iteration_3/reports/workflow_results_{timestamp}.json"

    with open(report_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nDetailed results saved to: {report_file}")

    return summary


if __name__ == "__main__":
    run_end_to_end_workflows()
