#!/usr/bin/env python
"""Kill stuck database connections - Interactive version"""
import asyncpg
import asyncio

async def check_and_kill_connections():
    try:
        print("=" * 60)
        print("Database Connection Analyzer")
        print("=" * 60)
        print("\nConnecting to database...")

        conn = await asyncpg.connect(
            user='postgres.kkfhwvgfwwrphexdmjsm',
            password='tp34plantopia',
            host='aws-1-ap-southeast-2.pooler.supabase.com',
            port=6543,
            database='postgres',
            statement_cache_size=0,
            timeout=15
        )

        # Get overall connection stats
        print("\n📊 Connection Statistics:")
        stats = await conn.fetchrow("""
            SELECT
                count(*) as total_connections,
                count(*) FILTER (WHERE state = 'active') as active,
                count(*) FILTER (WHERE state = 'idle') as idle,
                count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
            FROM pg_stat_activity
            WHERE datname = 'postgres'
        """)

        print(f"   Total connections:        {stats['total_connections']}")
        print(f"   Active (running queries): {stats['active']}")
        print(f"   Idle (can reuse):         {stats['idle']}")
        print(f"   Stuck (idle in txn):      {stats['idle_in_transaction']}")

        # Supabase free tier limits (approximate)
        MAX_CONNECTIONS = 30  # Typical Supabase free tier limit
        usage_pct = (stats['total_connections'] / MAX_CONNECTIONS) * 100

        print(f"\n💡 Connection pool usage:   {stats['total_connections']}/{MAX_CONNECTIONS} ({usage_pct:.1f}%)")
        if usage_pct > 80:
            print("   ⚠️  WARNING: Pool is almost full!")
        elif usage_pct > 60:
            print("   ⚠️  CAUTION: Pool usage is high")
        else:
            print("   ✅ Pool usage is healthy")

        # Get list of idle connections with duration
        idle_conns = await conn.fetch("""
            SELECT
                pid,
                state,
                application_name,
                backend_start,
                state_change,
                NOW() - state_change AS idle_duration
            FROM pg_stat_activity
            WHERE datname = 'postgres'
            AND state IN ('idle', 'idle in transaction')
            AND pid != pg_backend_pid()
            AND application_name NOT LIKE 'pg_%'
            ORDER BY state_change
        """)

        if len(idle_conns) == 0:
            print("\n✅ No idle connections to clean up!")
            await conn.close()
            return

        print(f"\n🔍 Found {len(idle_conns)} idle connection(s):")
        print("-" * 60)
        for row in idle_conns:
            print(f"   PID {row['pid']:7} | {row['state']:20} | Idle for: {row['idle_duration']}")

        # Ask for confirmation
        print("\n" + "=" * 60)
        response = input("Do you want to terminate these idle connections? (yes/no): ").strip().lower()

        if response not in ['yes', 'y']:
            print("\n❌ Cancelled. No connections were terminated.")
            await conn.close()
            return

        # Terminate connections
        print("\n💀 Terminating idle connections...")
        killed = 0
        failed = 0

        for row in idle_conns:
            pid = row['pid']
            try:
                result = await conn.fetchval(
                    "SELECT pg_terminate_backend($1)", pid
                )
                if result:
                    print(f"   ✅ Killed PID {pid}")
                    killed += 1
                else:
                    print(f"   ❌ Failed to kill PID {pid}")
                    failed += 1
            except Exception as e:
                error_msg = str(e).split('\n')[0]  # First line only
                print(f"   ❌ Error killing PID {pid}: {error_msg}")
                failed += 1

        print("\n" + "=" * 60)
        print(f"✅ Successfully terminated {killed} connection(s)")
        if failed > 0:
            print(f"❌ Failed to terminate {failed} connection(s) (permission issues)")
        print("=" * 60)

        await conn.close()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_and_kill_connections())