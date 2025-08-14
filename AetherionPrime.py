#!/usr/bin/env python3
import argparse, json, sys
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--diagnostics", action="store_true")
    p.add_argument("--version", action="store_true")
    args = p.parse_args()
    if args.version:
        print("AetherionPrime 0.1.0")
        return
    if args.diagnostics:
        print(json.dumps({"status":"ok","components":["kernel","agents","memory"]}, indent=2))
        return
    print("AetherionPrime: use --diagnostics or --version")
if __name__=="__main__": main()
