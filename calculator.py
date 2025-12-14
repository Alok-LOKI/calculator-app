from flask import Flask, render_template, request, jsonify, session
import math

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session-based memory

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    expression = data.get('expression', '').strip()
    mode = data.get('mode', 'radians')
    
    print(f"Received expression: '{expression}', Mode: {mode}")  # Debug log
    
    if not expression:
        return jsonify({'error': 'Empty expression'})
    
    # Handle memory operations
    if expression == 'MC':
        session['memory'] = 0
        return jsonify({'result': 0})
    elif expression == 'MR':
        return jsonify({'result': session.get('memory', 0)})
    elif expression.startswith('M+ '):
        try:
            val = float(expression[3:])
            session['memory'] = session.get('memory', 0) + val
            return jsonify({'result': session['memory']})
        except ValueError:
            return jsonify({'error': 'Invalid number for M+'})
    elif expression.startswith('M- '):
        try:
            val = float(expression[3:])
            session['memory'] = session.get('memory', 0) - val
            return jsonify({'result': session['memory']})
        except ValueError:
            return jsonify({'error': 'Invalid number for M-'})
    
    try:
        # Function to convert degrees to radians if needed
        def deg_to_rad(x):
            return math.radians(x) if mode == 'degrees' else x
        
        # Allowed functions for safe eval
        allowed_names = {
            'sin': lambda x: math.sin(deg_to_rad(x)),
            'cos': lambda x: math.cos(deg_to_rad(x)),
            'tan': lambda x: math.tan(deg_to_rad(x)),
            'asin': lambda x: math.degrees(math.asin(x)) if mode == 'degrees' else math.asin(x),
            'acos': lambda x: math.degrees(math.acos(x)) if mode == 'degrees' else math.acos(x),
            'atan': lambda x: math.degrees(math.atan(x)) if mode == 'degrees' else math.atan(x),
            'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
            'log': math.log10, 'ln': math.log, 'exp': math.exp,
            'sqrt': math.sqrt, 'pow': pow, '^': pow, 'pi': math.pi, 'e': math.e,
            'abs': abs, 'fact': math.factorial
        }
        
        result = eval(expression, {"__builtins__": None}, allowed_names)
        print(f"Calculated result: {result}")  # Debug log
        return jsonify({'result': result})
    except ZeroDivisionError:
        return jsonify({'error': 'Division by zero'})
    except ValueError as e:
        return jsonify({'error': f'Value error: {str(e)}'})
    except Exception as e:
        print(f"Eval error: {e}")  # Debug log
        return jsonify({'error': f'Invalid expression: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
