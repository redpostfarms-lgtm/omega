# System Migration Guide - H:\ Drive

## Overview
Migration of The Gatekeeper system to H:\ drive for improved organization.

## Migration Steps

### 1. Preparation
```bash
# Create backup
python scripts/create_backup.py

# Verify disk space
python scripts/check_disk_space.py
```text

### 2. Directory Structure
```text
H:\The Gatekeeper\
├── src/
├── config/
├── logs/
├── data/
├── backups/
├── docs/
└── scripts/
```text

### 3. Migration Process
```bash
# Copy files
robocopy "old_path" "H:\The Gatekeeper" /MIR

# Update paths in configs
python scripts/update_config_paths.py

# Test new location
python scripts/test_migration.py
```text

### 4. Verification
- [ ] All files copied successfully
- [ ] Configs updated with new paths
- [ ] Services restarted
- [ ] Tests passing
- [ ] Backups working

### 5. Cleanup
- Archive old location
- Update shortcuts
- Update documentation

## Rollback Plan
1. Stop all services
2. Restore from backup
3. Revert path changes
4. Restart services

## Post-Migration
- Monitor logs for path errors
- Update team on new location
- Archive migration documentation
