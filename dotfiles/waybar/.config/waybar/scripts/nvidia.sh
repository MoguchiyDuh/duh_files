#!/bin/bash
util=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits)
vram=$(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | sed 's/,//g' | awk '{print $1"MiB/"$2"MiB"}')
clock=$(nvidia-smi --query-gpu=clocks.gr --format=csv,noheader,nounits)
memclock=$(nvidia-smi --query-gpu=clocks.mem --format=csv,noheader,nounits)
temp=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits)
power=$(nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits)

echo "{\"text\":\"$util\",\"tooltip\":\"VRAM: $vram\nGPU Clock: ${clock} MHz\nMem Clock: ${memclock} MHz\nTemp: ${temp}°C\nPower: ${power}W\"}"
