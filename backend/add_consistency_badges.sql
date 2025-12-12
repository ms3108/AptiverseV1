-- Add new 50-day consistency badge
-- Run this SQL on your database to add the new badge

INSERT INTO badges (name, description, icon, criteria) 
VALUES (
    'Dedication Champion',
    'Practice consistently for 50 days in a row',
    '🏆',
    '{"current_streak": 50}'
)
ON CONFLICT (name) DO NOTHING;

-- Update the 100-day badge description
UPDATE badges 
SET description = 'Practice consistently for 100 days in a row - Ultimate dedication!'
WHERE name = 'Streak Master';