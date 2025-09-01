# Clean all
alias smd_clean_all="git clean -dfX --exclude='!*keepme*' --exclude='!.env' && find . -type d -empty -delete"

# Init a workspace
smd_init_all() {
  if [ -z "$1" ]; then
    echo "Usage: smd_init_all <app-name> <remote-url>"
    echo "DO NOT CREATE A README ON THE NEW REPOSITORY ON GITLAB"
    return 1
  fi
  smd_uv_init "$1"
  smd_git_init "$2"
  smd_gitlab_ci_init
  smd_git_gen_gitignore
}
