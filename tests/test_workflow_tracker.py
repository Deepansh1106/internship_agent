from unittest import TestCase, main

import streamlit as st

from frontend.streamlit_app import current_workflow_step


class TestWorkflowTracker(TestCase):

    def setUp(self):
        st.session_state.clear()
        st.session_state.thread_id = "workflow-test"
        st.session_state.workflow_state = {}
        st.session_state.interrupt = None

    def test_uses_role_interrupt_for_current_step(self):
        st.session_state.interrupt = {"type": "role_selection"}
        self.assertEqual(current_workflow_step(), 2)

    def test_uses_job_interrupt_for_current_step(self):
        st.session_state.interrupt = {"type": "job_selection"}
        self.assertEqual(current_workflow_step(), 4)

    def test_marks_workflow_complete_after_storage(self):
        st.session_state.workflow_state = {"stored_applications": []}
        self.assertEqual(current_workflow_step(), 6)


if __name__ == "__main__":
    main()
