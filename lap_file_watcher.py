from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time
import re
import json

class LapFileHandler(FileSystemEventHandler):
    def __init__(self, analyzer, results_file=None):
        self.analyzer = analyzer
        self.results_file = results_file
        self.processed_files = set()
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        if not event.src_path.endswith('.csv'):
            return
        
        if event.src_path in self.processed_files:
            return
        
        time.sleep(0.5)
        
        lap_number = self._extract_lap_number(event.src_path)
        
        print(f"New lap detected: {Path(event.src_path).name} (Lap {lap_number})")
        
        results = self.analyzer.process_new_lap(event.src_path, lap_number)
        
        self.processed_files.add(event.src_path)
        
        if self.results_file:
            try:
                with open(self.results_file, 'w') as f:
                    json.dump(results, f)
            except Exception as e:
                print(f"Error writing results to file: {e}")
        
        return results
    
    def _extract_lap_number(self, filepath):
        filename = Path(filepath).stem
        
        match = re.search(r'lap[_-]?(\d+)', filename, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        match = re.search(r'_(\d+)\.csv$', filepath)
        if match:
            return int(match.group(1))
        
        return len(self.processed_files) + 1

class LapFileWatcher:
    def __init__(self, watch_directory, analyzer, results_file=None):
        self.watch_directory = Path(watch_directory)
        self.analyzer = analyzer
        self.results_file = results_file
        self.observer = None
        self.event_handler = None
    
    def start(self):
        if not self.watch_directory.exists():
            self.watch_directory.mkdir(parents=True, exist_ok=True)
        
        self.event_handler = LapFileHandler(self.analyzer, self.results_file)
        
        self.observer = Observer()
        self.observer.schedule(
            self.event_handler,
            str(self.watch_directory),
            recursive=False
        )
        
        self.observer.start()
        print(f"Watching directory: {self.watch_directory}")
        print("Waiting for lap files...")
    
    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            print("File watcher stopped")
    
    def is_alive(self):
        return self.observer and self.observer.is_alive()