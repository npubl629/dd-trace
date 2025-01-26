# Debugging notes

## One-time setup ##

```bash
# Install prerequisites and setup home directory
mkdir -p /tmp/home
cd /tmp/home

apt update
apt install -y curl lldb procps htop vim

# Install perfcollect
curl -OL https://aka.ms/perfcollect
chmod +x perfcollect
./perfcollect install

# Install dotnet sdk
curl https://download.visualstudio.microsoft.com/download/pr/a91ddad4-a3c2-4303-9efc-1ca6b7af850c/be1763df9211599df1cf1c6f504b3c41/dotnet-sdk-8.0.405-linux-x64.tar.gz -o dotnet.tar.gz
mkdir -p /tmp/dotnet && tar -xzf dotnet.tar.gz -C /tmp/dotnet && mv dotnet.tar.gz /tmp/dotnet/dotnet.tar.gz

# Setup env vars for dotnet sdk
export HOME=/tmp/home
export DOTNET_ROOT=/tmp/dotnet
export PATH=/tmp/dotnet:/tmp/home/.dotnet/tools:$PATH

# Install dotnet debugging tools
dotnet tool install --global dotnet-debugger-extensions
dotnet tool install --global dotnet-dump
dotnet tool install --global dotnet-symbol

# Accept EULA for LLDB SOS extensions
dotnet-debugger-extensions install
```

## Any time you open a shell ##

```bash
cd /tmp/home
export HOME=/tmp/home
export DOTNET_ROOT=/tmp/dotnet
export PATH=/tmp/dotnet:/tmp/home/.dotnet/tools:$PATH
```

## Commands for debugging ##

Find dotnet process:

```
root@0dd1f88aa8c9:~# dotnet-dump ps
 458027  dotnet  /usr/share/dotnet/dotnet  dotnet Metrics.Idle.dll
```

Debug using lldb:

```bash
# Use pid from dotnet-dump ps
lldb -p 458027

# List threads
(lldb) thread list

# Select a thread
(lldb) thread select 16

# Output stack information using lldb's frame capture
(lldb) bt

# Output stack information using sos's frame capture
(lldb) dumpstack

# Find information about a specific managed method
(lldb) name2ee Datadog.Trace.dll Datadog.Trace.RuntimeMetrics.RuntimeMetricsWriter.PushEvents
```

Capture perf trace of a thread using `perf`, and use [hotspot](https://github.com/KDAB/hotspot?tab=readme-ov-file) to analyze it.

```bash
perf record -p 458027 -t 458087 sleep 180
perf report

./perfcollect collect sampleTrace -pid 2658863
```

## Useful debugging documentation ##

- https://learn.microsoft.com/en-us/dotnet/core/runtime-config/debugging-profiling
- https://learn.microsoft.com/en-us/dotnet/core/diagnostics/dotnet-debugger-extensions
- https://learn.microsoft.com/en-us/dotnet/core/diagnostics/debugger-extensions#syntax
- https://learn.microsoft.com/en-us/dotnet/core/diagnostics/trace-perfcollect-lttng
- https://github.com/dotnet/diagnostics/blob/main/documentation/FAQ.md
