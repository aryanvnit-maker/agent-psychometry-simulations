CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS runs (
    run_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    composition_matrix  JSONB NOT NULL,
    topology        TEXT NOT NULL CHECK (topology IN ('flat', 'chain', 'hub_spoke')),
    task_phase      TEXT NOT NULL CHECK (task_phase IN ('forming', 'storming', 'norming', 'performing')),
    scenario_category   TEXT NOT NULL CHECK (scenario_category IN ('strategic', 'crisis', 'resource', 'evaluation', 'creative')),
    composition_condition TEXT NOT NULL CHECK (composition_condition IN ('drafted', 'homogeneous', 'founder_brained', 'missing_role')),
    team_size       INTEGER NOT NULL,
    captain_agent_id    TEXT,
    draft_order     INTEGER,
    token_cost      INTEGER,
    turns_to_complete   INTEGER,
    cull_events     JSONB DEFAULT '[]',
    state_snapshot  JSONB,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS evaluations (
    eval_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          UUID NOT NULL REFERENCES runs(run_id),
    judge_index     INTEGER NOT NULL,
    scores          JSONB NOT NULL,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_runs_phase ON runs(task_phase);
CREATE INDEX IF NOT EXISTS idx_runs_team_size ON runs(team_size);
CREATE INDEX IF NOT EXISTS idx_runs_scenario ON runs(scenario_category);
CREATE INDEX IF NOT EXISTS idx_evals_run ON evaluations(run_id);
