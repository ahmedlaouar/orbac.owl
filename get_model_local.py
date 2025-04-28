from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import os
from huggingface_hub import notebook_login

#notebook_login()

# Define the model name and local directory
model_name = "meta-llama/Llama-3.2-3B" # "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B" # "google/gemma-2-2b" # "meta-llama/Llama-3.2-3B-Instruct" # "google/gemma-2-2b-it" # "distilbert/distilgpt2" 
# "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B" #  
# "EleutherAI/llemma_7b"
local_model_dir = "./local_models/Llama-3.2-3B" # "local_models/DeepSeek-R1-Distill-Llama-8B" # 

# Create the local directory if it doesn't exist
os.makedirs(local_model_dir, exist_ok=True)

# Download and cache the model and tokenizer
print("Downloading model and tokenizer...")
model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=local_model_dir)
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=local_model_dir)

# Save the model and tokenizer locally for future use
print("Saving model and tokenizer locally...")
# Save the model with error handling
try:
    model.save_pretrained(local_model_dir)
    tokenizer.save_pretrained(local_model_dir)
    print("Model saved successfully!")
except Exception as e:
    print(f"Failed to save model: {e}")
#
print(f"Model and tokenizer have been saved to {local_model_dir}")


# Ensure pad_token_id is set to eos_token_id (if required)
#model.config.pad_token_id = model.config.eos_token_id

"""
model = AutoModelForCausalLM.from_pretrained(local_model_dir)
tokenizer = AutoTokenizer.from_pretrained(local_model_dir)

# Example prompt to test the model
prompt = "1. **Overall Logic:** Explain the condition under which access is granted. An access is granted if and only if, for each support of a prohibition, there exists a corresponding support for a permission where the permission's support dominates the prohibition's. Dominance means that: each element of the support of the permission is strictly preferred to at least one element of the support of the prohibition. Here are the different elements which compose the decision: 2. **Supports of Permission:** List of the elements that compose the permission support: (support 1): The organization Institute3 grants the role researcher the Permission to perform the activity validate on the view secondment_agreement if the context management holds, and The organisation Institute3 employes Quinn_Thomas in the role researcher,  and The organisation Institute3 considers sign as a validate activity,  and The organisation Institute3 uses report6 in the view secondment_agreement,  and The context management holds between Quinn_Thomas, sign, and report6 in the organisation Institute3, .(support 2): The organization Institute2 grants the role team_leader the Permission to perform the activity validate on the view administration if the context management holds, and The organisation Institute2 employes Quinn_Thomas in the role team_leader,  and The organisation Institute2 considers sign as a validate activity,  and The organisation Institute2 uses report6 in the view administration,  and The context management holds between Quinn_Thomas, sign, and report6 in the organisation Institute2, .3. **Supports of Prohibition:** List of the elements composing the prohibition support: (support 1): The organization University1 grants the role PhD_student the Prohibition to perform the activity validate on the view secondment_report if the context default holds, and The organisation University1 employes Quinn_Thomas in the role PhD_student,  and The organisation University1 considers sign as a validate activity,  and The organisation University1 uses report6 in the view secondment_report,  and The context default holds between Quinn_Thomas, sign, and report6 in the organisation University1, .(support 2): The organization Institute3 grants the role staff_member the Prohibition to perform the activity validate on the view WP2 if the context default holds, and The organisation Institute3 employes Quinn_Thomas in the role staff_member,  and The organisation Institute3 considers sign as a validate activity,  and The organisation Institute3 uses report6 in the view WP2,  and The context default holds between Quinn_Thomas, sign, and report6 in the organisation Institute3, .(support 3): The organization Institute1 grants the role associate_professor the Prohibition to perform the activity validate on the view WP4 if the context default holds, and The organisation Institute1 employes Quinn_Thomas in the role associate_professor,  and The organisation Institute1 considers sign as a validate activity,  and The organisation Institute1 uses report6 in the view WP4,  and The context default holds between Quinn_Thomas, sign, and report6 in the organisation Institute1, .4. **Preferences Between the Elements:**The relation ``The organisation Institute3 employes Quinn_Thomas in the role researcher, `` is preferred to ``The organisation University1 employes Quinn_Thomas in the role PhD_student, `` because: researcher is preferred to PhD_student.The relation ``The organisation Institute3 employes Quinn_Thomas in the role researcher, `` is preferred to ``The organisation Institute3 employes Quinn_Thomas in the role staff_member, `` because: researcher is preferred to staff_member.The relation ``The organisation Institute3 employes Quinn_Thomas in the role researcher, `` is preferred to ``The organisation Institute1 employes Quinn_Thomas in the role associate_professor, `` because: researcher is preferred to associate_professor.The relation ``The organisation Institute2 employes Quinn_Thomas in the role team_leader, `` is preferred to ``The organisation University1 employes Quinn_Thomas in the role PhD_student, `` because: team_leader is preferred to PhD_student.The relation ``The organisation Institute2 employes Quinn_Thomas in the role team_leader, `` is preferred to ``The organisation Institute3 employes Quinn_Thomas in the role staff_member, `` because: team_leader is preferred to staff_member.The relation ``The organisation Institute2 employes Quinn_Thomas in the role team_leader, `` is preferred to ``The organisation Institute1 employes Quinn_Thomas in the role associate_professor, `` because: team_leader is preferred to associate_professor.The relation ``The context management holds between Quinn_Thomas, sign, and report6 in the organisation Institute3, `` is preferred to ``The context default holds between Quinn_Thomas, sign, and report6 in the organisation University1, `` because: management is preferred to default.The relation ``The context management holds between Quinn_Thomas, sign, and report6 in the organisation Institute3, `` is preferred to ``The context default holds between Quinn_Thomas, sign, and report6 in the organisation Institute3, `` because: management is preferred to default.The relation ``The context management holds between Quinn_Thomas, sign, and report6 in the organisation Institute3, `` is preferred to ``The context default holds between Quinn_Thomas, sign, and report6 in the organisation Institute1, `` because: management is preferred to default.The relation ``The context management holds between Quinn_Thomas, sign, and report6 in the organisation Institute2, `` is preferred to ``The context default holds between Quinn_Thomas, sign, and report6 in the organisation University1, `` because: management is preferred to default.The relation ``The context management holds between Quinn_Thomas, sign, and report6 in the organisation Institute2, `` is preferred to ``The context default holds between Quinn_Thomas, sign, and report6 in the organisation Institute3, `` because: management is preferred to default.The relation ``The context management holds between Quinn_Thomas, sign, and report6 in the organisation Institute2, `` is preferred to ``The context default holds between Quinn_Thomas, sign, and report6 in the organisation Institute1, `` because: management is preferred to default.**The Decision:** The outcome of the logical inference is that: the permission for Quinn_Thomas to perform sign on report6 is granted.**Request for Explanation:** Using the provided logic, supports, and preferences, please explain why the decision was made to grant or deny access in this specific case."
prompt = "1. **Overall Logic:** Explain the condition under which access is granted. An access is granted if and only if, for each support of a prohibition, there exists a corresponding support for a permission where the permission's support dominates the prohibition's. Dominance means that: each element of the support of the permission is strictly preferred to at least one element of the support of the prohibition. Here are the different elements which compose the decision: 2. **Supports of Permission:** List of the elements that compose the permission support: (support 1): The organization university1 grants the role secondee the Permission to perform the activity modify on the view secondment_reports if the context secondment holds, and The organisation university1 employes Bob in the role secondee,  and The organisation university1 considers edit as a modify activity,  and The organisation university1 uses report1 in the view secondment_reports,  and The context secondment holds between Bob, edit, and report1 in the organisation university1, .3. **Supports of Prohibition:** List of the elements composing the prohibition support: (support 1): The organization consortium grants the role staff_member the Prohibition to perform the activity modify on the view secondment_reports if the context default holds, and The organisation consortium employes Bob in the role staff_member,  and The organisation consortium considers edit as a modify activity,  and The organisation consortium uses report1 in the view secondment_reports,  and The context default holds between Bob, edit, and report1 in the organisation consortium, .4. **Preferences Between the Elements:**The relation ``The organisation university1 employes Bob in the role secondee, `` is preferred to ``The organisation consortium employes Bob in the role staff_member, `` because: secondee is preferred to staff_member.The relation ``The context secondment holds between Bob, edit, and report1 in the organisation university1, `` is preferred to ``The context default holds between Bob, edit, and report1 in the organisation consortium, `` because: secondment is preferred to default.**The Decision:** The outcome of the logical inference is that: the permission for Bob to perform edit on report1 is granted.**Request for Explanation:** Using the provided logic, supports, and preferences, please explain why the decision was made to grant or deny access in this specific case."
#"What is the capital of France?"

# Tokenize the input prompt
inputs = tokenizer(prompt, return_tensors="pt")

# Create attention mask if padding is needed
attention_mask = inputs['attention_mask'] if 'attention_mask' in inputs else None

# Generate the output from the model with attention mask
output = model.generate(inputs['input_ids'], max_new_tokens=300, ) #attention_mask=attention_mask, num_return_sequences=1

# Decode and print the output text
generated_text = tokenizer.decode(output[0], skip_special_tokens=True) #
print(generated_text)
"""