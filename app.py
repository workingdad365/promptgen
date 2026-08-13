import streamlit as st
import html as html_lib
import sys
import os
from dotenv import load_dotenv

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# 실행 위치와 무관하게 프로젝트 루트의 .env 로드
load_dotenv(os.path.join(APP_DIR, ".env"), override=True)

sys.path.insert(0, APP_DIR)

from data.prompt_database import (
    DATA,
    CATEGORY_LABELS,
    NATURAL_DIRECTIVE_KEYS,
    NATURAL_PHOTO_DIRECTIVES,
    get_category_options,
    NEGATIVE_PROMPTS,
)
from core.prompt_engine import (
    PromptGenerator,
    attach_natural_directives,
    create_generator,
    get_creative_categories,
)
from data.llm_prompts import PROMPT_TARGETS
from integrations.external_llm_integration import (
    ExternalLLMClient,
    ExternalLLMPromptEnhancer,
    check_api_key_for_model,
    get_external_llm_models,
    get_provider_label,
)
from integrations.model_config import ModelConfigError
from utils.history_manager import get_history_manager
from utils.settings_manager import load_settings, save_settings
from utils.wildcard_manager import (
    expand_wildcards,
    list_wildcards,
    resolve_directory,
)

st.set_page_config(
    page_title="Prompt Generator for Images and Videos",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem; color: white; text-align: center;
    }
    .main-header h1 { margin: 0; font-size: 2.2rem; font-weight: 700; }
    .main-header p { margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1rem; }
    
    .prompt-label {
        color: #00d4ff; font-weight: 600; margin-bottom: 0.5rem; display: block;
        font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px;
    }
    
    .translated-box {
        background-color: #f8fafc;
        border-left: 5px solid #4285f4;
        padding: 1.2rem;
        border-radius: 8px;
        color: #1e293b;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
        line-height: 1.6;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .stButton > button { border-radius: 8px; font-weight: 600; transition: all 0.3s ease; }
</style>
""",
    unsafe_allow_html=True,
)

try:
    EXTERNAL_LLM_MODELS = get_external_llm_models()
    MODEL_CONFIG_ERROR = None
except ModelConfigError as e:
    EXTERNAL_LLM_MODELS = []
    MODEL_CONFIG_ERROR = str(e)


PROMPT_BLOCK_STYLES = {
    "code": {
        "box": (
            "background: #1e1e1e; color: #d4d4d4; "
            "font-family: monospace; font-size: 14px;"
        ),
        "button": "background: #374151; color: #ffffff;",
    },
    "translated": {
        "box": (
            "background: #f8fafc; color: #1e293b; border-left: 5px solid #4285f4; "
            "font-size: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
        ),
        "button": "background: #4285f4; color: #ffffff;",
    },
}

# Streamlit이 'C' 키를 캐시 삭제 단축키로 처리해 Ctrl+C 복사 시 다이얼로그가 뜨는 것을 막음
HOTKEY_GUARD_HTML = """
<script>
(function () {
  try {
    const parentWin = window.parent;
    if (!parentWin || parentWin === window || parentWin.__promptgenHotkeyGuard) return;
    const guard = function (e) {
      const key = (e.key || '').toLowerCase();
      if ((e.ctrlKey || e.metaKey) && (key === 'c' || key === 'x' || key === 'v')) {
        e.stopImmediatePropagation();
      }
    };
    parentWin.addEventListener('keydown', guard, true);
    parentWin.document.addEventListener('keydown', guard, true);
    parentWin.__promptgenHotkeyGuard = true;
  } catch (err) {}
})();
</script>
""".strip()


def browse_directory(initial_dir: str):
    """OS 디렉토리 선택 대화상자 표시. (선택된 경로, 오류메시지) 반환.

    Streamlit 서버가 실행 중인 머신에 대화상자가 뜨므로 로컬 실행 시에만 동작함.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.wm_attributes("-topmost", 1)
        start = initial_dir if initial_dir and os.path.isdir(initial_dir) else APP_DIR
        selected = filedialog.askdirectory(initialdir=start, parent=root)
        root.destroy()
        return (os.path.normpath(selected) if selected else None), None
    except Exception as e:
        return None, str(e)


def render_copyable_prompt(
    text: str, element_id: str, height: int = 200, variant: str = "code"
) -> None:
    """복사 버튼이 포함된 프롬프트 블록 렌더링"""
    escaped = html_lib.escape(text)
    style = PROMPT_BLOCK_STYLES.get(variant, PROMPT_BLOCK_STYLES["code"])
    st.iframe(
        f"""
        <div style="position: relative; margin-bottom: 16px;">
            <button id="copyBtn-{element_id}"
                    style="position: absolute; top: 8px; right: 8px; {style['button']} border: none; border-radius: 4px; padding: 6px 10px; cursor: pointer; font-size: 14px; z-index: 10;">
                📋
            </button>
            <div id="prompt-{element_id}" style="{style['box']} padding: 16px; padding-right: 50px; border-radius: 8px; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; max-height: {height - 16}px; overflow-y: auto;">{escaped}</div>
        </div>
        <script>
            document.getElementById('copyBtn-{element_id}').addEventListener('click', function() {{
                const text = document.getElementById('prompt-{element_id}').innerText;
                navigator.clipboard.writeText(text).then(() => {{
                    this.innerText = '✅';
                    setTimeout(() => {{ this.innerText = '📋'; }}, 1500);
                }}).catch(() => {{
                    this.innerText = '❌';
                    setTimeout(() => {{ this.innerText = '📋'; }}, 1500);
                }});
            }});
        </script>
        """.strip(),
        height=height,
    )


SAVED_SETTINGS = load_settings()

if "mode" not in st.session_state:
    st.session_state.mode = SAVED_SETTINGS["mode"]
if "style" not in st.session_state:
    st.session_state.style = SAVED_SETTINGS["style"]
if "prompt_target" not in st.session_state:
    saved_target = SAVED_SETTINGS["prompt_target"]
    st.session_state.prompt_target = (
        saved_target if saved_target in PROMPT_TARGETS else "legacy"
    )
if "generator" not in st.session_state:
    st.session_state.generator = create_generator(st.session_state.mode)
if "external_llm_client" not in st.session_state:
    st.session_state.external_llm_client = None
if "external_llm_connected" not in st.session_state:
    st.session_state.external_llm_connected = False
if "external_llm_model" not in st.session_state:
    st.session_state.external_llm_model = (
        SAVED_SETTINGS["last_external_model"] if EXTERNAL_LLM_MODELS else None
    )
    if st.session_state.external_llm_model not in EXTERNAL_LLM_MODELS:
        st.session_state.external_llm_model = (
            EXTERNAL_LLM_MODELS[0] if EXTERNAL_LLM_MODELS else None
        )
if "user_requirements_input" not in st.session_state:
    st.session_state.user_requirements_input = SAVED_SETTINGS["last_user_requirements"]
if "dynamic_prompts_dir" not in st.session_state:
    st.session_state.dynamic_prompts_dir = SAVED_SETTINGS["dynamic_prompts_dir"]
if "save_history" not in st.session_state:
    st.session_state.save_history = SAVED_SETTINGS["save_history"]
if "history_manager" not in st.session_state:
    st.session_state.history_manager = get_history_manager()
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = None
if "prompt_counter" not in st.session_state:
    st.session_state.prompt_counter = 0
if "use_modifiers" not in st.session_state:
    st.session_state.use_modifiers = SAVED_SETTINGS["use_modifiers"]
if "use_quality_prefix" not in st.session_state:
    st.session_state.use_quality_prefix = SAVED_SETTINGS["use_quality_prefix"]
if "use_natural_photo" not in st.session_state:
    st.session_state.use_natural_photo = SAVED_SETTINGS["use_natural_photo"]
if "video_mode" not in st.session_state:
    st.session_state.video_mode = SAVED_SETTINGS["video_mode"]
if "natural_directive_keys" not in st.session_state:
    saved_keys = SAVED_SETTINGS["natural_directive_keys"]
    if isinstance(saved_keys, list):
        st.session_state.natural_directive_keys = [
            k for k in saved_keys if k in NATURAL_DIRECTIVE_KEYS
        ]
    else:
        st.session_state.natural_directive_keys = list(NATURAL_DIRECTIVE_KEYS)


def connect_external_llm(model_name):
    """외부 LLM 연결 시도. (성공 여부, 메시지) 반환."""
    if not model_name:
        return False, "❌ 사용 가능한 모델이 없습니다."

    has_key, key_msg = check_api_key_for_model(model_name)
    if not has_key:
        st.session_state.external_llm_client = None
        st.session_state.external_llm_connected = False
        return False, f"❌ {key_msg}"

    try:
        client = ExternalLLMClient(model=model_name)
        success, message = client.test_connection()
    except Exception as e:
        st.session_state.external_llm_client = None
        st.session_state.external_llm_connected = False
        return False, f"❌ 연결 실패: {e}"

    if success:
        st.session_state.external_llm_client = client
        st.session_state.external_llm_connected = True
        return True, message

    st.session_state.external_llm_client = None
    st.session_state.external_llm_connected = False
    return False, message


# 최초 실행 시 '연결' 버튼을 누른 것과 동일하게 자동 연결 시도
if "external_auto_connect_done" not in st.session_state:
    st.session_state.external_auto_connect_done = True
    if EXTERNAL_LLM_MODELS and st.session_state.external_llm_model:
        auto_ok, auto_msg = connect_external_llm(st.session_state.external_llm_model)
        st.session_state.external_auto_connect_result = (
            auto_msg,
            "success" if auto_ok else "error",
        )


with st.sidebar:
    st.markdown("## ⚙️ 엔진 설정")

    # 외부 LLM 연동 (연결되어야 프롬프트 생성 가능)
    st.markdown("### 🔑 외부 LLM 연동")
    if not EXTERNAL_LLM_MODELS:
        st.error(f"❌ 모델 설정을 불러오지 못했습니다: {MODEL_CONFIG_ERROR}")
    else:
        selected_model = st.selectbox(
            "모델 선택",
            options=EXTERNAL_LLM_MODELS,
            index=EXTERNAL_LLM_MODELS.index(st.session_state.external_llm_model)
            if st.session_state.external_llm_model in EXTERNAL_LLM_MODELS
            else 0,
            key="external_model_select",
        )
        if selected_model != st.session_state.external_llm_model:
            st.session_state.external_llm_client = None
            st.session_state.external_llm_connected = False
        st.session_state.external_llm_model = selected_model

        st.caption(f"제공자: {get_provider_label(selected_model)}")

        auto_result = st.session_state.pop("external_auto_connect_result", None)
        external_msg, external_msg_type = auto_result if auto_result else (None, None)

        col_ext1, col_ext2 = st.columns(2)
        with col_ext1:
            if st.button("🔌 연결", use_container_width=True, key="external_connect"):
                ok, message = connect_external_llm(
                    st.session_state.external_llm_model
                )
                external_msg = message
                external_msg_type = "success" if ok else "error"
        with col_ext2:
            if st.button(
                "🔌 해제", use_container_width=True, key="external_disconnect"
            ):
                st.session_state.external_llm_client = None
                st.session_state.external_llm_connected = False
                external_msg, external_msg_type = "해제됨", "info"

        if external_msg:
            if external_msg_type == "success":
                st.success(external_msg)
            elif external_msg_type == "error":
                st.error(external_msg)
            else:
                st.info(external_msg)

        if st.session_state.external_llm_connected:
            st.success(f"✅ 연결됨: {st.session_state.external_llm_model}")
        else:
            st.warning("⚠️ 외부 LLM에 연결해야 프롬프트를 생성할 수 있습니다.")

    st.markdown("---")

    # 모드 선택
    st.markdown("### 🎯 프롬프트 모드")
    mode_options = {"SFW (안전 모드)": "sfw", "NSFW (전체 포함)": "nsfw"}
    selected_mode_label = st.radio(
        "모드 선택",
        options=list(mode_options.keys()),
        index=0 if st.session_state.mode == "sfw" else 1,
    )
    new_mode = mode_options[selected_mode_label]
    if new_mode != st.session_state.mode:
        st.session_state.mode = new_mode
        st.session_state.generator = create_generator(new_mode)
        
    st.markdown("### 🎨 아트 스타일")
    style_options = {"실사 (Photorealistic)": "photorealistic", "애니메이션 (Anime)": "anime"}
    selected_style_label = st.radio(
        "스타일 선택",
        options=list(style_options.keys()),
        index=0 if st.session_state.style == "photorealistic" else 1,
    )
    st.session_state.style = style_options[selected_style_label]

    st.markdown("### 🧩 프롬프트 방식")
    target_keys = list(PROMPT_TARGETS.keys())
    selected_target = st.radio(
        "대상 이미지 모델",
        options=target_keys,
        format_func=lambda k: PROMPT_TARGETS[k],
        index=target_keys.index(st.session_state.prompt_target),
        help=(
            "레거시: 키워드를 나열하는 태그형 프롬프트로 개선합니다. "
            "최신 모델: 지시문을 이해하는 모델에 맞춰 자연어 문장형으로 재작성하고 "
            "8K/masterpiece 같은 품질 태그를 제거합니다. "
            "LLM 개선 단계에서만 적용됩니다."
        ),
    )
    st.session_state.prompt_target = selected_target

    st.checkbox(
        "기본 Modifiers 사용",
        key="use_modifiers",
        help="끄면 형용사/피부질감/상태/의상재질 수식어가 프롬프트에서 제외됩니다.",
    )

    st.checkbox(
        "품질 프리픽스 사용",
        key="use_quality_prefix",
        help="끄면 프롬프트 앞부분의 품질 수식구(QUALITY_PREFIXES)가 제외됩니다.",
    )

    st.checkbox(
        "🎬 비디오 생성용",
        key="video_mode",
        help=(
            "유튜브 쇼츠/틱톡 업로드를 가정한 8~10초 세로(9:16) 숏폼 영상 프롬프트로 재작성합니다. "
            "피사체 동작·카메라 무빙·한 컷 연출이 포함되며 자연스러운 사진 모드는 적용되지 않습니다."
        ),
    )

    st.markdown("---")

    # 자연스러운 사진 모드
    st.markdown("### 📷 자연스러운 사진 모드")
    st.checkbox(
        "AI 티 제거 지시문 적용",
        key="use_natural_photo",
        help=(
            "실사 스타일에서만 적용됩니다. 과장 수식어와 8K/HDR 같은 문구를 배제하고, "
            "화이트밸런스·렌즈 심도·재질감·광원 일관성 지시문을 붙입니다. "
            "LLM 개선 단계도 살을 붙이지 않고 다듬는 방식으로 바뀝니다."
        ),
    )

    if st.session_state.use_natural_photo:
        if st.session_state.video_mode:
            st.caption("⚠️ 비디오 생성용 모드에서는 적용되지 않습니다.")
        elif st.session_state.style != "photorealistic":
            st.caption("⚠️ 애니메이션 스타일에서는 적용되지 않습니다.")

        st.multiselect(
            "적용할 지시문",
            options=NATURAL_DIRECTIVE_KEYS,
            key="natural_directive_keys",
            help="필요한 항목만 골라 프롬프트 길이를 조절할 수 있습니다.",
        )

        with st.expander("지시문 내용 보기"):
            for _key in st.session_state.natural_directive_keys:
                st.markdown(f"**{_key}**")
                st.caption(NATURAL_PHOTO_DIRECTIVES[_key])

    st.markdown("---")

    # Dynamic Prompts 와일드카드
    st.markdown("### 📁 Dynamic Prompts Directory")
    col_dir1, col_dir2 = st.columns([1, 1])
    with col_dir1:
        if st.button("📂 찾기", use_container_width=True, key="dyn_dir_browse"):
            picked, pick_error = browse_directory(st.session_state.dynamic_prompts_dir)
            if picked:
                st.session_state.dynamic_prompts_dir = picked
                save_settings({"dynamic_prompts_dir": picked})
                st.rerun()
            elif pick_error:
                st.session_state.dyn_dir_error = pick_error
    with col_dir2:
        if st.button("🗑️ 해제", use_container_width=True, key="dyn_dir_clear"):
            st.session_state.dynamic_prompts_dir = ""
            save_settings({"dynamic_prompts_dir": ""})
            st.rerun()

    dynamic_prompts_dir = st.text_input(
        "와일드카드 디렉토리",
        key="dynamic_prompts_dir",
        help=(
            "사용자 요구사항에 `__hair__` 처럼 적으면 이 디렉토리의 hair.txt 에서 "
            "임의의 한 줄을 뽑아 치환합니다. 서브디렉토리는 탐색하지 않습니다."
        ),
    )
    # 기본값(.env)이 그대로 파일에 굳지 않도록 실제 변경이 있을 때만 저장
    if dynamic_prompts_dir != SAVED_SETTINGS["dynamic_prompts_dir"]:
        save_settings({"dynamic_prompts_dir": dynamic_prompts_dir})

    if st.session_state.pop("dyn_dir_error", None):
        st.warning("탐색기를 열 수 없습니다. 경로를 직접 입력해 주세요.")

    if not dynamic_prompts_dir.strip():
        st.caption("경로 미설정 - 와일드카드 치환이 비활성화됩니다.")
    elif resolve_directory(dynamic_prompts_dir) is None:
        st.error("❌ 디렉토리를 찾을 수 없습니다.")
    else:
        wildcard_names = list_wildcards(dynamic_prompts_dir)
        st.success(f"✅ 와일드카드 {len(wildcard_names)}개 인식됨")
        if wildcard_names:
            with st.expander("사용 가능한 와일드카드"):
                st.caption(", ".join(f"__{name}__" for name in wildcard_names))

    st.markdown("---")
    stats = st.session_state.history_manager.get_statistics()
    st.metric("전체 생성 수", stats["total"])

st.markdown(
    """
    <div class="main-header">
        <h1>🎨 Prompt Generator for Images and Videos</h1>
    </div>
""",
    unsafe_allow_html=True,
)

st.iframe(HOTKEY_GUARD_HTML, height=1)

tab1, tab2, tab3 = st.tabs(["🚀 프롬프트 생성", "📜 히스토리", "ℹ️ 사용 가이드"])

with tab1:
    user_requirements = st.text_area(
        "💡 사용자 요구사항 (선택)",
        placeholder="예: 'cyberpunk aesthetic with neon lights', '__hair__'...",
        height=80,
        key="user_requirements_input",
        help="`__이름__` 형식은 Dynamic Prompts Directory의 `이름.txt`에서 임의의 한 줄로 치환됩니다.",
    )

    st.markdown("---")
    st.markdown("### 🎨 세부 카테고리 설정")
    st.caption(
        "'제외'는 해당 항목을 프롬프트에서 빼고, 'LLM'은 LLM이 상상력을 발휘해 채우도록 맡깁니다. (LLM 연결 시)"
    )
    selected_configs = {}
    cols = st.columns(3)
    categories = list(DATA.keys())
    saved_categories = SAVED_SETTINGS["category_selections"]
    if not isinstance(saved_categories, dict):
        saved_categories = {}

    for i, category in enumerate(categories):
        with cols[i % 3]:
            options = ["랜덤", "제외", "LLM"] + get_category_options(
                category, st.session_state.mode
            )
            display_label = f"{category} ({CATEGORY_LABELS.get(category, category)})"
            widget_key = f"c_{category}"
            # 모드 변경 등으로 저장된 값이 옵션에 없으면 랜덤으로 되돌림
            current = st.session_state.get(widget_key, saved_categories.get(category))
            st.session_state[widget_key] = current if current in options else "랜덤"
            selected_configs[category] = st.selectbox(
                display_label, options=options, key=widget_key
            )

    st.markdown("---")
    col_gen, col_opt = st.columns([2, 1])

    # 외부 LLM 연결이 있어야만 생성 가능
    llm_available = st.session_state.external_llm_connected

    with col_opt:
        if llm_available:
            st.caption(f"사용: {st.session_state.external_llm_model}")
        else:
            st.caption("⚠️ 외부 LLM 미연결 - 생성 불가")

        save_history = st.checkbox("💾 저장", key="save_history")

    with col_gen:
        generate_clicked = st.button(
            "🚀 프롬프트 생성",
            use_container_width=True,
            type="primary",
            disabled=not llm_available,
        )

    if not llm_available:
        st.warning(
            "외부 LLM에 연결되어야 프롬프트를 생성할 수 있습니다. "
            "사이드바의 '외부 LLM 연동'에서 연결해 주세요."
        )

    if generate_clicked:
        st.session_state.prompt_counter += 1
        save_settings({"last_user_requirements": user_requirements})

        # 처리 로그 저장용
        process_logs = []

        user_requirements, wildcard_logs = expand_wildcards(
            user_requirements, st.session_state.dynamic_prompts_dir
        )

        with st.status("프롬프트 생성 중...", expanded=True) as status:
            if wildcard_logs:
                st.write(f"🎲 와일드카드 {len(wildcard_logs)}개 치환")
                for log in wildcard_logs:
                    process_logs.append(f"[와일드카드] {log}")

            # LLM 연결 상태 로그
            process_logs.append(
                f"[연결 상태] 외부LLM: 연결됨 ({st.session_state.external_llm_model})"
            )

            # 비디오 모드에서는 사진용 지시문을 쓰지 않음
            video_mode = st.session_state.video_mode
            process_logs.append(f"[옵션] 비디오 생성용 모드: {video_mode}")

            # 자연스러운 사진 모드는 실사 스타일에서만 적용
            natural_photo = (
                st.session_state.use_natural_photo
                and st.session_state.style == "photorealistic"
                and not video_mode
            )
            natural_keys = (
                st.session_state.natural_directive_keys if natural_photo else None
            )
            process_logs.append(
                f"[옵션] 자연스러운 사진 모드: {natural_photo}"
                + (f" - 지시문 {len(natural_keys)}개" if natural_photo else "")
            )
            prompt_target = st.session_state.prompt_target
            process_logs.append(
                f"[옵션] 프롬프트 방식: {PROMPT_TARGETS[prompt_target]}"
            )

            # 'LLM' 항목은 LLM이 상상으로 채우도록 위임
            creative_categories = get_creative_categories(selected_configs)
            if creative_categories:
                process_logs.append(
                    f"[옵션] LLM 상상 위임 항목: {', '.join(creative_categories)}"
                )

            # 1. 기본 프롬프트 생성 (지시문은 LLM 개선 후 부착)
            st.write("📝 기본 프롬프트 생성 중...")
            generator = create_generator(st.session_state.mode)
            english_prompt, negative_prompt = generator.generate(
                selected_configs,
                user_requirements,
                style=st.session_state.style,
                use_modifiers=st.session_state.use_modifiers,
                use_quality_prefix=st.session_state.use_quality_prefix,
                use_natural_photo=natural_photo,
                natural_directive_keys=natural_keys,
                include_natural_directives=False,
            )
            # 개선 전 원본은 지시문까지 붙인 완성형으로 저장 (개선 결과와 비교용)
            original_prompt = (
                attach_natural_directives(english_prompt, natural_keys)
                if natural_photo
                else english_prompt
            )
            process_logs.append(f"[기본 생성] 완료 - 스타일: {st.session_state.style}, 길이: {len(english_prompt)}자")
            st.write(f"✅ 기본 프롬프트 생성 완료 ({len(english_prompt)}자)")

            llm_enhanced = False
            enhanced_by = None

            # 2. LLM 개선 처리
            external_model = st.session_state.external_llm_model
            st.write(f"🤖 LLM 개선 중... ({external_model})")
            process_logs.append(f"[LLM 개선] 시작 - 사용: {external_model}")
            try:
                original_length = len(english_prompt)
                enhancer = ExternalLLMPromptEnhancer(
                    st.session_state.external_llm_client
                )
                english_prompt = enhancer.enhance_prompt(
                    english_prompt,
                    user_requirements=user_requirements,
                    style=st.session_state.style,
                    natural_photo=natural_photo,
                    prompt_target=prompt_target,
                    creative_categories=creative_categories,
                    video_mode=video_mode,
                )
                llm_enhanced = True
                enhanced_by = external_model

                process_logs.append(
                    f"[LLM 개선] 완료 - 길이: {original_length}자 → {len(english_prompt)}자"
                )
                st.write(
                    f"✅ LLM 개선 완료 ({original_length}자 → {len(english_prompt)}자)"
                )
            except Exception as e:
                error_msg = str(e)
                process_logs.append(f"[LLM 개선] 실패 - 오류: {error_msg}")
                st.write(f"⚠️ LLM 개선 실패: {error_msg}")

            # 3. 번역 처리
            korean_prompt = ""
            st.write(f"🌐 LLM 번역 중... ({external_model})")
            process_logs.append(f"[LLM 번역] 시작 - 사용: {external_model}")

            try:
                translator = ExternalLLMPromptEnhancer(
                    st.session_state.external_llm_client
                )
                korean_prompt = translator.translate_to_korean(english_prompt)

                if korean_prompt and korean_prompt.strip():
                    process_logs.append(
                        f"[LLM 번역] 완료 - 길이: {len(korean_prompt)}자"
                    )
                    st.write(f"✅ LLM 번역 완료 ({len(korean_prompt)}자)")
                else:
                    process_logs.append("[LLM 번역] 경고 - 빈 결과 반환")
                    st.write("⚠️ LLM 번역 결과가 비어있음")
                    korean_prompt = ""

            except Exception as e:
                error_msg = str(e)
                process_logs.append(f"[LLM 번역] 실패 - 오류: {error_msg}")
                st.write(f"⚠️ LLM 번역 실패: {error_msg}")
                korean_prompt = ""

            # 4. 자연스러움 지시문 부착
            # LLM 개선/번역이 끝난 뒤 붙여 지시문이 요약·변형되지 않도록 함
            if natural_photo:
                before_length = len(english_prompt)
                english_prompt = attach_natural_directives(
                    english_prompt, natural_keys
                )
                if len(english_prompt) > before_length:
                    process_logs.append(
                        f"[자연스러움 지시문] {len(natural_keys)}개 부착 - "
                        f"길이: {before_length}자 → {len(english_prompt)}자"
                    )
                    st.write(f"✅ 자연스러움 지시문 {len(natural_keys)}개 부착")
                else:
                    process_logs.append("[자연스러움 지시문] 선택된 항목 없음 - 생략")

            status.update(label="✅ 생성 완료!", state="complete", expanded=False)

        # 처리 로그를 세션에 저장
        st.session_state.last_process_logs = process_logs

        st.session_state.last_prompt = {
            "english": english_prompt,
            "original": original_prompt,
            "korean": korean_prompt,
            "negative": negative_prompt,
            "enhanced_by": enhanced_by,
            "natural_photo": natural_photo,
        }

        if save_history:
            st.session_state.history_manager.add(
                mode=st.session_state.mode,
                english_prompt=english_prompt,
                korean_prompt=korean_prompt,
                negative_prompt=negative_prompt,
                selected_options=selected_configs,
                user_requirements=user_requirements,
                ollama_enhanced=llm_enhanced,
            )

    # 결과 표시
    if st.session_state.last_prompt:
        st.markdown("---")
        st.markdown("### ✨ 결과 확인")

        # 1. 번역 결과 (가장 먼저 확인)
        st.markdown(
            '<span class="prompt-label">🇰🇷 한글 번역 (In-App)</span>',
            unsafe_allow_html=True,
        )
        render_copyable_prompt(
            st.session_state.last_prompt["korean"],
            "korean",
            height=180,
            variant="translated",
        )
        if st.session_state.last_prompt.get("natural_photo"):
            st.caption(
                "자연스러움 지시문은 매번 동일한 고정 문구이므로 번역에서 제외했습니다. "
                "내용은 사이드바에서 확인할 수 있습니다."
            )

        # 2. 개선 전 원본 프롬프트 (LLM 개선 사용 시에만 표시)
        if st.session_state.last_prompt.get(
            "enhanced_by"
        ) and st.session_state.last_prompt.get("original"):
            st.markdown(
                '<span class="prompt-label">📄 Original Prompt (Before Enhancement)</span>',
                unsafe_allow_html=True,
            )
            # key 있는 위젯은 세션 상태 값이 고착되어 재생성 시 갱신되지 않으므로
            # 표시 전용 렌더러 사용
            render_copyable_prompt(
                st.session_state.last_prompt["original"], "original", height=140
            )

        # 3. 영문 프롬프트
        enhanced_label = (
            f" (Enhanced by {st.session_state.last_prompt['enhanced_by']})"
            if st.session_state.last_prompt.get("enhanced_by")
            else ""
        )
        st.markdown(
            f'<span class="prompt-label">🇺🇸 English Prompt{enhanced_label}</span>',
            unsafe_allow_html=True,
        )

        # 복사 기능이 포함된 커스텀 텍스트 블록
        render_copyable_prompt(st.session_state.last_prompt["english"], "english")

        # 4. 네거티브 프롬프트
        with st.expander("📛 Negative Prompt"):
            st.code(st.session_state.last_prompt["negative"])

        # 4. 처리 로그 (디버그용)
        if (
            "last_process_logs" in st.session_state
            and st.session_state.last_process_logs
        ):
            with st.expander("🔍 처리 로그 (디버그)"):
                for log in st.session_state.last_process_logs:
                    st.text(log)

with tab2:
    history_items = st.session_state.history_manager.get_recent(10)
    if not history_items:
        st.info("기록이 없습니다.")
    for idx, item in enumerate(history_items):
        with st.expander(f"🕒 {item.timestamp[:16]} | {item.mode.upper()}"):
            st.markdown(
                '<span class="prompt-label">🇰🇷 한글 번역</span>', unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="translated-box">{item.korean_prompt if item.korean_prompt else "번역 기록 없음"}</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<span class="prompt-label">🇺🇸 English Prompt</span>',
                unsafe_allow_html=True,
            )
            render_copyable_prompt(item.english_prompt, f"history-{idx}")

with tab3:
    st.markdown(
        "### 사용 가이드\n"
        "1. 사용할 LLM 모델 선택 및 연결 (LLM API키 설정 필요)\n"
        "2. 세부 카테고리 취사 선택\n"
        "3. 생성 버튼을 누르면 최종 영문 프롬프트와 참고용 한국어 번역본이 생성됨\n"
        "\n"
        "### 프롬프트 방식\n"
        "LLM 개선 단계에서 어떤 형태의 프롬프트를 만들지 정하는 옵션.\n"
        "- 레거시: Stable Diffusion/Flux 계열에 맞춰 키워드를 나열하는 태그형으로 개선함\n"
        "- 최신 모델: GPT-Image, Nano Banana처럼 지시문을 이해하는 모델에 맞춰 "
        "자연어 문장으로 재작성하고 8K/masterpiece 같은 품질 태그와 가중치 문법을 제거함\n"
        "- 자연스러운 사진 모드가 켜져 있으면 그쪽 지시문이 우선 적용됨\n"
        "\n"
        "### 자연스러운 사진 모드\n"
        "AI가 만든 티가 나지 않는 결과를 얻기 위한 옵션. 실사 스타일에서만 적용됨.\n"
        "- 과장 형용사, 인공적인 피부 표현, 8K/HDR/리터칭 류의 품질 수식구를 프롬프트에서 배제함\n"
        "- 화이트밸런스, 렌즈 심도, 재질감, 광원 일관성 등의 지시문을 프롬프트 끝에 덧붙임\n"
        "- LLM 개선 단계가 살을 붙이는 방식에서 덜어내며 다듬는 방식으로 바뀜\n"
        "- 지시문은 LLM 개선이 끝난 뒤 원문 그대로 붙으므로 요약·변형되지 않음\n"
        "- 네거티브 프롬프트도 AI 티가 나는 후처리를 억제하는 항목으로 교체됨\n"
        "\n"
        "### 샷/프레이밍\n"
        "인물의 어느 부위까지 담을지 지정하는 카테고리. "
        "증명사진용 상반신 정면, 헤드샷, 전신샷 등을 선택할 수 있음."
    )

st.markdown("---")
st.markdown(
    '<div style="text-align:center; color:grey; font-size:0.8rem;">Prompt Generator for Images and Videos</div>',
    unsafe_allow_html=True,
)

# 렌더링이 끝난 시점의 설정을 파일에 반영 (변경분이 있을 때만 기록)
save_settings(
    {
        "mode": st.session_state.mode,
        "style": st.session_state.style,
        "prompt_target": st.session_state.prompt_target,
        "use_modifiers": st.session_state.use_modifiers,
        "use_quality_prefix": st.session_state.use_quality_prefix,
        "use_natural_photo": st.session_state.use_natural_photo,
        "video_mode": st.session_state.video_mode,
        "natural_directive_keys": list(st.session_state.natural_directive_keys),
        "last_external_model": st.session_state.external_llm_model,
        "save_history": st.session_state.save_history,
        "category_selections": {
            category: st.session_state.get(f"c_{category}", "랜덤")
            for category in DATA
        },
    }
)
