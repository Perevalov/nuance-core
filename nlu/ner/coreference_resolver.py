import operator
# Load your usual SpaCy model (one of SpaCy English models)
import spacy
nlp = spacy.load('en')

# load NeuralCoref and add it to the pipe of SpaCy's model
import neuralcoref
coref = neuralcoref.NeuralCoref(nlp.vocab, greedyness=0.8)
nlp.add_pipe(coref, name='neuralcoref')


def has_coref(text: str) -> bool:
    """returns true only if text is likely to contain a coreference"""
    # TODO: use NLTK word tagger (pronouns)
    pronouns = ['him', 'his', 'her', 'hers', 'it']
    # TODO: tokenize using tokenizer
    text = text.split()
    return any(word in text for word in pronouns)


def execute_resolver(text: str):
    # TODO: question mark issue
    doc = nlp(text)
    return doc


def get_coreferent_label(question_1: str, question_2: str, answer: str) -> dict:
    """Returns the label of the strongest coreference between the input parameter texts.

    given a coreference between either question_1 and answer or question_2 and answer exists,
    this method will find out which of these two options is more likely
    and return the  entity referenced by the corresponding coreference in text form.

    :param question_1:
    :param question_2:
    :param answer: The answer for question_1
    :return:
    """
    scores = [-9999, -9999]
    labels = ['', '']

    doc_1 = execute_resolver(question_1 + ' ' + question_2)
    doc_2 = execute_resolver(answer + ' ' + question_2)

    if doc_1._.has_coref:
        scores[0], labels[0] = extract_coreferences(doc_1, question_2)

    if doc_2._.has_coref:
        scores[1], labels[1] = extract_coreferences(doc_2, question_2)
        """for cluster in list(doc_2._.coref_scores.keys()):   # do for each eventual coreference that has been detected
                if str(cluster) in question_2:
                max_score = max(doc_2._.coref_scores[cluster].values())
                if max_score > scores[1]:
                    scores[1] = max_score
                    labels[1] = str(max(doc_2._.coref_scores[cluster], key=doc_2._.coref_scores[cluster].get))"""

    max_index = scores.index(max(scores))

    if scores[max_index] > -9999:
        return {'score': scores[max_index], 'label': labels[max_index], 'index': max_index}
    else:
        return None


def extract_coreferences(doc, question: str, min_score=-9999) -> (dict, dict):
    """Puts all the coreferences from a given question into a readable dictionary

    :param doc:
    :param question:
    :param min_score:
    :return:
    """
    score = min_score
    for cluster in list(doc._.coref_scores.keys()):  # do for each eventual coreference that has been detected
        if str(cluster) in question:
            max_score = max(doc._.coref_scores[cluster].values())
            if max_score > score[0]:
                score = max_score
                label = str(max(doc._.coref_scores[cluster], key=doc._.coref_scores[cluster].get))
    return score, label
