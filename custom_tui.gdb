# Define and load a custom tui layout. The script uses:
# - some gdb-provided windows: source, commands, assembly and registers
# - some custom windows, defined in a python script: locals, backtrace
# The layout is automatically applied when you source the file, you can
# comment the last line if you prefer to manually enable it.
source tui/layouts.py
tui new-layout custom {-horizontal {{-horizontal src 1 asm 1} 2 cmd 1} 3 {regs 1 backtrace 1 locals 1} 1} 1
layout custom

