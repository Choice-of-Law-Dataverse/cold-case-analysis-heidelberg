-def run_cold_case_analysis(state: AppState) -> AppState:
-    # 1. Choice-of-law section extraction
-    state_col = streamlit_col_extractor_runner(state)
-    # 2. Theme classification
-    state_theme = run_theme_classification(state_col.values)
-    # 3. Final case analysis
-    result = run_analysis(state_theme.values)
-    return result
+def run_cold_case_analysis():
+    # 1. Choice-of-law section extraction
+    streamlit_col_extractor_runner()
+    # 2. Theme classification
+    streamlit_theme_classification_runner()
+    # 3. Final case analysis
+    streamlit_case_analyzer_runner()
+    # at each runner completion, session_state["app_state"] is updated
+    return st.session_state["app_state"]

-# --- UI: title & input area ---
-st.title("Cold Case Analysis")
-# bind text area to session_state
-full_text = st.text_area(
-    "Court decision text:",
-    value=st.session_state["app_state"]["full_text"],
-    key="full_text_input",
-    height=300
-)
-# persist back
-st.session_state["app_state"]["full_text"] = full_text
+# UI: title & input area
+st.title("Cold Case Analysis")
+full_text = st.text_area(
+    "Court decision text:",
+    value=st.session_state["app_state"]["full_text"],
+    key="full_text_input",
+    height=300,
+)
+st.session_state["app_state"]["full_text"] = full_text

-if st.button("Run analysis"):
-    # reset any previous run context
-    for key in ["col_state","coler","waiting_for", "theme_state","themeer","theme_waiting_for", "analysis_state","caser","analysis_waiting_for"]:
-        st.session_state.pop(key, None)
-    with st.spinner("Analyzing…"):
-        final = run_cold_case_analysis()
-        st.session_state["app_state"] = final
-        st.success("Analysis complete")
-        st.subheader("Final State")
-        st.json(final)
+# Run analysis button
+if st.button("Run analysis"):
+    # clear previous runner contexts
+    for key in [
+        "col_state", "coler", "waiting_for",
+        "theme_state", "themeer", "theme_waiting_for",
+        "analysis_state", "caser"
+    ]:
+        st.session_state.pop(key, None)
+    with st.spinner("Analyzing…"):
+        final_state = run_cold_case_analysis()
+        st.session_state["app_state"] = final_state
+        st.success("Analysis complete")
+        st.subheader("Final State")
+        st.json(final_state)

-## display chat log
-if "messages" not in st.session_state:
-    st.session_state.messages = []
-for msg in st.session_state.messages:
-    with st.chat_message(msg["role"]):
-        st.markdown(msg["content"])
