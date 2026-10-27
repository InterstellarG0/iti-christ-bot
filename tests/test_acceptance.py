"""Acceptance tests for Christ Bot v1.2.4, mapped to the handoff's 11 tests
plus dual-edition safeguards.

Run: python3 -m unittest discover -s tests -v
No network, no API key, standard library only.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import Session, load_corpus, respond  # noqa: E402


def fresh():
    return Session(load_corpus())


class TestAcceptance(unittest.TestCase):
    def test_01_first_question_listens_before_scripture(self):
        s = fresh()
        r = respond(s, "I have been carrying a lot of worry lately.")
        self.assertNotIn("Scripture", r["text"])
        self.assertIn("Question", r["text"])
        self.assertTrue("worry" in r["text"].lower() or "anxiety" in r["text"].lower()
                        or "uncertain" in r["text"].lower())

    def test_02_scripture_separated_from_interpretation(self):
        s = fresh()
        r = respond(s, "Show me John 3:16")
        self.assertIn("Scripture (Ethiopian", r["text"])
        self.assertIn("King James Version (parallel", r["text"])
        self.assertIn("For God so loved the world", r["text"])
        self.assertIn("Interpretation (not Scripture)", r["text"])
        # Scripture block must come before interpretation in the rendered text.
        self.assertLess(r["text"].index("Scripture"), r["text"].index("Interpretation"))

    def test_03_disagreement_acknowledged_without_shaming(self):
        s = fresh()
        respond(s, "Show me John 3:16")
        r = respond(s, "I disagree with that reading.")
        self.assertIn("Disagreement is welcome", r["text"])
        self.assertNotIn("spiritual failure", r["text"].split("Disagreement is welcome")[0])
        self.assertNotIn("deficient", r["text"])

    def test_04_forgiveness_preserves_boundaries(self):
        s = fresh()
        respond(s, "Hello, I want to talk.")
        r = respond(s, "I need to forgive someone but I do not want them back in my life.")
        self.assertIn("does not require reconciliation", r["text"])
        self.assertIn("continued contact", r["text"])

    def test_05_no_divine_claim(self):
        s = fresh()
        r = respond(s, "Are you Jesus?")
        self.assertIn("not God, Jesus", r["text"])
        self.assertIn("software", r["text"])
        r2 = respond(s, "Show me John 3:16")
        self.assertNotIn("I am God", r2["text"])
        self.assertNotIn("I am Jesus", r2["text"])

    def test_06_sacred_pause_is_optional_and_unpressured(self):
        s = fresh()
        r = respond(s, "Show me John 3:16")
        self.assertTrue(r["pause_offered"])
        self.assertIn("Continue the conversation", r["text"])
        self.assertIn("Take a moment to reflect or pray", r["text"])
        self.assertIn("Pause and return later", r["text"])
        self.assertNotIn("streak", r["text"].lower())
        self.assertNotIn("points", r["text"].lower())
        r2 = respond(s, "Pause and return later")
        self.assertIn("no pressure", r2["text"].lower())

    def test_07_crisis_redirect(self):
        s = fresh()
        r = respond(s, "I want to kill myself.")
        self.assertTrue(r["crisis"])
        self.assertIn("988", r["text"])
        self.assertIn("741741", r["text"])
        self.assertFalse(r["pause_offered"])
        self.assertNotIn("Scripture", r["text"])

    def test_08_privacy_matches_implementation(self):
        s = fresh()
        r = respond(s, "/privacy")
        self.assertIn("memory only", r["text"])
        self.assertIn("Nothing is written to a file", r["text"])
        self.assertIn("not yet an offline app", r["text"])

    def test_09_offline_described_honestly(self):
        # The privacy response and README must not claim full offline capability.
        s = fresh()
        r = respond(s, "/privacy")
        self.assertNotIn("fully offline", r["text"])
        self.assertIn("not yet", r["text"])

    def test_10_errors_corrected_not_defended(self):
        s = fresh()
        r = respond(s, "Show me John 99:99")
        self.assertIn("could not retrieve", r["text"])
        self.assertNotIn("For God so loved", r["text"])
        # No invented verse text for an unknown reference.
        self.assertNotIn("John 99:99", r["text"].split("could not retrieve")[0])

    def test_11_no_diagnosis_and_no_spiritual_failure_framing(self):
        s = fresh()
        r = respond(s, "I am depressed and anxious all the time.")
        self.assertNotIn("you have depression", r["text"].lower())
        self.assertNotIn("you are diagnosed", r["text"].lower())
        # If a care note appears, it must disclaim diagnosis.
        if "Care note" in r["text"]:
            self.assertIn("not a diagnosis", r["text"].lower())

    def test_12_user_supplied_verse_is_not_claimed_as_retrieved(self):
        s = fresh()
        r = respond(s, "Here is a verse: Be kind to one another.")
        self.assertIn("User-supplied text (not retrieved", r["text"])
        self.assertNotIn("Scripture (Ethiopian", r["text"])

    def test_13_no_exclusive_confidant(self):
        s = fresh()
        respond(s, "Hello.")
        r = respond(s, "You are my only friend.")
        self.assertIn("not a substitute for human community", r["text"])

    def test_14_second_turn_can_offer_scripture_after_listening(self):
        s = fresh()
        respond(s, "I have been carrying a lot of worry lately.")
        r = respond(s, "yes")
        self.assertIn("Scripture (Ethiopian", r["text"])
        self.assertIn("Interpretation (not Scripture)", r["text"])

    def test_15_ethiopian_foundation_is_first_kjv_is_parallel(self):
        s = fresh()
        r = respond(s, "Show me Genesis 1:1")
        self.assertIn("Scripture (Ethiopian", r["text"])
        self.assertIn("In the beginning, God created the heavens and the earth.", r["text"])
        self.assertIn("King James Version (parallel, not merged)", r["text"])
        self.assertIn("Canon: shared", r["text"])
        # Ethiopian text comes before the KJV parallel.
        self.assertLess(r["text"].index("Scripture (Ethiopian"), r["text"].index("King James Version"))

    def test_16_ethiopian_only_book_has_no_kjv_parallel(self):
        s = fresh()
        r = respond(s, "Show me Jubilees 1:1")
        self.assertIn("Canon: Ethiopian-only", r["text"])
        self.assertIn("No parallel in the 66-book KJV canon", r["text"])
        r2 = respond(s, "Show me Psalm 151:1")
        self.assertIn("Canon: deuterocanonical", r2["text"])
        self.assertIn("I was small among my brothers", r2["text"])

    def test_17_susanna_alias_maps_to_daniel_13(self):
        s = fresh()
        r = respond(s, "Show me Susanna 1:1")
        self.assertIn("A man lived in Babylon", r["text"])
        self.assertIn("Canon: deuterocanonical", r["text"])

    def test_18_edition_command_states_foundation(self):
        s = fresh()
        r = respond(s, "/edition")
        self.assertIn("Ethiopian Orthodox Bible", r["text"])
        self.assertIn("modern English compilation", r["text"])
        self.assertIn("not an ancient manuscript", r["text"])

    def test_19_topic_words_are_not_substring_matches(self):
        # Regression: "ai" as a substring matched "said", "faith", and
        # "again", so almost every sentence was misread as science.
        for msg in ("I said I am tired", "faith is hard", "again, I feel lost"):
            s = fresh()
            r = respond(s, msg)
            self.assertNotIn("increasingly capable machines", r["text"])
        s = fresh()
        r = respond(s, "I am thinking about AI")
        self.assertIn("increasingly capable machines", r["text"])

    def test_20_complaining_gets_its_own_passage_not_science(self):
        # Regression: "complaining" and "complaints" contain "ai", so the
        # old substring matcher read them as science and gave Genesis 1:1.
        s = fresh()
        r = respond(s, "I am tired of complaints")
        self.assertNotIn("increasingly capable machines", r["text"])
        self.assertIn("complaint", r["text"].lower())
        r2 = respond(s, "scripture and guidance on complaining")
        self.assertIn("Philippians 2:14", r2["text"])
        self.assertIn("without complaining", r2["text"])
        self.assertNotIn("In the beginning, God created", r2["text"])

    def test_21_verse_request_after_listening_gives_a_passage(self):
        # Regression: "show me a verse about this", "find a passage
        # please", and "to look at a retrieved passage together" all fell
        # through to the generic turn, which offered the same options again.
        s = fresh()
        respond(s, "I'm tired of being present and working everyday.")
        r = respond(s, "Show me a verse about this")
        self.assertIn("Psalm 23:1", r["text"])
        self.assertNotIn("What would be most useful right now", r["text"])
        s2 = fresh()
        respond(s2, "I'm tired of being present and working everyday.")
        r2 = respond(s2, "find a passage please")
        self.assertIn("Psalm 23:1", r2["text"])
        s3 = fresh()
        respond(s3, "I'm tired of being present and working everyday.")
        respond(s3, "What would be most useful right now?")
        r3 = respond(s3, "to look at a retrieved passage together")
        self.assertIn("Psalm 23:1", r3["text"])

    def test_22_lust_topic_and_no_stale_passage(self):
        # Regression: lust was not a topic, so "What about lust problems"
        # and "more about lust" gave the generic turn, and "find a
        # passage about lust" then silently reused the complaining passage.
        s = fresh()
        respond(s, "I need your help with the urge of complaining and people complaining around me")
        respond(s, "Show me a verse about this please")
        respond(s, "Take a moment to reflect or pray")
        r = respond(s, "What about lust problems")
        self.assertIn("lust", r["text"].lower())
        self.assertNotIn("What would be most useful right now", r["text"])
        r2 = respond(s, "find a passage about lust")
        self.assertIn("1 Corinthians 10:13", r2["text"])
        self.assertIn("No temptation has taken you", r2["text"])
        self.assertNotIn("Philippians 2:14", r2["text"])
        s2 = fresh()
        respond(s2, "I need your help with the urge of complaining")
        respond(s2, "Show me a verse about this please")
        r3 = respond(s2, "find a passage about courage")
        self.assertNotIn("Philippians 2:14", r3["text"])
        self.assertIn("do not have a retrieved passage specifically tagged for courage", r3["text"])

    def test_23_all_new_topics_give_a_passage(self):
        # v1.2.4: 25 ready topics plus 5 manual groups. Each sample is
        # chosen to match only that topic, so the expected passage is
        # the first tagged passage in corpus order for that topic.
        cases = [
            ("I feel anger rising", "Proverbs 15:1"),
            ("I need peace", "Psalm 23:1"),
            ("I struggle to trust", "Psalm 23:1"),
            ("I need wisdom", "Psalm 119:105"),
            ("I need patience", "Ecclesiastes 3:1"),
            ("I want humility", "Micah 6:8"),
            ("I want faith", "Matthew 22:37"),
            ("I want truth", "John 8:32"),
            ("I need community", "Proverbs 27:17"),
            ("I need friends", "Proverbs 27:17"),
            ("I need mercy", "Micah 6:8"),
            ("I need comfort", "Matthew 5:4"),
            ("I need discernment", "Psalm 119:105"),
            ("I want someone listening", "James 1:19"),
            ("I want character", "Galatians 5:22"),
            ("I need help", "Psalm 121:1"),
            ("I want freedom", "John 8:32"),
            ("I think about the future", "Jeremiah 29:11"),
            ("I want a mission", "Matthew 28:19"),
            ("I want dignity", "Genesis 1:27"),
            ("I need solitude", "Psalm 46:10"),
            ("I think about time", "Ecclesiastes 3:1"),
            ("I study astronomy", "Psalm 19:1"),
            ("I wonder about origins", "Genesis 1:1"),
            ("I want abundant life", "John 10:10"),
            ("I feel guilt", "1 John 1:9"),
            ("I feel envy", "Proverbs 14:30"),
            ("I feel pride", "James 4:6"),
            ("I have an addiction", "Romans 7:15"),
            ("Money is stressing me", "Matthew 6:25"),
        ]
        for msg, expected in cases:
            with self.subTest(msg=msg):
                s = fresh()
                respond(s, "Hello")
                r = respond(s, msg)
                self.assertIn("Scripture (Ethiopian", r["text"])
                self.assertIn(expected, r["text"])
                self.assertIn("Interpretation (not Scripture)", r["text"])

    def test_24_multi_topic_specific_wins_over_generic(self):
        # Help and work are generic and placed last, so a specific
        # concern in the same sentence wins.
        s = fresh()
        respond(s, "Hello")
        r = respond(s, "I need your help with lust")
        self.assertIn("1 Corinthians 10:13", r["text"])
        s2 = fresh()
        respond(s2, "Hello")
        r2 = respond(s2, "I am anxious about money")
        self.assertIn("Matthew 6:33", r2["text"])
        self.assertNotIn("Matthew 6:25", r2["text"])
        s3 = fresh()
        respond(s3, "Hello")
        r3 = respond(s3, "I need your help with anger")
        self.assertIn("Proverbs 15:1", r3["text"])

    def test_25_context_change_replaces_old_topic(self):
        s = fresh()
        respond(s, "I am tired of being present and working everyday.")
        respond(s, "Show me a verse about this")
        r = respond(s, "Money is stressing me")
        self.assertIn("Matthew 6:25", r["text"])
        self.assertNotIn("Psalm 23:1", r["text"])
        r2 = respond(s, "I feel guilt")
        self.assertIn("1 John 1:9", r2["text"])
        self.assertNotIn("Matthew 6:25", r2["text"])

    def test_26_unknown_topic_does_not_reuse_old_passage(self):
        s = fresh()
        respond(s, "I need your help with complaining")
        respond(s, "Show me a verse about this please")
        r = respond(s, "find a passage about dinosaurs")
        self.assertNotIn("Philippians 2:14", r["text"])
        self.assertIn("do not have a retrieved passage specifically tagged for dinosaurs", r["text"])

    def test_27_passage_request_after_new_topic(self):
        s = fresh()
        respond(s, "I feel guilt")
        r = respond(s, "Show me a verse about this please")
        self.assertIn("1 John 1:9", r["text"])
        self.assertNotIn("What would be most useful right now", r["text"])

    def test_28_pause_and_crisis_hold_after_new_topics(self):
        s = fresh()
        respond(s, "I feel guilt")
        r = respond(s, "Show me a verse about this please")
        self.assertTrue(r["pause_offered"])
        self.assertIn("Continue the conversation", r["text"])
        self.assertIn("Take a moment to reflect or pray", r["text"])
        self.assertIn("Pause and return later", r["text"])
        r2 = respond(s, "I am anxious and I want to kill myself.")
        self.assertTrue(r2["crisis"])
        self.assertIn("988", r2["text"])
        self.assertFalse(r2["pause_offered"])
        self.assertNotIn("Scripture", r2["text"])


if __name__ == "__main__":
    unittest.main()
