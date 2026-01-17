# Flask-Migrate Setup Guide for Omega Control Panel

**Date:** January 2026  
**Developer:** Nick (Seattle)  
**Status:** Production-Ready  
**Integration:** Works hand-in-hand with [PostgreSQL JSONB Query Guide](./POSTGRESQL_JSONB_QUERY_GUIDE.md)

---

## Overview

This guide documents the Flask-Migrate setup for database migrations in the Omega Control Panel web interface. Use this guide for schema management (migrations), and the [PostgreSQL JSONB Query Guide](./POSTGRESQL_JSONB_QUERY_GUIDE.md) for advanced querying techniques.

---

## Prerequisites

1. **Flask** - Already installed
2. **Flask-Login** - Already installed
3. **Flask-SQLAlchemy** - Needs installation
4. **Flask-Migrate** - Needs installation

---

## Installation

### Step 1: Install Dependencies

```bash
pip install Flask-SQLAlchemy Flask-Migrate
```text

Or install from requirements file:
```bash
pip install -r requirements_migrate.txt
```text

---

## Current Implementation Status

### ✅ Completed

1. **Flask-SQLAlchemy imports** - Added availability checks
2. **Flask-Migrate imports** - Added availability checks
3. **Dependencies file** - Created `requirements_migrate.txt`

### ⏳ In Progress

1. **SQLAlchemy models** - Need to convert User model to SQLAlchemy
2. **Database initialization** - Need to set up SQLAlchemy db instance
3. **Flask-Migrate initialization** - Need to initialize Migrate
4. **Migration repository** - Need to create migrations directory
5. **Database URI configuration** - Need to add database config

### 📋 Pending

1. **Convert User model** - From simple class to SQLAlchemy model
2. **Add Role model** - SQLAlchemy model for roles
3. **Association table** - Many-to-many users ↔ roles
4. **Update user methods** - Replace demo_users dict with database queries
5. **Initialize migrations** - Run `flask db init`
6. **Create initial migration** - Run `flask db migrate`
7. **Apply migration** - Run `flask db upgrade`

---

## Implementation Plan

### Phase 1: Add SQLAlchemy Support (Current)

1. ✅ Add Flask-SQLAlchemy imports
2. ✅ Add Flask-Migrate imports
3. ⏳ Initialize SQLAlchemy db instance
4. ⏳ Initialize Flask-Migrate
5. ⏳ Add database configuration

### Phase 2: Convert Models

1. ⏳ Convert User class to SQLAlchemy model
2. ⏳ Create Role SQLAlchemy model
3. ⏳ Create association table (roles_users)
4. ⏳ Update user properties and methods

### Phase 3: Update User Management

1. ⏳ Replace `_init_demo_users()` with database initialization
2. ⏳ Update `_get_user_by_id()` to query database
3. ⏳ Update `_get_user_by_username()` to query database
4. ⏳ Add database initialization (create tables, seed roles)

### Phase 4: Migrations

1. ⏳ Set FLASK_APP environment variable
2. ⏳ Run `flask db init` to create migrations directory
3. ⏳ Run `flask db migrate -m "Initial migration"` to create migration
4. ⏳ Review and edit migration if needed
5. ⏳ Run `flask db upgrade` to apply migration

---

## Database Schema

### Users Table
- `id` (Integer, Primary Key)
- `username` (String, Unique, Not Null)
- `email` (String, Unique, Optional for now)
- `password_hash` (String, Not Null)
- `role` (String, Default: 'viewer') - **Temporary** - Will migrate to many-to-many
- `active` (Boolean, Default: True)
- `created_at` (DateTime, Default: UTC now)

### Roles Table (Future - Many-to-Many)
- `id` (Integer, Primary Key)
- `name` (String, Unique, Not Null)
- `description` (String, Optional)

### Roles_Users Association Table (Future - Many-to-Many)
- `user_id` (Integer, Foreign Key → users.id)
- `role_id` (Integer, Foreign Key → roles.id)

---

## Configuration

### Database URI

For development (SQLite):
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///omega.db'
```text

For production (PostgreSQL):
```python
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'postgresql://user:pass@localhost/omega'
```text

### Flask-Migrate

```python
migrate = Migrate(app, db)
```text

---

## Commands Reference

### Initialize Migrations (Run Once)
```bash
flask db init
```text

### Create Migration
```bash
flask db migrate -m "Description of changes"
```text

### Apply Migrations
```bash
flask db upgrade
```text

### Rollback Migration
```bash
flask db downgrade
```text

### Check Status
```bash
flask db current    # Show current revision
flask db history    # Show migration history
```text

---

## Environment Variables

### Windows
```cmd
set FLASK_APP=omega_control_panel_web.py
```text

### Linux/Mac
```bash
export FLASK_APP=omega_control_panel_web.py
```text

### Permanent (via .env file)
```text
FLASK_APP=omega_control_panel_web.py
DATABASE_URL=sqlite:///omega.db
```text

---

## Notes

- **Backward Compatibility:** Current demo_users system will be replaced, but we'll maintain the same API
- **Migration Strategy:** Start with simple role string, migrate to many-to-many later
- **Seeding:** Initial roles (admin, operator, viewer) will be created via migration or seed script
- **Demo Users:** Will be migrated to database, or created via seed script

---

## Status

✅ **Production-Ready** - Comprehensive Flask-Migrate setup guide  
✅ **Integrated** - Works seamlessly with [PostgreSQL JSONB Query Guide](./POSTGRESQL_JSONB_QUERY_GUIDE.md)  
⏳ **Next Steps** - Convert User model, initialize database, create migrations

## Related Documentation

- [PostgreSQL JSONB Query Guide](./POSTGRESQL_JSONB_QUERY_GUIDE.md) — Advanced JSONB querying, indexing, and optimization techniques
- Flask-Migrate Documentation — Official Flask-Migrate reference
- Alembic Documentation — Migration framework documentation

---

## Troubleshooting Common Migration Errors

### 1. "No changes detected" / Empty migration generated

**Symptoms:** `flask db migrate` creates a file with only `pass` in `upgrade()/downgrade()`.

**Most common causes & fixes (in order of likelihood):**

1. **Models not imported in `env.py`**
   - Ensure your models are imported so Alembic sees the current MetaData:
   ```python
   # migrations/env.py (inside run_migrations_online())
   from yourapp.models import *          # or explicit imports
   target_metadata = db.metadata         # or Base.metadata
   ```

2. **Database already matches models** (trivial but frequent)
   - Use `flask db check` (Alembic ≥1.8+) to see if changes would be detected without generating files.

3. **Alembic can't detect certain changes (by design)**
   - Known limitations (from official docs):
     - Column/table renames (treated as drop + add)
     - Type changes (enable `compare_type=True` — Flask-Migrate ≥4.0 does this automatically)
     - Unnamed/anonymous constraints
     - Complex check constraints, sequences, PostgreSQL-specific objects (views/functions)
   - **Workaround:** Always review & edit migration files manually. For renames: drop old column + add new one + data copy.

### 2. SQLite-specific errors (very common in dev)

**Symptoms:** `"No support for ALTER of constraints in SQLite dialect"` or `"Constraint must have a name"`

**Root cause:** SQLite doesn't support most ALTER TABLE operations → Alembic uses batch mode (temp table → copy data → rename).

**Solutions:**

1. **Flask-Migrate ≥4.0 enables `render_as_batch=True` automatically** — upgrade if you're on older version!

2. **Use explicit constraint names (critical for batch mode):**
   ```python
   metadata = MetaData(naming_convention={
       "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
       # ... other conventions ...
   })
   ```

3. **In generated migration scripts → replace `None` with a real name** when Alembic generates `create_foreign_key(None, ...)`:
   ```python
   op.create_foreign_key('fk_users_role_id_roles', 'users', 'roles', ['role_id'], ['id'])
   ```

4. **If batch still fails → manually write the "copy table" operations** (rare).

**Pro tip:** Use PostgreSQL/MySQL in dev when possible (matches production better, avoids batch headaches).

**See "Batch Mode Details" section below for comprehensive information.**

### 3. "Can't locate revision identified by 'xxx'" or "Target database is not up to date"

**Cause:** Alembic version tracking is out of sync (often from manual DB changes, deleted migrations, or multiple environments).

**Fixes:**
1. Check current version: `flask db current`
2. If mismatched → `flask db stamp head` (marks current DB as up-to-date with latest migration)
3. Extreme fix (dev only!): Drop `alembic_version` table + `flask db stamp head`
4. **Never delete migration files without downgrading first**

### 4. "Target database is not up to date"

**Cause:** DB state doesn't match the latest migration head (often after manual changes or failed partial migration).

**Fix:**
```bash
flask db current                # see what Alembic thinks
flask db history                # list revisions
flask db downgrade <revision>   # rollback to known good state
flask db upgrade head
```text
If stuck → `flask db stamp head` (marks DB as up-to-date — use carefully!)

### 5. Foreign key / constraint issues repeating (removed then added)

**Cause:** Schema diff due to:
- Schema/schema-less mismatch
- Driver differences (e.g., mysql-connector vs pymysql)
- Unnamed FKs

**Fixes:**
1. Add explicit names to constraints in models (see "Best Practices" below)
2. For multi-schema → add `include_schemas=True` in `env.py` config
3. Switch to pymysql/psycopg2 driver if needed

### 6. KeyError: 'migrate' or command not found

**Cause:** Setup issue — Flask CLI can't find the db command group.

**Fix:**
- Ensure you have: `migrate = Migrate(app, db)`
- And `FLASK_APP` is set correctly

---

## Best Practices for Naming Constraints

### Core Principles

1. **Always name constraints explicitly** — Never rely on database-generated names
2. **Use a consistent prefix** — Makes searching/filtering easy
3. **Include table name** — Usually the child/referencing table first
4. **Include relevant columns** — Especially for composite keys
5. **Keep names < 63 chars** (PostgreSQL limit)
6. **Use lowercase + underscores** (snake_case)
7. **Prefer declarative/auto-naming in SQLAlchemy** — Use `MetaData.naming_convention`

### Recommended Convention (2026 Standard)

| Constraint Type | Prefix | Format Example | Notes |
| ---------------- | -------- | ---------------- | ------- |
| Primary Key | `pk_` | `pk_users` | Almost always single-column (id) |
| Foreign Key | `fk_` | `fk_users_role_id_roles` | Most popular: `child_table_column_referenced_table` |
| Unique | `uq_` | `uq_users_email` | Include columns if composite |
| Check | `ck_` | `ck_users_age_positive` | Descriptive suffix (business rule) |
| Default | `df_` | `df_users_created_at_now` | Less common to name explicitly |
| Index | `ix_` | `ix_users_last_name_email` | Non-unique indexes |

### SQLAlchemy + Alembic Best Practice (Highly Recommended)

Use automatic naming conventions via `MetaData.naming_convention`. This way:
- You rarely name constraints manually
- Alembic autogenerate works perfectly
- Migrations become deterministic and safe

**Add this to your models/base file:**

```python
from sqlalchemy import MetaData

metadata = MetaData(naming_convention={
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",          # index
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",          # unique
    "ck": "ck_%(table_name)s_%(constraint_name)s",          # check
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"                               # primary key
})
```text

**Then in your base class:**

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    metadata = metadata
```text

**Result:**
- `Column(..., ForeignKey(...))` → auto-named `fk_users_role_id_roles`
- Alembic migrations use safe `op.f('fk_users_role_id_roles')` tokens
- No more `None` in `create_foreign_key` / `drop_constraint`

### Quick Checklist Before Any Migration

- ✅ `export FLASK_APP=your_app.py` (or factory)
- ✅ `flask db current` → know your state
- ✅ Make model changes → `flask db migrate -m "description"`
- ✅ **Always review/edit the generated file in `migrations/versions/`**
- ✅ `flask db upgrade`
- ✅ Commit `migrations/` folder!

**Tip:** If you're hitting SQLite batch errors frequently, consider switching to PostgreSQL for development (matches production better).

---

## Batch Mode Details (SQLite)

### What Is Batch Mode?

Batch mode in Alembic is a special mechanism used **exclusively when working with SQLite** to work around one of SQLite's most annoying limitations: **SQLite does not support most ALTER TABLE operations** that other databases handle easily (PostgreSQL, MySQL, etc.).

### What SQLite Actually Forbids or Restricts

SQLite only reliably supports these ALTER TABLE operations:
- `ADD COLUMN` (with some restrictions)
- `RENAME TO` (rename table)
- `RENAME COLUMN` (since SQLite 3.25.0 / 2018)

But it does **NOT support** (or supports very poorly):
- ❌ Dropping columns
- ❌ Modifying existing columns (type, nullability, default value)
- ❌ Adding/dropping constraints (foreign keys, unique, check)
- ❌ Renaming columns in a way that affects constraints
- ❌ Almost any complex schema change

### How Batch Mode Solves This (The "Copy → Drop → Rename" Dance)

When Alembic detects an operation that SQLite can't do with plain ALTER TABLE, and batch mode is enabled, it automatically switches to this workflow:

1. **Create a new temporary table**
   - This table has the desired final schema (after your changes)

2. **Copy all data from the old table to the new temporary table**
   ```sql
   INSERT INTO _alembic_batch_temp SELECT ... FROM users;
   ```

3. **Drop the original (old) table**
   ```sql
   DROP TABLE users;
   ```

4. **Rename the temp table to the original name**
   ```sql
   ALTER TABLE _alembic_batch_temp RENAME TO users;
   ```
   → This is the only ALTER TABLE operation SQLite reliably supports here

5. **Re-create indexes, foreign keys, triggers, etc.** on the new table
   (whatever was part of the migration)

The whole process happens inside a transaction, so if anything fails → rollback → old table remains untouched.

### Example: What You Write vs What Happens

**You write in models:**
```python
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(120), nullable=False, unique=True)  # ← adding unique constraint
```text

**Generated migration (simplified):**
```python
def upgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('email', nullable=False)
        batch_op.create_unique_constraint('uq_users_email', ['email'])
```text

**Under the hood with batch mode (SQLite):**
```sql
-- Step 1: create new table with desired schema
CREATE TABLE _alembic_batch_temp (
    id INTEGER NOT NULL PRIMARY KEY,
    email VARCHAR(120) NOT NULL,
    UNIQUE (email)
);

-- Step 2: copy data
INSERT INTO _alembic_batch_temp (id, email)
SELECT id, email FROM users;

-- Step 3: drop old
DROP TABLE users;

-- Step 4: rename
ALTER TABLE _alembic_batch_temp RENAME TO users;
```text

### When & How Batch Mode Is Activated (2026 Reality)

- **Flask-Migrate ≥ 4.0** (released late 2024) → automatically enables batch mode when it detects SQLite
  → You usually don't need to set `render_as_batch=True` manually anymore.

- **You can still force/explicitly control it:**
  ```python
  migrate = Migrate(app, db, render_as_batch=True)   # explicit
  # or disable (not recommended for SQLite)
  migrate = Migrate(app, db, render_as_batch=False)
  ```

- **Inside a migration you can also control it per table:**
  ```python
  with op.batch_alter_table("users", render_as_batch=True) as batch_op:
      ...
  ```

### Important Limitations & Gotchas

| Issue | Impact | Workaround / Best Practice |
| ------- | -------- | ---------------------------- |
| **Large tables** | Very slow (full copy) | Test on staging, consider PostgreSQL for serious projects |
| **Unnamed constraints** | `ValueError: Constraint must have a name` | Always use `MetaData.naming_convention` |
| **CHECK constraints** | Usually not copied | Re-create manually in migration if needed |
| **Foreign keys with circular refs** | Can cause issues | Alembic handles most cases, but test carefully |
| **Views/triggers referencing table** | Break after rename (SQLite < 3.35) | Rare; drop & recreate them in migration if necessary |

### Quick Summary Table (2026 Perspective)

| Database | Batch Mode Needed? | Typical ALTER TABLE support | Migration speed on large tables |
| ---------- | ------------------- | ---------------------------- | -------------------------------- |
| **SQLite** | Yes (auto in recent versions) | Very limited | Slow (full copy) |
| **PostgreSQL** | No | Excellent | Fast |
| **MySQL** | No | Good (some limitations) | Fast |

**Bottom line for most Flask developers in 2026:**
- If you're using SQLite for development → batch mode just works automatically with modern Flask-Migrate.
- The only thing you must do to avoid 95% of problems is: **use naming conventions for constraints.**

---

## Real-World Batch Mode Examples

### Example 1: Adding a Non-Nullable Column + Foreign Key

**Scenario:** You want to add a required `role_id` column with a foreign key to the `roles` table.

**Model change:**
```python
# Before
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)

# After
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)  # ← new!
```text

**Generated migration:**
```python
def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            batch_op.f('fk_users_role_id_roles'), 
            'roles', ['role_id'], ['id']
        )
        batch_op.alter_column('role_id', nullable=False)

def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f('fk_users_role_id_roles'), 
            type_='foreignkey'
        )
        batch_op.alter_column('role_id', nullable=True)
        batch_op.drop_column('role_id')
```text

**What actually happens (SQLite):**
```sql
-- 1. Create temporary table with NEW schema
CREATE TABLE _alembic_batch_temp (
    id INTEGER NOT NULL,
    username VARCHAR(80) NOT NULL,
    email VARCHAR(120) NOT NULL,
    role_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_users_role_id_roles FOREIGN KEY(role_id) REFERENCES roles (id)
);

-- 2. Copy data (role_id gets NULL because old table didn't have it)
INSERT INTO _alembic_batch_temp (id, username, email, role_id)
SELECT id, username, email, NULL FROM users;

-- 3. Set default values (CRITICAL: must do this before making non-nullable)
UPDATE _alembic_batch_temp SET role_id = 1 WHERE role_id IS NULL;

-- 4. Drop old table
DROP TABLE users;

-- 5. Rename temp table
ALTER TABLE _alembic_batch_temp RENAME TO users;
```text

**Important fix for existing data:**
```python
def upgrade():
    # ... batch operations ...
    # Set default role for existing users
    op.execute("UPDATE users SET role_id = 1 WHERE role_id IS NULL")
```text

### Example 2: Dropping a Column

**Scenario:** Remove a `temp_token` column from the `users` table.

**Model change:**
```python
# Before
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80))
    email = Column(String(120))
    temp_token = Column(String(255))  # ← to be removed

# After
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80))
    email = Column(String(120))
```text

**Generated migration:**
```python
def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('temp_token')

def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('temp_token', sa.String(length=255), nullable=True))
```text

**What actually happens (SQLite):**
```sql
-- 1. Create temp table (without temp_token)
CREATE TABLE _alembic_batch_temp (
    id INTEGER NOT NULL PRIMARY KEY,
    username VARCHAR(80),
    email VARCHAR(120)
);

-- 2. Copy data (dropping the column automatically)
INSERT INTO _alembic_batch_temp (id, username, email)
SELECT id, username, email FROM users;

-- 3. Drop old table
DROP TABLE users;

-- 4. Rename temp table
ALTER TABLE _alembic_batch_temp RENAME TO users;
```text

**⚠️ Data loss warning:** Dropping a column permanently deletes that data. If you need to preserve it, add a migration to copy to another table first, then drop.

### Example 3: Adding a Nullable Column (Simplest Case)

**Scenario:** Add a `last_login` timestamp column.

**Model change:**
```python
# After
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80))
    last_login = Column(DateTime, nullable=True)  # ← new column
```text

**Generated migration:**
```python
def upgrade():
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('users', 'last_login')
```text

**What happens:**
- ✅ **No batch mode needed** — SQLite supports `ADD COLUMN` directly
- ✅ Very fast even on large tables
- ✅ Simple `ALTER TABLE users ADD COLUMN last_login DATETIME`

### Example 4: Adding a Non-Nullable Column with Default

**Option A: Database-level default (easiest)**
```python
last_login = Column(DateTime, nullable=False, server_default=func.now())
```text

**Generated migration:**
```python
def upgrade():
    op.add_column('users', sa.Column(
        'last_login',
        sa.DateTime(),
        nullable=False,
        server_default=sa.func.now()
    ))
```text
→ Existing rows get current timestamp automatically — perfect for timestamps.

**Option B: Add nullable first → set values → make non-nullable (most flexible)**
```python
def upgrade():
    # Step 1: Add as nullable
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))

    # Step 2: Set values for existing rows
    op.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE last_login IS NULL")

    # Step 3: Make non-nullable (this may trigger batch mode on SQLite)
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('last_login', nullable=False)
```text

**Why this is popular:**
- ✅ Works safely even on large tables
- ✅ Lets you run complex data migrations (e.g. calculate values from other columns)
- ✅ Batch mode only used for the final `alter_column` (usually fast)

### Quick Summary Table – Common Column Operations (2026)

| Case | Batch Mode? (SQLite) | Speed on large table | Recommended Pattern |
| ------ | --------------------- | --------------------- | --------------------- |
| **Nullable column** | No | Very fast | Just `op.add_column(..., nullable=True)` |
| **Non-nullable + server default** | No | Very fast | `server_default=func.now()` or constant |
| **Non-nullable + custom data** | Yes (only last step) | Medium | Add nullable → migrate data → alter to non-null |
| **Column + FK / Unique** | No (unless non-null) | Very fast | Use naming conventions → Alembic handles cleanly |

### Best Practices Reminder (2026)

- ✅ **Always use naming conventions in MetaData** → prevents future pain when you need to drop/modify
- ✅ **Test migrations on a copy of your database:**
  ```bash
  cp omega.db test.db
  # change URI temporarily, then
  flask db upgrade
  ```
- ✅ **Commit migration files** — even simple ones document your schema evolution
- ✅ **Back up your SQLite file before `flask db upgrade`**
- ✅ **For production → strongly consider PostgreSQL** (batch mode not needed, migrations are 5–50× faster on large tables)

---

## References

- [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)
- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
