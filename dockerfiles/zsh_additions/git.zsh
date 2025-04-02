# Gitignore
smd_git_init() {
  if [ -z "$1" ]; then
    echo "Usage: smd_git_init <remote-url>"
    return 1
  fi

  git init
  git remote add origin "$1"
}

smd_gitlab_ci_init() {
  if [ -f .gitlab-ci.yml ]; then
    echo ".gitlab-ci.yml already exists"
    return 1
  fi
  cp ~/zsh_additions/statics/gitlab-ci.yml .gitlab-ci.yml
}

smd_git_gen_gitignore() {
  if [ -f .gitignore ]; then
    echo ".gitignore already exists"
    return 1
  fi

  touch .gitignore
  first=true

  for file in ~/zsh_additions/statics/gitignores/*.gitignore; do
    if [ "$first" = true ]; then
      first=false
    else
      echo "" >>.gitignore
    fi

    echo "##################### $(basename "$file" .gitignore) #####################" >>.gitignore
    cat "$file" >>.gitignore
  done
}
