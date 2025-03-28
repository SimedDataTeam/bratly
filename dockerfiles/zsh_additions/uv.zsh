# Generate a workspace
validate_name() {
  if [[ ! "$1" =~ ^[a-z][a-z0-9_]*$ ]]; then
    echo "Error: The name must start with a letter and only contain lowercase letters, numbers, and underscores."
    return 1
  fi
  return 0
}

smd_uv_init() {
  if [ -z "$1" ]; then
    echo "Usage: smd_uv_init <workspace-name>"
    return 1
  fi
  validate_name "$1" || return 1
  uv init --author-from none --vcs none --name "$1"-ws . && rm hello.py
  toml unset project.description --toml-path ./pyproject.toml
  toml add_section tool.uv.workspace --toml-path ./pyproject.toml
  toml set tool.uv.workspace.members TOOL_UV_WORKSPACE_MEMBERS_PLACEHOLDER --toml-path ./pyproject.toml
  sed -i 's|"TOOL_UV_WORKSPACE_MEMBERS_PLACEHOLDER"|["src_*/*"]|g' ./pyproject.toml
  rm ./README.md
  cp ~/zsh_additions/statics/README.md ./README.md
}

# Generate a library
smd_uv_gen_lib() {
  if [ -z "$1" ]; then
    echo "Usage: smd_uv_gen_lib <lib_name>"
    return 1
  fi
  validate_name "$1" || return 1
  uv init --author-from none --vcs none ./src_libs/"$1" --lib --no-readme --no-pin-python
}

# Generate an app
smd_uv_gen_app() {
  if [ -z "$1" ]; then
    echo "Usage: smd_uv_gen_app <app_name>"
    return 1
  fi
  validate_name "$1" || return 1
  uv init --author-from none --vcs none ./src_apps/"$1" --package --no-readme --no-pin-python
}

# Generate a dev app
smd_uv_gen_dev() {
  if [ -z "$1" ]; then
    echo "Usage: smd_uv_gen_dev <dev_app_name>"
    return 1
  fi
  validate_name "$1" || return 1
  uv init --author-from none --vcs none ./src_devs/"$1"_dev --package --no-readme --no-pin-python
}
