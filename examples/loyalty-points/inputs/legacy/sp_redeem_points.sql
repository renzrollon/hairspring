-- Harbourline legacy loyalty module (S-04), excerpt exported 2026-10-20 for the sample loop
-- Redemption, reversal, adjustment and nightly expiry. Table names are the vendor's.
CREATE OR REPLACE PROCEDURE sp_redeem_points (p_cust_id NUMBER, p_points NUMBER) AS
  v_value_sgd NUMBER;
BEGIN
  IF p_points < 500 THEN
    RAISE_APPLICATION_ERROR(-20001, 'MIN REDEEM 500');   -- programme minimum
  END IF;
  v_value_sgd := FLOOR(p_points / 100);                 -- 100 points = SGD 1
  IF SYSDATE < DATE '2018-12-31' THEN
    v_value_sgd := v_value_sgd * 2;                     -- XMAS2018 double voucher value, temporary
  END IF;
  UPDATE loy_customer SET balance = balance - (v_value_sgd * 100) WHERE cust_id = p_cust_id;
  INSERT INTO loy_voucher (cust_id, value_sgd, status) VALUES (p_cust_id, v_value_sgd, 'I');
  INSERT INTO prn_queue (queue, payload) VALUES ('BACKOFFICE_PRN', v_value_sgd);  -- print slip at service desk
END;
/
CREATE OR REPLACE PROCEDURE sp_adjust_points (p_cust_id NUMBER, p_points NUMBER,
                                              p_reason VARCHAR2, p_approver VARCHAR2) AS
BEGIN
  IF p_reason IS NULL THEN
    RAISE_APPLICATION_ERROR(-20002, 'REASON CODE REQUIRED');
  END IF;
  IF ABS(p_points) > 5000 AND p_approver IS NULL THEN
    RAISE_APPLICATION_ERROR(-20003, 'SECOND APPROVER REQUIRED');  -- maker-checker
  END IF;
  -- txn_type 'ADJ' is used for support adjustments and for return reversals alike
  INSERT INTO loy_txn (cust_id, txn_type, points, reason) VALUES (p_cust_id, 'ADJ', p_points, p_reason);
  UPDATE loy_customer SET balance = GREATEST(balance + p_points, 0)   -- never let balance go negative
   WHERE cust_id = p_cust_id;
EXCEPTION
  WHEN OTHERS THEN NULL;  -- ignore, support will fix it by hand
END;
/
-- Nightly expiry job
UPDATE loy_txn SET status = 'E'
 WHERE status = 'X' AND posted_at < ADD_MONTHS(SYSDATE, -12);   -- expire 12 months after posting
-- Nightly purge, audit retention
DELETE FROM loy_txn WHERE created_at < ADD_MONTHS(SYSDATE, -84);  -- keep 7 years for audit
