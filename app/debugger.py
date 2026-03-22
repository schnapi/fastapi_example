def _enable_debugpy():
    import debugpy

    debugpy.listen(("0.0.0.0", 5678))
    print("Waiting for debugger attach...")
    debugpy.wait_for_client()


def enable_debugpy():
    import signal
    import sys
    import threading

    threading.Thread(target=_enable_debugpy, daemon=True).start()

    def shutdown_handler(sig, frame):
        print("Debugger requested shutdown, exiting...")
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)
