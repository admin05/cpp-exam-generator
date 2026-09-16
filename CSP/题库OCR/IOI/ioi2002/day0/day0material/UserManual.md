

{0}------------------------------------------------

# User Manual for IOI 2002 Yong-In, Korea

## GENERAL

### Contestant materials

Contestants will get the competition materials in the competition envelope. The envelope will contain a sheet for a user id and password for the web services. You need them to access the services.

### Selecting operating system

You can select Linux or Windows XP at booting. Competition computers are configured for dual-booting. Use the cursor key to highlight your choice and type Enter key.

### Login

You do not need to login to Windows XP. You can login to Linux with

```
username: ioi  
password: ioi
```

### Restarting your computer

In Windows XP, click 'Start' and 'Turn off computer'. From the menu that appears choose 'Restart'.

In Linux, you may press **Ctrl-Alt-F1** to change console mode. (You can return to X-Windows mode by pressing **Ctrl-Alt-F7**.) Then you may press **Ctrl-Alt-Del** to restart.

### If you need help

If you need any assistance (system trouble, go to toilet, whatever), please just raise your hand and wait for help.

## PROGRAMMING

### Comment tags for grading

Your program or output file (for output-only tasks) must have certain tags in comments for the grading system to identify the task and the programming languages (for source code file). For the source code submission, the syntax will be

```
TASK: taskname  
LANG: LANGUAGE
```

where `LANGUAGE` is one of `C`, `C++`, or `PASCAL`. For the output only tasks, the syntax will be `#FILE taskname data`. See the task overviews and task descriptions for detail.

{1}------------------------------------------------

### Range of integer variable

The ordinary type 'integer' in freepascal has the range of -32768 to +32767. In some tasks, this may not be enough. Use 32bit variant 'longint' type which has the range of -2147483648 to +2147483647.

### Exit value

For C and C++ programmers: make sure that your program terminates with exit(0) or "return 0" in main(). Exiting with any other value is considered as an incorrect termination.

A normally terminated Pascal program returns a 0 when it terminates.

### Differences between Linux and Windows XP

A program submitted for grading or testing will be compiled using the options given in the overview sheet. The compiled program will be executed on Linux.

Running programs on a Linux machine differs slightly from running programs on a Windows machine.

- If you access a pointer variable that points the memory outside your allocation, your program may stop abnormally.
- If you access outside the boundary of an array, your program may stop abnormally.
- Linux does not initialize local variables to any predictable value.

These differences mean that your program might work fine on Windows XP and fail on Linux. Be careful when using pointers, arrays and uninitialized variables to avoid these problems

## TROUBLES

There are some inconveniences for programming in the competition environment. You can avoid these problems.

### RHIDE and debugging problem in Windows XP

**Trouble:** If you set breakpoints and the program terminates without reaching any of the breakpoints, the DOS box will be terminated without even a message.

**Solution:** Set any breakpoints on the first or last line to reach in any case.

### RHIDE and black screen in Windows XP

**Trouble:** If you launch RHIDE in full screen mode and you choose DOS shell, or execute the program, or exit RHIDE, you may see only a black screen.

**Solution:** Change to the window mode by pressing Alt+Enter. You may avoid this problem by launching RHIDE with '-S' option.

{2}------------------------------------------------

### Freepascal IDE in Linux

**Trouble:** The function of viewing user screen in FP IDE has some trouble. It breaks the IDE editing screen.

**Solution:** Returning of editing mode makes the screen clean again. You may avoid this problem by using console compilation and debugging.

## FORBIDDEN

### A contestant

- trying to interfere with other contestants' activities,
- trying to break the installations or evaluation facilities,
- trying to harmfully interfere with the running of the competition in any way, or
- trying to communicate in any way during a competition round with anyone other than the competition staff

will be disqualified from the competition.

### Submitted programs

- are not allowed to access the network,
- are not allowed to fork,
- are not allowed to read or create files directly,
- are not allowed to attack the system security or the grader,
- are not allowed to attempt to execute other programs,
- are not allowed to change file system permissions, and
- are not allowed to read file system information.

A contestant whose program attempts any of the above will be disqualified