-- Migration 006: Create Style Profiles Table
-- Purpose: Store writing style profiles for each workspace
-- Features:
--   - Voice characteristics (tone, formality)
--   - Sentence patterns (length, variety, question frequency)
--   - Vocabulary preferences (favorite phrases, avoided words)
--   - Structural preferences (intro style, section count, emoji usage)
--   - Example sentences for few-shot learning
-- Relations: One-to-one with workspaces table

-- =============================================================================
-- DROP EXISTING (if re-running)
-- =============================================================================

DROP TABLE IF EXISTS style_profiles CASCADE;

-- =============================================================================
-- CREATE TABLE: style_profiles
-- =============================================================================

CREATE TABLE style_profiles (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Voice Characteristics
    tone VARCHAR(50) NOT NULL DEFAULT 'professional', -- conversational, authoritative, humorous, professional
    formality_level DECIMAL(3,2) NOT NULL DEFAULT 0.50 CHECK (formality_level >= 0 AND formality_level <= 1), -- 0.0 (casual) to 1.0 (formal)

    -- Sentence Patterns
    avg_sentence_length DECIMAL(5,2) DEFAULT 15.0,
    sentence_length_variety DECIMAL(5,2) DEFAULT 5.0, -- std deviation
    question_frequency DECIMAL(4,3) DEFAULT 0.10 CHECK (question_frequency >= 0 AND question_frequency <= 1), -- questions per 100 words

    -- Vocabulary Preferences
    vocabulary_level VARCHAR(20) DEFAULT 'intermediate', -- simple, intermediate, advanced
    favorite_phrases TEXT[] DEFAULT '{}', -- array of frequently used phrases
    avoided_words TEXT[] DEFAULT '{}', -- array of words user never uses

    -- Structural Preferences
    typical_intro_style VARCHAR(50) DEFAULT 'question', -- question, statement, anecdote, statistic
    section_count INTEGER DEFAULT 4,
    uses_emojis BOOLEAN DEFAULT false,
    emoji_frequency DECIMAL(4,3) DEFAULT 0.00 CHECK (emoji_frequency >= 0 AND emoji_frequency <= 1),

    -- Example Sentences (for few-shot learning)
    example_intros TEXT[] DEFAULT '{}',
    example_transitions TEXT[] DEFAULT '{}',
    example_conclusions TEXT[] DEFAULT '{}',

    -- Metadata
    trained_on_count INTEGER DEFAULT 0, -- number of sample newsletters analyzed
    training_samples JSONB DEFAULT '[]'::jsonb, -- store sample texts for retraining

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT unique_workspace_style_profile UNIQUE(workspace_id)
);

-- =============================================================================
-- INDEXES
-- =============================================================================

CREATE INDEX idx_style_profiles_workspace_id ON style_profiles(workspace_id);
CREATE INDEX idx_style_profiles_updated_at ON style_profiles(updated_at DESC);

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

ALTER TABLE style_profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own workspace's style profile
CREATE POLICY "Users can view their workspace style profiles"
    ON style_profiles
    FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id
            FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

-- Policy: Users can insert style profiles for their workspaces
CREATE POLICY "Users can create style profiles for their workspaces"
    ON style_profiles
    FOR INSERT
    WITH CHECK (
        workspace_id IN (
            SELECT workspace_id
            FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'admin')
        )
    );

-- Policy: Users can update their workspace's style profiles
CREATE POLICY "Users can update their workspace style profiles"
    ON style_profiles
    FOR UPDATE
    USING (
        workspace_id IN (
            SELECT workspace_id
            FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'admin')
        )
    )
    WITH CHECK (
        workspace_id IN (
            SELECT workspace_id
            FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'admin')
        )
    );

-- Policy: Users can delete their workspace's style profiles
CREATE POLICY "Users can delete their workspace style profiles"
    ON style_profiles
    FOR DELETE
    USING (
        workspace_id IN (
            SELECT workspace_id
            FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'admin')
        )
    );

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Trigger: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_style_profiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_style_profiles_updated_at
    BEFORE UPDATE ON style_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_style_profiles_updated_at();

-- =============================================================================
-- UTILITY FUNCTIONS
-- =============================================================================

-- Function: Get style profile summary for workspace
CREATE OR REPLACE FUNCTION get_style_profile_summary(workspace_uuid UUID)
RETURNS JSONB AS $$
DECLARE
    profile_summary JSONB;
BEGIN
    SELECT jsonb_build_object(
        'has_profile', COUNT(*) > 0,
        'trained_on_count', COALESCE(MAX(trained_on_count), 0),
        'tone', MAX(tone),
        'formality_level', MAX(formality_level),
        'uses_emojis', BOOL_OR(uses_emojis),
        'last_updated', MAX(updated_at)
    )
    INTO profile_summary
    FROM style_profiles
    WHERE workspace_id = workspace_uuid;

    RETURN profile_summary;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================================
-- SEED DATA (Optional - for testing)
-- =============================================================================

-- Example style profile (commented out - create via API instead)
-- INSERT INTO style_profiles (
--     workspace_id,
--     tone,
--     formality_level,
--     avg_sentence_length,
--     favorite_phrases,
--     example_intros
-- ) VALUES (
--     'YOUR_WORKSPACE_ID_HERE',
--     'conversational',
--     0.35,
--     15.8,
--     ARRAY['Here''s the thing', 'Let''s dive in', 'Quick thought'],
--     ARRAY['Ever wonder why AI agents are everywhere now?']
-- );

-- =============================================================================
-- VERIFICATION
-- =============================================================================

-- Check table exists and is empty
DO $$
BEGIN
    IF EXISTS (SELECT FROM style_profiles LIMIT 1) THEN
        RAISE NOTICE 'Style profiles table created and has data';
    ELSE
        RAISE NOTICE 'Style profiles table created successfully (empty)';
    END IF;
END $$;

SELECT 'Migration 006 completed: style_profiles table created' AS status;
