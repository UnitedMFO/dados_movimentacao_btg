from flask import Flask, request
import json
import os

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello():
    return 'Hello, World!', 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    # Exibir o JSON recebido no terminal
    print("Dados recebidos:")
    print(json.dumps(data, indent=4))  # Exibe o JSON de forma formatada

    # Extrair o accountNumber e exibir no terminal
    account_number = data.get('response', {}).get('accountNumber', 'unknown')
    print(f"Account Number: {account_number}")

    return 'OK', 200

if __name__ == '__main__':
    app.run(port=5000)