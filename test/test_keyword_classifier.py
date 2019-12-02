from resources.constants import FALLBACK_CLASS
from nlu.classifiers.KeywordClassifier import KeywordClassifier


class TestKeywordClassifier:
    def test_two_classes(self):
        classes = {
            "right": {
                "keywords": ["correct", "alright", "fine"]
            },
            "wrong": {
                "keywords": ["incorrect", "false"]
            }
        }
        classifier = KeywordClassifier(classes, 0)

        right_sentence = "This sentence is correct."
        wrong_sentence = "But this one is false."
        unclear_sentence = "This sentence here is neither."
        both_right_and_wrong_sentence = "That sentence is generally incorrect, though for the most part quite fine."

        assert classifier.get_class(right_sentence) == "right"
        assert classifier.get_class(wrong_sentence) == "wrong"
        assert classifier.get_class(unclear_sentence) == FALLBACK_CLASS
        assert both_right_and_wrong_sentence == "right" or both_right_and_wrong_sentence == "wrong"
