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

        right_sentence = "This sentence is correct"
        wrong_sentence = "But this one is false"
        unclear_sentence = "This sentence here is neither"
        both_right_and_wrong_sentence = "That sentence is generally incorrect, though for the most part quite fine"

        assert classifier.get_class(right_sentence) == "right", \
            "The sentence containing \"correct\" was not classified as \"right\""
        assert classifier.get_class(wrong_sentence) == "wrong", \
            "The sentence containing \"false\" was not classified as \"wrong\""

        assert classifier.get_class(unclear_sentence) == FALLBACK_CLASS, \
            "The sentence containing no known keywords whatsoever was not classified as FALLBACK "
        assert classifier.get_class(both_right_and_wrong_sentence) == "right" \
               or classifier.get_class(both_right_and_wrong_sentence) == "wrong"

    def test_multiple_words_long_keywords(self):
        classes = {
            "greetings": {
                "keywords": ["greetings", "well met", "hello there", "welcome"]
            },
            "farewell": {
                "keywords": ["farewell", "see you later", "c u later", "see ya"]
            }
        }
        classifier = KeywordClassifier(classes, 0)

        greetings = "greetings everyone!"
        hello_there = "why hello there didn't expect to meet you out of all people"
        see_ya = "i gotta go home now see ya"
        c_u_later = "was nice talking to you c u later"
        fallback = "See you tomorrow"

        assert classifier.get_class(greetings) == "greetings"
        assert classifier.get_class(hello_there) == "greetings"
        assert classifier.get_class(see_ya) == "farewell"
        assert classifier.get_class(c_u_later) == "farewell"
        assert classifier.get_class(fallback) == "fallback"
