ALTER TABLE admin_campaign_targets ADD COLUMN IF NOT EXISTS last_activity_triggered_at TIMESTAMP;
ALTER TABLE admin_campaign_targets ADD COLUMN IF NOT EXISTS activity_send_count INTEGER DEFAULT 0 NOT NULL;
CREATE INDEX IF NOT EXISTS idx_campaign_targets_activity_trigger ON admin_campaign_targets(campaign_id, status, last_activity_triggered_at);
