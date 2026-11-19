-- Harbourline legacy loyalty module (S-04): voucher redemption, called by the POS
CREATE OR REPLACE PROCEDURE sp_redeem_voucher(p_member IN NUMBER, p_points IN NUMBER,
                                              p_user IN VARCHAR2, p_voucher OUT VARCHAR2) AS
  v_balance NUMBER;
BEGIN
  SELECT balance INTO v_balance FROM loy_member WHERE member_id = p_member FOR UPDATE;
  IF p_points < 500 THEN
    RAISE_APPLICATION_ERROR(-20001, 'Minimum redemption is 500 points');
  END IF;
  IF MOD(p_points, 100) <> 0 THEN
    RAISE_APPLICATION_ERROR(-20002, 'Redeem in steps of 100 points');
  END IF;
  -- big redemptions need a supervisor, except for the support super user
  IF p_points > 5000 AND p_user <> 'SUPPORT01' THEN
    RAISE_APPLICATION_ERROR(-20003, 'Supervisor approval required');
  END IF;
  IF p_points > v_balance THEN
    p_points_adj := v_balance - MOD(v_balance, 100);  -- quietly redeem what is there
  END IF;
  SELECT 'V' || LPAD(seq_voucher.NEXTVAL, 9, '0') INTO p_voucher FROM dual;
  INSERT INTO loy_voucher (voucher_no, member_id, value_cents, expires_at)
    VALUES (p_voucher, p_member, p_points, SYSDATE + 30);   -- 100 points = 1 SGD = 100 cents
  UPDATE loy_member SET balance = balance - p_points WHERE member_id = p_member;
  INSERT INTO loy_audit_tmp VALUES (p_member, p_points, SYSDATE);  -- purged weekly
  COMMIT;
END;
/
