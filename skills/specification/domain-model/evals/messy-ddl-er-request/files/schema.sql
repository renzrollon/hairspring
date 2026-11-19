-- loyalty service, v14 migration
CREATE TABLE members (
  id UUID PRIMARY KEY,
  member_no VARCHAR(12) UNIQUE NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);
CREATE TABLE points_txn (
  id UUID PRIMARY KEY,
  member_id UUID NOT NULL REFERENCES members(id),
  receipt_no VARCHAR(30) NOT NULL,
  pts INTEGER NOT NULL,
  state SMALLINT NOT NULL,          -- 0,1,2,3,4
  created_at TIMESTAMP NOT NULL
);
CREATE TABLE vouchers (
  id UUID PRIMARY KEY,
  member_id UUID NOT NULL REFERENCES members(id),
  code VARCHAR(16) UNIQUE NOT NULL,
  value_cents INTEGER NOT NULL,
  status SMALLINT NOT NULL,         -- 0,1,2,3
  created_at TIMESTAMP NOT NULL
);
CREATE TABLE voucher_txn_link (
  voucher_id UUID REFERENCES vouchers(id),
  txn_id UUID REFERENCES points_txn(id),
  pts_used INTEGER NOT NULL
);
CREATE TABLE outbox_events (id BIGSERIAL PRIMARY KEY, payload JSONB, sent BOOLEAN);
CREATE TABLE flyway_schema_history (installed_rank INT PRIMARY KEY, version VARCHAR(50));
