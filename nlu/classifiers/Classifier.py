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
