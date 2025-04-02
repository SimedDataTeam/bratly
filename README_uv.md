# Create a new lib

`smd_uv_gen_lib LIB_NAME`

# Create a new app

`smd_uv_gen_app APP_NAME`

# Install a lib in another lib or app

`uv add --package LIB_OR_APP_NAME LIB_NAME`

# You should always sync the "upper level" app/lib you're working on (it syncs it + all dependencies)

`uv sync --package LIB_OR_APP_NAME`

# Running (after sync)

`uv run --package APP_NAME SCRIPT_NAME`
