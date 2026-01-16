# Security Guidelines

## Password Management

### DO NOT use placeholder passwords in production!

### Required Actions
1. Generate strong passwords using password manager
2. Store in secure vault (e.g., AWS Secrets Manager, HashiCorp Vault)
3. Use environment variables for local development
4. Implement password rotation policy

### Password Requirements
- Minimum 16 characters
- Mix of uppercase, lowercase, numbers, symbols
- No common words or patterns
- Unique per service

### Setup
```bash
# Generate secure password
python scripts/generate_secure_password.py

# Store in environment
echo "DB_PASSWORD=your_secure_password" >> .env
```

### Audit Checklist
- [ ] All placeholder passwords replaced
- [ ] Secrets stored in secure vault
- [ ] Access logs enabled
- [ ] Rotation schedule defined
- [ ] Emergency procedures documented
