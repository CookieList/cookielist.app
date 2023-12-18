from pathlib import Path
from functools import cache

@cache
class __Assets:
    __assets: dict[str, Path] = {}
    
    def __init__(self) -> None:
        self.root = Path(__file__).parent
        for file in self.root.iterdir():
            if file.name != '__init__.py':
                self.__assets[file.name] = file
                
    def __getitem__(self, name: str) -> Path:
        return self.__assets[name]
    
assets = __Assets()