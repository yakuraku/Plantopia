"""
Test Data Cleanup Script for Iteration 3
Removes all test data created during comprehensive testing from production database.

Usage:
    python tests/iteration_3/cleanup_test_data.py

    Optional arguments:
    --dry-run         Show what would be deleted without actually deleting
    --confirm         Skip confirmation prompt (use with caution)

Safety Features:
- Identifies test data by email pattern "iteration3.test@plantopia.com"
- Shows summary before deletion
- Requires confirmation (unless --confirm flag used)
- Creates backup of deleted IDs for recovery if needed
"""

import sys
import os
import argparse
from datetime import datetime
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.models.database import (
    User,
    UserPlantInstance,
    UserProgressTracking,
    ChatSession,
    ChatMessage
)


class TestDataCleanup:
    """Cleanup manager for test data"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.cleanup_summary = {
            "users": 0,
            "plant_instances": 0,
            "progress_tracking_records": 0,
            "chat_sessions": 0,
            "chat_messages": 0
        }
        self.deleted_ids = {
            "users": [],
            "plant_instances": [],
            "chat_sessions": []
        }

    async def find_test_user(self, db: AsyncSession) -> User:
        """Find test user by email pattern"""
        query = select(User).where(User.email == "iteration3.test@plantopia.com")
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        return user

    async def find_test_plant_instances(self, db: AsyncSession, user_id: int) -> list:
        """Find all plant instances for test user"""
        query = select(UserPlantInstance).where(UserPlantInstance.user_id == user_id)
        result = await db.execute(query)
        instances = result.scalars().all()

        return instances

    async def find_test_chat_sessions(self, db: AsyncSession, user_id: int) -> list:
        """Find all chat sessions for test user"""
        query = select(ChatSession).where(ChatSession.user_id == user_id)
        result = await db.execute(query)
        chats = result.scalars().all()

        return chats

    async def count_related_records(self, db: AsyncSession, instance_ids: list, chat_ids: list):
        """Count related records that will be deleted"""

        # Count progress tracking records
        if instance_ids:
            query = select(UserProgressTracking).where(
                UserProgressTracking.user_plant_instance_id.in_(instance_ids)
            )
            result = await db.execute(query)
            progress_records = result.scalars().all()
            self.cleanup_summary["progress_tracking_records"] = len(progress_records)

        # Count chat messages
        if chat_ids:
            query = select(ChatMessage).where(ChatMessage.chat_session_id.in_(chat_ids))
            result = await db.execute(query)
            messages = result.scalars().all()
            self.cleanup_summary["chat_messages"] = len(messages)

    async def delete_test_data(self, db: AsyncSession, user: User):
        """Delete all test data for a user"""

        user_id = user.id
        print(f"\nCleaning up test data for user: {user.email} (ID: {user_id})")

        # Step 1: Find all related data
        plant_instances = await self.find_test_plant_instances(db, user_id)
        chat_sessions = await self.find_test_chat_sessions(db, user_id)

        instance_ids = [inst.id for inst in plant_instances]
        chat_ids = [chat.id for chat in chat_sessions]

        print(f"\nFound:")
        print(f"  - {len(plant_instances)} plant instances")
        print(f"  - {len(chat_sessions)} chat sessions")

        # Count related records
        await self.count_related_records(db, instance_ids, chat_ids)

        print(f"  - {self.cleanup_summary['progress_tracking_records']} progress tracking records")
        print(f"  - {self.cleanup_summary['chat_messages']} chat messages")

        if self.dry_run:
            print("\n[DRY RUN] Would delete the above records (no actual deletion performed)")
            return

        # Step 2: Delete chat messages (foreign key constraint)
        if chat_ids:
            await db.execute(
                delete(ChatMessage).where(ChatMessage.chat_session_id.in_(chat_ids))
            )
            print(f"\n✓ Deleted {self.cleanup_summary['chat_messages']} chat messages")

        # Step 3: Delete chat sessions
        if chat_ids:
            await db.execute(
                delete(ChatSession).where(ChatSession.id.in_(chat_ids))
            )
            self.cleanup_summary["chat_sessions"] = len(chat_ids)
            self.deleted_ids["chat_sessions"] = chat_ids
            print(f"✓ Deleted {len(chat_ids)} chat sessions")

        # Step 4: Delete progress tracking records (foreign key constraint)
        if instance_ids:
            await db.execute(
                delete(UserProgressTracking).where(
                    UserProgressTracking.user_plant_instance_id.in_(instance_ids)
                )
            )
            print(f"✓ Deleted {self.cleanup_summary['progress_tracking_records']} progress tracking records")

        # Step 5: Delete plant instances
        if instance_ids:
            await db.execute(
                delete(UserPlantInstance).where(UserPlantInstance.id.in_(instance_ids))
            )
            self.cleanup_summary["plant_instances"] = len(instance_ids)
            self.deleted_ids["plant_instances"] = instance_ids
            print(f"✓ Deleted {len(instance_ids)} plant instances")

        # Step 6: Delete user
        await db.execute(delete(User).where(User.id == user_id))
        self.cleanup_summary["users"] = 1
        self.deleted_ids["users"] = [user_id]
        print(f"✓ Deleted test user (ID: {user_id})")

        # Commit transaction
        await db.commit()

        print("\n✓ All test data cleaned up successfully!")

    async def cleanup_specific_instances(self, db: AsyncSession, instance_ids: list):
        """Clean up specific plant instances by ID"""

        if not instance_ids:
            print("No instance IDs provided")
            return

        print(f"\nCleaning up specific plant instances: {instance_ids}")

        # Delete progress tracking records
        await db.execute(
            delete(UserProgressTracking).where(
                UserProgressTracking.user_plant_instance_id.in_(instance_ids)
            )
        )

        # Delete plant instances
        result = await db.execute(
            delete(UserPlantInstance).where(UserPlantInstance.id.in_(instance_ids))
        )

        deleted_count = result.rowcount

        if not self.dry_run:
            await db.commit()
            print(f"\n✓ Deleted {deleted_count} plant instances and related data")
        else:
            print(f"\n[DRY RUN] Would delete {deleted_count} plant instances")

    async def cleanup_specific_chats(self, db: AsyncSession, chat_ids: list):
        """Clean up specific chat sessions by ID"""

        if not chat_ids:
            print("No chat IDs provided")
            return

        print(f"\nCleaning up specific chat sessions: {chat_ids}")

        # Delete chat messages
        message_result = await db.execute(
            delete(ChatMessage).where(ChatMessage.chat_session_id.in_(chat_ids))
        )

        # Delete chat sessions
        chat_result = await db.execute(
            delete(ChatSession).where(ChatSession.id.in_(chat_ids))
        )

        if not self.dry_run:
            await db.commit()
            print(f"\n✓ Deleted {chat_result.rowcount} chat sessions and {message_result.rowcount} messages")
        else:
            print(f"\n[DRY RUN] Would delete {chat_result.rowcount} chat sessions and {message_result.rowcount} messages")

    def save_deleted_ids_backup(self):
        """Save deleted IDs to backup file for potential recovery"""

        if self.dry_run:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"tests/iteration_3/reports/deleted_ids_backup_{timestamp}.json"

        import json

        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "deleted_ids": self.deleted_ids,
            "summary": self.cleanup_summary
        }

        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)

        print(f"\nBackup of deleted IDs saved to: {backup_file}")

    def print_summary(self):
        """Print cleanup summary"""
        print("\n" + "="*70)
        print("CLEANUP SUMMARY")
        print("="*70)

        print(f"\nRecords {'that would be ' if self.dry_run else ''}deleted:")
        print(f"  - Users: {self.cleanup_summary['users']}")
        print(f"  - Plant Instances: {self.cleanup_summary['plant_instances']}")
        print(f"  - Progress Tracking Records: {self.cleanup_summary['progress_tracking_records']}")
        print(f"  - Chat Sessions: {self.cleanup_summary['chat_sessions']}")
        print(f"  - Chat Messages: {self.cleanup_summary['chat_messages']}")

        total = sum(self.cleanup_summary.values())
        print(f"\nTotal Records: {total}")


async def run_cleanup(dry_run: bool = False, skip_confirm: bool = False):
    """Run the cleanup process"""
    print("\n" + "="*70)
    print("ITERATION 3 - TEST DATA CLEANUP")
    print("="*70)

    if dry_run:
        print("\n[DRY RUN MODE] No data will be deleted")

    cleanup = TestDataCleanup(dry_run=dry_run)

    # Get database session
    async for db in get_async_db():
        try:
            # Find test user
            test_user = await cleanup.find_test_user(db)

            if not test_user:
                print("\n✓ No test user found. Nothing to clean up.")
                return

            print(f"\nFound test user: {test_user.email} (ID: {test_user.id})")

            # Find related data
            instances = await cleanup.find_test_plant_instances(db, test_user.id)
            chats = await cleanup.find_test_chat_sessions(db, test_user.id)

            instance_ids = [inst.id for inst in instances]
            chat_ids = [chat.id for chat in chats]

            # Count related records
            await cleanup.count_related_records(db, instance_ids, chat_ids)

            # Update summary counts
            cleanup.cleanup_summary["users"] = 1
            cleanup.cleanup_summary["plant_instances"] = len(instances)
            cleanup.cleanup_summary["chat_sessions"] = len(chats)

            # Print what will be deleted
            cleanup.print_summary()

            # Confirm deletion
            if not skip_confirm and not dry_run:
                print("\n" + "="*70)
                response = input("\nAre you sure you want to delete this test data? (yes/no): ")

                if response.lower() != "yes":
                    print("\n✗ Cleanup cancelled by user")
                    return

            # Perform cleanup
            if not dry_run:
                await cleanup.delete_test_data(db, test_user)
                cleanup.save_deleted_ids_backup()
            else:
                print("\n[DRY RUN] Review the summary above. Run without --dry-run to delete.")

        except Exception as e:
            print(f"\n✗ Error during cleanup: {e}")
            await db.rollback()
            raise

        finally:
            await db.close()


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Clean up Iteration 3 test data")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without deleting")
    parser.add_argument("--confirm", action="store_true", help="Skip confirmation prompt")

    args = parser.parse_args()

    # Run async cleanup
    asyncio.run(run_cleanup(dry_run=args.dry_run, skip_confirm=args.confirm))


if __name__ == "__main__":
    main()
