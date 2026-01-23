import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

@dataclass
class PromptHistoryItem:
    id: str
    timestamp: str
    mode: str
    english_prompt: str
    korean_prompt: str
    negative_prompt: str
    selected_options: Dict[str, str]
    user_requirements: Optional[str]
    ollama_enhanced: bool
    ollama_model: Optional[str]
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PromptHistoryItem':
        return cls(**data)

class HistoryManager:
   
    DEFAULT_HISTORY_FILE = "prompt_history.json"
    MAX_HISTORY_ITEMS = 100
    
    def __init__(self, history_file: Optional[str] = None):
        self.history_file = history_file or self.DEFAULT_HISTORY_FILE
        self._history: List[PromptHistoryItem] = []
        self._load_history()
    
    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._history = [
                        PromptHistoryItem.from_dict(item) 
                        for item in data.get('history', [])
                    ]

                    if len(self._history) > self.MAX_HISTORY_ITEMS:
                        self._history = self._history[-self.MAX_HISTORY_ITEMS:]
                        self._save_history()
            except (json.JSONDecodeError, KeyError):
                self._history = []
        else:
            self._history = []
    
    def _save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(
                    {'history': [item.to_dict() for item in self._history]},
                    f,
                    ensure_ascii=False,
                    indent=2
                )
        except Exception as e:
            print(f"히스토리 저장 실패: {e}")
    
    def _generate_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    
    def add(
        self,
        mode: str,
        english_prompt: str,
        korean_prompt: str,
        negative_prompt: str,
        selected_options: Dict[str, str],
        user_requirements: Optional[str] = None,
        ollama_enhanced: bool = False,
        ollama_model: Optional[str] = None
    ) -> PromptHistoryItem:

        item = PromptHistoryItem(
            id=self._generate_id(),
            timestamp=datetime.now().isoformat(),
            mode=mode,
            english_prompt=english_prompt,
            korean_prompt=korean_prompt,
            negative_prompt=negative_prompt,
            selected_options=selected_options,
            user_requirements=user_requirements,
            ollama_enhanced=ollama_enhanced,
            ollama_model=ollama_model
        )
        
        # [수정] 데이터 추가 전 개수 확인 후 가장 오래된 것 삭제
        if len(self._history) >= self.MAX_HISTORY_ITEMS:
            # 10개 이상이면 가장 앞(인덱스 0)의 항목들을 제거하여 공간 확보
            self._history = self._history[-(self.MAX_HISTORY_ITEMS - 1):]
        
        self._history.append(item)
        self._save_history()
        
        return item
    
    def get_recent(self, count: int = 10) -> List[PromptHistoryItem]:
        return self._history[-count:][::-1]
    
    def delete_by_id(self, item_id: str) -> bool:
        for i, item in enumerate(self._history):
            if item.id == item_id:
                del self._history[i]
                self._save_history()
                return True
        return False
    
    def clear_all(self):
        self._history = []
        self._save_history()

    def get_statistics(self) -> Dict:
        if not self._history:
            return {"total": 0, "sfw": 0, "nsfw": 0, "ollama_enhanced": 0}
        return {
            "total": len(self._history),
            "sfw": len([i for i in self._history if i.mode == "sfw"]),
            "nsfw": len([i for i in self._history if i.mode == "nsfw"]),
            "ollama_enhanced": len([i for i in self._history if i.ollama_enhanced]),
        }

_history_manager = None
def get_history_manager(history_file=None):
    global _history_manager
    if _history_manager is None:
        _history_manager = HistoryManager(history_file)
    return _history_manager