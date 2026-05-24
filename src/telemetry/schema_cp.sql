-- KalibrBench-CP: competitive programming run storage
-- Run this against your Supabase instance before running the experiment.
-- Safe to re-run (IF NOT EXISTS throughout).

CREATE TABLE IF NOT EXISTS cp_runs (
    run_id              UUID        PRIMARY KEY,
    problem_id          TEXT        NOT NULL,
    difficulty          INTEGER     NOT NULL,
    topology            TEXT        NOT NULL CHECK (topology IN ('chain-1', 'chain-2', 'flat-2')),
    condition           TEXT        NOT NULL CHECK (condition IN ('generic', 'specialized')),
    passed              BOOLEAN     NOT NULL,
    compilation_error   BOOLEAN     NOT NULL,
    tests_passed        INTEGER     NOT NULL,
    tests_total         INTEGER     NOT NULL,
    pass_rate           FLOAT       NOT NULL,
    extraction_failed   BOOLEAN     NOT NULL,
    tokens_total        INTEGER     NOT NULL,
    model_family        TEXT        NOT NULL DEFAULT 'gemini',
    elapsed_seconds     FLOAT,
    timestamp           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cp_runs_problem    ON cp_runs(problem_id);
CREATE INDEX IF NOT EXISTS idx_cp_runs_topology   ON cp_runs(topology);
CREATE INDEX IF NOT EXISTS idx_cp_runs_condition  ON cp_runs(condition);
CREATE INDEX IF NOT EXISTS idx_cp_runs_difficulty ON cp_runs(difficulty);
