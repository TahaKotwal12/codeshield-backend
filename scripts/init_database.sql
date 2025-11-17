-- CodeShield AI Database Schema
-- PostgreSQL Database Setup Script

-- Create enum types
CREATE TYPE risk_score_enum AS ENUM ('High', 'Medium', 'Low');
CREATE TYPE severity_enum AS ENUM ('High', 'Medium', 'Low');

-- Code Analysis Table
CREATE TABLE IF NOT EXISTS code_analysis (
    analysis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_snippet TEXT NOT NULL,
    risk_score risk_score_enum NOT NULL,
    explanation TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Vulnerabilities Table
CREATE TABLE IF NOT EXISTS vulnerabilities (
    vulnerability_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES code_analysis(analysis_id) ON DELETE CASCADE,
    line INTEGER NOT NULL,
    severity severity_enum NOT NULL,
    type VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Fixes Table
CREATE TABLE IF NOT EXISTS fixes (
    fix_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES code_analysis(analysis_id) ON DELETE CASCADE,
    line INTEGER NOT NULL,
    original TEXT NOT NULL,
    fixed TEXT NOT NULL,
    explanation TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_code_analysis_created_at ON code_analysis(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_code_analysis_risk_score ON code_analysis(risk_score);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_analysis_id ON vulnerabilities(analysis_id);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_severity ON vulnerabilities(severity);
CREATE INDEX IF NOT EXISTS idx_fixes_analysis_id ON fixes(analysis_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_code_analysis_updated_at
    BEFORE UPDATE ON code_analysis
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE code_analysis IS 'Stores code analysis history';
COMMENT ON TABLE vulnerabilities IS 'Stores detected vulnerabilities for each analysis';
COMMENT ON TABLE fixes IS 'Stores suggested fixes for each analysis';

COMMENT ON COLUMN code_analysis.analysis_id IS 'Unique identifier for the analysis';
COMMENT ON COLUMN code_analysis.code_snippet IS 'First 1000 characters of the analyzed code';
COMMENT ON COLUMN code_analysis.risk_score IS 'Overall risk score: High, Medium, or Low';
COMMENT ON COLUMN code_analysis.explanation IS 'Detailed explanation of the security assessment';

COMMENT ON COLUMN vulnerabilities.vulnerability_id IS 'Unique identifier for the vulnerability';
COMMENT ON COLUMN vulnerabilities.analysis_id IS 'Reference to the parent analysis';
COMMENT ON COLUMN vulnerabilities.line IS 'Line number where vulnerability is found';
COMMENT ON COLUMN vulnerabilities.severity IS 'Severity level: High, Medium, or Low';
COMMENT ON COLUMN vulnerabilities.type IS 'Type of vulnerability (e.g., SQL Injection, XSS)';
COMMENT ON COLUMN vulnerabilities.description IS 'Detailed description of the vulnerability';

COMMENT ON COLUMN fixes.fix_id IS 'Unique identifier for the fix';
COMMENT ON COLUMN fixes.analysis_id IS 'Reference to the parent analysis';
COMMENT ON COLUMN fixes.line IS 'Line number where fix is needed';
COMMENT ON COLUMN fixes.original IS 'Original vulnerable code';
COMMENT ON COLUMN fixes.fixed IS 'Fixed code';
COMMENT ON COLUMN fixes.explanation IS 'Explanation of the fix';


