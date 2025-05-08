import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from logzero import logger
from transformers import pipeline
import textstat
import language_tool_python
from time import time

class Evaluator:
    def __init__(self, ):
        self.use_gpu = torch.cuda.is_available()
        logger.debug('Use GPU: %r' % self.use_gpu)
        # load nli model
        logger.debug('Loading models and tools...')
        self.model_name = "facebook/bart-large-mnli"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.device = "cuda" if self.use_gpu else "cpu"
        self.model.to(self.device)
        try:
            self.tool = language_tool_python.LanguageTool('en-GB')
        except Exception as e:
            logger.error(f"Falling back to public API due to: {e}")
            self.tool = language_tool_python.LanguageToolPublicAPI('en-GB')
        logger.debug('Ready.')

    def get_nli_score_pipeline(self, fact, text):
        """"""
        # Load an NLI pipeline (for textual entailment)
        nli_model = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")        
        # Split the text into sentences (or use paragraphs, depending on the granularity you want)
        text_sentences = [s.strip() for s in text.split('.') if s.strip()] # text.split('.')
        best_result = 0
        # Perform zero-shot classification (NLI) to see if the text entails the fact
        for sentence in text_sentences:
            if sentence == '':
                continue
            result = nli_model(sentence, candidate_labels=[fact])
            best_result = max(best_result, result['scores'][0])        
        return best_result

    def get_nli_score(self, fact, text):
        if self.use_gpu: self.model.to(torch.float16)
        # Split the text into sentences (or use paragraphs, depending on the granularity you want)
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        # Batch processing
        inputs = self.tokenizer(
            sentences,  # List of sentences
            [fact] * len(sentences),  # Duplicate fact for each sentence
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,  # Prevent OOM errors
        ).to(self.model.device)  # Automatically uses GPU if available        
        # Single forward pass for all sentences
        with torch.no_grad():
            logits = self.model(**inputs).logits        
        # Extract entailment scores (sigmoid or softmax)
        entailment_scores = torch.sigmoid(logits[:, 2]).cpu().numpy()
        if self.use_gpu:
            self.model = self.model.float()  # Reset to FP32
        # Return max score (or optionally the best sentence + score)
        return float(entailment_scores.max())
    
    def get_full_nli_score(self, fact, text):
        if self.use_gpu: self.model.to(torch.float16)
        inputs = self.tokenizer(
            text,  # premise
            fact,  # hypothesis
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,  # Prevent OOM errors
        ).to(self.model.device)  # Automatically uses GPU if available        
        # Single forward pass for all sentences
        with torch.no_grad():
            logits = self.model(**inputs).logits        
        # Extract entailment scores (sigmoid or softmax)
        entailment_scores = torch.sigmoid(logits[:, 2]).cpu().numpy()
        if self.use_gpu:
            self.model = self.model.float()  # Reset to FP32
        # Return max score (or optionally the best sentence + score)
        return float(entailment_scores.max())

    def evaluate_answer_logic_similarity_outcome_granted(self, text_answer, explanations):
        """Evaluates logic similarity between an answer and a set of explanations.
        Returns coverage (best score per explanation pair) and completeness (average score)."""
        facts = ""
        if not explanations:
            return 0.0, 0.0
        #OPPOSITE_SCORE_PENALTY = 0.2  # Tune as needed
        nb_logic_exp = 0
        sum_scores = 0
        sum_bests = 0
        for (employ_proh, define_proh), list_permissions in explanations.items():        
            nb_logic_exp += len(list_permissions)
            best_score = 0
            for employ_perm, define_perm in list_permissions:
                role_fact = f"the role {employ_perm.employesRole} in {employ_perm.employesEmployer} is preferred over the role {employ_proh.employesRole} in {employ_proh.employesEmployer}"
                facts += ". " + role_fact
                role_score = self.get_full_nli_score(role_fact, text_answer) # self.get_nli_score(role_fact, text_answer)
                #role_opposite_fact = f"{employ_perm.employesEmployee} playing the role {employ_perm.employesRole} in {employ_perm.employesEmployer} is not preferred over {employ_proh.employesEmployee} playing the role {employ_proh.employesRole} in {employ_proh.employesEmployer}"
                #role_opposite_score = self.get_nli_score(role_opposite_fact, text_answer)
                #role_score = role_score - OPPOSITE_SCORE_PENALTY * role_opposite_score
                context_fact = f"the definition of the context {define_perm.definesContext} in {define_perm.definesOrganisation} is preferred over the definition of the context {define_proh.definesContext} in {define_proh.definesOrganisation}"
                facts += ". " + context_fact
                context_score =  self.get_full_nli_score(context_fact, text_answer) # self.get_nli_score(context_fact, text_answer)
                #context_opposite_fact = f"the definition of the context {define_perm.definesContext} in {define_perm.definesOrganisation} is not preferred over the definition of the context {define_proh.definesContext} in {define_proh.definesOrganisation}"
                #context_opposite_score = self.get_nli_score(context_opposite_fact, text_answer)
                #context_score = context_score  - OPPOSITE_SCORE_PENALTY * context_opposite_score
                # average score of role and context preference relations (the score of a pair or tuple from an explanation)
                final_score = (role_score + context_score) / 2
                sum_scores += final_score
                # best_score looks for the best described permission's support that dominates the current prohibition's support
                best_score = max(best_score, final_score)
            sum_bests += best_score
        # coverage averages the best tuples' scores 
        coverage = sum_bests / len(explanations)
        completness = sum_scores / nb_logic_exp
        return coverage, completness, facts

    def evaluate_answer_logic_similarity_outcome_denied(self, text_answer, explanations):
        """Evaluates logic similarity between an answer and a set of explanations.
        Returns coverage (best score per explanation pair) and completeness (average score)."""
        facts = ""
        sum_scores = 0
        best_score = 0
        for (employ_proh, define_proh), list_permissions in explanations.items():    
            sum_one_scores = 0
            for employ_perm, define_perm in list_permissions:
                role_fact = f"the role {employ_perm.employesRole} in {employ_perm.employesEmployer} is not preferred over the role {employ_proh.employesRole} in {employ_proh.employesEmployer}"
                facts += ". " + role_fact
                role_score = self.get_full_nli_score(role_fact, text_answer) # self.get_nli_score(role_fact, text_answer)
                context_fact = f"the definition of the context {define_perm.definesContext} in {define_perm.definesOrganisation} is not preferred over the definition of the context {define_proh.definesContext} in {define_proh.definesOrganisation}"
                facts += ". " + context_fact
                context_score = self.get_full_nli_score(context_fact, text_answer) # self.get_nli_score(context_fact, text_answer)
                final_score = max(role_score,context_score)
                sum_one_scores += final_score
            # average score of current explanation
            one_exp_score = sum_one_scores / len(list_permissions)
            # best explanation score
            best_score = max(best_score, one_exp_score)
            sum_scores += one_exp_score
        # best explanation score
        coverage = best_score
        # average score of all explanations
        completness = sum_scores / len(explanations)
        return coverage, completness, facts

    def evaluate_grammaticality(self, text):
        matches = self.tool.check(text)
        num_errors = len(matches)        
        num_words = len(text.split())        
        if num_words == 0:
            return 1.0  # If there are no words, return the highest score        
        score = 1 - (num_errors / num_words)
        return max(score, 0)  # Clamp the score to a minimum of 0

    def evaluate_readability(self, text):
        readability_scores = {}
        # Flesch Reading Ease
        readability_scores["flesch_reading_ease"] = textstat.flesch_reading_ease(text)
        # Flesch-Kincaid Grade Level
        readability_scores["flesch_kincaid_grade"] = textstat.flesch_kincaid_grade(text)
        # Gunning Fog Index
        readability_scores["gunning_fog"] = textstat.gunning_fog(text)
        # SMOG Index
        readability_scores["smog_index"] = textstat.smog_index(text)
        # Coleman-Liau Index
        readability_scores["coleman_liau_index"] = textstat.coleman_liau_index(text)
        # Automated Readability Index
        readability_scores["ari"] = textstat.automated_readability_index(text)
        return readability_scores

    def get_hallucination_score(self, text, facts):
        """"""
        if self.use_gpu: self.model.to(torch.float16)
        inputs = self.tokenizer(facts,text,return_tensors="pt",padding=True,truncation=True,max_length=512,).to(self.model.device)  # Automatically uses GPU if available
        with torch.no_grad():
            logits = self.model(**inputs).logits
        entailment_score = torch.sigmoid(logits[:, 0]).cpu().numpy()[0]
        if self.use_gpu:
            self.model = self.model.float()  # Reset to FP32
        # Return max score (or optionally the best sentence + score)
        return float(entailment_score)

    def run_evaluations(self, access, answer, explanations):
        metrics = {}
        facts = ""
        # TODO : check supports (mainly permission and prohibition elements).
        # TODO : need more efficient evaluations, consider constructing tuples of (premise,hypothesis) to feed everything as a batch then get scores back
        # coverage: a score for identifying at least one explanation per support of prohibition (best score per explanation pair)
        # completness: average score of identifying all explanations (average explanation score)
        logger.debug('Running evaluations...')
        start_time = time() 
        if access.outcome and len(explanations) != 0:
            metrics["coverage"], metrics["completness"], ret_facts = self.evaluate_answer_logic_similarity_outcome_granted(answer, explanations)
            facts += ". " + ret_facts
        elif access.outcome and len(explanations) == 0:
            no_prohibition_support_fact = "There is no support for a prohibition."
            facts += ". " + no_prohibition_support_fact
            metrics["coverage"] = self.get_full_nli_score(no_prohibition_support_fact,answer)
            metrics["completness"] = metrics["coverage"]
        elif not access.outcome and len(explanations) != 0 and len(access.permission_supports) != 0:
            metrics["coverage"], metrics["completness"], ret_facts = self.evaluate_answer_logic_similarity_outcome_denied(answer, explanations)
            facts += ". " + ret_facts
        elif not access.outcome and len(explanations) != 0 and len(access.permission_supports) == 0:
            no_permission_support_fact = "There is no support for a permission."
            facts += ". " + no_permission_support_fact
            metrics["coverage"] = self.get_full_nli_score(no_permission_support_fact,answer)
            metrics["completness"] = metrics["coverage"]                        
        elif not access.outcome and len(explanations) == 0:
            no_supports_fact = "There is no support for a permission and there is no support for a prohibition."
            facts += ". " + no_supports_fact
            metrics["coverage"] = self.get_full_nli_score(no_supports_fact,answer) 
            metrics["completness"] = metrics["coverage"]
        logger.debug('Done coverage and completeness.')
        # corectness: a score for identifying the right decision outcome
        granted_fact = f"The access of {access.subject} with {access.action} to {access.obj} was granted"
        granted_score = self.get_full_nli_score(granted_fact,answer)
        denied_fact = f"The access of {access.subject} with {access.action} to {access.obj} was denied"
        denied_score = self.get_full_nli_score(denied_fact,answer)
        metrics["correctness"] = granted_score if access.outcome else denied_score # (granted_score - 0.2 * denied_score) if access.outcome else (denied_score - 0.2 * granted_score)
        logger.debug('Done correctness.')
        facts += ". " + granted_fact if access.outcome else ". " + denied_fact
        # clarity: a score for explaining how dominance works
        acceptance_rule = """An access is granted if and only if, for each support of a prohibition, there exists a corresponding support for a permission where the permission's support dominates the prohibition's."""
        #Dominance means that: each element of the support of the permission is strictly preferred to at least one element of the support of the prohibition.
        facts += ". " + acceptance_rule
        metrics["clarity"] = self.get_full_nli_score(acceptance_rule, answer)
        logger.debug('Done clarity.')
        # hallucination: scoring useless text by concatenating all facts as a premise and the generated explanation as a hypothesis and get the explanation's entailment score from them
        metrics["hallucination"] = self.get_hallucination_score(answer, facts)
        logger.debug('Done hallucination.')
        # Grammar score
        metrics["grammar_score"] = self.evaluate_grammaticality(answer)
        logger.debug('Done grammar score.')
        # readability scores:
        readability_scores = self.evaluate_readability(answer)
        logger.debug('Done readability.')
        # precision: a score for correctly identified relations / all mentioned relations
        # structure: a score for how the explanation is ordered (- Ensure you follow the structure of: Decision Rule -> Outcome -> Relations and Preferences. for each s_proh to a dominant s_perm -> outcome) 
        # terminilogy: a score for using the right terminology        
        for cle, valeur in readability_scores.items():
            metrics[cle] = valeur
        logger.debug(f'Evaluation scores computed in {time()-start_time:.2f} seconds.')
        return metrics # coverage, completness, correctness, clarity, grammar_score, readability_scores