from fuzzywuzzy import fuzz


class Classifier:
    def __init__(self, ):
        pass

    def predict(self, text):
        pass


def tell_me_more_classifier(question_text):
    """
    Rule based method for TELL_ME_MORE intent classification
    :param question_text: user's text
    :return: boolean value
    """
    return "tell me more" in question_text.lower()


def what_i_see_classifier(question_text):
    """
    Rule based method for WHAT_I_SEE intent classification
    :param questions_text: user's text
    :return: boolean value
    """
    key_phrases = ["what i see around me",
                    "what is this building",
                    "what is around me",
                    "what is this in front of me",
                   "what is this",
                   "what i see"]

    for phrase in key_phrases:
        if fuzz.ratio(phrase, question_text.lower()) > 80:
            return True
    return False

