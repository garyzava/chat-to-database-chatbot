import pickle
from pathlib import Path
import sys

current_dir = Path(__file__).parent
model_path = current_dir / 'combined_sql_classifier.pkl'

# Load the pickle file
with open(model_path, 'rb') as file:
    objects = pickle.load(file)

# Extract classifiers and related objects
binary_classifier = objects["binary_classifier"]
classifier_domain = objects["classifier_domain"]
classifier_complexity = objects["classifier_complexity"]
classifier_task_type = objects["classifier_task_type"]
vectorizer = objects["vectorizer"]
label_encoder_domain = objects["label_encoder_domain"]
label_encoder_complexity = objects["label_encoder_complexity"]
label_encoder_task_type = objects["label_encoder_task_type"]


def classify_prompt(prompt):
    # Transform the prompt using the vectorizer
    prompt_tfidf = vectorizer.transform([prompt])

    # Binary Classification (SQL vs Non-SQL)
    is_sql = binary_classifier.predict(prompt_tfidf)[0]

    # If not SQL, return early
    if is_sql == 0:
        return {"Intent": "Not SQL", "Details": None}

    # Predict using the classifiers
    domain_prediction = classifier_domain.predict(prompt_tfidf)[0]
    complexity_prediction = classifier_complexity.predict(prompt_tfidf)[0]
    task_type_prediction = classifier_task_type.predict(prompt_tfidf)[0]

    # Decode predictions
    domain = label_encoder_domain.inverse_transform([domain_prediction])[0]
    complexity = label_encoder_complexity.inverse_transform([complexity_prediction])[0]
    task_type = label_encoder_task_type.inverse_transform([task_type_prediction])[0]

    #return domain, complexity, task_type
    return {
        "Intent": "SQL",
        "Domain": domain,
        "Complexity": complexity,
        "Task Type": task_type
    }    

def print_results(result):
    print("\n" + "="*50)
    print("📊 Classification Results:")
    
    if result["Intent"] == "Not SQL":
        print("🔍 Type: Non-SQL Query")
    else:
        print("🔍 Type: SQL Query")
        print(f"🎯 Domain: {result['Domain']}")
        print(f"⚡ Complexity: {result['Complexity']}")
        print(f"🔧 Task Type: {result['Task Type']}")
    print("="*50 + "\n")

def main():
    print("Welcome to the Prompt Classifier! (type 'exit' to quit)")
    while True:
        try:
            user_input = input("\n🤔 Enter your prompt: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye! 👋")
                sys.exit(0)
                
            if not user_input:
                print("❌ Please enter a valid prompt")
                continue
                
            result = classify_prompt(user_input)
            print_results(result)            
            
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()