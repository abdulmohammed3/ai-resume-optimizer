# Database Migrations

This directory contains database migrations for the AI Resume Optimizer project using Supabase.

## Initial Setup

1. Access your Supabase project's SQL editor
2. Copy the contents of `001_create_tables.sql`
3. Execute the SQL in your Supabase SQL editor

## Schema Overview

### Tables

1. `resumes`
   - Stores user resume data and analysis results
   - Uses UUID for primary keys
   - Includes content, analysis, and file metadata
   - Row Level Security (RLS) enabled

2. `user_settings`
   - Stores user-specific settings and preferences
   - Controls storage quotas and premium status
   - Row Level Security (RLS) enabled

3. `resume_versions`
   - Tracks version history of resumes
   - Links to main resumes table
   - Includes version number and timestamps
   - Row Level Security (RLS) enabled

### Security

- Row Level Security (RLS) is enabled on all tables
- Policies ensure users can only access their own data
- Authentication is handled through Supabase Auth

### Storage

The project uses Supabase Storage with the following buckets:

1. `resumes` - Private bucket for storing resume files
   - Files are organized by user: `user_{user_id}/{resume_id}.{extension}`
   - Access controlled through RLS policies

## Manual Migration Steps

If you need to apply migrations manually:

1. Connect to your Supabase project's SQL editor
2. Create a new query
3. Copy and paste the migration file content
4. Execute the query
5. Verify the changes in the Table Editor

## Troubleshooting

Common issues and solutions:

1. **RLS Policy Errors**
   - Ensure policies are created in correct order
   - Verify auth.uid() function is available
   - Check user authentication status

2. **Storage Issues**
   - Verify bucket exists and is configured correctly
   - Check storage quotas in user_settings
   - Ensure proper file paths are used

3. **Version History**
   - version_number should increment automatically
   - Check resume_id references are valid
   - Verify cascade delete is working

## Best Practices

1. Always backup data before migrations
2. Test migrations in development first
3. Keep track of applied migrations
4. Use transactions for complex changes
5. Validate schema after migrations

## Environment Setup

Required environment variables in `.env`:

```bash
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_service_role_key
SUPABASE_JWT_SECRET=your_jwt_secret
```

## Validation

After applying migrations, verify:

1. Tables are created with correct columns
2. Indexes are present and optimized
3. RLS policies are active
4. Triggers are functioning
5. Foreign key constraints are enforced