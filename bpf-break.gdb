# Defines a new command allowing to break into a specific bpf program,
# identified by its name. The command will insert a breakpoint in
# bpf_prog_kallsyms_add to track any loaded program. If the name of the
# program being loaded matches the name of the program we want to break
# into, it will automatically insert a breakpoint at the program entry.
# For an advanced version, please check scripts/gdb/linux/bpf.py in the
# Linux kernel source tree
define bpf-break
  if $argc != 1
    printf "Usage: bpf-break <program_name>\n"
  else
    set $bpf_target_name_full = "$arg0"
    eval "set $bpf_target_name = \"%.15s\"", $bpf_target_name_full
    b bpf_prog_kallsyms_add
    commands
      silent
      set $__prog = (struct bpf_prog *)$rdi
      set $__name = (char *)$__prog->aux->name
      if $_streq($__name, $bpf_target_name)
        printf "Caught program %s loading\n", $bpf_target_name_full
        del $_hit_bpnum
        break *$__prog->bpf_func
      end
      c
    end
  c
  end
end
