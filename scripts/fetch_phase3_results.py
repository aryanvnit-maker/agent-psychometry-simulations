"""Pull Phase 3 results from Supabase."""
from dotenv import load_dotenv
load_dotenv()

from src.telemetry.database import get_conn
from psycopg2.extras import RealDictCursor

PHASE3_CONDITIONS = ["chain-2/clean", "chain-2/poisoned", "flat-2/clean", "flat-2/poisoned"]

with get_conn() as conn:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Summary per condition
        cur.execute("""
            SELECT condition,
                   COUNT(*) as n,
                   SUM(passed::int) as passed,
                   ROUND(AVG(pass_rate::numeric) * 100, 1) as avg_pass_rate,
                   SUM(compilation_error::int) as compilation_errors,
                   SUM(extraction_failed::int) as no_code
            FROM cp_runs
            WHERE condition = ANY(%s)
            GROUP BY condition
            ORDER BY condition
        """, (PHASE3_CONDITIONS,))
        rows = cur.fetchall()

        if not rows:
            print("No Phase 3 records found in cp_runs.")
            print("\nAll distinct conditions in cp_runs:")
            cur.execute("SELECT DISTINCT condition, COUNT(*) as n FROM cp_runs GROUP BY condition ORDER BY condition")
            for r in cur.fetchall():
                print(f"  {r['condition']}: {r['n']} records")
        else:
            print(f"{'Condition':<22} {'N':>4}  {'Passed':>6}  {'Pass@1':>7}  {'AvgPassRate':>11}  {'CE':>4}  {'NoCode':>6}")
            print(f"{'-'*22}  {'-'*4}  {'-'*6}  {'-'*7}  {'-'*11}  {'-'*4}  {'-'*6}")
            for r in rows:
                n = r['n']
                passed = r['passed'] or 0
                pass1 = passed / n * 100 if n else 0
                print(f"  {r['condition']:<20} {n:>4}  {passed:>6}  {pass1:>6.1f}%  {r['avg_pass_rate']:>11}  {r['compilation_errors'] or 0:>4}  {r['no_code'] or 0:>6}")

            # Compute the key metric: delta_chain vs delta_flat
            results = {r['condition']: r for r in rows}
            if all(c in results for c in PHASE3_CONDITIONS):
                chain_clean   = (results['chain-2/clean']['passed'] or 0)   / results['chain-2/clean']['n']   * 100
                chain_poison  = (results['chain-2/poisoned']['passed'] or 0) / results['chain-2/poisoned']['n'] * 100
                flat_clean    = (results['flat-2/clean']['passed'] or 0)     / results['flat-2/clean']['n']     * 100
                flat_poison   = (results['flat-2/poisoned']['passed'] or 0)  / results['flat-2/poisoned']['n']  * 100

                delta_chain = chain_poison - chain_clean
                delta_flat  = flat_poison  - flat_clean

                print(f"\n  Δchain (poisoned - clean) = {delta_chain:+.1f}pp")
                print(f"  Δflat  (poisoned - clean) = {delta_flat:+.1f}pp")
                print(f"\n  Hypothesis: |Δflat| > |Δchain|  →  {'CONFIRMED' if abs(delta_flat) > abs(delta_chain) else 'NOT CONFIRMED'}")
