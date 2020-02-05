import operator
# Load your usual SpaCy model (one of SpaCy English models)
import spacy
nlp = spacy.load('en')

# load NeuralCoref and add it to the pipe of SpaCy's model
import neuralcoref
coref = neuralcoref.NeuralCoref(nlp.vocab, greedyness=0.8)
nlp.add_pipe(coref, name='neuralcoref')


def has_coref(text):
    #TODO: use NLTK word tagger (pronouns)
    pronouns = ['him', 'his', 'her', 'hers', 'it']
    # TODO: tokenize using tokenizer
    text = text.split()
    return any(word in text for word in pronouns)


def execute_resolver(text):
    #TODO: question mark issue
    doc = nlp(text)
    return doc


def get_coreferent_label(question_1, question_2, answer):
    scores = [-9999, -9999]
    labels = ['', '']

    doc_1 = execute_resolver(question_1 + ' ' + question_2)
    doc_2 = execute_resolver(answer + ' ' + question_2)

    if doc_1._.has_coref:
        for cluster in list(doc_1._.coref_scores.keys()):
            if str(cluster) in question_2:
                max_score = max(doc_1._.coref_scores[cluster].values())
                if max_score > scores[0]:
                    scores[0] = max_score
                    labels[0] = str(max(doc_1._.coref_scores[cluster], key=doc_1._.coref_scores[cluster].get))

    if doc_2._.has_coref:
        for cluster in list(doc_2._.coref_scores.keys()):
            if str(cluster) in question_2:
                max_score = max(doc_2._.coref_scores[cluster].values())
                if max_score > scores[1]:
                    scores[1] = max_score
                    labels[1] = str(max(doc_2._.coref_scores[cluster], key=doc_2._.coref_scores[cluster].get))

    max_index = scores.index(max(scores))

    if scores[max_index] > -9999:
        return {'score': scores[max_index], 'label': labels[max_index], 'index': max_index}
    else:
        return None

