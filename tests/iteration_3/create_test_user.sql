-- Create Test User for Iteration 3 Testing
-- This user is required for chat functionality tests
-- Execute on VM: sudo -u postgres psql plantopia_db -f create_test_user.sql

-- First, check if user already exists
SELECT 'Checking for existing test user...' as status;
SELECT id, email, name, suburb_id, created_at
FROM users
WHERE id = 1 OR email = 'test@plantopia.com';

-- If user doesn't exist, create it
INSERT INTO users (
    id,
    email,
    name,
    suburb_id,
    experience_level,
    garden_type,
    available_space,
    climate_goal,
    created_at,
    updated_at
)
VALUES (
    1,
    'test@plantopia.com',
    'Test User',
    1,  -- Melbourne CBD suburb_id (adjust if needed)
    'beginner',
    'backyard',
    10.0,
    'general gardening',
    NOW(),
    NOW()
)
ON CONFLICT (id) DO UPDATE
SET
    email = EXCLUDED.email,
    name = EXCLUDED.name,
    updated_at = NOW();

-- Verify user was created/updated
SELECT 'Test user status:' as status;
SELECT id, email, name, suburb_id, experience_level, created_at
FROM users
WHERE id = 1;

-- Show total user count
SELECT 'Total users in database:' as status;
SELECT COUNT(*) as total_users FROM users;
