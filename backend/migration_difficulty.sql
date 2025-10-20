-- Database migration for Difficulty Algorithm
-- Run this SQL on your production database

-- Add difficulty tracking columns to questions table
ALTER TABLE questions ADD COLUMN IF NOT EXISTS difficulty_score FLOAT;
ALTER TABLE questions ADD COLUMN IF NOT EXISTS difficulty_confidence FLOAT DEFAULT 0.0;
ALTER TABLE questions ADD COLUMN IF NOT EXISTS difficulty_history JSON DEFAULT '[]';
ALTER TABLE questions ADD COLUMN IF NOT EXISTS tier_stats JSON DEFAULT '{}';

-- Verify columns were added
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'questions'
AND column_name IN ('difficulty_score', 'difficulty_confidence', 'difficulty_history', 'tier_stats')
ORDER BY column_name;
