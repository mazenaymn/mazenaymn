# GitHub Profile Setup Guide

## 📝 Setup Instructions

### 1. Create Special Repository
This repository must be named exactly as your GitHub username. For example, if your username is `mazenaymn`, create a repository called `mazenaymn`.

### 2. Repository Settings
- ✅ Make it **Public**
- ✅ Initialize with README (or push this README.md)
- ✅ The README.md will automatically appear on your profile

### 3. Update Your Username
Replace `mazenaymn` in README.md with your actual GitHub username in these sections:
- Profile views counter
- GitHub stats cards
- Contribution streak
- Top languages
- Trophies
- Activity graph
- Snake animation URLs

### 4. Enable GitHub Actions
1. Go to repository Settings → Actions → General
2. Enable "Read and write permissions" for workflows
3. Save changes

### 5. Run the Snake Animation
- The snake animation will generate automatically via GitHub Actions
- First run: Go to Actions tab → Click "Generate Snake" → Run workflow
- It will auto-update every 12 hours after that

## 🎨 Customization Options

### Change Theme Colors
Current theme: `tokyonight`

Other popular themes:
- `radical`
- `dracula`
- `monokai`
- `gruvbox`
- `onedark`
- `cobalt`
- `synthwave`
- `highcontrast`
- `dark`
- `merko`

Replace `theme=tokyonight` with your preferred theme in the README.

### Customize Tech Stack
Edit the badges in the "Tech Stack" section to match your actual skills. Find more badges at:
- https://github.com/Ileriayo/markdown-badges
- https://shields.io

### Add More Features

#### Spotify Now Playing
```markdown
[![Spotify](https://novatorem-mazenaymn.vercel.app/api/spotify)](https://open.spotify.com/user/YOUR_SPOTIFY_ID)
```

#### WakaTime Stats (Coding Activity)
```markdown
![WakaTime Stats](https://github-readme-stats.vercel.app/api/wakatime?username=YOUR_WAKATIME_USERNAME&theme=tokyonight)
```

#### Latest Blog Posts (DEV.to)
```markdown
[![Dev.to](https://img.shields.io/badge/dev.to-0A0A0A?style=for-the-badge&logo=dev.to&logoColor=white)](https://dev.to/YOUR_USERNAME)
```

## 🚀 Deploy Steps

```bash
# 1. Initialize git (if not already done)
git init

# 2. Add files
git add .

# 3. Commit
git commit -m "✨ Initial commit: Dynamic GitHub Profile"

# 4. Create repository on GitHub (name it as your username)
# Then connect and push:
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_USERNAME.git
git push -u origin main
```

## 🔧 Troubleshooting

### Snake animation not showing?
1. Make sure GitHub Actions ran successfully (check Actions tab)
2. Wait 5-10 minutes after first run
3. Check that the `output` branch was created
4. Verify workflow permissions are set correctly

### Stats not loading?
- The services might be rate-limited
- Try refreshing after a few minutes
- Check if your username is correct

### Profile not updating?
- Make sure repository name matches your GitHub username exactly
- Repository must be public
- README.md must be in the root directory

## 📱 Preview
Visit your profile at: `https://github.com/YOUR_USERNAME`

---

**Note:** Replace `mazenaymn` with your actual GitHub username throughout the README.md file!
