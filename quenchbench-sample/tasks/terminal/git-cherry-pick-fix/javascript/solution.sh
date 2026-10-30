git cherry-pick $(git log dev --format=%H --grep='^fix: empty cart total is 0$') >/dev/null
