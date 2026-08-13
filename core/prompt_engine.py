import random
from typing import Dict, Optional, List, Tuple
from data.prompt_database import (
    MODIFIERS, DATA, PROMPT_TEMPLATES,
    QUALITY_PREFIXES, QUALITY_SUFFIXES, NEGATIVE_PROMPTS,
    NATURAL_DIRECTIVE_KEYS, build_natural_directives,
    get_category_options, get_modifier_options, get_english_value
)
from data.llm_prompts import DEFAULT_PROMPT_TARGET, build_enhancement_system_prompt


def attach_natural_directives(
    prompt: str, keys: Optional[List[str]] = None
) -> str:
    """
    프롬프트 뒤에 자연스러운 사진 지시문 블록을 부착

    LLM 개선 단계에서 지시문이 요약/변형되는 것을 막기 위해
    본문 개선이 끝난 뒤 마지막에 붙이는 용도로 사용한다.

    Args:
        prompt: 본문 프롬프트
        keys: 포함할 지시문 키 목록 (None 이면 전체)
    """
    directives = build_natural_directives(keys)
    if not directives:
        return prompt

    return f"{prompt}\n\n{directives}"


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
        adjective: str,
        shot: Optional[str] = None
    ) -> str:
        parts = []
        if adjective:
            parts.append(adjective)
        if race:
            parts.append(race)
        if gender:
            parts.append(gender)
        if skin:
            parts.append(f"with {skin}")

        subject = " ".join(parts)

        # 샷/프레이밍은 주제 앞에 놓아 표현 범위를 먼저 규정
        if shot:
            return f"{shot} of {subject}" if subject else shot

        return subject
    
    def _build_appearance_description(
        self,
        hair: Optional[str],
        clothing: Optional[str],
        body_type: Optional[str],
        use_modifiers: bool = True
    ) -> List[str]:
        """외모 설명 구성"""
        parts = []
        
        if hair:
            hair_state = self._select_modifier("상태") if use_modifiers else ""
            parts.append(f"{hair_state} {hair}".strip())
        
        if clothing:
            # 의상 재질 추가 (40% 확률)
            if use_modifiers and random.random() > 0.6:
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
        style: str = "photorealistic",
        use_modifiers: bool = True,
        use_quality_prefix: bool = True,
        use_natural_photo: bool = False,
        natural_directive_keys: Optional[List[str]] = None,
        include_natural_directives: bool = True
    ) -> Tuple[str, str]:
        """
        프롬프트 생성

        Args:
            selected_options: 카테고리별 사용자 선택 (한글 키)
            user_requirements: 추가 요구사항 (선택)
            template_style: 템플릿 스타일
            use_modifiers: MODIFIERS(형용사/피부질감/상태/의상재질) 포함 여부
            use_quality_prefix: QUALITY_PREFIXES 포함 여부
            use_natural_photo: 자연스러운 사진 모드 (실사 스타일에서만 적용)
            natural_directive_keys: 포함할 자연스러움 지시문 키 목록 (None 이면 전체)
            include_natural_directives: 지시문 블록을 결과에 포함할지 여부.
                False 면 본문만 반환하므로 LLM 개선 후 build_natural_directives()로 별도 부착

        Returns:
            (positive_prompt, negative_prompt) 튜플 - 영문
        """
        # 자연스러운 사진 모드는 실사 스타일에서만 의미가 있음
        natural = use_natural_photo and style == "photorealistic"

        # 1. 핵심 수식어 선택
        # 자연 모드에서는 과장 형용사/인공적인 피부 표현을 배제
        allow_modifiers = use_modifiers and not natural
        adjective = self._select_modifier("형용사") if allow_modifiers else ""
        skin = self._select_modifier("피부질감") if allow_modifiers else ""

        # 2. 카테고리별 아이템 선택 (한글 -> 영문 변환)
        gender = self._select_item("나이/성별", selected_options.get("나이/성별", "랜덤"))
        race = self._select_item("인종/외모", selected_options.get("인종/외모", "랜덤"))
        hair = self._select_item("헤어스타일", selected_options.get("헤어스타일", "랜덤"))
        clothing = self._select_item("의상", selected_options.get("의상", "랜덤"))
        body_type = self._select_item("몸매/체형", selected_options.get("몸매/체형", "랜덤"))
        pose = self._select_item("포즈/행동", selected_options.get("포즈/행동", "랜덤"))
        shot = self._select_item("샷/프레이밍", selected_options.get("샷/프레이밍", "랜덤"))
        background = self._select_item("배경/장소", selected_options.get("배경/장소", "랜덤"))
        expression = self._select_item("상황/표정", selected_options.get("상황/표정", "랜덤"))
        lighting = self._select_item("촬영/조명", selected_options.get("촬영/조명", "랜덤"))

        # 3. 주제제 설명 구성
        subject = self._build_subject_description(gender, race, skin, adjective, shot)

        # 4. 외모 설명 구성
        appearance_parts = self._build_appearance_description(hair, clothing, body_type, allow_modifiers)

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
        elif natural:
            # 과장된 품질 수식구 대신 담백한 자연 사진 표현 사용
            prefix_key = "natural"
            suffix_key = "natural"

        prefix = (
            random.choice(QUALITY_PREFIXES.get(prefix_key, QUALITY_PREFIXES["sfw"]))
            if use_quality_prefix
            else ""
        )
        suffix = random.choice(QUALITY_SUFFIXES.get(suffix_key, QUALITY_SUFFIXES["sfw"]))

        # 8. 최종 프롬프트 구성
        main_description = ", ".join(all_parts)

        # 사용자 요구사항 적용
        main_description = self._apply_user_requirements(main_description, user_requirements)

        positive_prompt = f"{prefix} {main_description}, {suffix}".strip()

        # 9. 자연스러움 지시문 부착
        if natural and include_natural_directives:
            positive_prompt = attach_natural_directives(
                positive_prompt, natural_directive_keys
            )

        # 10. 네거티브 프롬프트 선택
        negative_prompt = (
            NEGATIVE_PROMPTS["natural"] if natural else NEGATIVE_PROMPTS["standard"]
        )

        return positive_prompt, negative_prompt
    
    def generate_with_ollama(
        self,
        selected_options: Dict[str, str],
        user_requirements: Optional[str],
        ollama_client,
        model_name: str,
        style: str = "photorealistic",
        use_modifiers: bool = True,
        use_quality_prefix: bool = True,
        use_natural_photo: bool = False,
        natural_directive_keys: Optional[List[str]] = None,
        prompt_target: str = DEFAULT_PROMPT_TARGET
    ) -> Tuple[str, str]:
        """
        Ollama 모델을 사용한 프롬프트 생성

        기본 생성된 프롬프트를 Ollama 모델로 개선합니다.
        자연스러운 사진 모드에서는 지시문 블록을 개선 대상에서 제외하고
        개선이 끝난 뒤 원문 그대로 다시 부착합니다.
        """
        natural = use_natural_photo and style == "photorealistic"

        # 기본 프롬프트 생성 (지시문은 개선 후 부착)
        base_positive, base_negative = self.generate(
            selected_options,
            user_requirements,
            style=style,
            use_modifiers=use_modifiers,
            use_quality_prefix=use_quality_prefix,
            use_natural_photo=use_natural_photo,
            include_natural_directives=False,
        )

        def finalize(prompt: str) -> str:
            if not natural:
                return prompt
            return attach_natural_directives(prompt, natural_directive_keys)

        # Ollama로 개선 요청
        system_prompt = build_enhancement_system_prompt(style, natural, prompt_target)

        if natural:
            user_prompt = f"""Rewrite this image generation prompt so it reads like a real photograph:

Original prompt: {base_positive}

Requirements: {user_requirements if user_requirements else "None specified"}

Return the rewritten prompt only."""
        else:
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
                return finalize(base_positive), base_negative

            return finalize(enhanced_prompt), base_negative

        except Exception as e:
            print(f"Ollama enhancement failed: {e}")
            return finalize(base_positive), base_negative


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
