import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.models.student_profile_model import StudentProfile
from app.api.synthetic_peer_api import (
    SyntheticPeerRequest,
    create_synthetic_peer_classroom,
)
from app.services.synthetic_peer_service import (
    is_topic_relevant,
    build_synthetic_peer_instruction,
    generate_synthetic_peers,
)


class TestSyntheticPeerLearningMemory(unittest.TestCase):
    def setUp(self):
        self.sample_memory = {
            "last_session": {
                "topic": "C Pointers",
                "misconception": "Pointers directly store value contents instead of memory addresses.",
                "final_understanding": "A pointer variable stores the hexadecimal memory address of another variable.",
                "next_thinking_question": "What happens in memory when you dereference a null pointer?",
                "calibration": "OVERCONFIDENT",
                "debate_result": "CLAIM PARTIALLY SUPPORTED",
            },
            "updated_at": "2026-10-10T10:00:00Z",
        }

    # 1. Topic Relevance Detection
    def test_is_topic_relevant_exact_match(self):
        self.assertTrue(is_topic_relevant("C Pointers", "c pointers"))
        self.assertTrue(is_topic_relevant("c pointers", "C Pointers"))

    def test_is_topic_relevant_substring_and_token_overlap(self):
        self.assertTrue(is_topic_relevant("Pointers in C", "C Pointers"))
        self.assertTrue(is_topic_relevant("Binary Search Trees", "Tree Traversal"))

    def test_is_topic_relevant_disjoint_topics(self):
        self.assertFalse(is_topic_relevant("Database Normalization", "C Pointers"))
        self.assertFalse(is_topic_relevant("TCP Handshake", "Binary Search Trees"))

    def test_is_topic_relevant_empty_or_none(self):
        self.assertFalse(is_topic_relevant("", "C Pointers"))
        self.assertFalse(is_topic_relevant("C Pointers", ""))
        self.assertFalse(is_topic_relevant("", ""))

    # 2. Prompt Builder: Relevant Previous Topic
    def test_build_instruction_with_matching_memory(self):
        instruction = build_synthetic_peer_instruction(
            topic="C Pointers",
            student_prompt="Help me review pointers",
            prior_learning_memory=self.sample_memory,
        )

        # Verify historical memory signals are present
        self.assertIn("Previous topic: C Pointers", instruction)
        self.assertIn(
            "Previous misconception signal: Pointers directly store value contents",
            instruction,
        )
        self.assertIn(
            "Previous final understanding: A pointer variable stores the hexadecimal memory address",
            instruction,
        )
        self.assertIn(
            "Previous thinking question: What happens in memory when you dereference a null pointer?",
            instruction,
        )

        # Verify personalized guidance directive
        self.assertIn("RELEVANT PREVIOUS TOPIC DETECTED", instruction)
        self.assertIn("SKEPTIC PEER CHALLENGE DIRECTIVE", instruction)
        self.assertIn(
            "Pointers directly store value contents instead of memory addresses",
            instruction,
        )

        # Verify strict grounding constraints
        self.assertIn("strictly grounded in the supplied study material", instruction)
        self.assertIn("Do NOT introduce external facts", instruction)

    # 3. Prompt Builder: Topic Shift
    def test_build_instruction_with_different_topic(self):
        instruction = build_synthetic_peer_instruction(
            topic="Database Normalization",
            student_prompt="Explain 3NF",
            prior_learning_memory=self.sample_memory,
        )

        # Verify topic shift is detected
        self.assertIn("DIFFERENT TOPIC", instruction)
        self.assertIn(
            'The current topic "Database Normalization" differs from previous topic "C Pointers"',
            instruction,
        )
        self.assertIn(
            'Do NOT assume or transfer facts, examples, or rules from "C Pointers" into "Database Normalization"',
            instruction,
        )
        self.assertIn(
            "All peer explanations, challenges, and exam points must be derived EXCLUSIVELY from the current study material",
            instruction,
        )

    # 4. Prompt Builder: Empty / Absent Memory
    def test_build_instruction_without_memory(self):
        instruction = build_synthetic_peer_instruction(
            topic="Operating Systems",
            student_prompt="What is paging?",
            prior_learning_memory=None,
        )

        self.assertIn("No previous learning memory is available.", instruction)
        self.assertIn("NO PREVIOUS MEMORY", instruction)
        self.assertIn("PEER 1 - EXPLAINER PEER", instruction)
        self.assertIn("PEER 2 - SKEPTIC PEER", instruction)
        self.assertIn("PEER 3 - EXAM PEER", instruction)

    # 5. End-to-End Service Call with Mocked LLM
    @patch("app.services.synthetic_peer_service.generate_grounded_content")
    def test_generate_synthetic_peers_passes_memory_to_llm(
        self, mock_generate_grounded
    ):
        mock_generate_grounded.return_value = (
            "PEER 1 - EXPLAINER PEER\n"
            "Pointers store addresses.\n\n"
            "PEER 2 - SKEPTIC PEER\n"
            "Do not confuse the address with the stored value.\n\n"
            "PEER 3 - EXAM PEER\n"
            "Remember syntax & and *."
        )

        study_context = "A pointer in C stores the memory address of another variable."
        result = generate_synthetic_peers(
            topic="C Pointers",
            student_prompt="Explain pointers",
            study_context=study_context,
            prior_learning_memory=self.sample_memory,
        )

        self.assertEqual(result["status"], "generated")
        self.assertEqual(result["topic"], "C Pointers")
        self.assertEqual(len(result["peer_roles"]), 3)

        # Verify mock received instruction with personalization and exact context
        mock_generate_grounded.assert_called_once()
        _, kwargs = mock_generate_grounded.call_args
        instruction_arg = kwargs.get("instruction", "")
        context_arg = kwargs.get("context", "")

        self.assertEqual(context_arg, study_context)
        self.assertIn("RELEVANT PREVIOUS TOPIC DETECTED", instruction_arg)
        self.assertIn("Previous misconception signal", instruction_arg)
        self.assertIn(
            "Pointers directly store value contents instead of memory addresses",
            instruction_arg,
        )

    # 6. API Route: User Profile Isolation
    @patch("app.api.synthetic_peer_api.get_student_profile")
    @patch("app.api.synthetic_peer_api.generate_synthetic_peers")
    def test_api_fetches_memory_for_authenticated_user_only(
        self, mock_generate_peers, mock_get_profile
    ):
        mock_profile = StudentProfile(
            student_id="student-test-uuid-456",
            learning_memory=self.sample_memory,
        )
        mock_get_profile.return_value = mock_profile
        mock_generate_peers.return_value = {
            "status": "generated",
            "topic": "C Pointers",
            "student_prompt": "Explain",
            "peer_roles": ["explainer", "skeptic", "exam_peer"],
            "classroom_discussion": "Mock discussion",
        }

        mock_db = MagicMock()
        request = SyntheticPeerRequest(
            topic="C Pointers",
            student_prompt="Explain",
            study_context="Pointers hold memory addresses.",
        )

        response = create_synthetic_peer_classroom(
            request=request,
            current_user={"id": "student-test-uuid-456", "access_token": "mock-token"},
            db=mock_db,
        )

        # Verify profile is queried using authenticated user's ID
        mock_get_profile.assert_called_once_with(mock_db, "student-test-uuid-456")

        # Verify memory from that authenticated user is passed into generation
        mock_generate_peers.assert_called_once_with(
            topic="C Pointers",
            student_prompt="Explain",
            study_context="Pointers hold memory addresses.",
            prior_learning_memory=self.sample_memory,
        )

        self.assertEqual(response.status, "generated")


if __name__ == "__main__":
    unittest.main()

