"""Predefined command configurations."""

COMMANDS = {
    "NPM": [
        ("▶️ Dev Server", "npm run dev"),
        ("📦 Build", "npm run build"),
        ("⚙️ Worker", "npm run worker"),
        ("📥 Install", "npm install"),
    ],
    "Prisma": [
        ("🗄️ Studio", "npx prisma studio"),
        ("🔄 Migrate", "npx prisma migrate dev"),
        ("⚡ Generate", "npx prisma generate"),
    ],
    "Git": [
        ("📊 Status", "git status"),
        ("⬇️ Pull", "git pull"),
        ("⬆️ Push", "git push"),
        ("✅ Commit", "GIT_COMMIT"),  # Special handler
    ],
    "Custom": []  # User-defined commands
}

# Icons for command categories
CATEGORY_ICONS = {
    "NPM": "📦",
    "Prisma": "🗄️",
    "Git": "🔀",
    "Custom": "⚡"
}
