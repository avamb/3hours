# Migration to TIMESTAMP WITH TIME ZONE

## Overview
This migration converts all datetime columns from `TIMESTAMP WITHOUT TIME ZONE` to `TIMESTAMP WITH TIME ZONE` for proper timezone handling.

## Why This Migration?
- **Current Problem**: Database stores timezone-naive timestamps, causing issues with timezone conversions
- **Solution**: Use PostgreSQL's native timezone-aware timestamps
- **Benefits**:
  - No more timezone conversion errors
  - Proper handling of users in different timezones
  - Cleaner code without `.replace(tzinfo=None)` hacks

## Affected Tables and Columns

### High Priority (User-facing data)
1. **users**
   - created_at
   - updated_at
   - last_active_at
   - notifications_paused_until

2. **moments**
   - created_at

3. **conversations**
   - created_at

4. **conversation_memories**
   - created_at
   - updated_at

### Medium Priority (System data)
5. **user_stats**
   - updated_at
   - last_good_moment_date

6. **feedback**
   - created_at
   - reviewed_at

7. **social_profiles**
   - created_at
   - updated_at
   - last_parsed_at

### Low Priority (Admin/System)
8. **api_usage**
   - timestamp

9. **system_logs**
   - created_at

10. **prompt_templates**
    - created_at
    - updated_at

11. **scheduled_notifications**
    - scheduled_for
    - created_at

## Migration Steps

### 1. Pre-Migration Checklist
- [ ] Create full database backup
- [ ] Test migration on staging environment
- [ ] Notify team about maintenance window
- [ ] Prepare rollback plan

### 2. Backup Current Data
```bash
# Full database backup
pg_dump -h localhost -U postgres -d mindsethappybot > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup specific tables with timestamps
pg_dump -h localhost -U postgres -d mindsethappybot \
  -t users -t moments -t conversations -t conversation_memories \
  -t user_stats -t feedback -t social_profiles \
  > timestamp_tables_backup_$(date +%Y%m%d_%H%M%S).sql
```

### 3. Run Migration
```bash
# Apply the migration
alembic upgrade head

# Verify migration
psql -h localhost -U postgres -d mindsethappybot -c "\d+ users"
```

### 4. Post-Migration Verification
- [ ] Check that all timestamps are in UTC
- [ ] Verify application can read/write timestamps
- [ ] Test timezone conversion for different user timezones
- [ ] Check scheduled notifications work correctly

### 5. Rollback Plan (if needed)
```bash
# Restore from backup
psql -h localhost -U postgres -d mindsethappybot < backup_YYYYMMDD_HHMMSS.sql

# Or downgrade migration
alembic downgrade -1
```

## Code Changes Required

### Before Migration
```python
# Current workaround
datetime.now(timezone.utc).replace(tzinfo=None)
```

### After Migration
```python
# Clean code
datetime.now(timezone.utc)
```

## Testing Strategy

### Unit Tests
- Test datetime operations with timezone-aware objects
- Verify no timezone conversion errors

### Integration Tests
- Create moments in different timezones
- Verify scheduled notifications respect user timezones
- Test "Today/Week/Month" filters with timezone boundaries

### Load Testing
- Verify no performance degradation
- Check index performance on timestamptz columns

## Risk Assessment

### Risks
1. **Data Loss**: Mitigated by comprehensive backups
2. **Downtime**: Estimated 5-10 minutes for migration
3. **Timezone Confusion**: All existing timestamps assumed to be UTC

### Rollback Triggers
- Migration fails with error
- Application cannot connect after migration
- Data corruption detected
- Performance degradation > 20%

## Timeline
- **Preparation**: 1 hour
- **Backup**: 15 minutes
- **Migration**: 5-10 minutes
- **Verification**: 30 minutes
- **Total Window**: 2 hours

## Success Criteria
- [ ] All datetime columns converted to TIMESTAMPTZ
- [ ] Application runs without timezone errors
- [ ] All tests pass
- [ ] No data loss
- [ ] Performance metrics within acceptable range