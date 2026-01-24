import random
from typing import Dict, Optional, List, Tuple
from data.prompt_database import (
    MODIFIERS, DATA, PROMPT_TEMPLATES,
    QUALITY_PREFIXES, QUALITY_SUFFIXES, NEGATIVE_PROMPTS,
    get_category_options, get_modifier_options, get_english_value
)


class PromptGenerator:
    """
    지능형 프롬프트 생성 엔진
    
    자연스러운 문장 구조와 일관된 스타일을 유지하면서
    다양하고 창의적인 프롬프트를 생성합니다.
    """
    
    def __init__(self, mode: str = "sfw"):
        """
        Args:
            mode: "sfw" 또는 "nsfw"
        """
        self.mode = mode.lower()
        self._validate_mode()
    
    def _validate_mode(self):
        """모드 유효성 검증"""
        if self.mode not in ["sfw", "nsfw"]:
            raise ValueError(f"Invalid mode: {self.mode}. Must be 'sfw' or 'nsfw'")
    
    def set_mode(self, mode: str):
        """모드 변경"""
        self.mode = mode.lower()
        self._validate_mode()
    
    def _select_item(self, category: str, user_selection: str = "랜덤") -> Optional[str]:
        """
        카테고리에서 아이템 선택 (영문 값 반환)
        
        Args:
            category: 카테고리 이름
            user_selection: 사용자 선택값 ("랜덤", "제외", 또는 한글 키)
        
        Returns:
            선택된 영문 값 또는 None
        """
        if user_selection == "제외":
            return None
        
        if user_selection != "랜덤":
            # 한글 키 -> 영문 값 변환
            return get_english_value(category, user_selection, self.mode)
        
        # 랜덤 선택
        options = get_category_options(category, self.mode)
        if not options:
            return None
        
        selected_korean = random.choice(options)
        return get_english_value(category, selected_korean, self.mode)
    
    def _select_modifier(self, modifier_type: str) -> str:
        options = get_modifier_options(modifier_type, self.mode)
        return random.choice(options) if options else ""
    
    def _build_subject_description(
        self,
        gender: Optional[str],
        race: Optional[str],
        skin: str,
        adjective: str
    ) -> str:
        if not gender:
            return ""
        
        parts = []
        if adjective:
            parts.append(adjective)
        if race:
            parts.append(race)
        parts.append(gender)
        parts.append(f"with {skin}")
        
        return " ".join(parts)
    
    def _build_appearance_description(
        self,
        hair: Optional[str],
        clothing: Optional[str],
        body_type: Optional[str]
    ) -> List[str]:
        """외모 설명 구성"""
        parts = []
        
        if hair:
            hair_state = self._select_modifier("상태")
            parts.append(f"{hair_state} {hair}")
        
        if clothing:
            # 의상 재질 추가 (40% 확률)
            if random.random() > 0.6:
                fabric = self._select_modifier("의상재질")
                parts.append(f"wearing {fabric} {clothing}")
            else:
                parts.append(f"wearing {clothing}")
        
        if body_type:
            parts.append(body_type)
        
        return parts
    
    def _build_scene_description(
        self,
        pose: Optional[str],
        background: Optional[str],
        expression: Optional[str],
        lighting: Optional[str]
    ) -> List[str]:
        """장면 설명 구성"""
        parts = []
        
        if pose:
            parts.append(pose)
        if expression:
            parts.append(expression)
        if background:
            parts.append(f"in {background}")
        if lighting:
            parts.append(lighting)
        
        return parts
    
    def _apply_user_requirements(
        self,
        base_prompt: str,
        user_requirements: Optional[str]
    ) -> str:
        """사용자 요구사항 적용"""
        if not user_requirements or not user_requirements.strip():
            return base_prompt
        
        # 사용자 요구사항을 자연스럽게 통합
        req = user_requirements.strip()
        
        # 요구사항이 이미 프롬프트 형태인 경우
        if any(keyword in req.lower() for keyword in ['wearing', 'with', 'in', 'at']):
            return f"{base_prompt}, {req}"
        
        # 일반 요구사항인 경우
        return f"{base_prompt}, incorporating {req}"
    
    def generate(
        self,
        selected_options: Dict[str, str],
        user_requirements: Optional[str] = None,
        template_style: str = "random",
        style: str = "photorealistic"
    ) -> Tuple[str, str]:
        """
        프롬프트 생성
        
        Args:
            selected_options: 카테고리별 사용자 선택 (한글 키)
            user_requirements: 추가 요구사항 (선택)
            template_style: 템플릿 스타일
        
        Returns:
            (positive_prompt, negative_prompt) 튜플 - 영문
        """
        # 1. 핵심 수식어 선택
        adjective = self._select_modifier("형용사")
        skin = self._select_modifier("피부질감")
        
        # 2. 카테고리별 아이템 선택 (한글 -> 영문 변환)
        gender = self._select_item("나이/성별", selected_options.get("나이/성별", "랜덤"))
        race = self._select_item("인종/외모", selected_options.get("인종/외모", "랜덤"))
        hair = self._select_item("헤어스타일", selected_options.get("헤어스타일", "랜덤"))
        clothing = self._select_item("의상", selected_options.get("의상", "랜덤"))
        body_type = self._select_item("몸매/체형", selected_options.get("몸매/체형", "랜덤"))
        pose = self._select_item("포즈/행동", selected_options.get("포즈/행동", "랜덤"))
        background = self._select_item("배경/장소", selected_options.get("배경/장소", "랜덤"))
        expression = self._select_item("상황/표정", selected_options.get("상황/표정", "랜덤"))
        lighting = self._select_item("촬영/조명", selected_options.get("촬영/조명", "랜덤"))
        
        # 3. 주제제 설명 구성
        subject = self._build_subject_description(gender, race, skin, adjective)
        
        # 4. 외모 설명 구성
        appearance_parts = self._build_appearance_description(hair, clothing, body_type)
        
        # 5. 장면 설명 구성
        scene_parts = self._build_scene_description(pose, background, expression, lighting)
        
        # 6. 전체 프롬프트 조합
        all_parts = [subject] + appearance_parts + scene_parts
        all_parts = [p for p in all_parts if p]  # 빈 문자열 제거
        
        # 7. 품질 프리픽스/서픽스 선택
        prefix_key = self.mode
        suffix_key = self.mode
        
        if style == "anime":
            # anime_sfw 또는 anime_nsfw 키 사용
            prefix_key = f"anime_{self.mode}"
            suffix_key = f"anime_{self.mode}"
            
            # 키가 없는 경우 안전장치 (기본 sfw)
            if prefix_key not in QUALITY_PREFIXES:
                prefix_key = "anime_sfw"
            if suffix_key not in QUALITY_SUFFIXES:
                suffix_key = "anime_sfw"
        
        prefix = random.choice(QUALITY_PREFIXES.get(prefix_key, QUALITY_PREFIXES["sfw"]))
        suffix = random.choice(QUALITY_SUFFIXES.get(suffix_key, QUALITY_SUFFIXES["sfw"]))
        
        # 8. 최종 프롬프트 구성
        main_description = ", ".join(all_parts)
        
        # 사용자 요구사항 적용
        main_description = self._apply_user_requirements(main_description, user_requirements)
        
        positive_prompt = f"{prefix} {main_description}, {suffix}"
        
        # 9. 네거티브 프롬프트 선택
        negative_prompt = NEGATIVE_PROMPTS["standard"]
        
        return positive_prompt, negative_prompt
    
    def generate_with_ollama(
        self,
        selected_options: Dict[str, str],
        user_requirements: Optional[str],
        ollama_client,
        model_name: str,
        style: str = "photorealistic"
    ) -> Tuple[str, str]:
        """
        Ollama 모델을 사용한 프롬프트 생성
        
        기본 생성된 프롬프트를 Ollama 모델로 개선합니다.
        """
        # 기본 프롬프트 생성
        base_positive, base_negative = self.generate(selected_options, user_requirements, style=style)
        
        # Ollama로 개선 요청
        style_desc = "photorealistic" if style == "photorealistic" else "high-quality anime style"
        
        system_prompt = f"""You are a world-class prompt engineer specializing in {style_desc} AI image generation.
Your task is to enhance and refine the given prompt while:
1. Maintaining natural, flowing English
2. Keeping technical details accurate for the target style ({style})
3. Ensuring coherent visual storytelling
4. Preserving the original intent and style
5. Adding subtle details that enhance quality

IMPORTANT: Return ONLY the enhanced prompt, no explanations or additional text."""

        user_prompt = f"""Enhance this image generation prompt for maximum quality and natural flow:

Original prompt: {base_positive}

Requirements: {user_requirements if user_requirements else "None specified"}

Return the enhanced prompt only."""

        try:
            response = ollama_client.chat(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            enhanced_prompt = response['message']['content'].strip()
            
            # 응답이 너무 짧거나 이상한 경우 기본값 사용
            if len(enhanced_prompt) < 50 or enhanced_prompt.startswith("I "):
                return base_positive, base_negative
            
            return enhanced_prompt, base_negative
            
        except Exception as e:
            print(f"Ollama enhancement failed: {e}")
            return base_positive, base_negative


class PromptVariationGenerator:
    """
    프롬프트 변형 생성기
    
    기존 프롬프트를 기반으로 다양한 변형을 생성합니다.
    """
    
    def __init__(self, base_generator: PromptGenerator):
        self.generator = base_generator
    
    def generate_variations(
        self,
        selected_options: Dict[str, str],
        num_variations: int = 3,
        user_requirements: Optional[str] = None
    ) -> List[Tuple[str, str]]:
        """
        여러 변형 프롬프트 생성
        
        Args:
            selected_options: 기본 선택 옵션 (한글)
            num_variations: 생성할 변형 수
            user_requirements: 사용자 요구사항
        
        Returns:
            (positive_prompt, negative_prompt) 튜플 리스트
        """
        variations = []
        
        for _ in range(num_variations):
            # 각 변형에서 일부 옵션을 랜덤하게 변경
            varied_options = selected_options.copy()
            
            # 30% 확률로 각 카테고리를 랜덤으로 변경
            for category in varied_options:
                if varied_options[category] != "제외" and random.random() > 0.7:
                    varied_options[category] = "랜덤"
            
            prompt = self.generator.generate(varied_options, user_requirements)
            variations.append(prompt)
        
        return variations


# 편의 함수
def create_generator(mode: str = "sfw") -> PromptGenerator:
    """프롬프트 생성기 인스턴스 생성"""
    return PromptGenerator(mode=mode)
