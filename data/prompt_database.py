MODIFIERS = {
    "형용사": {
        "positive": [
            "breathtaking", "exquisite", "stunning", "alluring", "enigmatic",
            "radiant", "sophisticated", "ethereal", "mysterious", "charismatic",
            "elegant", "bold", "majestic", "divine", "graceful", "intense",
            "charming", "mesmerizing", "unforgettable", "magnificent", "captivating",
            "striking", "luminous", "refined", "timeless", "iconic"
        ],
        "sensual": [
            "seductive", "voluptuous", "provocative", "sultry", "tempting",
            "enticing", "bewitching", "irresistible", "passionate", "fiery"
        ]
    },
    "피부질감": {
        "sfw": [
            "poreless silky skin", "highly detailed skin with visible pores",
            "dewy and moist complexion", "soft velvet-like skin",
            "flawless porcelain skin", "glowing healthy skin",
            "natural skin texture with subtle imperfections",
            "luminous skin catching the light", "smooth matte skin",
            "radiant youthful complexion"
        ],
        "nsfw": [
            "sweaty glistening skin", "oiled and shimmering skin",
            "translucent skin with subtle veins", "sun-kissed golden skin",
            "wet dewy skin reflecting light", "flushed warm skin tone"
        ]
    },
    "의상재질": [
        "shimmering silk", "delicate lace", "premium denim", "supple leather",
        "soft cashmere", "flowing chiffon", "structured tweed", "fine wool",
        "luxurious velvet", "smooth satin", "crisp linen", "technical mesh",
        "organic cotton", "rich brocade", "metallic lamé", "sheer organza"
    ],
    "의상재질_nsfw": [
        "glossy latex", "transparent mesh", "wet-look PVC", "sheer fabric",
        "see-through material", "body-hugging spandex"
    ],
    "상태": [
        "wind-swept", "perfectly styled", "elegantly arranged", "naturally flowing",
        "gently tousled", "meticulously groomed", "softly illuminated", "vibrant",
        "dreamlike", "crystalline"
    ],
    "상태_nsfw": [
        "soaking wet", "messy", "disheveled", "glistening", "dripping",
        "steamy", "tousled from movement"
    ]
}

DATA = {
    "나이/성별": {
        "sfw": {
            "20대 귀여운 여성": "cute woman in her 20s",
            "20대 예쁜 여성": "beautiful woman in her 20s",
            "20대 섹시한 여성": "sexy woman in her 20s",
            "20대 우아한 여성": "elegant woman in her 20s",
            "30대 세련된 여성": "sophisticated lady in her 30s",
            "우아한 젊은 여성": "graceful young woman",
            "40대 성숙한 여성": "mature elegant woman in her 40s",
            "20대 잘생긴 남성": "handsome young man in his 20s",
            "품격있는 신사": "distinguished gentleman",
            "전문 여성 모델": "professional female model",
            "우아한 중년 여성": "refined older woman",
            "운동선수 체형 남성": "athletic male model",
            "청초한 여성": "petite graceful woman",
            "카리스마 있는 남성": "tall charismatic man",
            "전문직 여성": "poised businesswoman",
            "예술적인 여성": "artistic creative woman",
            "클래식 미인": "classic beauty",
            "현대적 스타일 여성": "modern stylish woman",
            "시대를 초월한 우아함": "timeless elegant lady"
        },
        "nsfw": {
            "매혹적인 팜므파탈": "gorgeous femme fatale",
            "유혹적인 사이렌": "seductive siren",
            "신비로운 요부": "mysterious temptress",
            "매력적인 모델": "alluring model",
            "사로잡는 미인": "captivating beauty",
            "황홀한 여성": "enchanting woman",
            "도발적인 뮤즈": "provocative muse",
            "관능적인 여신": "sensual goddess",
            "매혹적인 자태": "bewitching figure"
        }
    },
    
    "인종/외모": {
        "한국인": "Korean",
        "일본인": "Japanese",
        "중국인": "Chinese",
        "백인": "Caucasian",
        "아프리카계 미국인": "African American",
        "라틴 아메리카인": "Latin American",
        "중동인": "Middle Eastern",
        "북유럽인": "Nordic",
        "동남아시아인": "Southeast Asian",
        "혼혈 (아시아-유럽)": "Mixed Asian-European",
        "동아시아인": "East Asian",
        "지중해인": "Mediterranean",
        "남아시아인": "South Asian",
        "동유럽인": "Eastern European",
        "브라질인": "Brazilian",
        "스칸디나비아인": "Scandinavian",
        "인도인": "Indian",
        "태국인": "Thai",
        "베트남인": "Vietnamese",
        "러시아인": "Russian",
        "프랑스인": "French",
        "이탈리아인": "Italian",
        "페르시아인": "Persian",
        "아랍인": "Arabic",
        "아일랜드인": "Irish",
        "스페인인": "Spanish"
    },
    
    "헤어스타일": {
        "sfw": {
            "긴 생머리": "long silky straight hair",
            "우아한 비치 웨이브": "elegant beach waves",
            "세련된 하이 포니테일": "sleek high ponytail",
            "시크한 픽시컷": "chic pixie cut",
            "부드러운 앞머리 단발": "classic bob with soft bangs",
            "볼륨있는 자연 컬": "voluminous natural curls",
            "플래티넘 금발 웨이브": "platinum blonde waves",
            "칠흑같은 어깨 길이 머리": "jet black shoulder-length hair",
            "세련된 업스타일": "sophisticated updo",
            "반묶음 스타일": "half-up half-down style",
            "깔끔한 올백 스타일": "polished slicked back",
            "우아한 더블번": "elegant double buns",
            "풍성한 적갈색 웨이브": "rich auburn waves",
            "단정한 탑노트": "neat top knot",
            "스타일리시 커튼뱅": "stylish curtain bangs",
            "로맨틱 프렌치 브레이드": "romantic french braid",
            "우아한 사이드 스윕": "graceful side-swept hair",
            "모던 울프컷": "modern wolf cut",
            "전통 히메컷": "traditional hime cut",
            "우아한 실버 그레이": "silver grey elegant style",
            "브레이드 크라운": "braided crown",
            "세련된 피쉬테일": "sophisticated fishtail braid"
        },
        "nsfw": {
            "흐트러진 침대 머리": "messy bedroom hair",
            "젖은 듯한 웨이브": "wet look tousled waves",
            "거친 야생 컬": "wild untamed curls",
            "흐트러진 관능적 스타일": "disheveled sensual style",
            "샤워 후 젖은 머리": "post-shower damp hair",
            "바람에 휘날린 드라마틱한 머리결": "windswept dramatic locks"
        }
    },
    
    "의상": {
        "sfw": {
            "레깅스": "tight leggings",
            "우아한 실크 이브닝 드레스": "elegant silk evening gown",
            "캐주얼 시크 오버사이즈 스웨터": "casual chic oversized sweater",
            "맞춤 정장 블레이저": "tailored professional blazer",
            "전통 한복": "traditional Korean Hanbok",
            "모던 미니멀 드레스": "modern minimalist dress",
            "빈티지풍 데님 재킷": "vintage-inspired denim jacket",
            "플로잉 섬머 원피스": "flowing summer sundress",
            "애슬레틱 요가 앙상블": "athletic yoga ensemble",
            "클래식 교복": "classic school uniform",
            "포근한 니트 가디건": "cozy knit cardigan",
            "럭셔리 울 코트": "luxurious wool coat",
            "세련된 터틀넥": "sophisticated turtleneck",
            "우아한 실크 기모노": "elegant silk kimono",
            "전통 치파오": "traditional Cheongsam",
            "스타일리시 패딩 재킷": "stylish puffer jacket",
            "로맨틱 플로럴 미디 드레스": "romantic floral midi dress",
            "모던 오피스 룩": "modern office attire",
            "캐주얼 청바지와 실크 블라우스": "casual jeans and silk blouse",
            "타임리스 리틀 블랙 드레스": "timeless little black dress",
            "보헤미안 맥시 드레스": "bohemian maxi dress"
        },
        "nsfw": {
            "정교한 레이스 란제리 세트": "intricate lace lingerie set",
            "시스루 네글리제": "sheer delicate negligee",
            "몸매 밀착 바디콘 드레스": "form-fitting bodycon dress",
            "노출 이브닝 가운": "revealing evening gown",
            "예술적 누드 (전략적 포즈)": "artistic nude with strategic posing",
            "관능적 실크 슬립 드레스": "sensual silk slip dress",
            "도발적 레더 앙상블": "provocative leather ensemble",
            "아찔한 비키니": "barely-there bikini",
            "젖어 달라붙는 시스루": "sheer wet fabric clinging",
            "스트랩리스 코르셋 탑": "strapless corset top",
            "깊은 V넥 가운": "plunging neckline gown",
            "하이슬릿 칵테일 드레스": "high-slit cocktail dress",
            "투명 레이스 오버레이": "transparent lace overlay",
            "몸에 붙는 라텍스": "body-hugging latex",
            "관능적 베이비돌": "sensual babydoll",
            "우아한 부드와르 의상": "elegant boudoir attire"
        }
    },
    
    "몸매/체형": {
        "sfw": {
            "슬림하고 우아한": "slim and graceful",
            "자연스럽게 탄탄한": "naturally athletic",
            "우아하게 키가 큰": "elegantly tall",
            "아담하고 섬세한": "petite and delicate",
            "클래식한 비율": "classically proportioned",
            "날씬하고 탄탄한": "lean and toned",
            "부드러운 여성스러운 실루엣": "soft feminine silhouette",
            "건강하고 탄탄한 체형": "healthy fit physique",
            "가늘고 우아한": "slender and poised",
            "우아한 댄서의 몸매": "graceful dancer's body",
            "정제된 우아한 피규어": "refined elegant figure"
        },
        "nsfw": {
            "볼륨감 있는 곡선": "voluptuous curves",
            "모래시계 실루엣": "hourglass silhouette",
            "관능적인 곡선미": "sensually curved",
            "글래머러스 피규어": "curvaceous figure",
            "풍만한 미인": "full-figured beauty",
            "탄탄하면서 여성스러운 곡선": "toned with feminine curves",
            "조각같은 애슬레틱 바디": "sculpted athletic body"
        }
    },
    
    "포즈/행동": {
        "sfw": {
            "조용한 자신감으로 서있는": "standing with quiet confidence",
            "우아하게 앉아있는": "sitting gracefully",
            "표면에 우아하게 기대어": "leaning elegantly against a surface",
            "목적있게 걷는": "walking with purpose",
            "부드러운 명상적 포즈": "gentle contemplative pose",
            "자연스러운 캔디드 순간": "natural candid moment",
            "멀리 생각에 잠긴 시선": "looking thoughtfully into distance",
            "눈으로 미소짓는": "subtle smile with eyes",
            "부드럽게 손을 모은": "hands gently clasped",
            "편안한 자연스러운 자세": "relaxed natural stance",
            "우아한 프로필 뷰": "elegant profile view",
            "고요하게 앉은 자세": "serene seated position",
            "부드럽게 팔짱 낀": "arms softly crossed",
            "부드러운 손동작": "gentle hand gesture",
            "평화롭게 책 읽는": "reading a book peacefully",
            "고독의 순간을 즐기는": "enjoying a moment of solitude"
        },
        "nsfw": {
            "침대에 관능적으로 누운": "lying sensually on bed",
            "극적으로 등을 젖힌": "arching back dramatically",
            "도발적인 어깨너머 시선": "provocative over-shoulder glance",
            "유혹적으로 무릎 꿇은": "kneeling seductively",
            "친밀한 자세로 기댄": "reclining in intimate pose",
            "관능적으로 스트레칭하는": "stretching sensually",
            "매혹적으로 앞으로 숙인": "bending forward alluringly",
            "머리카락을 쓸어넘기는": "hands running through hair",
            "나른하게 뻗은 포즈": "languid sprawling pose",
            "친밀한 클로즈업 자세": "intimate close-up position"
        }
    },
    
    "배경/장소": {
        "sfw": {
            "미니멀 모던 스튜디오": "minimalist modern studio",
            "햇살 가득한 카페 인테리어": "sun-drenched café interior",
            "고요한 자연 숲": "serene natural forest",
            "우아한 럭셔리 아파트": "elegant luxury apartment",
            "조용한 도시 거리": "quiet urban street",
            "골든아워의 평화로운 해변": "peaceful beach at golden hour",
            "전문 포토 스튜디오": "professional photo studio",
            "아늑한 독서 코너": "cozy reading nook",
            "도시 스카이라인 루프탑": "rooftop with city skyline",
            "전통 도서관": "traditional library",
            "빗방울 맺힌 창가": "rain-kissed window view",
            "만개한 꽃정원": "blooming flower garden",
            "아트 갤러리 공간": "art gallery space",
            "세련된 호텔 로비": "sophisticated hotel lobby",
            "벚꽃길": "cherry blossom path",
            "산 정상 전망대": "mountain vista overlook",
            "빈티지 서점": "vintage bookstore",
            "세련된 모던 오피스": "sleek modern office"
        },
        "nsfw": {
            "은은한 조명의 침실": "dimly lit intimate bedroom",
            "럭셔리 호텔 스위트": "luxurious hotel suite",
            "김이 서린 프라이빗 욕실": "steam-filled private bathroom",
            "실크로 장식된 부드와르": "silk-draped boudoir",
            "촛불 로맨틱 세팅": "candlelit romantic setting",
            "프라이빗 풀 사이드": "private pool area",
            "은밀한 펜트하우스": "secluded penthouse",
            "친밀한 스파 세팅": "intimate spa setting"
        }
    },
    
    "상황/표정": {
        "sfw": {
            "부드러운 진심어린 미소": "soft genuine smile",
            "평화로운 명상": "peaceful contemplation",
            "따뜻하고 매력적인 표정": "warm inviting expression",
            "자신감 있는 직접적인 시선": "confident direct gaze",
            "부드러운 웃음": "gentle laughter",
            "고요하게 감은 눈": "serene closed eyes",
            "생각에 잠긴 먼 시선": "thoughtful distant look",
            "은은한 아는 미소": "subtle knowing smile",
            "자연스럽고 편안한 표정": "natural relaxed expression",
            "우아한 품위": "elegant poise",
            "조용한 결연함": "quiet determination",
            "몽환적인 소프트 포커스": "dreamy soft focus",
            "전문적인 침착함": "professional composure",
            "친근한 따뜻함": "friendly warmth"
        },
        "nsfw": {
            "강렬한 유혹적 시선": "intense seductive gaze",
            "살짝 벌어진 입술": "lips slightly parted",
            "나른한 관능적 눈빛": "heavy-lidded sensual look",
            "상기된 볼": "flushed cheeks",
            "도발적인 미소": "provocative smirk",
            "침실 눈빛": "bedroom eyes",
            "열정적인 표정": "passionate expression",
            "취약한 친밀감": "vulnerable intimacy",
            "숨가쁜 기대감": "breathless anticipation",
            "관능적인 반쯤 미소": "sultry half-smile"
        }
    },
    
    "촬영/조명": {
        "sfw": {
            "85mm 인물렌즈, f/1.8": "85mm portrait lens, f/1.8",
            "자연 창가 조명": "natural window light",
            "부드러운 디퓨즈 스튜디오 조명": "soft diffused studio lighting",
            "골든아워 역광": "golden hour backlight",
            "시네마틱 컬러 그레이딩": "cinematic color grading",
            "하이패션 에디토리얼 스타일": "high-fashion editorial style",
            "클래식 뷰티 라이팅": "classic beauty lighting",
            "환경 인물 사진": "environmental portrait",
            "캔디드 다큐멘터리 스타일": "candid documentary style",
            "파인아트 포토그래피": "fine art photography",
            "부드러운 자연 일광": "soft natural daylight",
            "드라마틱 림 라이팅": "dramatic rim lighting",
            "렘브란트 라이팅": "Rembrandt lighting setup",
            "버터플라이 뷰티 라이트": "butterfly beauty light"
        },
        "nsfw": {
            "친밀한 로우키 조명": "intimate low-key lighting",
            "따뜻한 촛불 글로우": "warm candlelight glow",
            "관능적인 그림자 플레이": "sensual shadow play",
            "무디한 분위기 조명": "moody atmospheric lighting",
            "부드러운 로맨틱 헤이즈": "soft romantic haze",
            "드라마틱 키아로스쿠로": "dramatic chiaroscuro",
            "친밀한 부드와르 조명": "intimate boudoir lighting",
            "관능적인 네온 악센트": "sultry neon accents"
        }
    }
}

PROMPT_TEMPLATES = {
    "portrait_focused": [
        "A {adjective} portrait of a {race} {gender} with {skin}, {hair}, wearing {clothing}, {pose}, {expression}, {background}, {lighting}",
        "{adjective} {race} {gender}, {skin}, featuring {hair}, dressed in {clothing}, {pose}, {expression}, set in {background}, captured with {lighting}",
        "Editorial portrait: {adjective} {race} {gender} with {skin} and {hair}, {clothing}, {pose}, showing {expression}, {background}, {lighting}"
    ],
    "fashion_editorial": [
        "High-fashion editorial: {adjective} {race} {gender} model, {skin}, {hair}, showcasing {clothing}, {pose}, {expression}, {background}, shot with {lighting}",
        "Vogue-style portrait of {adjective} {race} {gender}, {skin}, with {hair}, wearing {clothing}, {pose}, {expression}, in {background}, {lighting}"
    ],
    "artistic": [
        "Fine art photography: {adjective} {race} {gender}, {skin}, {hair}, {clothing}, {pose}, capturing {expression}, {background}, {lighting}",
        "Cinematic portrait study: {adjective} {race} {gender} with {skin}, featuring {hair}, in {clothing}, {pose}, {expression}, against {background}, {lighting}"
    ],
    "intimate": [
        "Intimate portrait: {adjective} {race} {gender}, {skin}, {hair}, wearing {clothing}, {pose}, {expression}, in {background}, with {lighting}",
        "Personal moment captured: {adjective} {race} {gender} with {skin}, {hair}, {clothing}, {pose}, showing {expression}, {background}, {lighting}"
    ]
}

QUALITY_PREFIXES = {
    "sfw": [
        "Photorealistic masterpiece,",
        "Ultra-detailed professional photograph,",
        "Award-winning portrait photography,",
        "High-end fashion photograph,",
        "Studio quality portrait,"
    ],
    "nsfw": [
        "Photorealistic artistic nude,",
        "Intimate professional photograph,",
        "Sensual fine art photography,",
        "Boudoir photography masterpiece,",
        "Artistic intimate portrait,"
    ],
    "anime_sfw": [
        "Masterpiece, best quality, anime style, 2d,",
        "High quality anime art, cel shaded,",
        "Detailed anime illustration, vibrant colors,",
        "Beautiful anime character art,",
        "Kyoto Animation style, studio ghibli style,"
    ],
    "anime_nsfw": [
        "Masterpiece, best quality, anime style, 2d, ecchi,",
        "High quality anime art, sensual anime style,",
        "Detailed anime illustration, sensual gaze,",
        "Alluring anime character art,",
        "Mature anime style, cel shaded,"
    ]
}

QUALITY_SUFFIXES = {
    "sfw": [
        "extremely detailed eyes and facial features, natural skin texture with subtle imperfections, "
        "8K resolution, sharp focus, professional color grading, RAW photo quality",
        
        "highly detailed iris and catchlights, realistic skin pores and texture, "
        "cinematic composition, professional studio quality, 8K UHD",
        
        "meticulous attention to detail, natural lighting interaction with skin, "
        "magazine-quality finish, sharp focus throughout, professional retouching"
    ],
    "nsfw": [
        "extremely detailed eyes, glistening skin highlights, natural body contours, "
        "8K resolution, artistic composition, intimate atmosphere, professional quality",
        
        "highly detailed skin texture with natural highlights, sensual lighting, "
        "cinematic quality, sharp focus on key details, tasteful artistic expression",
        
        "meticulous attention to form and lighting, natural skin tone gradients, "
        "professional boudoir quality, 8K resolution, artistic composition"
    ],
    "anime_sfw": [
        "vibrant colors, detailed background, sharp lines, anime aesthetics, "
        "expressive eyes, smooth shading, high definition",

        "clean lines, cel shading, bright and colorful, atmospheric lighting, "
        "detailed clothes and accessories, anime production quality",

        "soft lighting, emotional atmosphere, detailed hair highlights, "
        "perfect anatomy, highres, 4k"
    ],
    "anime_nsfw": [
        "vibrant colors, blushing, soft shading, intimate atmosphere, "
        "detailed body, glowing skin, anime aesthetics, high definition",

        "cel shading, sensual lighting, expressive eyes, wet skin texture, "
        "detailed anatomy, highres, 4k, fanbox quality"
    ]
}

NEGATIVE_PROMPTS = {
    "standard": (
        "deformed, distorted, disfigured, poorly drawn, bad anatomy, wrong anatomy, "
        "extra limb, missing limb, floating limbs, mutated hands and fingers, "
        "disconnected limbs, mutation, mutated, ugly, disgusting, blurry, "
        "amputation, watermark, text, signature, low quality, worst quality, "
        "jpeg artifacts, cropped, out of frame"
    ),
    "face_focused": (
        "deformed face, distorted face, bad eyes, crossed eyes, asymmetrical eyes, "
        "bad teeth, distorted teeth, multiple faces, clone face, "
        "poorly drawn face, mutation, deformed, ugly, blurry, "
        "bad anatomy, bad proportions, extra limbs, watermark, signature"
    ),
    "body_focused": (
        "deformed body, bad anatomy, wrong proportions, extra limbs, missing limbs, "
        "floating limbs, disconnected body parts, mutation, ugly, disgusting, "
        "poorly drawn, blurry, low quality, watermark, text"
    )
}

CATEGORY_LABELS = {
    "나이/성별": "Age/Gender",
    "인종/외모": "Ethnicity/Appearance", 
    "헤어스타일": "Hairstyle",
    "의상": "Clothing",
    "몸매/체형": "Body Type",
    "포즈/행동": "Pose/Action",
    "배경/장소": "Background/Location",
    "상황/표정": "Mood/Expression",
    "촬영/조명": "Photography/Lighting"
}

def get_category_options(category: str, mode: str = "sfw") -> list:
    """카테고리별 옵션 리스트 반환 (한글 키 목록)"""
    if category not in DATA:
        return []
    
    cat_data = DATA[category]
    
    # 인종/외모는 dict 구조가 다름 (sfw/nsfw 구분 없음)
    if category == "인종/외모":
        return list(cat_data.keys())
    
    if isinstance(cat_data, dict):
        if "sfw" in cat_data:
            result = list(cat_data["sfw"].keys())
            if mode == "nsfw" and "nsfw" in cat_data:
                result += list(cat_data["nsfw"].keys())
            return result
        else:
            return list(cat_data.keys())
    
    return []


def get_english_value(category: str, korean_key: str, mode: str = "sfw") -> str:
    """한글 키에 해당하는 영문 값 반환"""
    if category not in DATA:
        return korean_key
    
    cat_data = DATA[category]
    
    # 인종/외모
    if category == "인종/외모":
        return cat_data.get(korean_key, korean_key)
    
    # sfw/nsfw 구분 있는 카테고리
    if isinstance(cat_data, dict):
        if "sfw" in cat_data:
            if korean_key in cat_data["sfw"]:
                return cat_data["sfw"][korean_key]
            if "nsfw" in cat_data and korean_key in cat_data["nsfw"]:
                return cat_data["nsfw"][korean_key]
        else:
            return cat_data.get(korean_key, korean_key)
    
    return korean_key


def get_modifier_options(modifier_type: str, mode: str = "sfw") -> list:
    """수식어 옵션 리스트 반환"""
    if modifier_type not in MODIFIERS:
        return []
    
    mod_data = MODIFIERS[modifier_type]
    
    if isinstance(mod_data, dict):
        if mode == "nsfw":
            result = mod_data.get("positive", mod_data.get("sfw", []))
            if "sensual" in mod_data:
                result = result + mod_data["sensual"]
            if "nsfw" in mod_data:
                result = result + mod_data["nsfw"]
            return result
        return mod_data.get("positive", mod_data.get("sfw", []))
    else:
        if mode == "nsfw" and f"{modifier_type}_nsfw" in MODIFIERS:
            return mod_data + MODIFIERS[f"{modifier_type}_nsfw"]
        return mod_data
