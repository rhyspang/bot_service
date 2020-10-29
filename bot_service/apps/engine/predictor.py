import random

import Levenshtein


class Predictor(object):

    def __init__(self, train_data):
        """
        [
            {
                id: ''
                question: "",
                answers: [],
                similar_questions": []
            }
        ]
        """
        self.train_data = train_data
        self.id_map = {item['id']: item['answers'] for item in train_data}

    def predict(self, text, mode=1):
        """
        mode: 1 for edit distance
              2 for key word
        """
        if mode == 1:
            scores = []
            for item in self.train_data:
                max_score = Levenshtein.ratio(text, item['question'])
                for question in item['similar_question']:
                    cur_score = Levenshtein.ratio(question, text)
                    if cur_score > max_score:
                        max_score = cur_score
                scores.append((item['id'], max_score))
            scores.sort(key=lambda x: x[1], reverse=True)
            return [
                {'answer': random.choice(self.id_map[item[0]]),
                 'id': item[0], 'score': item[1]}
                for item in scores[:1]
            ]
        elif mode == 2:
            for item in self.train_data:
                for question in item['question']:
                    if text in question:
                        return {
                            'answer': random.choice(self.id_map[item['id']]),
                            'id': item['id'],
                            'score': 1
                        }
        return []
