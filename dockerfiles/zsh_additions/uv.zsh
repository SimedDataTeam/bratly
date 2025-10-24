# Generate a workspace
validate_name() {
  if [[ ! "$1" =~ ^[a-z][a-z0-9_\-]*$ ]]; then
    echo "Error: The name must start with a letter and only contain lowercase letters, numbers, underscores, and hyphens."
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

# Internal helper: create a library project at a destination path, optionally setting requires-python
smd_uv_create_lib() {
  local dest="$1" pyreq="${2:-}"
  if [[ -z "$dest" ]]; then
    echo "Error: smd_uv_create_lib requires a destination path"
    return 1
  fi
  mkdir -p "$(dirname "$dest")"
  echo "+ uv init --author-from none --vcs none \"$dest\" --lib --no-readme --no-pin-python"
  uv init --author-from none --vcs none "$dest" --lib --no-readme --no-pin-python || return $?
  if [[ -n "$pyreq" ]] && command -v toml >/dev/null 2>&1; then
    toml set project.requires-python "$pyreq" --toml-path "${dest}/pyproject.toml"
  fi
}

# Generate a library
smd_uv_lib_namespace() {
  local ns="" lib="" pyreq=">=3.10"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --namespace) ns="$2"; shift 2;;
      --lib) lib="$2"; shift 2;;
      --python) pyreq="$2"; shift 2;;
      -h|--help)
        echo "Usage: create_lib_namespace --namespace <ns> --lib <lib> [--python <spec>]"
        return 0;;
      *) echo "Unknown arg: $1"; return 1;;
    esac
  done
  if [[ -z "$ns" || -z "$lib" ]]; then
    echo "Usage: create_lib_namespace --namespace <ns> --lib <lib> [--python <spec>]"
    return 1
  fi

  validate_name "$ns" || return 1
  validate_name "$lib" || return 1

  local dist="${ns}-${lib}"
  local dest="src_libs/${dist}"
  mkdir -p "src_libs"

  # Create project via internal helper (avoid recursion)
  smd_uv_create_lib "${dest}" "${pyreq}" || return $?

  # PEP 420 reshape
  local src_root="${dest}/src"
  local old_pkg="${ns}_${lib}"
  local old_dir="${src_root}/${old_pkg}"
  if [[ ! -d "${old_dir}" ]]; then
    echo "Error: Expected ${old_dir} to exist (did uv init run?)."
    return 1
  fi
  local ns_dir="${src_root}/${ns}"
  local lib_dir="${ns_dir}/${lib}"
  mkdir -p "${lib_dir}"

  # Move contents (skip __pycache__) using zsh-native options
  setopt local_options null_glob dotglob
  for p in "${old_dir}"/*; do
    [[ "$(basename "$p")" == "__pycache__" ]] && continue
    mv "$p" "${lib_dir}/"
  done
  rmdir "${old_dir}" 2>/dev/null || rm -rf "${old_dir}"

  # Remove namespace __init__.py if present
  [[ -f "${ns_dir}/__init__.py" ]] && rm -f "${ns_dir}/__init__.py"

  # Update README import examples if exists (best-effort)
  if [[ -f "${dest}/README.md" ]]; then
    sed -i "s/import ${ns}_${lib}/import ${ns}.${lib}/g" "${dest}/README.md"
    sed -i "s/from ${ns}_${lib} import/from ${ns}.${lib} import/g" "${dest}/README.md"
  fi

  # Set uv build-backend module name in pyproject
  if command -v toml >/dev/null 2>&1; then
    toml add_section tool.uv.build-backend --toml-path "${dest}/pyproject.toml"
    toml set tool.uv.build-backend.module-name "${ns}.${lib}" --toml-path "${dest}/pyproject.toml"
  else
    # Fallback: append/replace lines directly
    if ! grep -q "^\[tool\.uv\.build-backend\]" "${dest}/pyproject.toml"; then
      printf "\n[tool.uv.build-backend]\n" >> "${dest}/pyproject.toml"
    fi
    if grep -q "^[[:space:]]*module-name[[:space:]]*=" "${dest}/pyproject.toml"; then
      sed -i "s/^[[:space:]]*module-name[[:space:]]*=.*/module-name = \"${ns}.${lib}\"/" "${dest}/pyproject.toml"
    else
      printf "module-name = \"%s\"\n" "${ns}.${lib}" >> "${dest}/pyproject.toml"
    fi
  fi

  echo "[done] Created ${dest} with PEP 420 layout (import ${ns}.${lib})"
}

# Wrapper: extend smd_uv_gen_lib to accept --namespace/--lib and delegate to smd_uv_lib_namespace
smd_uv_gen_lib() {
  local ns="" lib="" pyreq="";
  local positional=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --namespace) ns="$2"; shift 2;;
      --lib) lib="$2"; shift 2;;
      --python) pyreq="$2"; shift 2;;
      -h|--help)
        echo "Usage: smd_uv_gen_lib <lib_name> | smd_uv_gen_lib --namespace <ns> --lib <lib> [--python <spec>]"
        return 0;;
      *) positional+=("$1"); shift;;
    esac
  done

  if [[ -n "$ns" ]]; then
    if [[ -z "$lib" ]]; then
      echo "Error: --lib is required when using --namespace"
      return 1
    fi
    if [[ -n "$pyreq" ]]; then
      smd_uv_lib_namespace --namespace "$ns" --lib "$lib" --python "$pyreq"
    else
      smd_uv_lib_namespace --namespace "$ns" --lib "$lib"
    fi
    return $?
  fi

  # Fallback to original behavior (single positional <lib_name>)
  if [[ ${#positional[@]} -eq 0 ]]; then
    echo "Usage: smd_uv_gen_lib <lib_name> | smd_uv_gen_lib --namespace <ns> --lib <lib> [--python <spec>]"
    return 1
  fi
  local name="${positional[1]}"
  validate_name "$name" || return 1
  local dest="src_libs/${name}"
  smd_uv_create_lib "${dest}" || return $?
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
