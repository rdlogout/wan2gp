# WAN2GP Scripts

This directory contains utility scripts for running and deploying the WAN2GP application.

## Starting the Gradio Server on Windows

### Option 1: Batch File (start_gradio.bat)

Double-click `start_gradio.bat` or run from command prompt:

```cmd
start_gradio.bat
```

### Option 2: PowerShell Script (start_gradio.ps1)

Run from PowerShell:

```powershell
.\start_gradio.ps1
```

Both scripts will:

- Check if Python is installed
- Create a virtual environment if it doesn't exist
- Install requirements if needed
- Set optimal environment variables
- Start the Gradio server on http://localhost:7860

## Pushing to Both Repositories

The project is configured to push to both Hugging Face and GitHub repositories:

- **Hugging Face**: https://huggingface.co/spaces/logoutrd/wan2gp (origin)
- **GitHub**: https://github.com/rdlogout/wan2gp.git (github)

### Option 1: Using Git Alias

```bash
git pushall
```

### Option 2: Using Shell Script (Linux/Mac)

```bash
./push_to_all.sh "Your commit message"
```

### Option 3: Using Batch File (Windows)

```cmd
push_to_all.bat "Your commit message"
```

### Option 4: Manual Push

```bash
git push origin main
git push github main
```

## Repository Setup

The repository has been configured with two remotes:

- `origin`: Hugging Face Spaces repository
- `github`: GitHub repository

To verify the setup:

```bash
git remote -v
```

## Environment Variables

The Windows scripts set these environment variables for optimal performance:

- `PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512`
- `CUDA_VISIBLE_DEVICES=0`

## Troubleshooting

### Windows PowerShell Execution Policy

If you get an execution policy error when running the PowerShell script:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Virtual Environment Issues

If the virtual environment fails to create or activate:

1. Delete the `venv` folder
2. Run the script again
3. Or manually create: `python -m venv venv`

### Git Push Issues

If pushing fails:

1. Check your Git credentials
2. Ensure you have push access to both repositories
3. Check your internet connection
4. Verify the remote URLs: `git remote -v`

### Binary Files and Hugging Face

The scripts automatically clean up Python cache files (`__pycache__`, `*.pyc`, `*.pyo`) before pushing, as Hugging Face Spaces rejects binary files. If you encounter binary file errors:

1. The scripts will automatically clean cache files
2. If issues persist, manually remove binary files:
   ```bash
   find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
   find . -name "*.pyc" -delete 2>/dev/null
   ```
3. For persistent issues, you may need to clean git history:
   ```bash
   git filter-branch --force --index-filter 'git rm -rf --cached --ignore-unmatch __pycache__' --prune-empty --tag-name-filter cat -- --all
   ```

### Repository Sync Issues

If repositories get out of sync:

1. Use `git status` to check current state
2. Use `git log --oneline -10` to see recent commits
3. Force push if necessary (use with caution):
   ```bash
   git push --force origin main
   git push --force github main
   ```
