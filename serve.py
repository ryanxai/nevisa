#!/usr/bin/env python3
"""
Custom HTTP server that gracefully handles broken pipe errors.
"""
import http.server
import socketserver
import sys
import threading

# Store original exception handlers
_original_excepthook = sys.excepthook

def quiet_excepthook(exc_type, exc_value, exc_traceback):
    """Custom exception handler that suppresses broken pipe errors."""
    if exc_type is BrokenPipeError:
        # Silently ignore broken pipe errors
        return
    # For other exceptions, use the original handler
    _original_excepthook(exc_type, exc_value, exc_traceback)

# Install custom exception handler for main thread
sys.excepthook = quiet_excepthook

# Install custom exception handler for threads (Python 3.8+)
if hasattr(threading, 'excepthook'):
    _original_thread_excepthook = threading.excepthook
    
    def quiet_thread_excepthook(args):
        """Custom thread exception handler that suppresses broken pipe errors."""
        if args.exc_type is BrokenPipeError:
            # Silently ignore broken pipe errors
            return
        # For other exceptions, use the original handler
        if _original_thread_excepthook:
            _original_thread_excepthook(args)
        else:
            # Fallback to default behavior
            print(f"Exception in thread {args.thread.name}:", file=sys.stderr)
            _original_excepthook(args.exc_type, args.exc_value, args.exc_traceback)
    
    threading.excepthook = quiet_thread_excepthook

class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler that suppresses broken pipe errors."""
    
    def log_message(self, format, *args):
        """Override to suppress broken pipe errors."""
        # Check if this is a broken pipe error
        if 'Broken pipe' in str(args):
            return  # Silently ignore broken pipe errors
        super().log_message(format, *args)
    
    def finish(self):
        """Override finish to catch and ignore broken pipe errors."""
        try:
            super().finish()
        except (BrokenPipeError, OSError):
            # Client disconnected, ignore silently
            pass
    
    def handle_one_request(self):
        """Override to catch broken pipe errors during request handling."""
        try:
            super().handle_one_request()
        except (BrokenPipeError, OSError):
            # Client disconnected, ignore silently
            pass
    
    def copyfile(self, source, outputfile):
        """Override copyfile to catch broken pipe errors when sending files."""
        try:
            super().copyfile(source, outputfile)
        except (BrokenPipeError, OSError):
            # Client disconnected while sending file, ignore silently
            pass

class QuietThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Threading TCP server that suppresses broken pipe errors."""
    
    allow_reuse_address = True  # Allow reusing the address/port
    
    def finish_request(self, request, client_address):
        """Override to catch and suppress broken pipe errors."""
        try:
            super().finish_request(request, client_address)
        except BrokenPipeError:
            # Client disconnected, ignore silently
            pass
    
    def process_request_thread(self, request, client_address):
        """Override to catch and suppress broken pipe errors in threads."""
        try:
            super().process_request_thread(request, client_address)
        except BrokenPipeError:
            # Client disconnected, ignore silently
            pass

if __name__ == '__main__':
    PORT = 8000
    
    # Try to find an available port starting from 8000
    port = PORT
    while port < PORT + 10:
        try:
            httpd = QuietThreadingTCPServer(("", port), QuietHTTPRequestHandler)
            print(f"Serving HTTP on :: port {port} (http://[::]:{port}/) ...")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nShutting down server...")
                httpd.shutdown()
                sys.exit(0)
            break
        except OSError as e:
            if e.errno == 48:  # Address already in use
                if port == PORT:
                    print(f"Port {port} is already in use. Trying next available port...", file=sys.stderr)
                port += 1
                continue
            else:
                raise
    else:
        print(f"Error: Could not find an available port in range {PORT}-{PORT + 9}", file=sys.stderr)
        sys.exit(1)

