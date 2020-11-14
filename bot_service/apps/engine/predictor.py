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

    def _predict_levenshtein(self, text):
        scores = []
        for item in self.train_data:
            max_score = Levenshtein.ratio(text, item['question'])
            for question in item['similar_question']:
                cur_score = Levenshtein.ratio(question, text)
                if cur_score > max_score:
                    max_score = cur_score
            scores.append((item['id'], max_score))
        return scores

    def _predict_keyword(self, text):
        scores = []
        for item in self.train_data:
            hit = False
            for question in [item['question']] + item['similar_question']:
                if question in text:
                    hit = True
                    break
            scores.append((item['id'], int(hit)))
        return scores

    def predict(self, text, mode=1):
        """
        mode: 1 for edit distance
              2 for key word
        """
        if mode == 1:
            scores = self._predict_levenshtein(text)
            scores.sort(key=lambda x: x[1], reverse=True)
            return self.generate_outputs(scores), scores[0][1] >= 0.7
        elif mode == 2:
            scores = self._predict_keyword(text)
            scores.sort(key=lambda x: x[1], reverse=True)
            return self.generate_outputs(scores), scores[0][1] == 1
        elif mode == 3:
            ed_scores = self._predict_levenshtein(text)
            match_scores = self._predict_keyword(text)
            fusion_scores = [
                (qid, ed_score, match_score)
                for ((qid, ed_score), (_, match_score)) in zip(ed_scores, match_scores)]
            fusion_scores.sort(key=lambda x: (x[2], x[1]), reverse=True)
            return (self.generate_outputs(fusion_scores, score_index=2),
                    self.fusion_should_response(fusion_scores))
        return []

    def generate_outputs(self, sorted_scores, score_index=1, limit=1):
        return [
            {
                'answer': random.choice(self.id_map[item[0]]),
                'id': item[0],
                'score': item[score_index]
            }
            for item in sorted_scores[:limit]
        ]

    def fusion_should_response(self, sorted_scores):
        return sorted_scores[0][2] == 1 or sorted_scores[0][1] >= 0.7
