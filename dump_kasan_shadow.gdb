# Defines a new command that takes an address and size for a memory region,
# and prints the corresponding KASAN shadow memory for this area + a few
# bytes before + a few bytes after
# This command does not check that the running kernel has KASAN enabled !
# Things may blow up if you call it on a non-KASAN kernel
define dump_kasan_shadow
  if $argc != 2 
    printf "usage: dump_kasan_shadow <address> <len>\n"
  else
    set $_mem_addr = (unsigned long)($arg0) - (unsigned long)($arg0)%8
    set $_mem_len = (unsigned long)($arg1)
    set $_shadow_addr = ($_mem_addr >> 3) + 0xdffffc0000000000
    set $_shadow_len = $_mem_len >> 3
    if $_shadow_len % 8 != 0
	set $_extra_shadow = 8 -  $_shadow_len % 8
    else
	set $_extra_shadow = 8
    end
    printf "KASAN shadow for %d(+%d)B@%lx\n", $_mem_len, $_extra_shadow*8, $_mem_addr
    x/8bx $_shadow_addr - 8
    printf "-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\t\n"
    eval "x/%dbx $_shadow_addr", $_shadow_len + $_extra_shadow
  end
end
