import streamlit as st
import streamlit.components.v1 as components
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.prompt_database import DATA, CATEGORY_LABELS, get_category_options, NEGATIVE_PROMPTS
from core.prompt_engine import PromptGenerator, create_generator
from integrations.ollama_integration import OllamaClient, PromptEnhancer, get_ollama_client
from integrations.external_llm_integration import (
    ExternalLLMClient, ExternalLLMPromptEnhancer, 
    check_api_key_for_model, EXTERNAL_LLM_MODELS, get_provider_from_model
)
from utils.history_manager import get_history_manager

st.set_page_config(
    page_title="Prompt Generator for Images",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
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
    
    .ollama-status { padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; }
    .ollama-connected { background: #d1fae5; border: 1px solid #10b981; color: #065f46; }
    .ollama-disconnected { background: #fee2e2; border: 1px solid #ef4444; color: #991b1b; }
</style>
""", unsafe_allow_html=True)

if 'mode' not in st.session_state: st.session_state.mode = "sfw"
if 'generator' not in st.session_state: st.session_state.generator = create_generator("sfw")
if 'ollama_client' not in st.session_state: st.session_state.ollama_client = None
if 'ollama_connected' not in st.session_state: st.session_state.ollama_connected = False
if 'selected_ollama_model' not in st.session_state: st.session_state.selected_ollama_model = None
if 'external_llm_client' not in st.session_state: st.session_state.external_llm_client = None
if 'external_llm_connected' not in st.session_state: st.session_state.external_llm_connected = False
if 'external_llm_model' not in st.session_state: st.session_state.external_llm_model = EXTERNAL_LLM_MODELS[0]
if 'history_manager' not in st.session_state: st.session_state.history_manager = get_history_manager()
if 'last_prompt' not in st.session_state: st.session_state.last_prompt = None
if 'prompt_counter' not in st.session_state: st.session_state.prompt_counter = 0
if 'chk_llm_enhance' not in st.session_state: st.session_state.chk_llm_enhance = False
if 'chk_llm_translate' not in st.session_state: st.session_state.chk_llm_translate = False


with st.sidebar:
    st.markdown("## ⚙️ 엔진 설정")
    
    # 모드 선택
    st.markdown("### 🎯 프롬프트 모드")
    mode_options = {"SFW (안전 모드)": "sfw", "NSFW (전체 포함)": "nsfw"}
    selected_mode_label = st.radio(
        "모드 선택",
        options=list(mode_options.keys()),
        index=0 if st.session_state.mode == "sfw" else 1
    )
    new_mode = mode_options[selected_mode_label]
    if new_mode != st.session_state.mode:
        st.session_state.mode = new_mode
        st.session_state.generator = create_generator(new_mode)
    
    st.markdown("---")
    
    # 외부 LLM 연동
    st.markdown("### 🔑 외부 LLM 연동")
    st.session_state.external_llm_model = st.selectbox(
        "모델 선택",
        options=EXTERNAL_LLM_MODELS,
        index=EXTERNAL_LLM_MODELS.index(st.session_state.external_llm_model) if st.session_state.external_llm_model in EXTERNAL_LLM_MODELS else 0,
        key="external_model_select"
    )
    
    # 선택된 모델의 제공자 표시
    provider = get_provider_from_model(st.session_state.external_llm_model)
    provider_display = {"openai": "OpenAI", "gemini": "Google Gemini", "anthropic": "Anthropic Claude"}.get(provider, provider)
    st.caption(f"제공자: {provider_display}")
    
    external_msg = None
    external_msg_type = None
    col_ext1, col_ext2 = st.columns(2)
    with col_ext1:
        if st.button("🔌 연결", use_container_width=True, key="external_connect"):
            has_key, key_msg = check_api_key_for_model(st.session_state.external_llm_model)
            if not has_key:
                external_msg, external_msg_type = f"❌ {key_msg}", "error"
            else:
                client = ExternalLLMClient(model=st.session_state.external_llm_model)
                success, message = client.test_connection()
                if success:
                    st.session_state.external_llm_client = client
                    st.session_state.external_llm_connected = True
                    st.session_state.chk_llm_enhance = True
                    st.session_state.chk_llm_translate = True
                    external_msg, external_msg_type = message, "success"
                else:
                    st.session_state.external_llm_connected = False
                    external_msg, external_msg_type = message, "error"
    with col_ext2:
        if st.button("🔌 해제", use_container_width=True, key="external_disconnect"):
            st.session_state.external_llm_client = None
            st.session_state.external_llm_connected = False
            external_msg, external_msg_type = "해제됨", "info"
    
    if external_msg:
        if external_msg_type == "success": st.success(external_msg)
        elif external_msg_type == "error": st.error(external_msg)
        else: st.info(external_msg)
    
    if st.session_state.external_llm_connected:
        st.success(f"✅ 연결됨: {st.session_state.external_llm_model}")
    
    st.markdown("---")
    
    # Ollama 연동
    st.markdown("### 🤖 Ollama 연동")
    ollama_host = st.text_input("Ollama 서버 주소", value="http://localhost:11434")
    
    ollama_msg = None
    ollama_msg_type = None
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 연결", use_container_width=True, key="ollama_connect"):
            client = OllamaClient(ollama_host)
            success, message = client.test_connection()
            if success:
                st.session_state.ollama_client, st.session_state.ollama_connected = client, True
                st.session_state.chk_llm_enhance = True
                st.session_state.chk_llm_translate = True
                ollama_msg, ollama_msg_type = message, "success"
            else:
                st.session_state.ollama_connected = False
                ollama_msg, ollama_msg_type = message, "error"
    with col2:
        if st.button("🔌 해제", use_container_width=True, key="ollama_disconnect"):
            st.session_state.ollama_client, st.session_state.ollama_connected = None, False
            ollama_msg, ollama_msg_type = "해제됨", "info"
    
    if ollama_msg:
        if ollama_msg_type == "success": st.success(ollama_msg)
        elif ollama_msg_type == "error": st.error(ollama_msg)
        else: st.info(ollama_msg)

    if st.session_state.ollama_connected:
        models = st.session_state.ollama_client.get_model_names()
        if models:
            st.session_state.selected_ollama_model = st.selectbox("모델 선택", options=models, key="ollama_model_select")
    
    st.markdown("---")
    stats = st.session_state.history_manager.get_statistics()
    st.metric("전체 생성 수", stats['total'])

st.markdown("""
    <div class="main-header">
        <h1>🎨 Prompt Generator for Images</h1>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 프롬프트 생성", "📜 히스토리", "ℹ️ 사용 가이드"])

with tab1:
    user_requirements = st.text_area(
        "💡 사용자 요구사항 (선택)",
        placeholder="예: 'cyberpunk aesthetic with neon lights'...",
        height=80
    )
    
    st.markdown("---")
    st.markdown("### 🎨 세부 카테고리 설정")
    selected_configs = {}
    cols = st.columns(3)
    categories = list(DATA.keys())
    
    for i, category in enumerate(categories):
        with cols[i % 3]:
            options = get_category_options(category, st.session_state.mode)
            display_label = f"{category} ({CATEGORY_LABELS.get(category, category)})"
            selected_configs[category] = st.selectbox(display_label, options=["랜덤", "제외"] + options, key=f"c_{i}")

    st.markdown("---")
    col_gen, col_opt = st.columns([2, 1])
    
    # LLM 사용 가능 여부 확인
    llm_available = st.session_state.ollama_connected or st.session_state.external_llm_connected
    
    with col_opt:
        # LLM 연결 상태에 따라 자동 결정
        use_llm_enhance = llm_available
        use_llm_translate = llm_available
        
        # LLM 연결 시 사용할 LLM 자동 선택
        if llm_available:
            llm_options = []
            if st.session_state.ollama_connected:
                llm_options.append("Ollama")
            if st.session_state.external_llm_connected:
                llm_options.append(f"외부LLM ({st.session_state.external_llm_model})")
            
            if len(llm_options) > 1:
                selected_llm = st.radio("LLM 선택", options=llm_options, horizontal=True, key="llm_select")
            elif len(llm_options) == 1:
                selected_llm = llm_options[0]
                st.caption(f"사용: {selected_llm}")
            else:
                selected_llm = None
        else:
            selected_llm = None
            st.caption("⚠️ LLM 미연결 - 개선/번역 비활성화")
        
        save_history = st.checkbox("💾 저장", value=True)
    
    with col_gen:
        generate_clicked = st.button("🚀 프롬프트 생성", use_container_width=True, type="primary")

    if generate_clicked:
        st.session_state.prompt_counter += 1
        
        # 처리 로그 저장용
        process_logs = []
        
        with st.status("프롬프트 생성 중...", expanded=True) as status:
            # LLM 연결 상태 로그
            process_logs.append(f"[연결 상태] Ollama: {'연결됨' if st.session_state.ollama_connected else '미연결'}")
            process_logs.append(f"[연결 상태] 외부LLM: {'연결됨 (' + st.session_state.external_llm_model + ')' if st.session_state.external_llm_connected else '미연결'}")
            process_logs.append(f"[옵션] LLM 개선: {use_llm_enhance}, LLM 번역: {use_llm_translate}")
            if use_llm_enhance:
                process_logs.append(f"[옵션] 선택된 LLM: {selected_llm if selected_llm else '없음'}")
            
            # 1. 기본 프롬프트 생성
            st.write("📝 기본 프롬프트 생성 중...")
            generator = create_generator(st.session_state.mode)
            english_prompt, negative_prompt = generator.generate(selected_configs, user_requirements)
            original_prompt = english_prompt  # 개선 전 원본 저장
            process_logs.append(f"[기본 생성] 완료 - 길이: {len(english_prompt)}자")
            st.write(f"✅ 기본 프롬프트 생성 완료 ({len(english_prompt)}자)")
            
            llm_enhanced = False
            enhanced_by = None
            
            # 2. LLM 개선 처리
            if use_llm_enhance and selected_llm:
                st.write(f"🤖 LLM 개선 중... ({selected_llm})")
                process_logs.append(f"[LLM 개선] 시작 - 사용: {selected_llm}")
                try:
                    original_length = len(english_prompt)
                    if selected_llm == "Ollama" and st.session_state.ollama_connected:
                        enhancer = PromptEnhancer(st.session_state.ollama_client)
                        enhancer.set_default_model(st.session_state.selected_ollama_model)
                        process_logs.append(f"[LLM 개선] Ollama 모델: {st.session_state.selected_ollama_model}")
                        english_prompt = enhancer.enhance_prompt(english_prompt, user_requirements=user_requirements)
                        llm_enhanced = True
                        enhanced_by = f"Ollama ({st.session_state.selected_ollama_model})"
                    elif selected_llm.startswith("외부LLM") and st.session_state.external_llm_connected:
                        enhancer = ExternalLLMPromptEnhancer(st.session_state.external_llm_client)
                        process_logs.append(f"[LLM 개선] 외부LLM 모델: {st.session_state.external_llm_model}")
                        english_prompt = enhancer.enhance_prompt(english_prompt, user_requirements=user_requirements)
                        llm_enhanced = True
                        enhanced_by = st.session_state.external_llm_model
                    
                    process_logs.append(f"[LLM 개선] 완료 - 길이: {original_length}자 → {len(english_prompt)}자")
                    st.write(f"✅ LLM 개선 완료 ({original_length}자 → {len(english_prompt)}자)")
                except Exception as e:
                    error_msg = str(e)
                    process_logs.append(f"[LLM 개선] 실패 - 오류: {error_msg}")
                    st.write(f"⚠️ LLM 개선 실패: {error_msg}")
            
            # 3. 번역 처리 (LLM 연결 시에만)
            korean_prompt = ""
            if use_llm_translate and llm_available:
                translate_llm = selected_llm
                st.write(f"🌐 LLM 번역 중... ({translate_llm})")
                process_logs.append(f"[LLM 번역] 시작 - 사용: {translate_llm}")
                
                try:
                    if translate_llm == "Ollama" and st.session_state.ollama_connected:
                        translator = PromptEnhancer(st.session_state.ollama_client)
                        translator.set_default_model(st.session_state.selected_ollama_model)
                        process_logs.append(f"[LLM 번역] Ollama 모델: {st.session_state.selected_ollama_model}")
                        korean_prompt = translator.translate_to_korean(english_prompt)
                    elif translate_llm.startswith("외부LLM") and st.session_state.external_llm_connected:
                        translator = ExternalLLMPromptEnhancer(st.session_state.external_llm_client)
                        process_logs.append(f"[LLM 번역] 외부LLM 모델: {st.session_state.external_llm_model}")
                        korean_prompt = translator.translate_to_korean(english_prompt)
                    
                    if korean_prompt and korean_prompt.strip():
                        process_logs.append(f"[LLM 번역] 완료 - 길이: {len(korean_prompt)}자")
                        st.write(f"✅ LLM 번역 완료 ({len(korean_prompt)}자)")
                    else:
                        process_logs.append(f"[LLM 번역] 경고 - 빈 결과 반환")
                        st.write("⚠️ LLM 번역 결과가 비어있음")
                        korean_prompt = ""
                        
                except Exception as e:
                    error_msg = str(e)
                    process_logs.append(f"[LLM 번역] 실패 - 오류: {error_msg}")
                    st.write(f"⚠️ LLM 번역 실패: {error_msg}")
                    korean_prompt = ""
            else:
                # LLM 미연결 시 번역 생략
                process_logs.append("[번역] LLM 미연결 - 번역 생략")
                st.write("⏭️ 번역 생략 (LLM 미연결)")
            
            status.update(label="✅ 생성 완료!", state="complete", expanded=False)
        
        # 처리 로그를 세션에 저장
        st.session_state.last_process_logs = process_logs
        
        st.session_state.last_prompt = {
            'english': english_prompt,
            'original': original_prompt,
            'korean': korean_prompt,
            'negative': negative_prompt,
            'enhanced_by': enhanced_by
        }
        
        if save_history:
            st.session_state.history_manager.add(
                mode=st.session_state.mode,
                english_prompt=english_prompt,
                korean_prompt=korean_prompt,
                negative_prompt=negative_prompt,
                selected_options=selected_configs,
                user_requirements=user_requirements,
                ollama_enhanced=llm_enhanced
            )

    # 결과 표시
    if st.session_state.last_prompt:
        st.markdown("---")
        st.markdown("### ✨ 결과 확인")
        
        # 1. 번역 결과 (가장 먼저 확인)
        st.markdown('<span class="prompt-label">🇰🇷 한글 번역 (In-App)</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="translated-box">{st.session_state.last_prompt["korean"]}</div>', unsafe_allow_html=True)
        
        # 2. 개선 전 원본 프롬프트 (LLM 개선 사용 시에만 표시)
        if st.session_state.last_prompt.get('enhanced_by') and st.session_state.last_prompt.get('original'):
            st.markdown('<span class="prompt-label">📄 Original Prompt (Before Enhancement)</span>', unsafe_allow_html=True)
            st.text_area("원본", value=st.session_state.last_prompt['original'], height=100, label_visibility="collapsed", key="original_prompt")
        
        # 3. 영문 프롬프트
        enhanced_label = f" (Enhanced by {st.session_state.last_prompt['enhanced_by']})" if st.session_state.last_prompt.get('enhanced_by') else ""
        st.markdown(f'<span class="prompt-label">🇺🇸 English Prompt{enhanced_label}</span>', unsafe_allow_html=True)
        
        # 복사 기능이 포함된 커스텀 텍스트 블록
        english_text_escaped = st.session_state.last_prompt['english'].replace('\\', '\\\\').replace('`', '\\`').replace('</script>', '<\\/script>')
        components.html(f'''
        <div style="position: relative; margin-bottom: 16px;">
            <button id="copyBtn" 
                    style="position: absolute; top: 8px; right: 8px; background: #374151; color: white; border: none; border-radius: 4px; padding: 6px 10px; cursor: pointer; font-size: 14px; z-index: 10;">
                📋
            </button>
            <div id="english-prompt" style="background: #1e1e1e; color: #d4d4d4; padding: 16px; padding-right: 50px; border-radius: 8px; font-family: monospace; font-size: 14px; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; max-height: 200px; overflow-y: auto;">{english_text_escaped}</div>
        </div>
        <script>
            document.getElementById('copyBtn').addEventListener('click', function() {{
                const text = document.getElementById('english-prompt').innerText;
                navigator.clipboard.writeText(text).then(() => {{
                    this.innerText = '✅';
                    setTimeout(() => {{ this.innerText = '📋'; }}, 1500);
                }}).catch(() => {{
                    this.innerText = '❌';
                    setTimeout(() => {{ this.innerText = '📋'; }}, 1500);
                }});
            }});
        </script>
        ''', height=200)
        
        # 4. 네거티브 프롬프트
        with st.expander("📛 Negative Prompt"):
            st.code(st.session_state.last_prompt['negative'])
        
        # 4. 처리 로그 (디버그용)
        if 'last_process_logs' in st.session_state and st.session_state.last_process_logs:
            with st.expander("🔍 처리 로그 (디버그)"):
                for log in st.session_state.last_process_logs:
                    st.text(log)

with tab2:
    history_items = st.session_state.history_manager.get_recent(10)
    if not history_items:
        st.info("기록이 없습니다.")
    for idx, item in enumerate(history_items):
        with st.expander(f"🕒 {item.timestamp[:16]} | {item.mode.upper()}"):
            st.markdown('<span class="prompt-label">🇰🇷 한글 번역</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="translated-box">{item.korean_prompt if item.korean_prompt else "번역 기록 없음"}</div>', unsafe_allow_html=True)
            
            st.markdown('<span class="prompt-label">🇺🇸 English Prompt</span>', unsafe_allow_html=True)
            english_text_escaped = item.english_prompt.replace('\\', '\\\\').replace('`', '\\`').replace('</script>', '<\\/script>')
            components.html(f'''
            <div style="position: relative; margin-bottom: 16px;">
                <button id="copyBtn_{idx}" 
                        style="position: absolute; top: 8px; right: 8px; background: #374151; color: white; border: none; border-radius: 4px; padding: 6px 10px; cursor: pointer; font-size: 14px; z-index: 10;">
                    📋
                </button>
                <div id="english-prompt-{idx}" style="background: #1e1e1e; color: #d4d4d4; padding: 16px; padding-right: 50px; border-radius: 8px; font-family: monospace; font-size: 14px; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; max-height: 200px; overflow-y: auto;">{english_text_escaped}</div>
            </div>
            <script>
                document.getElementById('copyBtn_{idx}').addEventListener('click', function() {{
                    const text = document.getElementById('english-prompt-{idx}').innerText;
                    navigator.clipboard.writeText(text).then(() => {{
                        this.innerText = '✅';
                        setTimeout(() => {{ this.innerText = '📋'; }}, 1500);
                    }}).catch(() => {{
                        this.innerText = '❌';
                        setTimeout(() => {{ this.innerText = '📋'; }}, 1500);
                    }});
                }});
            </script>
            ''', height=200)

with tab3:
    st.markdown("### 사용 가이드\n1. 사용할 LLM 모델 선택 및 연결 (LLM API키 설정 필요)\n2. 세부 카테고리 취사 선택\n3. 생성 버튼을 누르면 최종 영문 프롬프트와 참고용 한국어 번역본이 생성됨")

st.markdown("---")
st.markdown('<div style="text-align:center; color:grey; font-size:0.8rem;">Prompt Generator for Images</div>', unsafe_allow_html=True)