"""Shared Streamlit rendering helpers."""

from __future__ import annotations

from typing import Dict, List

import streamlit as st


def render_task(task: Dict[str, object]) -> None:
    task_id = task["id"]
    title = task["title"]
    subtitle = task["subtitle"]
    summary = task["summary"]
    steps: List[str] = task["steps"]
    outputs: List[str] = task["outputs"]
    notes: List[str] = task["notes"]

    with st.expander(f"Task {task_id}. {title}", expanded=(task_id == 1)):
        st.caption(subtitle)
        st.write(summary)

        st.markdown("**Steps**")
        for idx, step in enumerate(steps, start=1):
            st.markdown(f"{idx}. {step}")

        st.markdown("**Expected outputs**")
        for output in outputs:
            st.markdown(f"- {output}")

        st.markdown("**Notes**")
        for note in notes:
            st.info(note)


def render_phase_page(phase_title: str, phase_summary: str, tasks: List[Dict[str, object]]) -> None:
    st.title(phase_title)
    st.write(phase_summary)
    st.divider()
    for task in tasks:
        render_task(task)


def render_research_frame(
    gap: str,
    questions: List[str],
    objective: str,
    contribution: List[str],
    expected_results: List[str],
) -> None:
    st.divider()
    st.subheader("Research Frame")
    st.markdown("**Research Gap**")
    st.write(gap)

    st.markdown("**Research Questions**")
    for idx, q in enumerate(questions, start=1):
        st.markdown(f"{idx}. {q}")

    st.markdown("**Research Objective**")
    st.write(objective)

    st.markdown("**Contribution**")
    for item in contribution:
        st.markdown(f"- {item}")

    st.markdown("**Expected Results**")
    for item in expected_results:
        st.markdown(f"- {item}")
