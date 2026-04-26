from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch
from transformers import Mistral3ForConditionalGeneration, FineGrainedFP8Config


quant_config = BitsAndBytesConfig(load_in_8bit=True)
model_name = '/workspace/Ministral-3-3B-Instruct-2512'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = Mistral3ForConditionalGeneration.from_pretrained(
    model_name,
    device_map="auto",
    quantization_config=FineGrainedFP8Config(dequantize=True)
)
input_text = 'Pourquoi le ciel est-il bleu ?'
inputs = tokenizer(input_text, return_tensors='pt').to('cuda')
outputs = model.generate(**inputs, max_new_tokens=50)
print('Réponse:', tokenizer.decode(outputs[0], skip_special_tokens=True))
