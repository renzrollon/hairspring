-- Harbourline legacy loyalty module (S-04), exported 2026-10-20
-- Nightly job: post pending points older than 24 hours.
CREATE OR REPLACE PROCEDURE sp_post_points AS
  CURSOR c_pending IS
    SELECT txn_id, member_id, store_id, amount_cents, created_at
      FROM loy_txn
     WHERE status = 'P'
       AND created_at < SYSDATE - 1;            -- return window: 24 h
  v_points NUMBER;
BEGIN
  FOR r IN c_pending LOOP
    v_points := FLOOR(r.amount_cents / 100);    -- 1 point per SGD 1, rounded down
    IF r.store_id IN (17, 23) AND r.created_at < DATE '2019-12-31' THEN
      v_points := v_points * 3;                 -- XMAS2019 triple points, temporary
    END IF;
    IF v_points > 5000 THEN
      v_points := 5000;                         -- cap per transaction (ops request 2016?)
    END IF;
    UPDATE loy_member
       SET balance = GREATEST(balance + v_points, 0)   -- never let balance go negative
     WHERE member_id = r.member_id;
    UPDATE loy_txn SET status = 'X', points = v_points WHERE txn_id = r.txn_id;
    INSERT INTO loy_txn_tmp (txn_id) VALUES (r.txn_id);  -- staging for CRM nightly pickup
  END LOOP;
  COMMIT;
EXCEPTION
  WHEN OTHERS THEN
    ROLLBACK;  -- whole batch is retried next night
END;
/
