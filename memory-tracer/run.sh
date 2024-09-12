#!/bin/bash

# Credits: https://gist.github.com/cgarciae/abff0b720e142e1015ed3e3789996c21#file-timed-sh

echo "Tracing EVM Memory..."

/usr/bin/time --format "⏲️  Processing time: %E (in [hours:]minutes:seconds)\n💾 Memory usage: %MKB\n🧠 CPU usage: %P"  python tracer.py "$@"
