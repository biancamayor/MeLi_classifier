import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class SentimentClassifier():
    #esse  model_path é um modelo de bertimbau finetunado para análise de sentimento em português.
    def __init__(self, model_path="lipaoMai/BERT-sentiment-analysis-portuguese"):
        #Carrega o tokenizer adequado para o modelo BERTimbau. Tokenizer é responsável por converter o texto em números que o modelo pode entender.
        #Ele transforma frases em IDs numéricos que representam palavras ou subpalavras.
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        #Carrega o modelo pré-treinado.
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        #Coloca o modelo em modo de avaliação, desabilitando coisas que só fazem sentido em treinamento (como dropout).
        self.model.eval()  

        #O índice do rótulo (0, 1, 2) corresponde ao índice na saída do modelo.
        self.labels = ["NEGATIVE", "NEUTRAL", "POSITIVE"]

    def predict(self, text, rating, temperature=0.7):
        #Retorna algo como: {'input_ids': tensor([[101, 234, 456, 789, 102]]),'attention_mask': tensor([[1,1,1,1,1]])}
        inputs = self.tokenizer(text, return_tensors="pt")

        #desativa o cálculo de gradientes (economiza memória e processamento, pois não vamos treinar o modelo).
        with torch.no_grad():
            outputs = self.model(**inputs) #passa os tokens pelo modelo e retorna a saída.

            #O Hugging Face retorna um objeto chamado SequenceClassifierOutput. Ele funciona como um pacote de informações que o modelo entrega depois de processar o texto.
            #Esse objeto pode conter várias coisas (dependendo de como o modelo foi treinado), mas o mais importante é:
            #logits → os “valores crus” de saída do modelo, antes de serem convertidos em probabilidades. Esses números não são probabilidades ainda. Eles podem ser negativos, positivos, grandes, pequenos…
            #São apenas “pontuações internas” do modelo.

            logits = outputs.logits / temperature  

            #Eleva todos os números exponencialmente.Normaliza dividindo pela soma total. Resultado → valores entre 0 e 1, que somam 1 (probabilidades).
            logits_to_prob = F.softmax(logits, dim=-1)
            
            # .argmax: pega o índice da maior probabilidade.
            # .item(): converte de tensor para número Python.
            prob_index = torch.argmax(logits_to_prob, dim=1).item()
            label = self.labels[prob_index]


        # Força neutros para POSITIVE
        if rating >= 4:
            final_label = "POSITIVE"
            final_score = 90.0
        elif rating <= 2:
            final_label = "NEGATIVE"
            final_score = 90.0
        else:
            # usa o modelo só quando rating médio
            pos_score = logits_to_prob[0][self.labels.index("POSITIVE")].item()
            neg_score = logits_to_prob[0][self.labels.index("NEGATIVE")].item()
            if pos_score >= neg_score:
                final_label = "POSITIVE"
                final_score = pos_score * 100
            else:
                final_label = "NEGATIVE"
                final_score = neg_score * 100
                
        return {
            "label": final_label,
            "score": final_score
            }

