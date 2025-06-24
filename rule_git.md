# Detailed Git Usage Guidelines

## 1. Repository Management

### Repository Naming
- Use platform-specific suffixes to clearly identify project type:
  ```
  ✅ Good Examples:
  - project-name-web
  - project-name-ios
  - project-name-android
  - project-name-flutter
  - project-name-api        (for API projects)
  
  ❌ Bad Examples:
  - project-name-frontend
  - project-name-backend
  - project-name-mobile
  ```

### Repository Access
- Always set repositories as private for client projects
- Manage access through user groups/teams:
  - Project Name - General: Write access (developers)
  - Project Name - Admin: Admin access (leads, managers)

### Branch Protection
- Enable branch protection rules for `develop` and `master`
- Enforce pull request workflow
- Prevent direct commits to protected branches
- Require code review approvals

## 2. Branch Management

### Primary Branches
- `develop`: Default development branch
  - All feature branches originate from here
  - Represents staging environment code
  - Requires PR for all changes

- `master`: Production branch
  - Contains production-ready code
  - Only receives merges from release branches
  - Each merge must be tagged with version

### Working Branch Types
1. **Feature Branches**
   ```
   Format: feature/<ticket-id>-<description>
   Example: feature/sc-123-user-authentication
   ```

2. **Bug Fix Branches**
   ```
   Format: bug/<ticket-id>-<description>
   Example: bug/sc-456-fix-login-crash
   ```

3. **Release Branches**
   ```
   Format: release/<version>
   Example: release/1.0.0
   ```

4. **Hotfix Branches**
   ```
   Format: hotfix/<ticket-id>-<description>
   Example: hotfix/sc-789-fix-payment-error
   ```

### Branch Naming Rules
- Use lowercase kebab-case
- Include meaningful descriptions
- Always include ticket ID when applicable
- Use forward slash (/) to separate type and description

✅ Good Examples:
```
feature/sc-123-implement-user-login
bug/sc-456-fix-payment-validation
feature/939-improve-search-performance
```

❌ Bad Examples:
```
feature/listJobPositions
Bug/userResetPassword
feature-paymentSystem
```

### Branch Management Best Practices
1. **Creation**
   - Always branch from `develop` for new features
   - Branch from `master` for hotfixes only

2. **Lifecycle**
   - Delete branches after merging
   - Keep branches focused on single features
   - Regularly rebase with develop to stay current

3. **Dependencies**
   - Use rebase strategy for updating branches
   - Cherry-pick specific commits when needed
   - Avoid long-running feature branches

## 3. Commit Guidelines

### Commit Message Structure
```
Format: [<Ticket-ID>] <Action> <description>

Examples:
[SC-123] Add user authentication system
[SC-456] Fix payment validation logic
[#789] Update documentation for API endpoints
```

### Message Formatting Rules
1. **Capitalization and Punctuation**
   - Capitalize first word
   - Use present tense verbs
   - No period at single-line end
   ```
   ✅ Good: [SC-123] Add login feature
   ❌ Bad: [sc-123] added login feature.
   ```

2. **Content Guidelines**
   - Start with action verb
   - Be specific and descriptive
   - Include context when needed
   ```
   ✅ Good: [SC-123] Implement OAuth2 authentication with Google
   ❌ Bad: [SC-123] Fix stuff
   ```

3. **Special Tags**
   - WIP commits: Add 'wip' suffix
     ```
     [SC-123] Implement payment system wip
     ```
   - Skip CI builds:
     ```
     [skip ci] [SC-123] Update documentation
     ```

### Commit Best Practices
1. **Atomic Commits**
   - One logical change per commit
   - Related files changed together
   - Independently testable changes

2. **Regular Commits**
   - Commit frequently
   - Keep changes focused
   - Avoid giant commits

3. **Quality Guidelines**
   - Write clear, meaningful messages
   - Include context for future reference
   - Think about maintainability

## 4. Release Management

### Release Process
1. **Branch Creation**
   ```
   git checkout -b release/1.0.0 develop
   ```

2. **Pull Request Format**
   - Title: `Release - 1.0.0`
   - Description Template:
   ```
   Release Link: <project-management-tool-link>

   ## Features
   - [SC-123] Implement user authentication
   - [SC-124] Add payment integration

   ## Chores
   - [SC-125] Update dependencies
   - [SC-126] Optimize build process

   ## Bugs
   - [SC-127] Fix login validation
   - [SC-128] Resolve payment error
   ```

3. **Version Tagging**
   ```
   git tag -a 1.0.0
   ```
   Tag message format:
   ```
   Version 1.0.0

   ## Features
   - [SC-123] User authentication (#125)
   - [SC-124] Payment integration (#126)

   ## Chores
   - [SC-125] Dependencies update (#127)

   ## Bugs
   - [SC-127] Login validation fix (#128)
   ```

### Version Numbering
- Follow Semantic Versioning (MAJOR.MINOR.PATCH)
  - MAJOR: Breaking changes
  - MINOR: New features (backward compatible)
  - PATCH: Bug fixes
- Start from 0.1.0
- First stable release: 1.0.0

### Release Package
1. Create GitHub/GitLab release
2. Include comprehensive changelog
3. Attach relevant artifacts
4. Close related milestone

## 5. Additional Best Practices

### Code Review
- Review PR before merging
- Address all comments
- Keep PR size manageable
- Use meaningful commit messages

### Conflict Resolution
- Rebase frequently with develop
- Resolve conflicts promptly
- Use proper merge/rebase strategies

### Documentation
- Keep README updated
- Document significant changes
- Maintain changelog
- Update API documentation

This guide ensures consistent version control practices across the project. Follow these guidelines to maintain clean repository history and efficient collaboration.