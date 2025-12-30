import gc
import sys
import ctypes
import os
import time

class MemoryManager:
    @staticmethod
    def configure_for_embedded():
        """Configure GC for aggressive collection on embedded systems"""
        # Lower thresholds mean more frequent collections
        # (700, 10, 5) -> (threshold0, threshold1, threshold2)
        gc.set_threshold(700, 10, 5)
        print("[MemoryManager] GC configured for embedded system")

    @staticmethod
    def force_memory_release():
        """Force release of free memory back to OS (Linux only)"""
        try:
            # Only works on Linux with glibc
            libc = ctypes.CDLL("libc.so.6")
            # malloc_trim(0) forces heap trimming
            for _ in range(3):  # Try a few times
                libc.malloc_trim(0)
        except Exception:
            # Pass silently on Windows or if libc not found
            pass

    @staticmethod
    def aggressive_cleanup():
        """Perform aggressive multi-generation garbage collection"""
        # Collect multiple times to handle reference cycles
        for _ in range(3):
            gc.collect(0)
            gc.collect(1)
            gc.collect(2)

    @staticmethod
    def unload_module_tree(module_name):
        """Recursively unload a module and its submodules"""
        to_unload = []
        for name in sys.modules:
            if name == module_name or name.startswith(module_name + "."):
                to_unload.append(name)
        
        for name in to_unload:
            try:
                del sys.modules[name]
            except KeyError:
                pass
        
        return len(to_unload)

    @staticmethod
    def cleanup_heavy_modules():
        """Unload specific heavy modules if they are loaded"""
        heavy_modules = ['reportlab', 'openpyxl', 'pandas', 'numpy', 'matplotlib', 'PIL']
        count = 0
        for mod in heavy_modules:
            count += MemoryManager.unload_module_tree(mod)
        if count > 0:
            print(f"[MemoryManager] Unloaded {count} heavy module components")

    @staticmethod
    def full_cleanup():
        """complete cleanup sequence"""
        MemoryManager.cleanup_heavy_modules()
        MemoryManager.aggressive_cleanup()
        MemoryManager.force_memory_release()

    @staticmethod
    def get_ram_usage():
        """Get current RAM usage in MB (Linux only)"""
        try:
            with open(f"/proc/{os.getpid()}/status", "r") as f:
                for line in f:
                    if "VmRSS" in line:
                        # Format: VmRSS:   1234 kB
                        kb = int(line.split()[1])
                        return kb / 1024
        except Exception:
            return 0.0
