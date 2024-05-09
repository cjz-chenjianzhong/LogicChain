gunicorn moonshot_llm_infer:app -w 1 -t 5000 -b 127.0.0.1:5000
gunicorn rule:app -w 1 -t 5000 -b 127.0.0.1:5001
gunicorn agent:app -w 1 -t 5000 -b 127.0.0.1:5002
gunicorn act:app -w 1 -t 5000 -b 127.0.0.1:5003
gunicorn ctrl:app -w 1 -t 5000 -b 127.0.0.1:5004